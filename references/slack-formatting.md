# Slack mrkdwn formatting reference

The output target is **a person pasting text into the Slack desktop composer**. Not Block Kit, not the Web API. The skill must produce text that renders correctly even when the user pastes with plain Cmd+V and the "Apply formatting" prompt does not appear.

## The single most important rule

The skill ships text written via `pbcopy` (plain text only). That means:

1. The "Apply formatting" prompt frequently does **not** appear on plain-text paste.
2. The user's *Preferences → Advanced → Format messages with markup* setting (on or off) changes the typing experience but mrkdwn renders correctly after Send in both modes.
3. Slack's mrkdwn is **not** Markdown. It shares some symbols but the rules differ.

Stay inside the durable subset that works in every mode.

## Always works

| Element | Syntax | Notes |
|---|---|---|
| Bold | `*bold*` | Single asterisks. Non-whitespace inside. |
| Italic | `_italic_` | Single underscores. |
| Strikethrough | `~strike~` | |
| Inline code | `` `code` `` | Disables all other formatting inside. |
| Code block | triple-backtick, **no language** | Slack has no syntax highlighting in messages. A language hint shows as literal text. |
| Block quote (one line) | `> quoted` | One `>` per line. |
| Block quote (multi-paragraph) | `>>>` once, then text | Everything from `>>>` to end of message becomes one quoted block. |
| Bullet | literal `•` + space | Avoids `- `/`* ` ambiguity entirely. |
| Numbered | `1. item` | Renders fine after Send in both modes. |
| Link with label | `<https://example.com\|Label>` | The only link form that always works. |
| Bare URL | `https://example.com` | Slack auto-linkifies. |
| Email link | `<mailto:a@b.com\|Display>` | |
| User mention | `<@U01234567>` | Real Slack ID required. `@username` is plain text. |
| Channel mention | `<#C01234567\|name>` | Real channel ID required. |
| @here | `<!here>` | |
| @channel | `<!channel>` | |
| Date | `<!date^TIMESTAMP^{date_pretty}\|fallback>` | |
| Emoji | `:white_check_mark:`, `:warning:`, `:tada:`, `:rocket:` | Stick to standard shortcodes. Custom workspace emoji won't render elsewhere. |
| Escapes | `&lt;` `&gt;` `&amp;` | These three only. Don't over-escape. |

### Defaults to apply unconditionally

- `*Section name*` on its own line for headings.
- `•` + space for bullets.
- `<url|label>` for every link.
- Triple backticks with **no language hint** for code blocks.
- One blank line between sections. Never `---` rules.
- Wrap every code-like token in backticks: filenames, paths, env vars, function names, shell commands, regex.

## Never works

| Pattern | Why it breaks | Use instead |
|---|---|---|
| `# Heading` / `## Heading` | Renders literally with hash marks visible. Headings exist in Posts/Canvases, not messages. | `*Heading*` on its own line. |
| `**bold**` | Slack treats each `*` as a delimiter — produces visual artifacts. The #1 LLM-output Slack bug. | `*bold*`. |
| `[label](url)` | Inconsistent across modes. Markup-mode users see literal brackets. | `<url\|label>`. |
| Tables (pipes + dashes) | Not parsed. Render as raw `\|` and `---`. | Bullet list with `Field: value`. |
| Horizontal rules `---` / `***` / `___` | Not supported. Render literally. | Blank line. |
| Indented code blocks (4-space) | Not supported. | Triple-backtick fenced blocks. |
| Triple-backtick + language hint | The language token shows as literal text on the first line of the block. | Bare triple-backtick. |
| Backslash escapes `\*` | Not honored. | Wrap literals in inline code. |
| Underline | Not in messages. | Bold. |
| Task list `- [ ]` | Not parsed. | `• :white_large_square:` / `• :white_check_mark:`. |
| Inline images | Not possible in typed/pasted messages. | Upload separately or paste a URL Slack auto-unfurls. |
| `@username` text | Plain text. Does not ping. | `<@U…>` with the real Slack ID. |
| Nested block quotes | Only one level supported. | Single-level quote. |
| Nested lists | Not reliable across modes. | Flat list. |

