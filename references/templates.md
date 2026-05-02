# Templates and length tiers

Pick a tier first. Then fill the template. Sections may be omitted when empty — never pad.

## Length-tier picker

Count the number of *decisions* the reader needs to absorb (not bullets, not characters).

| Decisions | Tier | Lines | Words | When |
|---|---|---|---|---|
| 0 | 1 — ack-and-link | ~3 | 30–60 | A merge, a routine fix, a "shipped it" status, a continuation of an active thread. |
| 1 | 2 — default recap | 8–12 | 120–220 | A feature shipped. A non-trivial choice was made. Stakeholders need to know the state of a thing. |
| 2+ or a reversal | 3 — decision-heavy | 15–25 | 300–450 | Multiple options genuinely weighed. A previous decision was undone. Doubles as a lightweight ADR. |
| Bigger than that | (not Slack) | — | — | Post a Tier 2 in-channel and link a doc / thread / canvas for the long form. |

When in doubt, go shorter. Walls of text get skimmed at best, ignored at worst.

## The skeleton (Tier 2 default)

Use this as the canonical shape. Trim sections for Tier 1, expand the *Options* section for Tier 3.

```
*{One-line headline — what shipped or what changed.}*
TL;DR: {1–2 sentences. State the outcome and its impact. Lead with the bottom line.}

*What I did*
• {Concrete change 1 — file/system/behavior, in plain words}
• {Concrete change 2}
• {Concrete change 3}

*Why*
{1–3 sentences. Connect the work to the agreed goal or the problem it solves. Cite the data, doc, or conversation that justified it.}

*Chose:* {Option A} — {one-line reason}
*Rejected:* {Option B} — {one-line reason it lost}

*What's next*
• {Next step + owner + rough timing}
• {Open question, if any}

<@U…> — {specific ask, only if you actually need them}
```

Formatting rules:

- Bold the headline and the section labels. Nothing else.
- Bullets for parallel items. Prose for reasoning. Never bullet a single item.
- One blank line between sections.
- Code identifiers, filenames, paths, env vars, commands → always inline backticks.
- Links → always `<url|label>`.
- No emoji unless the user has explicitly opted in.

## Tier 1 — example

Use when there is no decision the reader needs to absorb.

```
*Webhook retries — fixed*
Down from ~12 fails/day to 0 in staging. Watching prod overnight. Diff: <https://github.com/org/repo/pull/482|PR #482>.
```

## Tier 2 — example

The default. One decision was made.

```
*Webhook retries — fixed*
TL;DR: Stripe webhook failures dropped from ~12/day to 0 in staging. Watching prod overnight.

*What I did*
• Added an idempotent retry queue keyed on `event_id`.
• Backfilled the last 7 days of failed events.
• Added a Grafana panel for the retry-queue depth.

*Why*
Failures were silent. <@U07XYZ9ABC> flagged it on Tuesday after support tickets piled up. Linked dashboard: <https://grafana.example/d/stripe|Stripe webhook health>.

*Chose:* DB trigger — survives app restarts and gives us a single source of truth.
*Rejected:* Cron job — race-condition window on retry; would have needed a separate lock.

*Next:* I'll watch prod through Friday. <@U07XYZ9ABC> — ping me if you see new failures.
```

## Tier 3 — example

Use when 2+ decisions or a reversal. Expand the *Options* section to multiple `Chose:` / `Rejected:` lines.

```
*Queue backend — switched to SQS*
TL;DR: We're moving the job queue from Redis Streams to SQS. Migration starts Monday, fully cut over by 2026-05-15. No user-visible downtime.

> Two weeks ago we said we'd stick with Redis Streams. This is a reversal — see *Why* below.

*What I'm doing*
• Standing up an SQS queue per environment, with DLQs.
• Porting the four producer call-sites and the three consumers behind a thin `JobQueue` interface so we can swap implementations.
• Running both queues in parallel for one week before flipping the switch.

*Why*
Redis Streams hit a memory cliff in load tests at ~3× current peak — we'd be paying for that headroom anyway and AWS support hours don't extend to our self-hosted Redis.

*Chose:* SQS — managed, scales without us, native DLQ semantics, fits the team's AWS bias.
*Rejected:* Redis Streams (status quo) — see memory cliff above; would also need a Redis on-call rotation.
*Rejected:* RabbitMQ — more features than we need; nobody on the team has run it in prod.
*Rejected:* SNS+Lambda fanout — re-architects too much; we want a queue, not pub/sub.

*Risks / open questions*
• SQS visibility-timeout tuning is still TBD; <@U02ABC1DEF> is benchmarking.
• Cost projection assumes ~12M messages/month; if usage spikes we'll re-check.

*Next*
• Mon 5/4 — SQS queues live in staging. Owner: me.
• Wed 5/6 — both queues running in parallel in prod. Owner: me + <@U02ABC1DEF>.
• Fri 5/15 — Redis Streams turned off. Owner: me.

<@U07XYZ9ABC> — does this conflict with the work you're doing on the on-call rotation? Need answer by Friday.
```

## Filling each slot

- **Headline.** Past tense, outcome-focused. "Webhook retries — fixed", not "Working on webhook retries". If the work is in progress, "Webhook retries — in flight, ETA Friday."
- **TL;DR.** One or two sentences that stand alone. If the reader stops reading after the TL;DR, they should know what shipped, what its impact is, and whether they need to act.
- **What I did.** Concrete, specific, parallel grammar. "Added an idempotent retry queue" not "Improved retry handling". Each bullet is one change. Three to five bullets max.
- **Why.** Connects to the prior commitment or the problem. Cites the source: a metric, a ticket, a Slack message, a person. *This is where Authority shows up — link the data.*
- **Chose / Rejected.** One-line reasons each. If a reason needs more than one sentence, link out to a doc instead of expanding inline. Showing three rejected options with one-line reasons is more credible than one chosen option with three paragraphs of justification.
- **Next.** Verb + owner + rough timing. "Watch prod through Friday" beats "continue monitoring". Unbounded next-steps don't belong.
- **Ask.** Last line only. Named `<@U…>` + verb. "<@U…> — ping me if you see new failures." If there's no ask, omit this line entirely.
