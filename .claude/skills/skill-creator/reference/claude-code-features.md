# Claude Code Skills — Features Reference

Captured from the official Claude Code skills docs on 2026-06-03.
Source: https://code.claude.com/docs/en/skills

Claude Code skills follow the open [Agent Skills](https://agentskills.io) standard (see
`specification.md`) and add the extras below: invocation control, subagent execution, and
dynamic context injection. Custom commands have been merged into skills —
`.claude/commands/deploy.md` and `.claude/skills/deploy/SKILL.md` both create `/deploy`.

## Contents
- Where skills live (locations & precedence)
- How a skill gets its command name
- Discovery (parent/nested dirs, additional dirs, live reload)
- Frontmatter field reference (full table)
- String substitutions
- Dynamic context injection (`!` command)
- Control who invokes a skill
- Skill content lifecycle (compaction)
- Pre-approve tools (`allowed-tools`)
- Pass arguments
- Run skills in a subagent (`context: fork`)
- Restrict Claude's skill access
- Troubleshooting

## Where skills live

| Location | Path | Applies to |
| :-- | :-- | :-- |
| Enterprise | managed settings | All users in the org |
| Personal | `~/.claude/skills/<name>/SKILL.md` | All your projects |
| Project | `.claude/skills/<name>/SKILL.md` | This project only |
| Plugin | `<plugin>/skills/<name>/SKILL.md` | Where the plugin is enabled |

Precedence when names collide: **enterprise > personal > project**. Plugin skills use a
`plugin-name:skill-name` namespace and never conflict. If a skill and a `.claude/commands/`
command share a name, the skill wins.

## How a skill gets its command name

The `/command` you type comes from **where the file lives**, not the frontmatter `name`
(which only sets the display label) — except for a plugin-root `SKILL.md`.

| Location | Command name source | Example |
| :-- | :-- | :-- |
| `~/.claude/skills/` or `.claude/skills/<dir>/SKILL.md` | Directory name | `deploy-staging/` → `/deploy-staging` |
| `.claude/commands/<file>.md` | File name | `deploy.md` → `/deploy` |
| Plugin `skills/<dir>/SKILL.md` | Directory name, namespaced | `my-plugin/skills/review/` → `/my-plugin:review` |
| Plugin root `SKILL.md` | Frontmatter `name` (dir name fallback) | `name: review` → `/my-plugin:review` |

## Discovery

- **Parent + nested dirs:** project skills load from `.claude/skills/` in the start
  directory and every parent up to the repo root; nested package dirs
  (`packages/frontend/.claude/skills/`) are discovered on demand (monorepo-friendly).
- **Additional dirs:** `--add-dir`/`/add-dir` load `.claude/skills/` from the added dir
  (an exception — other config is not loaded). The `permissions.additionalDirectories`
  *setting* grants file access only and does **not** load skills.
- **Live change detection:** edits to `SKILL.md` under watched dirs take effect within the
  session. Creating a brand-new top-level skills directory needs a restart. For skill folders
  that are also plugins, `hooks/`, `.mcp.json`, `agents/` changes need `/reload-plugins`.

## Frontmatter field reference

All fields are optional; only `description` is recommended.

