#!/usr/bin/env python3
"""
Slack mrkdwn lint: deterministic post-process before pbcopy.

Reads stdin, writes stdout. Idempotent. Fixes the eight high-leverage patterns
that account for ~95% of Slack-formatting breakage when pasting LLM output:

  1. **bold**            -> *bold*
  2. # heading line      -> *heading line* (per heading level)
  3. [label](url)        -> <url|label>
  4. ```lang fenced      -> ``` (strip language hint)
  5. --- / *** / ___ HR  -> blank line
  6. pipe-tables         -> bullets (best-effort row flatten)
  7. - [ ] / - [x]       -> • :white_large_square: / • :white_check_mark:
  8. bare < > & outside  -> &lt; &gt; &amp; (preserves <@U..>, <#C..>, <!..>,
     code/links              <https://...>, <url|label>, code spans, fences)

Code fences and inline code are protected: rules 1-3, 7, 8 do not touch
content inside ``` ... ``` or ` ... ` spans.
"""

from __future__ import annotations

import re
import sys


FENCE_RE = re.compile(r"```([^\n`]*)\n(.*?)```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")


def _protect(text: str) -> tuple[str, list[str]]:
    """Replace fenced and inline code with placeholders so other rules skip them."""
    stash: list[str] = []

    def stash_fence(m: re.Match) -> str:
        # Rule 4: strip language hint from the opening fence.
        lang_part = m.group(1).strip()
        body = m.group(2)
        if lang_part and re.fullmatch(r"[A-Za-z0-9_+\-#]+", lang_part):
            replaced = f"```\n{body}```"
        else:
            # Preserve any non-language opening text (rare).
            replaced = m.group(0)
        stash.append(replaced)
        return f"\x00FENCE{len(stash) - 1}\x00"

    text = FENCE_RE.sub(stash_fence, text)

    # An opening ``` with no closing one: protect it through end of text so
    # its contents are not linted, and strip the language hint like rule 4.
    open_m = re.search(r"^[ \t]*```", text, flags=re.MULTILINE)
    if open_m:
        open_at = open_m.start()
        tail = re.sub(r"^([ \t]*```)[A-Za-z0-9_+\-#]+[ \t\r]*\n", r"\1\n", text[open_at:])
        stash.append(tail)
        text = text[:open_at] + f"\x00FENCE{len(stash) - 1}\x00"

    def stash_inline(m: re.Match) -> str:
        stash.append(m.group(0))
        return f"\x00ICODE{len(stash) - 1}\x00"

    text = INLINE_CODE_RE.sub(stash_inline, text)
    return text, stash


def _restore(text: str, stash: list[str]) -> str:
    def restore_fence(m: re.Match) -> str:
        return stash[int(m.group(1))]

    def restore_inline(m: re.Match) -> str:
        return stash[int(m.group(1))]

    text = re.sub(r"\x00FENCE(\d+)\x00", restore_fence, text)
    text = re.sub(r"\x00ICODE(\d+)\x00", restore_inline, text)
    return text


def _double_asterisk_to_single(text: str) -> str:
    # Rule 1: collapse **x** to *x* without touching odd-count strays.
    return re.sub(r"\*\*([^*\n]+?)\*\*", r"*\1*", text)


def _md_headings_to_bold(text: str) -> str:
    # Rule 2: heading lines become *bold* on their own line. Any *x* already
    # inside the heading (e.g. from rule 1) is unwrapped first, since Slack
    # can't nest bold and the leftover asterisks would break idempotence.
    def to_bold(m: re.Match) -> str:
        inner = re.sub(r"\*([^*\n]+)\*", r"\1", m.group(1).strip())
        inner = inner.strip("* \t")
        return f"*{inner}*" if inner else m.group(0)

    return re.sub(
        r"^[ \t]*#{1,6}[ \t]+(.+?)[ \t]*$",
        to_bold,
        text,
        flags=re.MULTILINE,
    )


def _md_links_to_slack(text: str) -> str:
    # Rule 3: [label](url) -> <url|label>. Skip empty url. Tolerate one level
    # of balanced parens in url since Slack <url|label> doesn't care about them;
    # a url with an unbalanced "(" falls back to ending at the first ")".
    return re.sub(
        r"\[([^\]\n]+)\]\("
        r"((?![)\s])(?:[^()\n]|\([^()\n]*\))+|[^)\s][^)\n]*)"
        r"\)",
        lambda m: f"<{m.group(2)}|{m.group(1)}>",
        text,
    )


