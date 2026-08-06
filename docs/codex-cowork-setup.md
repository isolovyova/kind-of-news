sed: --: No such file or directory
# Install Kind of News for private use

Readers should subscribe at <https://buttondown.com/kindofnews>. Use this
document only when you want Codex or Claude Code to generate one personal issue
on demand.

## Codex

Install the repository's plugin from
<https://github.com/isolovyova/kind-of-news>, then ask for a personalized issue.
The skill researches and validates exactly four blocks, displays the issue in
the conversation, and saves a local Markdown copy only when requested. It does
not subscribe anyone, schedule delivery, connect a channel, use Buttondown, or
send email.

## Claude Code

```text
/plugin marketplace add https://github.com/isolovyova/kind-of-news.git
/plugin install kind-of-news@kind-of-news --scope user
```

Then invoke:

```text
/kind-of-news:kind-of-news
```

For a no-repository install, the plugin is the only setup required. The public
GitHub Actions workflow is separate repository plumbing for the Buttondown
newsletter and is not part of private use.
