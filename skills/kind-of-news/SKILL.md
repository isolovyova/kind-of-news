---
name: kind-of-news
description: >
  Install, configure, or use Kind of News: a warm, gently witty, fact-checked
  English digest with one recent good-news story, a date-anchored or current
  curiosity, one tiny fact, and one pressure-releasing thought. Use when a user
  provides the Kind of News GitHub URL, asks for guided recurring delivery, or
  requests a LinkedIn-ready bulletin.
---

# Kind of News

Create a small, warm, fact-checked window into the parts of the world that do not
scream. The default cadence is Monday, Wednesday, and Friday. The default output
is English and is suitable for a LinkedIn post, email, Telegram message, or
generic webhook.

## Guided installation

Treat a Kind of News GitHub URL or an installation request as a setup task, not
as a request to draft an issue immediately. Read the repository's
`docs/assistant-setup.md` when it is available and follow its one-question-at-a-
time flow.

Use GitHub Actions as the canonical recurring-delivery backend. Guide the user
through channel, timezone, and time choices, then through the user's own GitHub
repository and secret store. Do not ask for or echo API keys, OAuth secrets,
refresh tokens, bot tokens, or webhook URLs in chat. If the current environment
cannot write to GitHub, give the user the exact page and button to use.

Do not say the automation is installed until the non-secret configuration is
saved, setup validation is green, and a dry run has produced a valid issue. Ask
for explicit confirmation before the first real send.

## Universal introduction

Start every issue with the date-based issue identifier and slogan. Do not create
a personal author top line and do not leave a top-line placeholder.

```text
Kind of News #YYYY-MM-DD
The world is noisy. This is a small, warm window into the parts that don't scream.
```

Use the publication date in `YYYY-MM-DD` format. The date is also the issue ID
used by scheduled delivery to prevent duplicate sends.

## Output structure

Use exactly these four content blocks, in this order, with exactly one emoji in
each header:

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

—
Sources:
[1] Source name — brief descriptor
[2] Source name — brief descriptor
[3] Source name — brief descriptor

Full links (for verification, remove before publishing):
[1] https://...
[2] https://...
[3] https://...

Kind of News — sent with love and verified links.
```

The second block may become `⚡ Happening now` only when a genuinely striking,
non-political event from the last 24–48 hours is more interesting than a good
anniversary. Otherwise use `📅 On this day`.

## Day-of-week character

- Monday: gentle, settling, forgiving. Prefer animals, communities, and quiet
  kindness.
- Wednesday: curious and slightly meatier. Prefer unusual science, history, and
  intellectually satisfying details.
- Friday: warmer, funnier, and a little stranger. Use a visible observational
  angle without turning it into a joke.

These are tendencies, not restrictions. A strong story wins.

## Research and fact-checking

Search before drafting. Use the available web-search capability and make
multiple queries when needed. Every factual claim must be supported by a real,
reputable source before it is included.

Prefer primary or reputable secondary sources such as official institutions,
peer-reviewed journals, museums, universities, BBC, Reuters, AP, Smithsonian,
National Geographic, and local reporting for local stories.

Reject claims that can only be found on listicles, Pinterest, content farms, or
AI-generated pages. If a fact cannot be verified, discard it and find another.
Never invent a source, URL, date, quote, number, or attribution.

For each issue:

1. Check the publication date and weekday.
2. Search for a recent good-news story.
3. Check whether a qualified `Happening now` item should replace the anniversary.
4. Find a strong date-specific human detail for `On this day` when needed.
5. Find one curious, verified tiny fact.
6. Cross-check every factual block and record its source URL.
7. Draft only after the evidence is complete.

The source list must follow block order. The `Thought for the day` does not need
a source. Keep full verification links in the separate links section.

## Story selection

Prefer stories that are:

- small-scale, human, and specific;
- connected to named people, places, objects, or institutions;
- strange in a good way;
- warm without being sentimental;
- interesting without a lesson taped to the front.

Avoid political news, celebrity news, generic corporate donations, PR copy,
exploitative stories about children, miracle framing, and moralizing conclusions.

For `On this day`, do not repeat a Wikipedia summary. Look for the rejected first
draft, odd hobby, small request, overlooked person, or human detail around the
event.

For `Tiny fact`, prefer animal behavior, linguistics, astronomy, botany, postal
history, perception, memory, sleep, and other verifiable details. Avoid common
myths and context-free trivia.

## Voice and style

Write like a thoughtful friend who reads broadly and notices quiet, interesting
things:

- warm without syrup;
- witty without performing cleverness;
- smart without sounding academic;
- brief without becoming curt;
- observant rather than motivational.

Use short sentences and varied rhythm. Use normal English capitalization. Do not
use em dashes inside prose; use commas, periods, or parentheses instead. The
standalone `—` separator before Sources is structural and allowed.

Avoid corporate verbs such as `leverage`, `unpack`, `curate`, `elevate`,
`amplify`, and `champion`. Avoid LinkedIn clichés, hashtag walls, motivational
posters, generic encouragement, and jokes with punchlines. Use at most two
lowercase hashtags only when explicitly requested.

## Scheduled delivery contract

The repository runner may load this file as its generation policy. The runner
must preserve the structure and evidence rules above, produce a structured issue
before rendering channel text, and send only after deterministic validation.

When asked to configure Kind of News, use the repository's one-time setup flow.
Never ask a user to paste API keys or OAuth tokens into chat or into a committed
file. Delivery credentials belong in the user's secret store.

The product delivers a finished LinkedIn-ready text but never publishes to
LinkedIn automatically. Manual publication remains the user's action.

## What this skill never does

- Never invents facts, citations, URLs, dates, or quotes.
- Never produces an issue without researching first.
- Never leaves the author top line blank or writes a personal author top line.
- Never adds extra content blocks or decorative emoji.
- Never uses em dashes in prose.
- Never sends an unvalidated issue.
- Never auto-posts to LinkedIn.
