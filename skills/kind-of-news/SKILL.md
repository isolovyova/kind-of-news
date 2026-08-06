sed: --: No such file or directory
---
name: kind-of-news
description: >
  Generate a personalized, fact-checked Kind of News issue on demand.
  Research first, validate exactly four content blocks and source links, then
  display the issue or save it locally when requested.
---

# Kind of News

Generate a small, warm, fact-checked window into the parts of the world that do
not scream. This skill is for a private, on-demand issue: display the finished
issue in the conversation by default and save a local Markdown copy only when
the user asks.

Readers who want the public newsletter should subscribe at
<https://buttondown.com/kindofnews>. The scheduled repository runner uses the
same issue structure, validates it, and publishes it through Buttondown. It is
separate from this private on-demand interaction.

## Output contract

Use the publication date in `YYYY-MM-DD` format as the issue identifier. Create
exactly these four content blocks, in this order, with one emoji in each
header:

```text
Kind of News #YYYY-MM-DD
The world is noisy. This is a small, warm window into the parts that don't scream.

☀️ Good thing
(Location): A real, recent, verified good-news story in 2–4 sentences.

📅 On this day
A date-anchored historical fact with a human detail.

🧠 Tiny fact
One curious, verified fact.

🌱 Thought for the day
One sentence that releases pressure rather than adding it.

Sources:
[1] [Source name](https://...) — brief descriptor
[2] [Source name](https://...) — brief descriptor
[3] [Source name](https://...) — brief descriptor
```

The second block may be `⚡ Happening now` only when a genuinely striking,
non-political event from the last 24–48 hours is more interesting than a good
anniversary. Otherwise use `📅 On this day`.

There must be at least one source for each of the first three blocks, at least
three sources total, and every source URL must be an absolute HTTPS link. Put
each source URL directly in its numbered Sources item, preferably as a Markdown
link on the source name. The thought does not need a source. Do not add a
standalone separator before Sources.

## Research and validation

Research before drafting. Use the available web-search capability and make
multiple queries when needed. Every factual claim must be supported by a real,
reputable source before it is included.

Prefer primary or reputable secondary sources such as official institutions,
peer-reviewed journals, museums, universities, BBC, Reuters, AP, Smithsonian,
National Geographic, and local reporting for local stories. Reject listicles,
content farms, unsupported claims, invented citations, incomplete URLs, and
facts that cannot be verified.

For each issue:

1. Check the publication date.
2. Find a recent, specific, non-political good-news story.
3. Find a strong date-specific human detail, or qualify a genuinely current
   non-political event when it is more interesting.
4. Find one curious, verified tiny fact.
5. Cross-check every factual block and record its source URL.
6. Draft only after the evidence is complete.
7. Validate the issue structure, date, prose, and source links before showing
   or saving it.

## Story selection and voice

Prefer stories that are small-scale, human, specific, strange in a good way,
and warm without being sentimental. Avoid political news, celebrity news,
generic corporate donations, PR copy, exploitative stories about children,
miracle framing, and moralizing conclusions.

Write like a thoughtful friend who reads broadly and notices quiet, interesting
things: warm without syrup, witty without performing cleverness, smart without
sounding academic, and brief without becoming curt. Use short sentences and
normal English capitalization. Do not use em dashes inside prose. Avoid
corporate verbs, social-media clichés, hashtag walls, motivational posters, and
generic encouragement.

## Scheduled pipeline policy

The repository's scheduled workflow is operational plumbing for the public
Buttondown newsletter. It uses one repository-controlled schedule, researches and
generates an issue, validates it, renders safe HTML with clickable source links,
and publishes it through the Buttondown API. `BUTTONDOWN_API_KEY` belongs only
in the secure host or GitHub Actions secret store. The runner's explicit
fixture and dry-run options are validation tools; they do not create a second
user-facing product mode.

Every published issue uses its publication date as its issue ID. Per-issue
state must skip a Buttondown publish that already succeeded and retry only a
failed issue. A research or validation failure must stop publishing.

## What this skill never does

- Never invent facts, citations, URLs, dates, or quotes.
- Never produce an issue without researching first.
- Never add extra content blocks or decorative emoji.
- Never use em dashes in prose.
- Never show or save an unvalidated issue.
- Never claim that a private issue was emailed or scheduled.
