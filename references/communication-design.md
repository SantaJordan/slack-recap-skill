# Communication design — plain language and ethical influence

The reader is a smart engineer or stakeholder who is skim-reading Slack between meetings. The recap must land in seconds, feel credible without performing effort, and apply influence principles only when they reflect what is actually true about the work.

## Word-choice cheatsheet

Apply these swaps mechanically before sending. The right column is almost always the right pick.

| Don't say | Say |
|---|---|
| utilize | use |
| leverage (as verb) | use |
| in order to | to |
| prior to | before |
| subsequent to | after |
| at this point in time / at the present time | now |
| in the near future | soon |
| due to the fact that | because |
| in the event that | if |
| with regard to / in regard to | about |
| in close proximity to | near |
| a number of | some, several, many (be specific) |
| has the ability to | can |
| is responsible for | handles, owns |
| in order for X to Y | so X can Y |
| facilitate | help, run, cause |
| commence / initiate | start |
| terminate | end, stop |
| endeavor | try |
| ascertain | find out, confirm |
| methodology | method, approach |
| functionality | feature, behavior |
| implement (verb) | build, ship, add |
| operationalize | put in place, run |
| holistic / robust / scalable (vague flex) | (cut, or replace with the concrete property) |
| best-in-class / world-class | (cut) |
| circle back | follow up, revisit |
| touch base | check in, talk |
| at the end of the day | (cut) |
| moving forward / going forward | next, from here |
| it should be noted that | (cut, just say the thing) |
| as previously mentioned | (cut, or link the prior message) |

## Technical terms are not jargon

When the topic is technical, keep the precise noun (`auth middleware`, `migration`, `webhook retry`, `connection pool`, `idempotency key`) and put the plain-English consequence next to it. Pattern:

> Changed the `auth middleware` so failed token refreshes log the user out instead of silently 401-ing. Result: support tickets about "stuck loading" should drop.

That sentence reads at an 8th-grade level because the *frame* is plain — "changed X so Y instead of Z; result: W" — even though the noun is technical. Do not dumb the noun down. Dumb the *sentence shape* down.

## Sentence rules

- Average 15–20 words per sentence. Split anything over ~25.
- One idea per sentence.
- Active voice. Subject-verb-object: "I shipped X", "the team agreed Y" — not "X was shipped" / "agreement was reached on Y".
- Concrete numbers beat adjectives. "Cuts p95 from 800ms to 240ms" beats "much faster".
- No throat-clearing openers ("So basically", "Just wanted to", "Quick note that").
- No closing apologies ("sorry for the long message", "hope this makes sense").

## The seven Cialdini principles, ethical version

For each: the *ethical move* a recap can make, and the *dark-pattern version* to refuse. Frame: every principle should reflect something *that is actually true* about the work. If you would be uncomfortable having the reader see your full reasoning, you are doing the dark version.

**1. Reciprocity** — give before you ask.
- *Ethical:* End with something useful for the reader: a link to the diff, a runbook, a screenshot, an answer to a question they asked last week. If the recap closes a loop someone else opened, say so by name.
- *Refuse:* Manufactured favors. "I worked all weekend on this" framing meant to guilt people into agreement. Do not perform sacrifice.

**2. Commitment / Consistency** — restate the agreed goal before the update.
- *Ethical:* Open by anchoring to the prior commitment ("We agreed last sprint to cut signup drop-off; here is where I got to."). Quote the prior decision with `>` if it lives in Slack.
- *Refuse:* Putting words in people's mouths ("As we all decided…") when the decision was actually one person's call. Do not fabricate consensus.

**3. Social Proof** — name who else converged on this.
- *Ethical:* "<@U…> and <@U…> both flagged this in review and we landed on the same fix." Cite real signals — review comments, prior tickets, user reports — with links.
- *Refuse:* "Everyone agrees that…", vague majority claims, padding with names of people who were not actually involved. Never imply consensus that does not exist.

