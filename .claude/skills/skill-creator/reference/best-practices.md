# Agent Skills — Authoring Best Practices

Captured from the official best-practices guide on 2026-06-03.
Source: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices

Good skills are concise, well-structured, and tested with real usage.

## Contents
- Core principles (conciseness, degrees of freedom, model testing)
- Naming conventions
- Writing effective descriptions
- Progressive disclosure patterns
- Workflows and feedback loops
- Content guidelines (no time-sensitive info, consistent terms)
- Common patterns (template, examples, conditional)
- Evaluation and iteration
- Anti-patterns
- Skills with executable code
- Checklist for effective skills

## Core principles

### Concise is key
The context window is a public good — your skill shares it with the system prompt,
conversation history, other skills' metadata, and the actual request. Only Level-1
metadata is preloaded; SKILL.md loads when relevant. But once loaded, every token competes
with everything else, so keep it tight.

**Default assumption: Claude is already very smart.** Add only context Claude lacks.
Challenge each piece: "Does Claude really need this?" "Can I assume Claude knows this?"
"Does this paragraph justify its token cost?" The concise version assumes Claude knows what
PDFs are and how libraries work; the verbose version explains them and wastes ~100 tokens.

### Set appropriate degrees of freedom
Match specificity to the task's fragility and variability:
- **High freedom** (text instructions) — multiple valid approaches, context-dependent
  decisions, heuristics. *Open field, many safe paths.* e.g. code-review guidance.
- **Medium freedom** (pseudocode / parameterized scripts) — a preferred pattern with some
  acceptable variation.
- **Low freedom** (specific scripts, few/no parameters) — fragile, error-prone, or
  consistency-critical operations that must follow an exact sequence. *Narrow bridge with
  cliffs.* e.g. `python scripts/migrate.py --verify --backup` — "Do not modify the command."

### Test with all models you plan to use
Skills add to a model, so effectiveness depends on it. What works for Opus may need more
detail for Haiku. Aim for instructions that work across Haiku, Sonnet, and Opus.

## Naming conventions
Prefer **gerund form** (verb + -ing): `processing-pdfs`, `analyzing-spreadsheets`,
`managing-databases`, `writing-documentation`. Acceptable alternatives: noun phrases
(`pdf-processing`) or action-oriented (`process-pdfs`). **Avoid** vague (`helper`, `utils`,
`tools`), overly generic (`documents`, `data`), reserved words (`anthropic-*`, `claude-*`),
and inconsistent patterns within a collection. (Remember: lowercase/numbers/hyphens only.)

## Writing effective descriptions
The `description` enables discovery — Claude selects among potentially 100+ skills using it.

- **Always third person.** It's injected into the system prompt; mixed point-of-view hurts
  discovery. Good: "Processes Excel files and generates reports." Avoid: "I can help you…"
  / "You can use this to…".
- **Be specific, include key terms** — both *what* it does and *when* to use it.

Effective examples:
```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
description: Analyze Excel spreadsheets, create pivot tables, generate charts. Use when analyzing Excel files, spreadsheets, tabular data, or .xlsx files.
description: Generate descriptive commit messages by analyzing git diffs. Use when the user asks for help writing commit messages or reviewing staged changes.
```
Avoid: `Helps with documents` · `Processes data` · `Does stuff with files`.

## Progressive disclosure patterns
SKILL.md is an overview that points to detail as needed — like a table of contents.
- Keep the SKILL.md body **under 500 lines**; split when approaching the limit.
- **Pattern 1 — High-level guide with references:** quick start in SKILL.md; "see
  [FORMS.md], [REFERENCE.md], [EXAMPLES.md]" for advanced material.
- **Pattern 2 — Domain-specific organization:** split by domain (`reference/finance.md`,
  `reference/sales.md`) so a sales question never loads finance schemas. Offer `grep`
  hints for searching reference files.
- **Pattern 3 — Conditional details:** show basic content inline, link advanced content
  (tracked changes, low-level formats) for when it's actually needed.

**Avoid deeply nested references.** Claude may only partially read files reached through
other referenced files (e.g. `head -100`). Keep references **one level deep from SKILL.md** —
all reference files link directly from SKILL.md.

**Structure long reference files with a table of contents.** For files > 100 lines, put a
contents list at the top so Claude sees the full scope even on a partial read.

## Workflows and feedback loops

### Workflows for complex tasks
Break complex operations into clear sequential steps. For particularly complex workflows,
give a **checklist Claude copies into its response** and checks off:
```
Task Progress:
- [ ] Step 1: Analyze the form (run analyze_form.py)
- [ ] Step 2: Create field mapping (edit fields.json)
- [ ] Step 3: Validate mapping (run validate_fields.py)
- [ ] Step 4: Fill the form (run fill_form.py)
- [ ] Step 5: Verify output (run verify_output.py)
```
Clear steps prevent Claude from skipping critical validation. Works for code and non-code
(e.g. research synthesis) tasks alike.

