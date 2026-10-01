// The GitHub client against a fake GitHub that records every request.
import { test } from "node:test";
import assert from "node:assert/strict";
import { GitHub, GitHubError, decodeBase64, encodeBase64, explain } from "../lib/github.js";

function fakeGitHub(routes) {
  const calls = [];
  const fetch = async (url, init) => {
    const path = url.replace("https://api.github.com", "");
    const body = init.body ? JSON.parse(init.body) : undefined;
    calls.push({ method: init.method, path, body, auth: init.headers.Authorization });
    for (const [pattern, handler] of routes) {
      const [method, re] = pattern;
      if (method === init.method && re.test(path)) {
        const [status, data] = handler(path, body);
        return new Response(data === null ? "" : JSON.stringify(data), {
          status,
          headers: { "x-oauth-scopes": "project, public_repo" },
        });
      }
    }
    return new Response(JSON.stringify({ message: "Not Found" }), { status: 404 });
  };
  return { calls, fetch };
}

test("base64 round-trips UTF-8 text", () => {
  const text = "Café · naïve · 12,965 skills\r\n";
  assert.equal(decodeBase64(encodeBase64(text)), text);
});

test("whoAmI reports the login, scopes, and write access", async () => {
  const { fetch, calls } = fakeGitHub([
    [["GET", /^\/user$/], () => [200, { login: "AllieHgs", name: "Allie" }]],
    [["GET", /^\/repos\/jeraddunne\/csc580-group9-msr2027$/], () => [200, { permissions: { push: true } }]],
  ]);
  const me = await new GitHub("tok", fetch).whoAmI();
  assert.equal(me.login, "AllieHgs");
  assert.deepEqual(me.scopes, ["project", "public_repo"]);
  assert.equal(me.canWrite, true);
  assert.equal(calls[0].auth, "Bearer tok");
});

test("proposeFileChange branches from main, commits one file, opens a PR, and asks for review", async () => {
  const charter = "## 14. Signatures\n\n| Allie Hodges | Not signed | none |\n";
  const { fetch, calls } = fakeGitHub([
    [["GET", /\/git\/ref\/heads\/main$/], () => [200, { object: { sha: "abc123" } }]],
    [["GET", /\/git\/ref\/heads\/process\/51-sign$/], () => [200, { object: { sha: "taken" } }]],
    [["GET", /\/git\/ref\/heads\/process\/51-sign-2$/], () => [404, { message: "Not Found" }]],
    [["GET", /\/contents\/TEAM_CHARTER\.md\?ref=abc123$/], () => [200, { content: encodeBase64(charter), sha: "blob1" }]],
    [["POST", /\/git\/refs$/], () => [201, {}]],
    [["PUT", /\/contents\/TEAM_CHARTER\.md$/], () => [200, {}]],
    [["POST", /\/pulls$/], () => [201, { number: 80, html_url: "https://github.com/x/pull/80" }]],
    [["POST", /\/pulls\/80\/requested_reviewers$/], () => [201, {}]],
  ]);
  const pr = await new GitHub("tok", fetch).proposeFileChange({
    path: "TEAM_CHARTER.md",
    branch: "process/51-sign",
    change: (old) => old.replace("Not signed | none", "2026-10-02 | #51"),
    message: "Sign the team charter",
    title: "Sign the team charter",
    body: "Closes #51",
    reviewers: ["angel06la"],
  });
  assert.equal(pr.number, 80);
  const writes = calls.filter((c) => c.method !== "GET");
  assert.deepEqual(
    writes.map((c) => `${c.method} ${c.path.replace("/repos/jeraddunne/csc580-group9-msr2027", "")}`),
    ["POST /git/refs", "PUT /contents/TEAM_CHARTER.md", "POST /pulls", "POST /pulls/80/requested_reviewers"]
  );
  assert.equal(writes[0].body.ref, "refs/heads/process/51-sign-2", "an existing branch name gets -2");
  assert.equal(writes[0].body.sha, "abc123");
  assert.equal(writes[1].body.sha, "blob1");
  assert.equal(writes[1].body.branch, "process/51-sign-2");
  assert.ok(decodeBase64(writes[1].body.content).includes("| Allie Hodges | 2026-10-02 | #51 |"));
  assert.deepEqual(writes[2].body, { title: "Sign the team charter", head: "process/51-sign-2", base: "main", body: "Closes #51" });
});

