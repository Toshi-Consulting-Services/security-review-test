# security-review-test

Demo repo to watch the Claude Code GitHub Action perform a security review on a PR.

The `main` branch holds a tiny safe Flask app. Feature branches deliberately introduce
vulnerable code so the action's PR review has something interesting to find.

## How the review runs

`.github/workflows/claude-review.yml` triggers `anthropics/claude-code-action@v1` on
every `pull_request` event, prompting it to do an OWASP-aligned security review and
post findings as a PR comment.

Required: an `ANTHROPIC_API_KEY` GitHub Actions secret on this repo.

<!-- trigger Phase 3 reviewdog validation 2026-05-12T12:01:50Z -->
<!-- reviewdog retry 1778587635 -->
