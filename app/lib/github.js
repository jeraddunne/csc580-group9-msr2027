// A small GitHub client for the app. Every write uses the signed-in member's own key, so
// GitHub records the member as the author of each issue, comment, commit, pull request,
// and review. The key never leaves the browser except in requests to api.github.com.

export const OWNER = "jeraddunne";
export const REPO = "csc580-group9-msr2027";
export const PROJECT_NUMBER = 1;
const API = "https://api.github.com";

export class GitHubError extends Error {
  constructor(status, message, detail) {
    super(message);
    this.status = status;
    this.detail = detail;
  }
}

// Plain-language explanations for the errors members are likely to meet.
export function explain(error) {
  if (!(error instanceof GitHubError)) return error?.message || String(error);
  switch (error.status) {
    case 401:
      return "GitHub did not accept your key. It may have expired: make a new one on the sign-in page.";
    case 403:
      return /rate limit/i.test(error.message)
        ? "GitHub's hourly limit for this computer was reached. Sign in, or wait a few minutes."
        : "Your key is not allowed to do this. Check that it has the public_repo and project boxes ticked, and that you accepted the repository invitation.";
    case 404:
      return "GitHub could not find that. If you just accepted the invitation, wait a minute and try again.";
    case 409:
    case 422:
      return `GitHub refused the change: ${error.message}`;
    default:
      return `GitHub error ${error.status}: ${error.message}`;
  }
}

// base64 of UTF-8 text and back, for the contents API.
export function encodeBase64(text) {
  const bytes = new TextEncoder().encode(text);
  let binary = "";
  for (let i = 0; i < bytes.length; i += 0x8000) binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return btoa(binary);
}

export function decodeBase64(b64) {
  const binary = atob(b64.replace(/\s/g, ""));
  const bytes = Uint8Array.from(binary, (c) => c.charCodeAt(0));
  return new TextDecoder().decode(bytes);
}

export class GitHub {
  constructor(token, fetchImpl = globalThis.fetch.bind(globalThis)) {
    this.token = token || null;
    this.fetch = fetchImpl;
    this.cache = new Map();
    this.project = null;
  }

