# Working as part of a software team

You are not the only one editing this codebase. Other developers and other AI agents may be touching adjacent code right now, and the work you do here will be read, extended, and reviewed by people who weren't in the conversation that produced it.

The biggest failure mode of multi-contributor coding — especially with parallel AI agents — is **fragmentation**: two helpers that do the same thing, three styles of error handling in one module, drive-by refactors tangled into feature PRs. None of these come from one bad decision; they come from each contributor optimizing locally, in isolation, without checking the room.

**Tradeoff:** these guidelines bias toward caution over speed. For trivial tasks, use judgment — §8 says when to relax.

This doc encodes four principles. When sections seem to conflict, fall back to these:

- **[A] Coherence preservation** — the codebase reads as one author across contributors.
- **[B] Visibility of in-flight state** — others see what you're doing *before* it lands.
- **[C] Conservation of shared invariants** — when you change shared things, others don't break.
- **[D] Proportionality** — process matches scope; both over- and under-process are failures.

## 1. Surface uncertainty before coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

- State your assumptions explicitly. If you're uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

Why: silent assumptions become silent bugs. A question now is cheaper than a rewrite later, and the cost compounds — everything you build on top of a wrong assumption inherits the mistake.

## 2. Read the room

**Orient before touching code.**

- Look at the most recently modified files in the area you're about to edit (`git log --oneline -n 20 -- <path>`). Note their patterns for naming, errors, tests, imports.
- Skim recent commit messages on the branch and on `main`. Is someone mid-stream on related work? Is there a migration in progress your change should fit into?
- Check for other active branches or worktrees that signal parallel work in your area.
- Read any of these that exist and are relevant to your scope: `CLAUDE.md`, `AGENTS.md`, `README`, `ARCHITECTURE.md`, `docs/adr/`.

Why: conventions live in the code, not in a doc. The point isn't exhaustive research — it's avoiding the embarrassing mistake of writing a feature in a style the team abandoned three weeks ago.

## 3. Define success before you start

**Turn the task into something you can verify.**

- Reframe ambiguous asks into testable goals: "Add validation" → "Write tests for invalid inputs, then make them pass." "Fix the bug" → "Write a test that reproduces it, then make it pass." "Refactor X" → "Ensure tests pass before and after."
- For multi-step work, write a brief plan with a verify-check after each step.
- For non-trivial work, commit a plan file (e.g., `PLAN.md` on the feature branch) *before* coding. Format: `# Goal` (success criteria) → `## Steps` (numbered, each with a verify-check) → `## Out of scope`. Update step status as you go. Why: forward-looking visibility that `git log` can't give.

Why: strong success criteria let you loop independently and know when you're done. Weak criteria ("make it work") require constant clarification and produce unfocused changes.

## 4. Coordinate around shared interfaces

**Touching shared things is a coordination point. Surface it.**

- Public function signatures, exported types, database schemas, API endpoints — flag in your plan before changing. Quietly redefining a contract that other contributors are calling against is how parallel work breaks.
- Prefer **additive over invasive**: add the new name and deprecate the old; add the new field and migrate consumers. Renames, moves, and broad reformats can silently break work that other agents have in flight on a different branch.
- For a brand-new module or contract, sketch the public surface — types, signatures, the 5-10 line shape of the API — *before* implementing the body. Showing the sketch first gives other contributors a target to integrate against rather than a moving one.
- Before changing a shared interface, check active plan files / branches that signal in-flight work.

Why: in a parallel-work environment, you can't be sure who else is mid-edit on the same area. Additive changes coexist with in-flight work; invasive ones collide with it.

## 5. Reuse over reinvent

**Grep before you build. Match what's already there.**

- Search for any utility, helper, type, or constant before writing it. If something almost-but-not-quite right exists, prefer extending it over forking it.
- Match the style of the code around your change, even when you'd write it differently from scratch. Idiomatic-for-this-repo beats idiomatic-in-general.
- If the codebase is genuinely split between conventions (three files use approach A, three use approach B), surface the inconsistency and let the user decide. Don't pick a third style.

Why: two parallel implementations is the most common form of mess, and a 30-second grep prevents a 30-minute future cleanup. Style drift is the most visible "messy" symptom across a codebase and the hardest to clean up later.

## 6. Surgical changes

**Touch only what you must. Clean up only your own mess.**

- Don't "improve" adjacent code, comments, or formatting that you didn't come here to change. Such changes widen the diff, risk colliding with another agent who *did* come there to refactor that thing, and hide the actual change behind incidental noise.
- If you spot a real bug or smell outside scope, note it (in the conversation, in a TODO, in an issue) — don't silently fix it.
- Remove imports/variables/functions that *your* changes made unused. Don't remove pre-existing dead code unless asked.
- Ask yourself: would a senior engineer say this is overcomplicated? If yes, simplify.
- Before submitting, re-read the full diff with one question: *would a stranger see this as one author's coherent change, or as a feature plus three unrelated drive-bys?* Anything that fails the stranger-read should be dropped or called out explicitly.

Why: every changed line should trace directly to the user's request. Scope creep makes reviews harder, increases collision risk with other agents, and inflates the surface area future contributors have to reason about.

## 7. Write handoffs others will discover

**Other contributors find your decisions through `git log`, not this conversation.**

Commit messages and PR descriptions should state:

- **Scope**: what changed and what was deliberately not touched.
- **New contracts**: any new public interface, type, schema, or convention introduced. This is what others will grep for.
- **Follow-ups**: anything you didn't do that someone will need to.

Keep it tight — a few lines, not an essay. The target reader is another contributor six commits later trying to figure out whether your change affects what they're about to do.

## 8. Calibrate ceremony to scope

**The right amount of process is the smallest amount that prevents the codebase from getting messy.**

Both over- and under-process produce equally messy outcomes. Sections 1-7 describe the disciplines; this section says when to relax them.

**Non-trivial** = touches more than a couple of files, has a verifiable success criterion beyond "compiles", or you'd want to explain the change to a teammate. Sections 1-7 apply in full to non-trivial work.

When to relax:

- **Trivial fix** (typo, one-line bug, comment fix): skip §3's plan file and §7's handoff template. A clear commit message is enough.
- **Solo developer with no parallel work**: §2's parallel-branches check and §4's coordination ceremony are mostly overhead. Conventions, scope, and reuse rules still apply — future-you is your teammate.
- **Spike or prototype**: mark it clearly (file header, branch name, PR title). §5 reuse and §6 simplicity matter less inside the spike, but the *boundary* of the spike must be obvious so it's not reused as production.

The check: if you find yourself reaching for a sprawling new doc, file, or process, ask whether a paragraph at the top of the new file does the same job. Usually it does.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
