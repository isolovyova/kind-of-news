# Advanced self-managed GitHub Actions setup

This is an optional, repo-backed deployment path for users who explicitly want
to own a GitHub repository, manage its secrets, and maintain its scheduled
workflow. It is not required for the guided Codex or Claude Code setup.

## Setup

1. Create a repository from this template or fork this project.
2. Open **Actions → Kind of News Setup → Run workflow**. Choose one or more
   channels (`gmail`, `telegram`, or `webhook`), the timezone, local delivery
   time, and a webhook provider when `webhook` is selected. The workflow writes
   only the non-secret `config.yml` and commits it to the repository.
3. Add the required values as GitHub Actions Secrets. Never put them in
   `config.yml`, issues, logs, or chat.
4. Run **Kind of News Setup** again. It checks the skill and credentials.
5. Run **Actions → Kind of News → Run workflow** with the advanced
   repo-runner `dry-run` first. This preview intentionally sends nothing.
6. Inspect the result. Choose `send` only after the dry run looks correct and
   you have explicitly confirmed the first live delivery.

The checked-in scheduled workflow currently runs Monday, Wednesday, and Friday
at 06:00 in `America/Vancouver`. Changing the setup workflow's time or timezone
writes those values to `config.yml`, but does not rewrite the schedule block in
`.github/workflows/kind-of-news.yml`; update that workflow too before relying on
a different recurring time.

GitHub scheduled workflows can be delayed during high-load periods. In public
repositories they can also be disabled after 60 days without repository
activity, so delivery time is approximate and the Actions tab should be checked
if a run is missing.

This advanced runner's `dry-run` is different from the normal guided setup. In
the guided setup, the assistant collects the configuration, asks one final
confirmation, then validates the issue, activates recurring delivery for
subsequent issues, and sends issue #1 immediately. It reports success only
after both schedule activation and the immediate send succeed.

## Actions secrets

All Actions runs need:

- `OPENAI_API_KEY`

When Gmail is selected:

- `GMAIL_CLIENT_ID`
- `GMAIL_CLIENT_SECRET`
- `GMAIL_REFRESH_TOKEN`
- `GMAIL_TO`

### Optional Gmail sender alias

`GMAIL_FROM` is an optional repository variable, not a secret. Set it only to
an email address that has already been verified in the OAuth-authorized Gmail
account under **Settings → Accounts and Import → Send mail as**. The workflow
continues to call Gmail's `users/me/messages/send` endpoint, so the OAuth
account remains the authorized sender; `GMAIL_FROM` only adds the verified
alias to the message's `From` header. This repository cannot create or verify
the alias. `GMAIL_TO` remains the recipient address.

When Telegram is selected:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

When webhook is selected:

- `WEBHOOK_URL`

For Gmail OAuth, create a desktop OAuth client and run the helper locally:

```bash
python3 scripts/gmail_oauth.py \
  --client-id "YOUR_CLIENT_ID"
```

The helper asks for the OAuth client secret without putting it in shell history.
Store the printed refresh token only in GitHub Secrets. Never paste it into a
chat or commit it.

## Delivery behavior

- Gmail sends the complete issue as an email.
- Telegram sends the complete issue as plain text through a bot.
- Webhook supports `generic`, `slack`, `discord`, and `ntfy` payloads.

The issue is sent only after structured-output and source validation. Each
numbered Sources item contains its direct source URL as a link; there is no
separate verification-links section. The publication date is the issue ID. If
a channel already succeeded for that ID, it is not sent again. If a channel
fails, a supported host retries only that channel.

## Local setup and checks

For a local runner, copy `config.example.yml` to `config.yml` and run:

```bash
python3 scripts/setup.py
```

Commit only the resulting non-secret configuration. To validate the checkout:

```bash
python3 scripts/validate_skill.py skills/kind-of-news
python3 -m unittest discover -s tests -v
python3 -m runner --config config.yml --fixture tests/fixtures/valid_issue.json --date 2026-08-03 --dry-run
```

For direct skill installation, use the standard GitHub skill installer:

```bash
python3 /path/to/install-skill-from-github.py \
  --repo isolovyova/kind-of-news \
  --path skills/kind-of-news-setup
python3 /path/to/install-skill-from-github.py \
  --repo isolovyova/kind-of-news \
  --path skills/kind-of-news
```

After installation, invoke `kind-of-news-setup` immediately. Keep credentials
in the host's secure connection flow or the Actions secret store.

## Official references

- [OpenAI Responses API and web search](https://platform.openai.com/docs/quickstart/make-your-first-api-request)
- [ChatGPT Scheduled Tasks](https://help.openai.com/en/articles/10291617-scheduled-tasks-in-chatgpt)
- [Gmail API sending](https://developers.google.com/workspace/gmail/api/guides/sending)
- [Telegram Bot API](https://core.telegram.org/bots/api#sendmessage)
- [Claude Code skills](https://code.claude.com/docs/en/slash-commands)
- [Claude Code Desktop scheduled tasks](https://code.claude.com/docs/en/desktop-scheduled-tasks)
- [Claude Code Routines](https://code.claude.com/docs/en/web-scheduled-tasks)
- [Claude Code plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
- [GitHub scheduled workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
- [GitHub Actions secrets](https://docs.github.com/en/actions/reference/security/secrets)
