# Codex / Claude Code setup

The simplest user experience is one copy-paste message:

```text
Install and configure Kind of News from https://github.com/isolovyova/kind-of-news. Guide me one step at a time, ask only one question at a time, use GitHub Actions for automatic Monday/Wednesday/Friday delivery, and do not ask me to paste secrets into chat.
```

The assistant should read [`assistant-setup.md`](assistant-setup.md), help the
user create their own repository from the template, collect non-secret
preferences, explain the required GitHub Secrets, verify setup, and run a dry
run before the first real send.

The repository skill can also be installed directly by advanced users:

```bash
python3 /path/to/install-skill-from-github.py \
  --repo OWNER/kind-of-news \
  --path skills/kind-of-news
```

The exact installer and available connectors vary by environment. The guided
flow is therefore the supported path for Codex, Claude Code, and similar tools.
