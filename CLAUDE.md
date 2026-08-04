# Kind of News assistant instructions

When a user asks to install or configure this repository, or provides its
GitHub URL, read `docs/assistant-setup.md` and follow it as the setup contract.

Use one question at a time, keep the GitHub Actions implementation hidden
behind the guided flow, never request secrets in chat, and do not claim the
automation is installed until setup validation and a dry run pass.
