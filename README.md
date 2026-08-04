# Kind of News

Kind of News is a small, warm, fact-checked English news bulletin for people
who have had enough bulletins. It creates one issue every Monday, Wednesday, and
Friday and sends it to the channel you choose.

The public repository has two surfaces:

1. A reusable `kind-of-news` skill for Codex/Cowork.
2. A self-hosted GitHub Actions runner for the one-time setup → automatic delivery flow.

## The one-time setup flow

1. Create a repository from this template or fork it.
2. Copy `config.example.yml` to `config.yml`:

   ```bash
   cp config.example.yml config.yml
   ```

3. Run the setup helper locally:

   ```bash
   python3 -m pip install -r requirements.txt
   python3 scripts/setup.py
   ```

   The defaults are English, Monday/Wednesday/Friday, 06:00, and
   `America/Vancouver`. Select one or more channels: `gmail`, `telegram`, or
   `webhook`.

4. Commit `config.yml` to your fork. It contains only non-secret preferences.
5. Add the printed names as GitHub Actions Secrets. Never put the values in
   `config.yml` or commit them.
6. Run **Actions → Kind of News Setup**. It checks the skill and credentials.
7. Run **Actions → Kind of News → Run workflow** with `dry-run` first.
8. Choose `send` only after the dry run looks correct. Scheduled runs then
   deliver automatically.

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

## Codex/Cowork installation

Install the skill from the repository with the standard skill installer:

```bash
python3 /path/to/install-skill-from-github.py \
  --repo OWNER/kind-of-news \
  --path skills/kind-of-news
```

The skill can generate the same LinkedIn-ready issue on demand. Its scheduled
delivery depends on the connected apps available in the user's Codex/Cowork
environment; GitHub Actions is the canonical automated path.

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
