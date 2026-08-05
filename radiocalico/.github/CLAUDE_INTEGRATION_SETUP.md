# Claude GitHub Actions Integration Setup

This guide walks through setting up the Claude integration with GitHub Actions for automated code review, documentation generation, and issue processing.

## Prerequisites

- GitHub repository with Actions enabled
- Claude API key from Anthropic
- GitHub token with appropriate permissions

## Setup Instructions

### 1. Get Your Claude API Key

1. Visit [Anthropic Console](https://console.anthropic.com)
2. Navigate to API keys section
3. Create a new API key
4. Copy the key (you won't be able to see it again)

### 2. Add GitHub Secrets

Add the following secrets to your GitHub repository:

**For the repository:**
1. Go to Settings → Secrets and variables → Actions
2. Create a new repository secret named `ANTHROPIC_API_KEY`
3. Paste your Claude API key
4. Click "Add secret"

The `GITHUB_TOKEN` is automatically available in GitHub Actions workflows.

### 3. Enable Actions

1. Go to your repository's Actions tab
2. Click "I understand my workflows, go ahead and enable them"

## Workflow Features

### Code Review Workflow
- **Trigger:** Pull requests (opened or synchronized)
- **Features:**
  - Reviews PR diff for bugs and code quality issues
  - Analyzes security concerns
  - Provides actionable suggestions
  - Posts review as a PR comment

**Permissions Required:**
- `contents: read` — to read code
- `pull-requests: write` — to comment on PRs

### Documentation Generation
- **Trigger:** Pull requests targeting `docs` branches
- **Features:**
  - Analyzes project structure
  - Generates API documentation
  - Creates database schema documentation
  - Generates development guides
  - Commits generated docs to the PR

**Permissions Required:**
- `contents: write` — to commit changes
- `pull-requests: write` — to comment on PRs

### Issue Processing
- **Trigger:** New issues or issue edits
- **Features:**
  - Analyzes issue content
  - Classifies issue type (bug, feature, documentation)
  - Assigns priority level
  - Posts analysis as comment
  - Auto-labels issues

**Permissions Required:**
- `issues: write` — to add labels and comments
- `contents: read` — to provide context

## Manual Workflow Trigger

All workflows can be manually triggered via:

1. Go to Actions tab
2. Select "Claude Integration"
3. Click "Run workflow"
4. Select the branch
5. Click "Run workflow"

## Configuration

### Workflow Triggers

Modify `.github/workflows/claude-integration.yml` to adjust triggers:

```yaml
on:
  pull_request:
    types: [opened, synchronize]  # Adjust PR triggers
  issues:
    types: [opened, edited]       # Adjust issue triggers
  workflow_dispatch:              # Manual trigger
```

### Model Selection

The workflow uses `claude-opus-5` by default. To use a different model, edit the scripts:

```python
model="claude-opus-5",  # Change to claude-sonnet-5, claude-haiku-4.5, etc.
```

## Monitoring

### View Workflow Runs

1. Go to Actions tab
2. Click on a workflow run to see detailed logs
3. Check for any errors or warnings

### Troubleshooting

**"ANTHROPIC_API_KEY not set"**
- Ensure the secret is added to repository settings
- Verify the secret name is exactly `ANTHROPIC_API_KEY`

**"GITHUB_TOKEN not set"**
- This should be automatic; check workflow permissions
- Ensure `permissions` block is correctly indented in YAML

**API Rate Limiting**
- Claude API has rate limits; check Anthropic console for usage
- GitHub Actions API has rate limits; use exponential backoff for retries

**Workflow Timeouts**
- Workflows have a 6-hour timeout
- Long-running analyses might need optimization

## Customization Examples

### Custom Code Review Criteria

Edit `.github/scripts/claude_code_review.py` to modify the system prompt:

```python
system="""You are an expert code reviewer. Focus on:
- Performance optimizations
- Memory leaks
- Database query optimization
- Security vulnerabilities
- Test coverage
"""
```

### Additional Issue Labels

Edit `.github/scripts/process_issues.py` to add custom labels:

```python
labels = [
    "claude-reviewed",
    analysis["issue_type"],
    analysis["priority"],
    "needs-triage",  # Add custom label
]
```

### Filter Code Review by File Type

Modify the code review script to ignore certain file patterns:

```python
IGNORE_PATTERNS = [
    "*.min.js",
    "*.lock",
    ".env",
    "dist/",
]
```

## Best Practices

1. **Review Claude's suggestions** — AI analysis can be helpful but isn't perfect
2. **Adjust system prompts** — Tailor reviews to your project's needs
3. **Monitor costs** — Track API usage in Anthropic console
4. **Iterate on prompts** — Refine what Claude looks for based on your feedback
5. **Add human review** — Use Claude as a helper, not a replacement for code review
6. **Test workflows** — Create a test PR/issue to verify setup

## Cost Considerations

- Code review: ~1,000-2,000 tokens per PR (small-medium PRs)
- Documentation generation: ~2,000-5,000 tokens
- Issue analysis: ~500-1,000 tokens per issue

Exact costs depend on:
- PR/issue size
- Selected model
- Max tokens settings

Check Anthropic pricing and monitor your usage.

## Support

For issues or questions:
1. Check workflow run logs in Actions tab
2. Review Claude API documentation
3. Check GitHub Actions documentation
4. File an issue in the repository

## Security Notes

- **Never commit API keys** to the repository
- Always use GitHub Secrets for sensitive data
- Review generated code carefully before merging
- Ensure GitHub Actions is enabled only for trusted branches
- Regularly rotate API keys

## Next Steps

1. Follow setup instructions above
2. Create a test PR to trigger code review
3. Create a test issue to trigger issue processing
4. Monitor workflow runs and adjust as needed
5. Customize prompts for your project's needs
