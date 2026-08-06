# Security

The automated newsletter runner requires `OPENAI_API_KEY` for generation and
`BUTTONDOWN_API_KEY` for publishing. Treat both as secrets.

- Store credentials only in GitHub Actions Secrets or an equivalent secure
  host secret store.
- Do not paste credentials into issues, pull requests, chat, logs, or config
  files.
- Do not print full API responses from the publisher.
- Rotate a token immediately if it appears in a commit or log.
- Keep the repository workflow read-only for repository contents.
- Review third-party workflow changes before enabling them in a fork.

The runner stores only the generated issue and its per-issue Buttondown success
marker in the local state directory. It does not commit generated issues back
to the repository.

Report suspected security issues privately to the repository owner rather than
opening a public issue with credentials or exploit details.
