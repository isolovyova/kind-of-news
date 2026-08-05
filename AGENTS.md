# Kind of News assistant instructions

When a user asks to install or configure this repository, or provides its
GitHub URL, read `docs/assistant-setup.md` and follow it as the setup contract.

For an ordinary reader, direct them to the branded newsletter subscription at
https://buttondown.com/kindofnews. Do not turn that request into a personal
Gmail/Telegram connection or an individual schedule. The private connected-
channel wizard is only for users who explicitly request a personal digest.
The newsletter author uses one advanced GitHub Actions schedule and the
Buttondown API; Buttondown owns subscriber management and delivery.

Use one question at a time, keep implementation details hidden behind the
guided flow, never request secrets in chat, and do not stop after installing
the plugin. Invoke `kind-of-news-setup` immediately, explain what Kind of News
does, and ask the first channel question. Do not claim the automation is
installed until the skill is loaded, the delivery connection is authorized, the
recurring task is active, and issue #1 has been sent after final confirmation.
Report success only after both schedule activation and the immediate send are
verified. A preview or dry run is opt-in; do not ask for it in the normal flow.
Do not ask end users to create a GitHub repository for the default setup.
