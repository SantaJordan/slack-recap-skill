---
name: slack-recap
description: Generate a Slack-formatted recap of the current Claude Code session and copy it to the macOS clipboard via pbcopy. Use this skill whenever the user asks to "copy for Slack", "make a Slack message", "Slackify this", "format this for Slack", "give me a Slack recap", "wrap this up for Slack", or any variant of putting session results into Slack — even when the word "skill" is not used. Produces clean Slack mrkdwn (no markdown headings, no double-asterisk bold, no `[label](url)` links), follows BLUF + plain-language structure, applies Cialdini's principles ethically (Authority = link the data, Social Proof = name who actually agreed, never the dark-pattern versions), and tags people via `<@USERID>` when the Slack ID is known — asking once and saving to contacts.md when it isn't.
---

# Slack-recap

Generate a Slack-paste-ready recap of the current session and put it in the user's clipboard. Never produce broken formatting. Read at an 8th-grade level. Show credibility through evidence, not jargon.

## When this skill fires

The user wants the result of the current session as a Slack message. Common phrasings:

- "copy this for Slack"
- "Slackify this"
- "make a Slack message"
- "give me a Slack recap"
- "wrap this up for Slack"
- "what should I post in Slack about this?"
- "draft an update I can paste in #eng"

Fire even when the user does not say the word "skill". If the user says only "summarize this", that is a different intent — do not fire.

## What the skill produces

A clean Slack mrkdwn message that:

1. Leads with the bottom line (BLUF — Bottom Line Up Front).
2. States what changed and why.
3. Surfaces options considered and why others were rejected, when a real decision was made.
4. Names what is next and the specific person to ping for the next step.
5. Uses only formatting that Slack will render correctly when pasted into the desktop composer.
6. Lands in the macOS clipboard via `pbcopy`, after a preview is shown to the user.

## The 9-step flow

Run these in order. Each step is short — most of the work is in steps 4 and 5.

1. **Gather session context.** From the current conversation: what was actually built or changed, which files were touched, what decisions were made, which options were rejected, what is left to do, and which people came up. If the user pre-pasted a draft they want formatted, treat that as the source instead of the session.
2. **Pick a length tier** using the decision-count heuristic in `references/templates.md`. The composer must explicitly choose Tier 1 (3 lines), Tier 2 (8–12 lines), or Tier 3 (15–25 lines). When in doubt, go shorter.
3. **Resolve `@`-mentions.** For each person worth tagging, look up their Slack ID in `~/.claude/skills/slack-recap/contacts.md`. If found, emit `<@U01234567>`. If not found, ask the user once: *"I'd like to tag Sarah — what's her Slack ID? (Slack: profile → ⋮ → Copy member ID. Reply 'skip' to use plain @Sarah text.)"*. Append the answer to `contacts.md` so the question never repeats. If the user replies `skip`, emit `@Sarah` as plain text and warn in the preview that this won't actually ping.
4. **Draft the message** using the template in `references/templates.md` and the word swaps + sentence rules in `references/communication-design.md`. Apply Cialdini's principles in their ethical form (Authority = link the data, Social Proof = name who actually agreed, etc.) — never the dark-pattern versions listed in that reference.
5. **Self-check against the Slack-formatting "never works" list** in `references/slack-formatting.md`. The most common failures: `**bold**` (use `*bold*`), `# Heading` (use `*Heading*` on its own line), `[label](url)` (use `<url|label>`), triple-backtick with a language hint, tables, horizontal rules, raw filenames with underscores (wrap in backticks).
6. **Run the lint script.** Pipe the draft through `python3 ~/.claude/skills/slack-recap/scripts/slack_lint.py`. The script applies the eight high-leverage fixes deterministically and is idempotent. Use the linted output for everything that follows.
7. **Show the preview.** Print the linted message in a fenced block to the terminal so the user can see what is going to clipboard. Lead the preview with the chosen tier and the message length, e.g. *"Tier 2 recap, 184 chars. Preview below — copying to clipboard next."*
8. **Copy to clipboard.** Pipe the linted text to `pbcopy`. Do this with a here-string or shell pipe; do not echo (echo adds a trailing newline).
9. **Confirm.** Print: *"Copied N chars. Paste with Cmd+V (Cmd+Shift+V if Slack tries to re-format). If Slack offers an 'Apply formatting' bar, accepting it is safe — the message renders correctly either way."*

## How to write the message

Read these in this order before drafting:

- **`references/templates.md`** — the BLUF skeleton, the three length tiers, and a worked example for each tier.
- **`references/communication-design.md`** — the word-swap table, sentence rules, the ethical Cialdini checklist (with the dark-pattern version explicitly called out for each), and the 14 anti-patterns to refuse.
- **`references/slack-formatting.md`** — the always-works cheatsheet, the never-works list, paste-behavior notes, and the eight lint rules the post-process applies.

Hard rules baked in below so you do not need to re-read references for every invocation:

