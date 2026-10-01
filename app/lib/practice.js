// Practice mode: the guide behaves as if signed in as a chosen member, reading the real,
// public project, but every change is only recorded in a practice log. Nothing is sent
// to GitHub, so members can try every button before doing it for real.
import { GitHub } from "./github.js";

export class PracticeGitHub extends GitHub {
  constructor(member, fetchImpl) {
    super(null, fetchImpl);
    this.practice = true;
    this.member = member;
    this.log = [];
    this.nextNumber = 9001;
  }

  record(action, detail) {
    this.log.unshift({ action, detail: String(detail ?? "").slice(0, 400), at: new Date() });
    this.onChange?.();
  }

  async whoAmI() {
    return {
      login: this.member.login,
      name: this.member.name,
      avatar: `https://github.com/${this.member.login}.png?size=52`,
      scopes: ["public_repo", "project"],
      canWrite: true,
      practice: true,
    };
  }

  async createIssue(fields) {
    const number = this.nextNumber++;
    this.record(`Create task #${number}`, `${fields.title} · labels ${fields.labels?.join(", ")}`);
    return { number, title: fields.title, html_url: "#/help", node_id: "practice" };
  }

  async comment(number, body) {
    this.record(`Comment on #${number}`, body);
    return {};
  }

  async updateIssue(number, fields) {
    const what = fields.state ? `state → ${fields.state}` : fields.assignees ? `assignees → ${fields.assignees.join(", ") || "nobody"}` : "tick a step";
    this.record(`Update #${number}`, what);
    return {};
  }

  async boardStatuses() {
    return new Map();
  }

  async board() {
    return { id: "practice", fields: {} };
  }

  async addToBoard() {
    return "practice-item";
  }

  async setBoardField(itemId, field, value) {
    this.record(`Board: ${field}`, value);
  }

  async setBoardDate(itemId, field, day) {
    this.record(`Board: ${field}`, day);
  }

  async review(number, event, body) {
    this.record(`Review #${number}: ${event.replace("_", " ").toLowerCase()}`, body);
    return {};
  }

  // Runs the form's change on the real file, so form errors show exactly as they would,
  // then records what would have been sent instead of sending it.
  async proposeFileChange({ path, branch, change, title }) {
    let old = null;
    try {
      old = (await this.fileText(path, "main")).text;
    } catch (e) {
      if (e?.status !== 404) throw e;
    }
    const next = change(old);
    if (next === old) throw new Error("Nothing changed, so there is nothing to send.");
    const number = this.nextNumber++;
    this.record(`Pull request #${number}: ${title}`, `branch ${branch}, file ${path} (${old === null ? "new file" : "changed"})`);
    return { number, html_url: "#/help", practice: true, path, text: next };
  }
}