test("a form error stops before anything is written to GitHub", async () => {
  const { fetch, calls } = fakeGitHub([
    [["GET", /\/git\/ref\/heads\/main$/], () => [200, { object: { sha: "abc123" } }]],
    [["GET", /\/contents\//], () => [200, { content: encodeBase64("text"), sha: "b" }]],
  ]);
  await assert.rejects(
    new GitHub("tok", fetch).proposeFileChange({
      path: "TEAM_CHARTER.md",
      branch: "process/51-sign",
      change: () => {
        throw new Error("Allie Hodges already signed on 2026-10-02.");
      },
      message: "m",
      title: "t",
      body: "b",
    }),
    /already signed/
  );
  assert.ok(calls.every((c) => c.method === "GET"));
});

test("a new file is created without a sha", async () => {
  const { fetch, calls } = fakeGitHub([
    [["GET", /\/git\/ref\/heads\/main$/], () => [200, { object: { sha: "abc" } }]],
    [["POST", /\/git\/refs$/], () => [201, {}]],
    [["PUT", /\/contents\/docs\/meeting-notes\/2026-10-01-checkin\.md$/], () => [201, {}]],
    [["POST", /\/pulls$/], () => [201, { number: 81 }]],
  ]);
  await new GitHub("tok", fetch).proposeFileChange({
    path: "docs/meeting-notes/2026-10-01-checkin.md",
    branch: "docs/meeting-notes-2026-10-01",
    change: (old) => (assert.equal(old, null), "# Checkin meeting 2026-10-01\n"),
    message: "m",
    title: "t",
    body: "b",
  });
  const put = calls.find((c) => c.method === "PUT");
  assert.equal(put.body.sha, undefined);
});

test("errors are explained in plain words", () => {
  assert.match(explain(new GitHubError(401, "Bad credentials")), /did not accept your key/);
  assert.match(explain(new GitHubError(403, "API rate limit exceeded")), /hourly limit/);
  assert.match(explain(new GitHubError(403, "Resource not accessible")), /public_repo and project/);
});

test("issues() drops pull requests, which GitHub lists with issues", async () => {
  const { fetch } = fakeGitHub([
    [["GET", /\/issues\?/], () => [200, [{ number: 1 }, { number: 2, pull_request: {} }]]],
  ]);
  const issues = await new GitHub(null, fetch).issues();
  assert.deepEqual(issues.map((i) => i.number), [1]);
});

test("practice mode runs the form's change on the real file but never writes", async () => {
  const { PracticeGitHub } = await import("../lib/practice.js");
  const { fetch, calls } = fakeGitHub([
    [["GET", /\/contents\/TEAM_CHARTER\.md\?ref=main$/], () => [200, { content: encodeBase64("| Allie Hodges | Not signed | none |\n"), sha: "b" }]],
  ]);
  const gh = new PracticeGitHub({ login: "AllieHgs", name: "Allie Hodges" }, fetch);
  const pr = await gh.proposeFileChange({
    path: "TEAM_CHARTER.md",
    branch: "process/51-sign",
    change: (old) => old.replace("Not signed | none", "2026-10-02 | #51"),
    title: "Sign the team charter",
  });
  assert.equal(pr.practice, true);
  assert.ok(pr.text.includes("2026-10-02 | #51"));
  await gh.comment(51, "hello");
  await gh.createIssue({ title: "t", labels: [] });
  await gh.review(72, "APPROVE", "checked");
  assert.ok(calls.every((c) => c.method === "GET"), "practice mode only reads");
  assert.equal(gh.log.length, 4);
  assert.equal((await gh.whoAmI()).practice, true);
});