## Edge cases the skill must defend against

These are the silent killers — they don't error, they just render wrong.

- **Underscores in identifiers/filenames.** `my_file_name.txt` renders the middle italicized. Wrap in inline code: `` `my_file_name.txt` ``.
- **Asterisks in shell commands.** `rm *.log` looks like the start of bold. Wrap in inline code.
- **Tildes in paths.** `~/path/to/file` plus another `~` later produces strikethrough. Wrap in inline code.
- **URLs containing `|`, `<`, or `>`.** Percent-encode (`%7C`, `%3C`, `%3E`) before emitting `<url|label>`.
- **URLs with parentheses.** Use `<url|label>` (parens-safe). Never `[label](url)` (parens break the syntax).
- **Adjacent formatting characters.** `*foo**bar*` is ambiguous. Insert a space, restructure, or wrap in code.
- **Stray odd-count `*` or `_` in dynamic content.** A single unbalanced delimiter can render everything after it as bold/italic. When emitting build output, error messages, or any LLM-generated content, wrap the whole blob in a triple-backtick code block to neutralize all formatting characters.
- **Code blocks containing triple backticks.** You cannot nest. Replace inner ` ``` ` with `'''` or split into two blocks.
- **Long messages.** Slack limit is 40,000 chars; practical limit is ~3,000 before readers stop reading. If the recap exceeds Tier 3 length, it shouldn't be a Slack message — recommend a doc instead.
- **Custom workspace emoji.** `:my-team-logo:` won't render in workspaces that don't have that emoji. Stick to common shortcodes.
- **Trailing newline from `echo`.** Use `printf '%s'` not `echo` when piping to `pbcopy`.

## Paste behavior — the "Apply formatting" prompt

The skill cannot rely on this prompt firing.

- It appears inconsistently. Plain-text paste (the case for `pbcopy`) often does not trigger it.
- It is more likely to appear on rich-text paste (HTML in clipboard) than on plain-text paste.
- Cmd+Shift+V forces plain-text paste and skips the prompt entirely.
- Accepting the prompt converts `*x*` → bold, `_x_` → italic, `[label](url)` → labeled link (sometimes), and HTML headings → bold. It does **not** fix `**bold**`.

The skill emits clean mrkdwn that works without the prompt. If the user wants rich-text paste behavior they can document the workaround themselves; do not try to write multi-flavor clipboard data.

## Eight lint rules (deterministic post-process)

`scripts/slack_lint.py` applies these. Documented here so the skill author understands what the post-process catches and what it doesn't.

1. `**x**` → `*x*`
2. `^#{1,6}\s+(.*)$` → `*\1*` (heading line becomes bold line)
3. `[label](url)` → `<url|label>`
4. ```` ```lang\n ```` → strip the language token
5. `^(---|\*\*\*|___)$` → blank line
6. Pipe-tables → bullets (best-effort; flatten body rows to `• Header: value; …`)
7. `- [ ]` / `- [x]` → `• :white_large_square:` / `• :white_check_mark:`
8. Bare `<` `>` `&` outside Slack tokens (`<@U…>`, `<#C…>`, `<!…>`, `<https://…>`, `<url|label>`, `<mailto:…>`) and outside code spans/fences → escape to `&lt;` `&gt;` `&amp;`

What the lint does **not** do (the skill must handle these in the draft):

- Wrap bare filenames/paths/identifiers in backticks. Always do this in the draft.
- Replace `- ` and `* ` bullet markers with `•`. Always emit `•` directly.
- Resolve `@Name` to `<@U…>`. The skill resolves via `contacts.md` and asks the user for unknowns.
- Truncate over-length messages. The skill must pick the right tier upstream.

## Block Kit vs mrkdwn

Block Kit (the JSON `blocks` array with `header`, `section`, `divider`, etc.) is for messages posted via the Web API or webhooks. You cannot paste Block Kit into the composer. A clipboard-based skill is constrained to mrkdwn — accept the limitations and ship clean text.