### Feedback loops
Common pattern: **run validator → fix errors → repeat**, and only proceed when it passes.
The "validator" can be a script *or* a reference doc (e.g. draft against STYLE_GUIDE.md,
check the checklist, revise). This greatly improves output quality.

## Content guidelines
- **Avoid time-sensitive information** ("before August 2025, use…"). Instead keep a current
  method and tuck deprecated material into an "Old patterns" `<details>` section.
- **Use consistent terminology** — pick one term and keep it (always "API endpoint", always
  "field", always "extract"); don't mix synonyms. Consistency helps Claude follow instructions.

## Common patterns
- **Template pattern:** provide an output template. Use "ALWAYS use this exact template" for
  strict formats; "a sensible default… use your best judgment" for flexible ones.
- **Examples pattern:** when quality depends on format/style, give input→output pairs (e.g.
  commit messages). Examples convey style better than descriptions.
- **Conditional workflow pattern:** route at decision points ("Creating new content? →
  Creation workflow. Editing? → Editing workflow."). Push large branches into separate files.

## Evaluation and iteration

### Build evaluations first
Create evaluations **before** writing extensive docs, so the skill solves real problems:
1. **Identify gaps** — run Claude on representative tasks *without* the skill; note failures.
2. **Create evaluations** — build ~3 scenarios testing those gaps.
3. **Baseline** — measure performance without the skill.
4. **Write minimal instructions** — just enough to pass.
5. **Iterate** — run, compare to baseline, refine.

Evaluation structure:
```json
{
  "skills": ["pdf-processing"],
  "query": "Extract all text from this PDF file and save it to output.txt",
  "files": ["test-files/document.pdf"],
  "expected_behavior": [
    "Reads the PDF using an appropriate library or tool",
    "Extracts text from all pages without missing any",
    "Saves the text to output.txt in a readable format"
  ]
}
```
(There's no built-in runner; build your own. Evaluations are your source of truth.)

### Develop iteratively with Claude
Use "Claude A" to author/refine the skill and "Claude B" (a fresh instance with the skill
loaded) to test it on real tasks; bring observations back to Claude A. Claude understands
the skill format natively — just ask it to create a skill. Watch how Claude **navigates**
the skill: unexpected read order, missed reference links, over-reliance on one file, or
ignored files all signal structural fixes. The `name`/`description` are the most critical
levers for triggering.

## Anti-patterns to avoid
- **Windows-style paths** — always use forward slashes (`scripts/helper.py`), never `\`.
- **Too many options** — don't list five libraries. Give a default with an escape hatch
  ("Use pdfplumber… for scanned PDFs needing OCR, use pdf2image with pytesseract").

## Skills with executable code
- **Solve, don't punt:** scripts should handle error conditions (missing file, permission
  error) rather than failing for Claude to fix.
- **No voodoo constants:** justify/document every magic value ("30s covers slow
  connections", "3 retries balances reliability vs speed"), not `TIMEOUT = 47`.
- **Provide utility scripts:** more reliable than generated code, save tokens/time, ensure
  consistency. State whether Claude should **execute** ("Run analyze_form.py") or **read**
  it ("See analyze_form.py for the algorithm").
- **Verifiable intermediate outputs:** for batch/destructive/high-stakes work, use
  plan → validate → execute → verify (e.g. write `changes.json`, validate it, then apply).
- **Declare dependencies:** don't assume packages exist (`pip install pypdf` first). Note
  API has no network/install; claude.ai varies; Claude Code has full network.
- **MCP tool references:** use fully qualified `ServerName:tool_name` (e.g.
  `BigQuery:bigquery_schema`) to avoid "tool not found".

## Checklist for effective skills

Core quality:
- [ ] Description is specific and includes key terms
- [ ] Description states both what the skill does and when to use it
- [ ] SKILL.md body is under 500 lines
- [ ] Detail moved to separate files (if needed), referenced one level deep
- [ ] No time-sensitive info (or in an "old patterns" section)
- [ ] Consistent terminology throughout
- [ ] Examples are concrete, not abstract
- [ ] Progressive disclosure used appropriately
- [ ] Workflows have clear steps

Code and scripts:
- [ ] Scripts solve problems rather than punt to Claude
- [ ] Explicit, helpful error handling
- [ ] No voodoo constants
- [ ] Required packages listed and verified available
- [ ] Scripts documented; no Windows-style paths
- [ ] Validation/verification steps for critical operations
- [ ] Feedback loops for quality-critical tasks

Testing:
- [ ] At least three evaluations created
- [ ] Tested with the models you'll use (Haiku/Sonnet/Opus)
- [ ] Tested with real usage scenarios
- [ ] Team feedback incorporated (if applicable)
