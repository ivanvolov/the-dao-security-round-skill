#!/usr/bin/env node
const { execFileSync } = require("node:child_process");
const { existsSync, mkdirSync } = require("node:fs");
const { homedir } = require("node:os");
const path = require("node:path");

const REPO = "https://github.com/ivanvolov/the-dao-security-round-skill.git";
const SKILL_DIR_NAME = "the-dao-security-round-skill";

const skillsDir = path.join(homedir(), ".claude", "skills");
const target = path.join(skillsDir, SKILL_DIR_NAME);

mkdirSync(skillsDir, { recursive: true });

const run = (cmd, args, opts = {}) =>
  execFileSync(cmd, args, { stdio: "inherit", ...opts });

if (existsSync(target)) {
  console.log(`Updating existing install at ${target}`);
  try {
    run("git", ["-C", target, "pull", "--ff-only"]);
  } catch {
    console.error("git pull failed — leaving existing install untouched.");
    process.exit(1);
  }
} else {
  console.log(`Installing skill to ${target}`);
  run("git", ["clone", "--depth", "1", REPO, target]);
}

console.log("");
console.log("Done. Restart Claude Code, then ask things like:");
console.log("  - Which projects work on fuzzing?");
console.log("  - What SEAL org projects are in the round?");
