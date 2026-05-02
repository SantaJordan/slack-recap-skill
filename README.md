# Slack Recap Skill for Claude Code

Paste-ready Slack recaps from any Claude Code session. Three parallel research agents, a deterministic 200-line lint, one contacts file. Idempotent and end-to-end verified.

Free from [On the Edge by Blueprint](https://edge.blueprintgtm.com).

## What it does

Say "Slackify this" or "copy for Slack" at the end of any Claude Code session. The skill:

1. Pulls what was built, changed, and decided from the session
2. Drafts a BLUF (Bottom Line Up Front) message at the right length
3. Runs the draft through an 8-rule deterministic lint that catches every way Slack mangles LLM output
4. Copies the result to your clipboard via `pbcopy`

No bot. No app. The message lands in your clipboard, and it comes from you.

## The 8 formatting traps the lint catches

| What breaks | What the lint ships |
|---|---|
| `**bold**` | `*bold*` |
| `# Heading` | `*Heading*` (own line) |
| `[label](url)` | `<url\|label>` |
| ` ```python ` | ` ``` ` (strip lang hint) |
| `---` / `***` | blank line |
| Pipe tables | Bullet-flattened rows |
| `- [ ]` / `- [x]` | Emoji checkboxes |
| Bare `<` `>` `&` | Escaped (preserves mentions) |

## Install

```bash
git clone https://github.com/SantaJordan/slack-recap-skill.git ~/.claude/skills/slack-recap
```

That's it. Claude Code discovers skills in `~/.claude/skills/` automatically. Next time you open Claude Code in any project, say "Slackify this" and it fires.

## What's inside

```
slack-recap/
  SKILL.md                          # Skill definition (triggers, 9-step flow, rules)
  contacts.md                       # Name -> Slack ID mapping (grows as you use it)
  references/
    slack-formatting.md             # What works, what breaks, paste behavior
    communication-design.md         # Word swaps, Cialdini ethics, anti-patterns
    templates.md                    # BLUF skeleton, 3 length tiers, worked examples
  scripts/
    slack_lint.py                   # 200-line deterministic lint (idempotent)
```

## Contacts

The skill keeps a `contacts.md` file mapping names to Slack member IDs. First time it sees someone worth tagging, it asks once. The answer is saved forever. If you skip, it falls back to plain `@Name` text (with a warning that it won't ping).

Find a Slack member ID: profile > three dots > Copy member ID.

## Built by

[Jordan Crawford](https://edge.blueprintgtm.com) at Blueprint GTM. Read the full build log: [The 8 Ways Slack Eats Your Claude Output](https://edge.blueprintgtm.com/p/the-8-ways-slack-eats-your-claude-output).
