# Claude GitHub Actions Setup (Opus 5 + Pro subscription)

This repository's Claude workflows run on **Claude Opus 5**, authenticated with a
**`CLAUDE_CODE_OAUTH_TOKEN`** so that usage bills against a **Claude Pro subscription**
instead of API credits.

---

## Why the old setup was replaced

The previous workflows called the Anthropic Python SDK directly:

```python
pip install anthropic
client = Anthropic()                        # reads ANTHROPIC_API_KEY
client.messages.create(model="claude-haiku-4-5-20251001", ...)
```

That path **always bills API credits**. `CLAUDE_CODE_OAUTH_TOKEN` is *not* a drop-in
replacement for `ANTHROPIC_API_KEY` — it is a Claude Code credential, not an API key.
Passing it as `api_key=` to the raw SDK fails authentication.

Subscription billing requires the official **`anthropics/claude-code-action@v1`** action,
which accepts the token via its `claude_code_oauth_token` input. All workflows here were
migrated to that action.

| | Before | After |
|---|---|---|
| Invocation | hand-rolled `anthropic` SDK | `anthropics/claude-code-action@v1` |
| Secret | `ANTHROPIC_API_KEY` | `CLAUDE_CODE_OAUTH_TOKEN` |
| Model | `claude-haiku-4-5-20251001` | `claude-opus-5` |
| Billing | API credits | Pro subscription |

---

## Prerequisites

- **Admin access** to this repository
- An active **Claude Pro, Max, Team, or Enterprise** subscription
- **GitHub CLI** installed and authenticated (`gh auth login`) — required for quick setup

---

## Setup

### Option A — Quick setup (recommended)

From a terminal in this repository:

```bash
claude
```

Then inside the Claude Code session:

```
/install-github-app
```

This single command:

