# Kind of News

Kind of News is a small, warm, fact-checked English news bulletin for people
who have had enough bulletins. It creates a short issue every Monday,
Wednesday, and Friday and delivers it to the channel the user chooses.

## For users: one link, no GitHub repository

You do not need to create a GitHub repository, fork this project, configure
GitHub Actions, or maintain code. GitHub is only where the public skill is
stored. Your AI host keeps the skill, schedule, and authorized delivery
connection in your own account or local profile.

Copy this one message into Codex or Claude Code:

```text
Install the Kind of News plugin from https://github.com/isolovyova/kind-of-news and immediately start its setup tutorial in this same turn. Do not stop after saying installed. First explain in two sentences what Kind of News does, then ask me one question at a time. Do not ask me to create a GitHub repository. Use Monday/Wednesday/Friday at 06:00 in my timezone as defaults, keep secrets in the host's secure connection flow, run a dry run first, and create automatic delivery only after I confirm.
```

The assistant will:

1. install the plugin, or both skills when plugin installation is unavailable;
2. immediately start a short welcome and setup tutorial;
3. ask which channel, timezone, and time to use;
4. connect Gmail, Telegram, Slack, Discord, ntfy, or a webhook when the host
   supports it;
5. generate a dry run without sending anything;
6. create the recurring task after the user confirms the first live send.

After that, the digest runs automatically. There is no approval gate for every
future issue. The user can pause or edit the task in the host where it was
created.

### Where the schedule lives

| Host | Durable no-repository option | Important limitation |
| --- | --- | --- |
| Codex app | Codex recurring automation | Availability and delivery connectors depend on the account and app surface. |
| ChatGPT | Scheduled Task | Tasks are managed in ChatGPT, not the Codex app; connected Gmail is available only when enabled for the account. |
| Claude Code Desktop | Local scheduled task | The app must be open and the computer awake. |
| Claude Code cloud | Routine | Routines run in the cloud but may require a repository context; disclose that before setup. |
| GitHub Actions | Repo-backed workflow | Advanced path; requires the user's own repository and secrets. |

The default no-repository recommendation is Codex recurring automation or a
ChatGPT Scheduled Task. Claude Code Desktop is the local alternative. The
assistant should choose the option available in the user's current product and
say clearly when a connector or cloud scheduler is unavailable.

Read the complete assistant contract in
[`docs/assistant-setup.md`](docs/assistant-setup.md).

## What gets installed

The user-facing plugin contains two skills:

1. `kind-of-news-setup` is the interactive tutorial and scheduling handoff.
2. `kind-of-news` controls research, fact-checking, tone, and the four-block
   format.

The host's recurring task invokes the editorial skill and performs delivery
through the user's authorized account or connector. Installing the plugin alone
does not authorize a channel or create a schedule; the setup tutorial handles
those steps explicitly.

The Python runner and GitHub Actions workflows in this repository are retained
for users who explicitly want a self-managed, repo-backed deployment.

## Claude Code plugin install

Claude Code users can install the public plugin in personal scope when plugin
management is available:

```text
/plugin marketplace add https://github.com/isolovyova/kind-of-news.git
/plugin install kind-of-news@kind-of-news --scope user
```

Then invoke the setup wizard if Claude does not start it automatically:

```text
/kind-of-news:kind-of-news-setup
```

The plugin contains the tutorial and editorial skill. Scheduling and delivery
are still configured once in Claude Code Desktop/Routines or another connected
host.

## Advanced fallback: GitHub Actions

Use this route only when the user explicitly wants a repository-backed,
self-managed deployment:

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

GitHub scheduled workflows can be delayed during high-load periods. In public
repositories they can also be disabled after 60 days without repository
activity, so delivery time is approximate and the Actions tab should be checked
if a run is missing.

For local setup, copy `config.example.yml` to `config.yml` and run
`python3 scripts/setup.py`; commit only the resulting non-secret configuration.

## Advanced Actions secrets

All Actions runs need:

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

The helper asks for the OAuth client secret without putting it in shell
history. Copy only the printed refresh token into GitHub Secrets. The helper
uses the Gmail `gmail.send` scope and does not write credentials to the
repository.

## Delivery behavior

- Gmail sends the complete issue as an email.
- Telegram sends the complete issue as plain text through a bot.
- Webhook supports `generic`, `slack`, `discord`, and `ntfy` payloads.

The issue is sent only after structured-output and source validation. The
publication date is the issue ID. If a channel already succeeded for that ID,
it is not sent again. If a channel fails, a supported host retries only that
channel.

## Editorial contract

Every issue begins with:

```text
Kind of News #YYYY-MM-DD
The world is noisy. This is a small, warm window into the parts that don't scream.
```

It contains four blocks: Good thing, On this day or Happening now, Tiny fact,
and Thought for the day. Sources and full verification links are included.

The product creates LinkedIn-ready text but never auto-posts to LinkedIn.

## Skill-only install for advanced users

Codex can install the two reusable skills directly with the standard GitHub
skill installer:

```bash
python3 /path/to/install-skill-from-github.py \
  --repo isolovyova/kind-of-news \
  --path skills/kind-of-news-setup
python3 /path/to/install-skill-from-github.py \
  --repo isolovyova/kind-of-news \
  --path skills/kind-of-news
```

After installation, invoke `kind-of-news-setup` immediately. For automatic
delivery, use the host setup flow above, or choose the advanced GitHub Actions
fallback.

## Local checks

```bash
python3 scripts/validate_skill.py skills/kind-of-news
python3 -m unittest discover -s tests -v
python3 -m runner --config config.yml --fixture tests/fixtures/valid_issue.json --date 2026-08-03 --dry-run
```

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

## License

MIT. See [LICENSE](LICENSE).