  async request(method, path, body, { accept = "application/vnd.github+json", cache = false } = {}) {
    const url = path.startsWith("http") ? path : `${API}${path}`;
    if (cache && method === "GET" && this.cache.has(url + accept)) return this.cache.get(url + accept);
    const headers = { Accept: accept, "X-GitHub-Api-Version": "2022-11-28" };
    if (this.token) headers.Authorization = `Bearer ${this.token}`;
    if (body !== undefined) headers["Content-Type"] = "application/json";
    const res = await this.fetch(url, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
    const text = await res.text();
    const data = text ? JSON.parse(text) : null;
    if (!res.ok) {
      const detail = data?.errors?.map((e) => e.message || e.code).join("; ");
      throw new GitHubError(res.status, data?.message || res.statusText || "request failed", detail);
    }
    const out = { data, headers: res.headers };
    if (cache && method === "GET") this.cache.set(url + accept, out);
    return out;
  }

  async get(path, opts) {
    return (await this.request("GET", path, undefined, opts)).data;
  }

  clearCache() {
    this.cache.clear();
  }

  repo(path = "") {
    return `/repos/${OWNER}/${REPO}${path}`;
  }

  // Who the key belongs to, its scopes, and whether it can write to the repository.
  async whoAmI() {
    const { data: user, headers } = await this.request("GET", "/user");
    const scopes = (headers.get?.("x-oauth-scopes") || "").split(",").map((s) => s.trim()).filter(Boolean);
    const repo = await this.get(this.repo());
    return {
      login: user.login,
      name: user.name || user.login,
      avatar: user.avatar_url,
      scopes,
      canWrite: Boolean(repo.permissions?.push),
      fineGrained: scopes.length === 0,
    };
  }

  async paginate(path, max = 500) {
    const out = [];
    for (let page = 1; out.length < max; page += 1) {
      const sep = path.includes("?") ? "&" : "?";
      const batch = await this.get(`${path}${sep}per_page=100&page=${page}`);
      out.push(...batch);
      if (batch.length < 100) break;
    }
    return out;
  }

  milestones() {
    return this.paginate(this.repo("/milestones?state=all&sort=due_on&direction=asc"));
  }

  labels() {
    return this.paginate(this.repo("/labels"));
  }

  assignees() {
    return this.paginate(this.repo("/assignees"));
  }

  // Issues only (GitHub's issues endpoint also returns pull requests).
  async issues({ state = "all", assignee, milestone } = {}) {
    let q = `/issues?state=${state}&sort=updated&direction=desc`;
    if (assignee) q += `&assignee=${encodeURIComponent(assignee)}`;
    if (milestone) q += `&milestone=${milestone}`;
    return (await this.paginate(this.repo(q))).filter((i) => !i.pull_request);
  }

  // One issue with its text both raw (for checklists) and as GitHub's own safe HTML.
  issue(number) {
    return this.get(this.repo(`/issues/${number}`), { accept: "application/vnd.github.full+json" });
  }

  commentsHtml(number) {
    return this.get(this.repo(`/issues/${number}/comments?per_page=100`), {
      accept: "application/vnd.github.full+json",
    });
  }

  comment(number, body) {
    return this.request("POST", this.repo(`/issues/${number}/comments`), { body }).then((r) => r.data);
  }

  updateIssue(number, fields) {
    return this.request("PATCH", this.repo(`/issues/${number}`), fields).then((r) => r.data);
  }

  createIssue(fields) {
    return this.request("POST", this.repo("/issues"), fields).then((r) => r.data);
  }

  pulls(state = "open") {
    return this.paginate(this.repo(`/pulls?state=${state}&sort=updated&direction=desc`), 200);
  }

  pull(number) {
    return this.get(this.repo(`/pulls/${number}`), { accept: "application/vnd.github.full+json" });
  }

  pullFiles(number) {
    return this.paginate(this.repo(`/pulls/${number}/files`), 300);
  }

  reviews(number) {
    return this.get(this.repo(`/pulls/${number}/reviews?per_page=100`));
  }

  review(number, event, body) {
    return this.request("POST", this.repo(`/pulls/${number}/reviews`), { event, body }).then((r) => r.data);
  }

  async fileText(path, ref = "main") {
    const data = await this.get(this.repo(`/contents/${encodePath(path)}?ref=${encodeURIComponent(ref)}`));
    return { text: decodeBase64(data.content), sha: data.sha };
  }

  async fileExists(path, ref = "main") {
    try {
      await this.get(this.repo(`/contents/${encodePath(path)}?ref=${encodeURIComponent(ref)}`));
      return true;
    } catch (e) {
      if (e instanceof GitHubError && e.status === 404) return false;
      throw e;
    }
  }

  // The whole browser-only pull request: branch from main, commit one file, open the PR,
  // and ask for a review. `change(oldText)` returns the new text (oldText is null for a
  // new file). Returns the pull request.
  async proposeFileChange({ path, branch, change, message, title, body, reviewers = [] }) {
    // Read and change the file first, so a form error leaves nothing behind on GitHub.
    const main = await this.get(this.repo("/git/ref/heads/main"));
    let old = null;
    let sha;
    try {
      const f = await this.fileText(path, main.object.sha);
      old = f.text;
      sha = f.sha;
    } catch (e) {
      if (!(e instanceof GitHubError && e.status === 404)) throw e;
    }
    const next = change(old);
    if (next === old) throw new Error("Nothing changed, so there is nothing to send.");
    const name = await this.freeBranchName(branch);
    await this.request("POST", this.repo("/git/refs"), { ref: `refs/heads/${name}`, sha: main.object.sha });
    const put = { message, content: encodeBase64(next), branch: name };
    if (sha) put.sha = sha;
    await this.request("PUT", this.repo(`/contents/${encodePath(path)}`), put);
    const pr = (await this.request("POST", this.repo("/pulls"), { title, head: name, base: "main", body })).data;
    const others = reviewers.filter(Boolean);
    if (others.length) {
      try {
        await this.request("POST", this.repo(`/pulls/${pr.number}/requested_reviewers`), { reviewers: others });
      } catch {
        // The pull request exists; a failed review request is not worth failing the whole change.
      }
    }
    return pr;
  }

  async freeBranchName(branch) {
    for (let i = 1; i < 50; i += 1) {
      const name = i === 1 ? branch : `${branch}-${i}`;
      try {
        await this.get(this.repo(`/git/ref/heads/${encodePath(name)}`));
      } catch (e) {
        if (e instanceof GitHubError && e.status === 404) return name;
        throw e;
      }
    }
    throw new Error("Could not find a free branch name.");
  }

  // ---- Project board (GitHub Projects), needs the "project" scope ------------------------

  async graphql(query, variables = {}) {
    const { data } = await this.request("POST", `${API}/graphql`, { query, variables });
    if (data.errors?.length) throw new GitHubError(200, data.errors.map((e) => e.message).join("; "));
    return data.data;
  }

  // The board's id and its single-select fields (Status, Sprint, Priority, Work type) by name.
  async board() {
    if (this.project) return this.project;
    const d = await this.graphql(
      `query($owner: String!, $number: Int!) {
        user(login: $owner) { projectV2(number: $number) { id title url
          fields(first: 40) { nodes {
            ... on ProjectV2FieldCommon { id name dataType }
            ... on ProjectV2SingleSelectField { options { id name } } } } } } }`,
      { owner: OWNER, number: PROJECT_NUMBER }
    );
    const p = d.user.projectV2;
    const fields = {};
    for (const f of p.fields.nodes) if (f?.name) fields[f.name] = f;
    this.project = { id: p.id, title: p.title, url: p.url, fields };
    return this.project;
  }

  // Board status and item id of each issue, keyed by issue number.
  async boardStatuses() {
    const out = new Map();
    let cursor = null;
    for (let page = 0; page < 10; page += 1) {
      const d = await this.graphql(
        `query($owner: String!, $number: Int!, $after: String) {
          user(login: $owner) { projectV2(number: $number) {
            items(first: 100, after: $after) { pageInfo { hasNextPage endCursor }
              nodes { id
                status: fieldValueByName(name: "Status") { ... on ProjectV2ItemFieldSingleSelectValue { name } }
                content { ... on Issue { number } ... on PullRequest { number } } } } } } }`,
        { owner: OWNER, number: PROJECT_NUMBER, after: cursor }
      );
      const items = d.user.projectV2.items;
      for (const n of items.nodes) if (n.content?.number) out.set(n.content.number, { itemId: n.id, status: n.status?.name || "" });
      if (!items.pageInfo.hasNextPage) break;
      cursor = items.pageInfo.endCursor;
    }
    return out;
  }

  async addToBoard(issueNodeId) {
    const board = await this.board();
    const d = await this.graphql(
      `mutation($project: ID!, $content: ID!) {
        addProjectV2ItemById(input: { projectId: $project, contentId: $content }) { item { id } } }`,
      { project: board.id, content: issueNodeId }
    );
    return d.addProjectV2ItemById.item.id;
  }

  // Set a single-select field (for example Status to "In progress") by names.
  async setBoardField(itemId, fieldName, optionName) {
    const board = await this.board();
    const field = board.fields[fieldName];
    const option = field?.options?.find((o) => o.name.toLowerCase() === String(optionName).toLowerCase());
    if (!field || !option) throw new Error(`The board has no ${fieldName} option called ${optionName}.`);
    await this.graphql(
      `mutation($project: ID!, $item: ID!, $field: ID!, $option: String!) {
        updateProjectV2ItemFieldValue(input: { projectId: $project, itemId: $item, fieldId: $field,
          value: { singleSelectOptionId: $option } }) { projectV2Item { id } } }`,
      { project: board.id, item: itemId, field: field.id, option: option.id }
    );
  }

  async setBoardDate(itemId, fieldName, isoDay) {
    const board = await this.board();
    const field = board.fields[fieldName];
    if (!field) return;
    await this.graphql(
      `mutation($project: ID!, $item: ID!, $field: ID!, $date: Date!) {
        updateProjectV2ItemFieldValue(input: { projectId: $project, itemId: $item, fieldId: $field,
          value: { date: $date } }) { projectV2Item { id } } }`,
      { project: board.id, item: itemId, field: field.id, date: isoDay }
    );
  }
}

function encodePath(path) {
  return path.split("/").map(encodeURIComponent).join("/");
}
