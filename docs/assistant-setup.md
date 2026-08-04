# AI-assisted Kind of News setup

This is the setup contract for Codex, Claude Code, or another coding assistant
that can read this public repository.

## Start condition

Treat either of these as an installation request:

- the user provides `https://github.com/isolovyova/kind-of-news`;
- the user says “install Kind of News”, “set up the news digest”, or asks for
  recurring delivery.

Do not start by explaining YAML, Python, GitHub Actions, OAuth scopes, or API
schemas. Start as a setup guide.

## Conversation flow

Ask one question at a time. Use these defaults unless the user changes them:

1. Delivery channel: Gmail, Telegram, webhook, or more than one.
2. Timezone: `America/Vancouver`.
3. Local delivery time: `06:00`.
4. Webhook preset, only when webhook is selected: generic, Slack, Discord, or
   ntfy.

Then:

1. Help the user create their own repository from the template, or use an
   existing repository if they already made one.
2. Run **Kind of News Setup** with the selected non-secret preferences. The
   workflow creates `config.yml` and commits it to the user's repository.
3. Explain the exact secret names required for the selected channels.
4. Direct the user to add secret values in the repository's GitHub Actions
   secret store. Never ask the user to paste a token, OAuth secret, refresh
   token, bot token, or webhook URL into chat or a committed file.
5. Run the setup check again and do not claim success until it is green.
6. Run the main workflow in `dry-run` mode and show the user what to inspect.
7. Ask for explicit confirmation before the first `send` run.

If the assistant has no GitHub write access, give the user the exact page and
button to click. Do not pretend that a public link alone can create a repo or
secrets without authorization.

## Secret guidance

Always derive the list from the selected channels:

- all configurations: `OPENAI_API_KEY`;
- Gmail: `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, `GMAIL_REFRESH_TOKEN`,
  `GMAIL_TO`;
- Telegram: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`;
- webhook: `WEBHOOK_URL`.

For Gmail, point the user to `scripts/gmail_oauth.py` for the local OAuth
helper. It prints a refresh token for the user to enter directly into GitHub
Secrets and does not save it in the repository.

## Completion criteria

Report “installed” only when all of these are true:

- the user's repository contains non-secret `config.yml`;
- the setup check is green;
- a dry run produced a date-matched, four-block, source-validated issue;
- the user knows that the schedule may be delayed by GitHub Actions load;
- no real message was sent without explicit confirmation.

The product creates LinkedIn-ready text but never auto-posts to LinkedIn.
