# Codex/Cowork setup

The canonical Kind of News automation runs in GitHub Actions. Codex/Cowork is
the secondary path for users who want to install the reusable skill and create a
scheduled automation in their own Codex environment.

## Install the skill

```bash
python3 /path/to/install-skill-from-github.py \
  --repo OWNER/kind-of-news \
  --path skills/kind-of-news
```

## Create the automation

Create a recurring automation with these defaults:

- Monday, Wednesday, and Friday;
- 06:00 in the user's timezone;
- English output;
- the four Kind of News blocks;
- the universal date-based intro.

The automation prompt should ask Codex to generate the issue using the
`kind-of-news` skill and deliver it through the connected channel. Use the
available Gmail or other authorized app connector. Do not put API keys or bot
tokens in the prompt.

Telegram delivery is guaranteed by the GitHub Actions runner, not by this
Codex/Cowork path, because connector availability varies between environments.

## Recommendation

For a public, repeatable one-time setup flow, use GitHub Actions. Use the
Codex/Cowork path for on-demand drafting, local experimentation, or environments
that already have the required connectors.