**4. Authority** — cite the data or source you used.
- *Ethical:* Link to the metric, the doc, the test result, the RFC, the commit, the conversation. Show your work. If you used an external benchmark, link it. If you ran a measurement, give the numbers.
- *Refuse:* Borrowing prestige ("industry best practice", "the standard pattern") without a link. If you can't cite it, don't claim it.

**5. Liking** — be human, give credit.
- *Ethical:* Credit specific people for specific contributions ("<@U…>'s question about idempotency was what unblocked this"). Acknowledge what was hard. Use plain warm language, not corporate.
- *Refuse:* Flattery, in-jokes that exclude readers, faux humility ("just a small thing I shipped" when it is not small).

**6. Scarcity** — be honest about what was on the line.
- *Ethical:* Note real time/cost trade-offs: "If we don't pick a path on the queue backend by Friday, we slip the launch by a week." Real constraints, real numbers.
- *Refuse:* Manufactured urgency. "We have to decide NOW" pressure when there is no actual deadline. Never invent a clock.

**7. Unity** — speak as the team, not the lone hero.
- *Ethical:* "We" when it really was we. "I" when it was you. Frame the work as part of the team's shared goal. Use the team's vocabulary (project codenames, shared metric names) so readers feel oriented.
- *Refuse:* Co-opting "we" to dilute responsibility for a bad call, or to claim others' credit. Never use shared identity to suppress dissent.

## The single ethical test

Before pbcopy, ask: *if the reader saw my full reasoning and all the unsent context, would they still feel good about this message in 24 hours?* If no, rewrite.

## Anti-patterns to refuse

The composer must not produce any of these:

1. **Wall-of-text without a TL;DR.** Always lead with the bottom line. If the reader stops after one sentence, they should still know what shipped and whether they need to act.
2. **Vague verbs without nouns.** "Improved performance" / "refactored things" / "cleaned up some code" — replace with the specific change and the specific number or behavior.
3. **Hedging stack.** "I think maybe we could possibly consider…" — state the recommendation, then give the caveat once. Hedges compound; one is honest, three is evasive.
4. **Fake humility / fake confidence.** "Just a tiny thing" when it is a week of work. "Production-ready" when it is behind a feature flag with 1% of traffic. State the actual status.
5. **Unearned consensus language.** "We all agreed", "the team feels", "everyone's aligned" — only when literally true and traceable.
6. **Decoration over information.** Emojis everywhere, dividers, ALL CAPS HEADERS — these signal effort rather than clarity. One headline + bold section labels is enough.
7. **Buried asks.** If you need someone to do something, the ask goes on its own line at the end with `<@U…>` and a verb. Never hide an ask inside a paragraph.
8. **`@channel` / `@here` for non-urgent updates.** Use these only when every recipient genuinely needs to act in the next few hours. Default to no broad mention.
9. **Apologizing for length / for the update existing.** "Sorry this is long" / "sorry for the spam" — cut. If it is too long, shorten it.
10. **Manufactured urgency or scarcity.** "We need to decide today" when no deadline exists.
11. **Borrowed authority without a link.** "Best practice is…" / "the standard approach is…" — cite or cut.
12. **Recapping process instead of outcome.** "I spent the morning debugging, then tried X, then Y, then Z…" — the reader wants the result and the reasoning, not the play-by-play. Process belongs in the thread, not the top-level message.
13. **Unbounded next-steps.** "Next: continue working on the project." Next steps need a verb, an owner, and a rough timeframe — or they don't belong.
14. **Mentioning people just to be seen by them.** Tag only when you need a response or you're crediting specific work. Performative tagging is noise.

## Pre-send checklist

1. Does the first sentence tell the reader the outcome? (BLUF)
2. Is every claim either obvious-from-context or backed by a link/number?
3. Are options-considered visible if the work involved a real choice?
4. Did I credit the specific people whose input mattered?
5. Did I run the word-swap pass (utilize → use, leverage → use, etc.)?
6. Average sentence under ~20 words? Active voice? One idea per sentence?
7. Is there an ask? If yes, is it on its own line with a named `<@U…>` and a verb?
8. Would the reader still feel good about this message in 24 hours if they saw my full reasoning?
9. Is this the right length tier? If in doubt, shorter.
