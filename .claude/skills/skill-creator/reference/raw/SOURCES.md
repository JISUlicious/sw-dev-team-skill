# Verbatim source mirrors

This folder holds **unmodified** copies of the official Agent Skills documentation, so
this skill works as offline portable documentation. The curated summaries one level up
(`../specification.md`, `../claude-code-features.md`, `../best-practices.md`) are the
reading entry point; these raw files are the authoritative source to drill into.

Do not edit these files by hand — re-fetch them from the source URLs to update, then
refresh the checksums below.

| File | Source URL | Fetched (UTC) | SHA-256 |
| :-- | :-- | :-- | :-- |
| `claude-code-skills.md` | https://code.claude.com/docs/en/skills.md | 2026-06-03T23:34:39Z | `ac720bf63d8ded1aa7bd0b2f4249b725e531d272958ce0d60016b5737bfe6976` |
| `agent-skills-overview.md` | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview.md | 2026-06-03T23:34:39Z | `0bd9758afca5cc32441bb59a9b59b1a3fe3717b77fa7cc48abd6f24b0ff0e9cb` |
| `agent-skills-best-practices.md` | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices.md | 2026-06-03T23:34:39Z | `d1da876439d60b3c813f6fac53745a0b518a7cc4af7973e6e9318dda64bee23a` |

The `.md` URLs are the raw-markdown form Mintlify serves for each docs page (append `.md`
to the human page URL). The open-standard spec at https://agentskills.io/specification is
not mirrored here — it returns HTTP 403 to automated fetches; the standard's substance is
covered by the overview page above.

To re-fetch and re-checksum (run from this directory):

```bash
curl -sSL --fail "https://code.claude.com/docs/en/skills.md" -o claude-code-skills.md
curl -sSL --fail "https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview.md" -o agent-skills-overview.md
curl -sSL --fail "https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices.md" -o agent-skills-best-practices.md
shasum -a 256 *.md
```
