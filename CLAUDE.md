# Kind of News assistant instructions

When a user asks to install or configure this repository, or provides its
GitHub URL, read `docs/assistant-setup.md` and follow it as the setup contract.

Use one question at a time, keep implementation details hidden behind the
guided flow, never request secrets in chat, and do not claim the automation is
installed until the skill is loaded, the delivery connection is authorized, the
recurring task is active, and a dry run passes. Do not ask end users to create a
GitHub repository for the default setup.
