# Security

Kind of News requires API credentials for generation and optional delivery
channels. Treat every token, OAuth client secret, refresh token, chat ID, and
webhook URL as sensitive.

- Store credentials only in GitHub Actions Secrets or an equivalent secret store.
- Do not paste credentials into issues, pull requests, chat, logs, or `config.yml`.
- Do not print full API responses from delivery adapters.
- Rotate a token immediately if it appears in a commit or log.
- Keep the repository workflow read-only for repository contents.
- Review third-party workflow changes before enabling them in a fork.

The runner stores only the generated issue and per-channel success markers in
its local state directory. It does not commit generated issues back to the
repository.

Report suspected security issues privately to the repository owner rather than
opening a public issue with credentials or exploit details.