def _strip_horizontal_rules(text: str) -> str:
    # Rule 5: a line that is only --- / *** / ___ becomes blank.
    return re.sub(
        r"^[ \t]*(?:-{3,}|\*{3,}|_{3,})[ \t]*$",
        "",
        text,
        flags=re.MULTILINE,
    )


def _flatten_pipe_tables(text: str) -> str:
    # Rule 6: detect a markdown pipe-table (header row, separator row of dashes,
    # body rows) and flatten to "Header: value" bullets per body row. Best
    # effort — when uncertain, leave alone.
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Header candidate: contains | and isn't itself a separator
        if (
            "|" in line
            and i + 1 < len(lines)
            and re.fullmatch(r"[ \t]*\|?[ \t:|\-]+\|?[ \t]*", lines[i + 1])
            and "-" in lines[i + 1]
        ):
            headers = [h.strip() for h in line.strip().strip("|").split("|")]
            j = i + 2
            rows: list[list[str]] = []
            while j < len(lines) and "|" in lines[j]:
                cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
                rows.append(cells)
                j += 1
            for row in rows:
                pieces = []
                for h, c in zip(headers, row):
                    if c:
                        pieces.append(f"{h}: {c}" if h else c)
                if pieces:
                    out.append("• " + "; ".join(pieces))
            i = j
            continue
        out.append(line)
        i += 1
    return "\n".join(out)


def _checkboxes_to_emoji(text: str) -> str:
    # Rule 7: - [ ] / - [x] -> • :white_large_square: / • :white_check_mark:
    text = re.sub(
        r"^[ \t]*[-*][ \t]+\[ \][ \t]*",
        "• :white_large_square: ",
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(
        r"^[ \t]*[-*][ \t]+\[[xX]\][ \t]*",
        "• :white_check_mark: ",
        text,
        flags=re.MULTILINE,
    )
    return text


def _escape_bare_html(text: str) -> str:
    # Rule 8: escape < > & that aren't part of a Slack token. Slack tokens
    # we preserve: <@U…>, <#C…>, <!…>, <url>, <url|label>, <mailto:…|…>,
    # <!date^…>. Anything else gets escaped.
    slack_token_re = re.compile(
        r"<(?:"
        r"@[A-Z0-9]+(?:\|[^<>]*)?"                 # user mention (optional label)
        r"|#[A-Z0-9]+(?:\|[^<>]*)?"                 # channel mention
        r"|![a-zA-Z][^>]*"                          # !here / !channel / !date^…
        r"|mailto:[^>|]+(?:\|[^>]+)?"               # mailto link
        r"|https?://[^>|\s]+(?:\|[^>]+)?"           # http(s) link
        r")>"
    )

    placeholders: list[str] = []

    def stash(m: re.Match) -> str:
        placeholders.append(m.group(0))
        return f"\x00TOK{len(placeholders) - 1}\x00"

    protected = slack_token_re.sub(stash, text)
    # Now escape remaining bare < > &.
    protected = protected.replace("&", "&amp;")
    # Restore the &amp; we just made for already-escaped entities (best-effort).
    protected = re.sub(r"&amp;(amp|lt|gt|#\d+|#x[0-9a-fA-F]+);", r"&\1;", protected)
    protected = protected.replace("<", "&lt;").replace(">", "&gt;")

    def unstash(m: re.Match) -> str:
        return placeholders[int(m.group(1))]

    return re.sub(r"\x00TOK(\d+)\x00", unstash, protected)


def lint(text: str) -> str:
    text, stash = _protect(text)
    text = _double_asterisk_to_single(text)
    text = _md_headings_to_bold(text)
    text = _md_links_to_slack(text)
    text = _strip_horizontal_rules(text)
    text = _flatten_pipe_tables(text)
    text = _checkboxes_to_emoji(text)
    text = _escape_bare_html(text)
    text = _restore(text, stash)
    # Collapse 3+ blank lines to 2 (one paragraph break is enough).
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


if __name__ == "__main__":
    sys.stdout.write(lint(sys.stdin.read()))
