# Kind of News

Kind of News is a small, warm, fact-checked English news bulletin for people
who have had enough bulletins. It creates one issue every Monday, Wednesday, and
Friday and sends it to the channel you choose.

The easiest way to install Kind of News is through an AI coding assistant. The
assistant is the guide; GitHub Actions is the quiet backend that keeps the
schedule running.

## Install with one copy-paste message

Copy this one line into Codex or Claude Code:

```text
Install and configure Kind of News from https://github.com/isolovyova/kind-of-news. Guide me one step at a time, ask only one question at a time, use GitHub Actions for automatic Monday/Wednesday/Friday delivery, and do not ask me to paste secrets into chat.
```

The assistant should:

- help create the user's own repository from this public template;
- ask for delivery channel(s), timezone, and time using the defaults below;
- explain exactly which secret is needed for the selected channel;
- guide the user through credential authorization without handling secret
  values in chat;
- run setup checks and a dry run before any real delivery;
- wait for the user's confirmation before sending the first real issue.

A bare URL can be treated as a reference by some assistants. The one-line
message above makes the installation request explicit while keeping the user
out of the implementation details.

The user still has to authorize Gmail, Telegram, or a webhook once. No public
repository link can safely create those credentials on the user's behalf.

Read the assistant contract in
[`docs/assistant-setup.md`](docs/assistant-setup.md) when implementing or
testing this flow.

## What gets installed

The assistant sets up two pieces:

1. The `kind-of-news` skill, which controls research, fact-checking, tone, and
   the four-block format.
2. A GitHub Actions workflow that generates and delivers the issue every
   Monday, Wednesday, and Friday after the one-time setup.

The default schedule is 06:00 in `America/Vancouver`. The user can change it
during setup.

## Manual fallback: GitHub Actions

If the assistant cannot access GitHub, use this direct path:

1. Create a repository from this template or fork it.
2. Open **Actions → Kind of News Setup → Run workflow**. Choose one or more
   channels as a comma-separated list, plus the timezone, local delivery time,
   and webhook preset. The workflow writes only the non-secret `config.yml`
   and commits it to the repository.
3. Add the required values as GitHub Actions Secrets. Never put the values in
   `config.yml` or commit them.
4. Run **Kind of News Setup** again. It checks the skill and credentials.
5. Run **Actions → Kind of News → Run workflow** with `dry-run` first.
6. Choose `send` only after the dry run looks correct. Scheduled runs then
   deliver automatically.

For local setup, copy `config.example.yml` to `config.yml` and run
`python3 scripts/setup.py`; commit only the resulting non-secret configuration.

GitHub scheduled workflows can be delayed during high-load periods. In public
repositories they can also be disabled after 60 days without repository
activity, so treat delivery time as approximate and check the Actions tab if a
run is missing.

## Required secrets

All runs need:

- `OPENAI_API_KEY`

When Gmail is selected:

- `GMAIL_CLIENT_ID`
- `GMAIL_CLIENT_SECRET`
- `GMAIL_REFRESH_TOKEN`
- `GMAIL_TO`

When Telegram is selected:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

When webhook is selected:

- `WEBHOOK_URL`

For Gmail OAuth, create a desktop OAuth client and run:

```bash
python3 scripts/gmail_oauth.py \
  --client-id "YOUR_CLIENT_ID"
```

The helper asks for the OAuth client secret without putting it in shell history.

Copy only the printed refresh token into GitHub Secrets. The helper uses the
Gmail `gmail.send` scope and does not write credentials to the repository.

## Delivery options

- Gmail sends the complete issue as an email.
- Telegram sends the complete issue as plain text through a bot.
- Webhook supports `generic`, `slack`, `discord`, and `ntfy` payloads. Set the
  provider in `config.yml`.

The issue is sent only after structured-output and source validation. If a
channel fails, the run attempts the remaining channels and stores the validated
issue plus per-channel success markers in the GitHub Actions cache. A rerun
retries failed channels without re-sending successful ones.

## Advanced: install the skill only

For users who only want the reusable skill, install it with the standard skill
installer:

```bash
python3 /path/to/install-skill-from-github.py \
  --repo OWNER/kind-of-news \
  --path skills/kind-of-news
```

The skill can generate the same LinkedIn-ready issue on demand. For automatic
delivery, use the guided setup above so the schedule and delivery state live in
the user's own repository.

## Editorial contract

Every issue begins with:

```text
Kind of News #YYYY-MM-DD
The world is noisy. This is a small, warm window into the parts that don't scream.
```

It contains four blocks: Good thing, On this day or Happening now, Tiny fact,
and Thought for the day. Sources and full verification links are included.

The product creates LinkedIn-ready text but never auto-posts to LinkedIn.

## Local checks

```bash
python3 scripts/validate_skill.py skills/kind-of-news
python3 -m unittest discover -s tests -v
python3 -m runner --config config.yml --fixture tests/fixtures/valid_issue.json --date 2026-08-03 --dry-run
```

## Official references

- [OpenAI Responses API and web search](https://platform.openai.com/docs/quickstart/make-your-first-api-request)
- [Gmail API sending](https://developers.google.com/workspace/gmail/api/guides/sending)
- [Telegram Bot API](https://core.telegram.org/bots/api#sendmessage)
- [GitHub scheduled workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
- [GitHub Actions secrets](https://docs.github.com/en/actions/reference/security/secrets)

## License

MIT. See [LICENSE](LICENSE).
