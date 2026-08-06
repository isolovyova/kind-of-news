# Kind of News

A small, fact-checked newsletter about useful things, curious facts, and what
is worth noticing.

## Subscribe

Receive an automatically generated Kind of News edition every Monday,
Wednesday, and Friday.

[Subscribe on Buttondown](https://buttondown.com/kindofnews)

After you confirm your subscription, Buttondown sends exactly one native
Welcome email. This repository does not generate a second welcome email.

A scheduled GitHub Actions workflow runs the public newsletter at 06:00 in
`America/Vancouver` on Monday, Wednesday, and Friday. The reader pipeline:

1. Collects fresh sources.
2. Generates the newsletter with AI.
3. Validates the four content blocks and their source links.
4. Publishes the validated issue through the Buttondown API.
5. Buttondown delivers it to subscribers.

## Run privately

Use Codex or Claude Code to generate one personalized issue on demand. No
subscription, scheduled delivery, Buttondown, connected channel, or email is
required. The issue appears in the conversation; ask to save a local Markdown
copy if you want one.

Copy this prompt:

```text
Install Kind of News from https://github.com/isolovyova/kind-of-news and generate a personalized issue for me now. Research and validate it, display it here, and do not subscribe me, schedule delivery, use Buttondown, connect a channel, or send email.
```

## Example issue

This is a compact sourced example, not a Welcome email or a current issue.

### ☀️ Good thing

The first free modern public library in Peterborough, New Hampshire, opened in
1833. Its founding model treated library access as a public good, available to
the whole community.

### 📅 On this day

Before Apollo 11 reached the Moon, NASA carried messages from people around the
world on a tiny silicon disc. A very small object held a very large hello.

### 🧠 Tiny fact

Octopuses have three hearts, and two of them stop beating while the animal
swims.

### 🌱 Thought for the day

Not everything useful has to be urgent.

Sources:

[1] [American Library Association](https://www.ala.org/aboutala/1833) — public-library history
[2] [NASA](https://www.nasa.gov/history/55-years-ago-one-month-until-the-moon-landing/) — Apollo 11 messages
[3] [NOAA Fisheries](https://www.fisheries.noaa.gov/feature-story/celebrate-holidays-our-ink-blot-and-stumpy-paper-snowflakes) — octopus biology

## License

MIT. See [LICENSE](LICENSE).
