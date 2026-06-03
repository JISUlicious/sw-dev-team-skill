---
name: your-skill-name
description: What this skill does and when to use it, key terms first, in the third person. Replace this with a specific sentence — e.g. "Analyze Excel spreadsheets, build pivot tables, generate charts. Use when working with .xlsx files or tabular data." Max 1024 characters.
# --- Optional Claude Code fields (delete any you don't need) ---
# disable-model-invocation: true   # only the user can invoke (use for side-effecting actions)
# user-invocable: false            # only Claude can invoke (background knowledge)
# allowed-tools: Read Grep Bash(git status *)
# argument-hint: [issue-number]
# context: fork                    # run in an isolated subagent
# agent: Explore                   # subagent type when context: fork
# paths: src/**/*.ts               # only auto-trigger when working on matching files
---

# Your Skill Name

One or two sentences on what this skill helps with. Assume Claude is already capable —
include only context it does not already have. Keep the whole body under 500 lines; it
stays in context for the rest of the session once loaded.

## Instructions

Give clear, standing guidance. Match specificity to the task:
- Open-ended judgment → general direction (high freedom).
- Fragile, must-be-exact sequences → precise steps / exact commands (low freedom).

1. First step.
2. Second step.
3. Third step.

## Examples

Show a concrete input → output pair when output quality depends on format or style.

## Additional resources

Link bundled files one level deep so Claude loads them only when needed:

- For detailed API docs, see [reference/reference.md](reference/reference.md)
- For more examples, see [reference/examples.md](reference/examples.md)
- Run the helper script: `python3 ${CLAUDE_SKILL_DIR}/scripts/helper.py <args>`