- **Bold:** `*bold*` only. Never `**bold**`.
- **Headings:** `*Section name*` on its own line. Never `#`, `##`, etc.
- **Links:** `<https://example.com|Label>`. Never `[Label](https://example.com)`.
- **Bullets:** literal `•` (U+2022) followed by a space. Not `- ` or `* `.
- **Code identifiers, filenames, paths, env vars, commands:** always wrap in inline backticks. This protects underscores from becoming italic and asterisks from becoming bold. Example: `` `auth_middleware.py` ``, not `auth_middleware.py`.
- **Code blocks:** triple backticks, no language hint. Slack does not syntax-highlight in messages and the language token shows as literal text.
- **No tables, no `---`, no underline, no task-list checkboxes, no `\*` escapes, no nested lists.** All of these break.
- **Mentions:** `<@U01234567>` only. Never `@username` (renders as plain text and does not ping).
- **Channel refs:** `<#C01234567|name>`. Never `#channel-name` alone.

## How to handle unknown contacts

`contacts.md` is the single source of truth for name → Slack ID. Format:

```
# Slack contacts. Format: `Name: U01234567` (one per line). Skill appends to this file.
Sarah: U01ABC2DEF
Alex: U07XYZ9ABC
```

When a candidate `@`-mention surfaces during drafting:

1. Read `contacts.md`.
2. Match the name case-insensitively. If found, emit `<@U…>`.
3. If not found, ask the user once with the exact prompt above. Wait for the answer. Append `Name: U…` to `contacts.md` if they provide an ID, or do not modify the file if they reply `skip`.
4. Never invent IDs. A guessed ID either silently no-ops or pings the wrong person — both are worse than plain text.

## Length-tier picker (memorize)

Count the number of *decisions* the reader needs to absorb (not characters, not bullet count):

- **0 decisions** → Tier 1, ~3 lines. A merge, a routine fix, a "shipped it" status.
- **1 decision** → Tier 2, ~8–12 lines. The default. Feature shipped, a non-trivial choice was made.
- **2+ decisions, or a reversal** → Tier 3, ~15–25 lines. Multiple options weighed, or a previous decision was undone. Doubles as a lightweight ADR (architecture decision record).
- **More than that** → not a Slack message. Suggest the user post a Tier 2 in-channel and link to a doc or thread for the long form.

When the user has not signaled a preference, default to the smallest tier that fits.

## Ethical compass

Before pbcopy, run the gut check from `references/communication-design.md`: *if the reader saw the full reasoning and all the unsent context, would they still feel good about this message in 24 hours?* If no, rewrite. The skill must not produce flattery that did not happen, consensus that was not reached, urgency that does not exist, or authority that cannot be cited.

## Invocation example

User: "Slackify this and copy it"

Skill:

1. Reads the session.
2. Determines: 1 decision (chose to use a database trigger over a cron job).
3. Picks Tier 2.
4. Identifies one person to tag (Alex, the on-call engineer who flagged the original issue).
5. Looks up `Alex` in `contacts.md` → found `U07XYZ9ABC`.
6. Drafts the message against the template.
7. Runs through `slack_lint.py`.
8. Prints preview:

   ```
   Tier 2 recap, 271 chars. Preview below — copying to clipboard next.
   ───
   *Webhook retries — fixed*
   TL;DR: Stripe webhook failures dropped from ~12/day to 0 in staging. Watching prod overnight.

   *What I did*
   • Added an idempotent retry queue keyed on `event_id`.
   • Backfilled the last 7 days of failed events.

   *Why*
   Failures were silent and `<@U07XYZ9ABC>` flagged it on Tuesday. Linked to the on-call dash: <https://grafana.example/d/stripe|Stripe webhook health>.

   *Chose:* DB trigger — survives app restarts.
   *Rejected:* Cron job — race-condition window on retry.

   *Next:* I'll watch prod through Friday. <@U07XYZ9ABC> — ping me if you see new failures.
   ───
   ```

9. Pipes that block to `pbcopy`.
10. Prints: `Copied 271 chars. Paste with Cmd+V…`

## Bash commands the skill runs

```sh
# Run the lint pass and copy to clipboard in one shot.
printf '%s' "$DRAFT" | python3 ~/.claude/skills/slack-recap/scripts/slack_lint.py | pbcopy

# Confirm what is on the clipboard (sanity check before user pastes).
pbpaste | wc -c
```

Use `printf '%s'` not `echo` — `echo` appends a trailing newline that creates a stray blank line after paste.

## When something looks off

- **The user says "this is too long / too short."** Re-pick the tier and re-draft. Do not just trim — restructure.
- **A `*bold*` survived through the lint with stray asterisks.** Wrap the offending blob in a fenced code block; that neutralizes every formatting character.
- **The lint script changed something the user wanted preserved.** The lint is conservative inside code spans and fences. If the user wants literal `**`, `#`, or `[label](url)` to render as text, wrap that text in inline code.
- **The user says the ping didn't fire.** Their Slack ID in `contacts.md` is wrong or stale. Ask for the current ID and overwrite the line.