1. Installs the [Claude GitHub App](https://github.com/apps/claude) on the repository
2. Prompts you to create a long-lived subscription token, and saves it as the
   `CLAUDE_CODE_OAUTH_TOKEN` repository secret
3. Pushes a branch with workflow files and opens a PR in your browser

Because this repository **already has migrated workflow files**, you only need steps 1
and 2. When it offers to add workflow files, you can decline — or accept and discard the
generated ones in favour of the versions already committed here.

### Option B — Manual setup

**1. Install the GitHub App**

Install <https://github.com/apps/claude> on this repository. The action needs three of its
permissions: Contents (read/write), Issues (read/write), Pull requests (read/write).

**2. Generate the subscription token**

Run locally:

```bash
claude setup-token
```

This requires an active subscription and prints a long-lived OAuth token. Copy it.

> This token is tied to **your personal subscription**. Treat it like a password.

**3. Add it as a repository secret**

Via GitHub CLI:

```bash
gh secret set CLAUDE_CODE_OAUTH_TOKEN --repo pkjha-aero/Udemy_ClaudeCode_SundogEdu
# paste the token when prompted
```

Or via the web UI: **Settings → Secrets and variables → Actions → New repository secret**,
named exactly `CLAUDE_CODE_OAUTH_TOKEN`.

**4. Verify**

```bash
gh secret list --repo pkjha-aero/Udemy_ClaudeCode_SundogEdu
```

You should see `CLAUDE_CODE_OAUTH_TOKEN`.

**5. Remove the obsolete secret (optional)**

Once the new workflows are confirmed working:

```bash
gh secret delete ANTHROPIC_API_KEY --repo pkjha-aero/Udemy_ClaudeCode_SundogEdu
```

Deleting the secret does not revoke the key itself — retire it in the
[Claude Console](https://console.anthropic.com) if you no longer need it.

---

## Workflows in this repository

| Workflow | Mode | Trigger | Output |
|---|---|---|---|
| [`claude.yml`](workflows/claude.yml) | Interactive | `@claude` in an issue, PR comment, review, or new issue | Comment on the issue/PR |
| [`claude-code-review.yml`](workflows/claude-code-review.yml) | Automation | Every PR touching code paths | **Actions run log** |

Both pin the model with:

```yaml
claude_args: |
  --model claude-opus-5
```

### Note on review output

The `code-review` plugin writes findings to the **workflow run log**, not as a PR comment.
Open the run from the **Actions** tab to read them. The previous hand-rolled workflow
posted a PR review comment — that behaviour changed with this migration.

If you want reviews posted directly on the PR without maintaining a workflow, consider the
separate [Code Review product](https://code.claude.com/docs/en/code-review), which does
this automatically.

---

## Testing

1. **Test the responder:** open an issue and comment `@claude summarise this repository`.
2. **Test the reviewer:** open a PR touching a `.py` file, then check the **Actions** tab.
3. **Confirm billing:** visit <https://claude.ai/usage>. Runs should appear under your
   subscription, not as API credit spend.

---

## Cost control

Both workflows already include guards:

- `timeout-minutes: 20` caps runaway jobs
- `--max-turns 15` (in `claude.yml`) caps iterations
- `paths:` filters on `claude-code-review.yml` skip PRs that touch no code
- The `if:` condition on `claude.yml` avoids starting a runner for non-`@claude` comments

Runs consume **GitHub Actions minutes** *and* subscription usage. Keeping `CLAUDE.md`
concise helps, since Claude reads it on every run.

---

## Troubleshooting

**Claude doesn't respond to `@claude`**
- Confirm the GitHub App is installed on the repository
- Confirm `CLAUDE_CODE_OAUTH_TOKEN` exists (`gh secret list`)
- The comment must contain `@claude` as a whole word — not `/claude` or `@claude-bot`
- The commenting user needs **write access** to the repository
- Bot actors are rejected by default (prevents loops); allow specific ones with `allowed_bots`

**Authentication errors / the job finishes in ~10s having done nothing**

First check the **exact secret name**. It must be `CLAUDE_CODE_OAUTH_TOKEN` —
note the **`O`** in `OAUTH`. A near-miss like `CLAUDE_CODE_AUTH_TOKEN` does not error:
`${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}` silently resolves to an empty string, the action
starts with no credential, and the job exits almost immediately looking like a pass.

Confirm what the repository actually has:

```bash
gh secret list --repo pkjha-aero/Udemy_ClaudeCode_SundogEdu
```

To diagnose from a run log, expand the action's step and look at the `with:` block. If
`claude_code_oauth_token` is **absent from the listed inputs**, the secret name is wrong or
the secret does not exist. GitHub redacts a populated secret as `***`, so a correctly-named
secret still appears in that list.

Secrets cannot be renamed in place — add one under the correct name, then delete the old:

```bash
gh secret set CLAUDE_CODE_OAUTH_TOKEN --repo pkjha-aero/Udemy_ClaudeCode_SundogEdu
gh secret delete CLAUDE_CODE_AUTH_TOKEN --repo pkjha-aero/Udemy_ClaudeCode_SundogEdu
```

Also note: **Actions secrets must be repository-level** (or organization-level). An
account-level Codespaces secret is not visible to Actions.

Other causes:
- Verify the token works locally by running `claude` before debugging the workflow
- Regenerate with `claude setup-token` if it has been revoked or expired

**`Context access might be invalid: CLAUDE_CODE_OAUTH_TOKEN`**
- This is an editor lint warning, not a failure. It disappears once the secret exists.

**CI doesn't run on Claude's commits**
- Don't pass `github_token: ${{ secrets.GITHUB_TOKEN }}` to the action. GitHub does not
  trigger workflows on commits made with the default token. Omitting it lets the action
  authenticate as the Claude GitHub App instead.

**Fork PRs get no review**
- Expected on public repositories: GitHub withholds secrets from fork-triggered runs.

---

## Team / organization note

An OAuth token is tied to the subscription of whoever ran `claude setup-token`. If runs
should not bill one person, or you need the credential shared across repositories, use an
API key from the [Claude Console](https://console.anthropic.com) with the
`anthropic_api_key` input instead — or set up workload identity federation to avoid storing
a long-lived secret at all.

---

## Rollback

The previous API-key implementation is recoverable from git history:

```bash
git log --oneline --diff-filter=D -- .github/scripts/
git show <commit>^:.github/scripts/claude_code_review.py
```

---

## Reference

- [Claude Code GitHub Actions docs](https://code.claude.com/docs/en/github-actions)
- [Action configuration reference](https://github.com/anthropics/claude-code-action/blob/main/docs/usage.md#inputs)
- [Long-lived token generation](https://code.claude.com/docs/en/authentication#generate-a-long-lived-token)