| Field | Description |
| :-- | :-- |
| `name` | Display name in listings. Defaults to the directory name. |
| `description` | What the skill does and when to use it; Claude uses it to decide when to apply the skill. Combined `description` + `when_to_use` truncated at 1,536 chars in the listing — put the key use case first. |
| `when_to_use` | Extra trigger context / example requests. Appended to `description`; counts toward the 1,536-char cap. |
| `argument-hint` | Autocomplete hint, e.g. `[issue-number]` or `[filename] [format]`. |
| `arguments` | Named positional args for `$name` substitution. Space-separated string or YAML list; names map to positions in order. |
| `disable-model-invocation` | `true` stops Claude from auto-loading the skill (manual `/name` only) and from preloading into subagents. Default `false`. |
| `user-invocable` | `false` hides it from the `/` menu (background knowledge Claude shouldn't be invoked directly). Default `true`. |
| `allowed-tools` | Tools usable without a permission prompt while the skill is active. Space/comma string or YAML list. Does not restrict other tools. |
| `disallowed-tools` | Tools removed from the pool while the skill is active (e.g. block `AskUserQuestion` for a background loop). Clears on your next message. |
| `model` | Model to use while the skill is active (rest of the current turn). Same values as `/model`, or `inherit`. |
| `effort` | Effort level while active: `low`, `medium`, `high`, `xhigh`, `max` (model-dependent). |
| `context` | `fork` runs the skill in a forked subagent context. |
| `agent` | Subagent type when `context: fork` (built-in `Explore`/`Plan`/`general-purpose`, or a custom agent). Defaults to `general-purpose`. |
| `hooks` | Hooks scoped to this skill's lifecycle. |
| `paths` | Glob patterns limiting when the skill auto-activates (same format as path-specific memory rules). Comma string or YAML list. |
| `shell` | Shell for `` !`cmd` `` and ` ```! ` blocks: `bash` (default) or `powershell`. |

## String substitutions

| Variable | Meaning |
| :-- | :-- |
| `$ARGUMENTS` | All arguments as typed. If absent from the body, args are appended as `ARGUMENTS: <value>`. |
| `$ARGUMENTS[N]` / `$N` | The Nth argument, 0-based (`$0`, `$1`, …). Shell-style quoting; quote multi-word values. |
| `$name` | Named argument declared in the `arguments` frontmatter list, mapped by position. |
| `${CLAUDE_SESSION_ID}` | Current session ID (logging, session-specific files). |
| `${CLAUDE_EFFORT}` | Current effort level (`low`…`max`; ultracode reports as `xhigh`). |
| `${CLAUDE_SKILL_DIR}` | Directory containing this `SKILL.md`. Use it to reference bundled scripts/files regardless of the working directory. For plugin skills, the skill subdir (not the plugin root). |

## Dynamic context injection

`` !`<command>` `` runs a shell command **before** the skill content reaches Claude; the
output replaces the placeholder, so Claude sees real data, not the command. This is
preprocessing — Claude does not execute it.

```yaml
---
name: pr-summary
description: Summarize changes in a pull request
allowed-tools: Bash(gh *)
---

## Pull request context
- PR diff: !`gh pr diff`
- Changed files: !`gh pr diff --name-only`

## Your task
Summarize this pull request...
```

Notes:
- Substitution runs **once** over the original file; injected output is not re-scanned.
- The inline form is only recognized when `!` is at line start or after whitespace
  (`KEY=!`cmd`` is left literal).
- For multi-line commands use a fenced block opened with ` ```! `.
- Disable globally with `"disableSkillShellExecution": true` in settings.
- Include `ultrathink` anywhere in the content to request deeper reasoning.

## Control who invokes a skill

| Frontmatter | You can invoke | Claude can invoke | When loaded |
| :-- | :-- | :-- | :-- |
| (default) | Yes | Yes | Description always in context; body loads when invoked |
| `disable-model-invocation: true` | Yes | No | Description **not** in context; body loads when you invoke |
| `user-invocable: false` | No | Yes | Description always in context; body loads when invoked |

Use `disable-model-invocation: true` for side-effecting actions (`/commit`, `/deploy`) you
don't want Claude triggering on its own. Use `user-invocable: false` for background
knowledge that isn't a meaningful user command.

## Skill content lifecycle

When invoked, the rendered `SKILL.md` enters the conversation as one message and **stays
for the rest of the session** — Claude Code does not re-read the file on later turns. Write
guidance as standing instructions, not one-time steps. Auto-compaction re-attaches the most
recent invocation of each skill (first 5,000 tokens each, 25,000-token combined budget,
filled newest-first). If a large skill stops influencing behavior, re-invoke it.

## Pre-approve tools

`allowed-tools` grants permission for the listed tools while the skill is active (no
per-use prompt). It does **not** restrict other tools — your permission settings still
govern those. For project skills, it takes effect after you accept the workspace trust
dialog. Example:

```yaml
allowed-tools: Bash(git add *) Bash(git commit *) Bash(git status *)
```

## Pass arguments

```yaml
---
name: fix-issue
description: Fix a GitHub issue
disable-model-invocation: true
---

Fix GitHub issue $ARGUMENTS following our coding standards.
```

`/fix-issue 123` → "Fix GitHub issue 123 …". Use `$ARGUMENTS[0]`/`$0` for positional access.

## Run skills in a subagent

`context: fork` runs the skill in isolation; the SKILL.md body becomes the subagent's
prompt (no conversation history). Only meaningful for skills with an explicit **task** —
pure guidelines produce no actionable prompt. Pick the executor with `agent:` (built-in
`Explore`/`Plan` skip CLAUDE.md and git status to stay small).

```yaml
---
name: deep-research
description: Research a topic thoroughly
context: fork
agent: Explore
---

Research $ARGUMENTS thoroughly: find relevant files, read them, summarize with references.
```

## Restrict Claude's skill access

Via permission rules (`/permissions`):
```text
Skill                 # deny the Skill tool → disable all skills
Skill(commit)         # allow exact
Skill(review-pr *)    # allow prefix with any args
Skill(deploy *)       # deny
```
Or hide individual skills with `disable-model-invocation: true`. The `skillOverrides`
setting (`on` / `name-only` / `user-invocable-only` / `off`) controls visibility without
editing a skill's frontmatter.

## Troubleshooting

- **Not triggering:** ensure the description includes natural keywords; check it appears in
  "What skills are available?"; rephrase the request; invoke `/name` directly.
- **Triggers too often:** make the description more specific, or add
  `disable-model-invocation: true`.
- **Descriptions cut short:** the listing budget is ~1% of the context window; least-used
  skills' descriptions drop first. Run `/doctor` to check overflow. Raise with
  `skillListingBudgetFraction` / `SLASH_COMMAND_TOOL_CHAR_BUDGET`, or set low-priority
  skills to `name-only`. Per-entry cap is 1,536 chars (`maxSkillDescriptionChars`).
