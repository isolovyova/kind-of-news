# Kind of News assistant instructions

When a user asks to install or configure this repository, or provides its
GitHub URL, read `docs/assistant-setup.md` and follow it as the setup contract.

Use one question at a time, keep implementation details hidden behind the
guided flow, never request secrets in chat, and do not stop after installing
the plugin. Invoke `kind-of-news-setup` immediately, explain what Kind of News
does, and ask the first channel question. Do not claim the automation is
installed until the skill is loaded, the delivery connection is authorized, the
recurring task is active, and issue #1 has been sent after final confirmation.
Report success only after both schedule activation and the immediate send are
verified. A preview or dry run is opt-in; do not ask for it in the normal flow.
Do not ask end users to create a GitHub repository for the default setup.
