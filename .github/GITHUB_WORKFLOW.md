# GitHub Workflow Guide for AI Agents

## Mom's Accounting Automation System (MAAS)

This guide explains how AI agents should interact with GitHub for this project.

---

## 🚀 Getting Started

### 1. Repository Setup

**First Time Setup:**

```bash
# Clone repository
git clone https://github.com/[username]/mom-accounting-automation.git
cd mom-accounting-automation

# Set up Git configuration
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Create and switch to develop branch
git checkout -b develop
```

**Branch Naming Convention:**

- `feature/[description]` - New features (e.g., `feature/gemini-extraction`)
- `bugfix/[issue-number]-[description]` - Bug fixes (e.g., `bugfix/42-validation-error`)
- `hotfix/[description]` - Urgent production fixes
- `docs/[description]` - Documentation updates
- `test/[description]` - Test additions/improvements
- `refactor/[description]` - Code refactoring

---

## 📝 Issue-Driven Development

### Creating Issues

**For New Features:**

1. Use `.github/ISSUE_TEMPLATE/feature_request.md` template
2. Label: `enhancement`
3. Assign to appropriate milestone (Phase 1/2/3)
4. Link to related issues

**For Bugs:**

1. Use `.github/ISSUE_TEMPLATE/bug_report.md` template
2. Label: `bug` + severity (`critical`, `high`, `medium`, `low`)
3. Include reproduction steps and logs
4. Assign priority

**For Phase Tasks:**

1. Use `.github/ISSUE_TEMPLATE/phase_task.md` template
2. Label: `task` + phase label (`phase-1`, `phase-2`, `phase-3`)
3. Break down into subtasks if large
4. Link dependencies

### Issue Labels

**Priority:**

- `critical` - System-breaking, needs immediate attention
- `high` - Important feature or significant bug
- `medium` - Standard priority
- `low` - Nice to have

**Type:**

- `bug` - Something isn't working
- `enhancement` - New feature request
- `task` - Implementation task
- `documentation` - Documentation improvements
- `question` - Further information requested
- `wontfix` - Will not be implemented
- `duplicate` - Duplicate of another issue

**Phase:**

- `phase-1` - MVP (Weeks 1-2)
- `phase-2` - Enhancement (Week 3)
- `phase-3` - Polish & Production (Week 4)
- `post-launch` - Future enhancements

**Component:**

- `backend` - Backend/API code
- `frontend` - UI code
- `automation` - ACSoft automation
- `extraction` - PDF/Gemini extraction
- `validation` - Data validation
- `database` - Database-related
- `testing` - Test-related
- `deployment` - Deployment-related

---

## 🔀 Branching & Pull Request Workflow

### Standard Development Flow

```bash
main (production)
 ├── develop (integration)
 │    ├── feature/gemini-extraction
 │    ├── feature/acsoft-automation
 │    └── bugfix/42-validation-error
```

**Step-by-Step Workflow:**

#### 1. Start New Feature/Fix

```bash
# Update develop branch
git checkout develop
git pull origin develop

# Create feature branch from develop
git checkout -b feature/gemini-extraction

# Alternatively, create from issue
# This creates branch named feature/issue-123-add-gemini-api
git checkout -b feature/issue-123-add-gemini-api develop
```

#### 2. Make Changes

```bash
# Make your code changes
# Write tests
# Update documentation

# Check status
git status

# Stage changes
git add app/services/gemini_client.py
git add tests/test_gemini_client.py
git add requirements.txt

# Or stage all
git add .

# Commit with clear message
git commit -m "feat: Add Gemini API client for invoice extraction

- Implement GeminiClient class with retry logic
- Add exponential backoff for API failures
- Include cost tracking per API call
- Add unit tests with mocked responses

Closes #123"
```

#### 3. Push to Remote

```bash
# Push feature branch
git push origin feature/gemini-extraction

# If branch doesn't exist remotely yet
git push -u origin feature/gemini-extraction
```

#### 4. Create Pull Request

**Via GitHub Web Interface:**

1. Go to repository on GitHub
2. Click "Pull requests" → "New pull request"
3. Base: `develop` ← Compare: `feature/gemini-extraction`
4. Fill out PR template (auto-populated from `.github/pull_request_template.md`)
5. Add reviewers (if applicable)
6. Assign to yourself
7. Link related issues (e.g., "Closes #123")
8. Add labels (phase, component)
9. Create pull request

**PR Title Format:**

```bash
feat: Add Gemini API client for invoice extraction
fix: Correct tax calculation in validator
docs: Update README with installation steps
test: Add integration tests for PDF processing
refactor: Simplify error handling in automation service
```

**PR Description Checklist:**

- [ ] Clear description of changes
- [ ] Links to related issues
- [ ] Testing performed and results
- [ ] Code quality checklist completed
- [ ] Documentation updated
- [ ] Breaking changes noted (if any)

#### 5. Code Review & Iteration

**If changes requested:**

```bash
# Make requested changes
git add .
git commit -m "refactor: Address PR review comments

- Improve error handling in retry logic
- Add more descriptive docstrings
- Extract magic numbers to constants"

# Push updates
git push origin feature/gemini-extraction
```

**PR automatically updates with new commits**

#### 6. Merge Pull Request

**Merge Strategies:**

**For feature branches (most common):**

- Use "Squash and merge" to keep history clean
- All commits squashed into single commit on develop

**For hotfixes:**

- Use "Merge commit" to preserve history
- Shows exact changes made in emergency fix

**After merge:**

```bash
# Switch back to develop
git checkout develop

# Pull latest (includes your merged changes)
git pull origin develop

# Delete local feature branch
git branch -d feature/gemini-extraction

# Delete remote feature branch (optional, GitHub can auto-delete)
git push origin --delete feature/gemini-extraction
```

---

## 🤖 AI Agent Git Commands Reference

### Common Operations

**Check current status:**

```bash
git status
git branch          # List branches
git branch -a       # List all branches (including remote)
git log --oneline   # View commit history
```

**Update from remote:**

```bash
git fetch origin    # Fetch updates without merging
git pull origin develop  # Pull and merge latest develop
```

**Create and switch branches:**

```bash
git checkout -b feature/new-feature     # Create and switch
git checkout existing-branch            # Switch to existing
git branch feature/new-feature          # Create without switching
```

**Stage and commit:**

```bash
git add file1.py file2.py              # Stage specific files
git add app/services/                  # Stage directory
git add .                              # Stage all changes
git commit -m "feat: Add new feature"  # Commit with message
git commit --amend                     # Amend last commit
```

**Push and pull:**

```bash
git push origin feature-branch         # Push branch
git push -u origin feature-branch      # Push and set upstream
git push --force-with-lease origin feature-branch  # Force push (careful!)
git pull origin develop                # Pull from develop
```

**Merge and rebase:**

```bash
git merge develop                      # Merge develop into current branch
git rebase develop                     # Rebase current branch onto develop
git rebase -i HEAD~3                   # Interactive rebase last 3 commits
```

**Resolve conflicts:**

```bash
# After conflict occurs
git status                             # See conflicted files
# Edit files to resolve conflicts
git add resolved-file.py
git commit -m "fix: Resolve merge conflicts"
```

**Stash changes:**

```bash
git stash                              # Stash current changes
git stash list                         # List stashes
git stash pop                          # Apply and remove latest stash
git stash apply                        # Apply latest stash (keep in stash)
git stash drop                         # Remove latest stash
```

**View diffs:**

```bash
git diff                               # Unstaged changes
git diff --staged                      # Staged changes
git diff develop                       # Diff against develop branch
git diff HEAD~1                        # Diff against previous commit
```

**Undo changes:**

```bash
git checkout -- file.py                # Discard changes in file
git reset HEAD file.py                 # Unstage file
git reset --soft HEAD~1                # Undo last commit (keep changes)
git reset --hard HEAD~1                # Undo last commit (discard changes)
git revert abc123                      # Create new commit undoing abc123
```

---

## 📋 Commit Message Guidelines

### Format

```bash
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation only
- `style` - Code style (formatting, no logic change)
- `refactor` - Code refactoring
- `test` - Adding or updating tests
- `chore` - Maintenance tasks
- `perf` - Performance improvement

### Scope (optional)

- `extraction` - PDF/Gemini extraction
- `validation` - Data validation
- `automation` - ACSoft automation
- `api` - API endpoints
- `db` - Database
- `ui` - User interface
- `config` - Configuration

### Examples

**Simple commit:**

```bash
feat(extraction): Add Gemini API integration
```

**Detailed commit:**

```bash
feat(extraction): Add Gemini API integration for invoice extraction

- Implement GeminiClient class with retry logic
- Add exponential backoff for API rate limits
- Include per-request cost tracking
- Support multi-page PDF processing

The Gemini 2.0 Flash model provides superior Vietnamese OCR
compared to alternatives. Cost is estimated at $0.03-0.05 per
invoice which meets budget requirements.

Closes #123
Refs #45, #67
```

**Bug fix:**

```bash
fix(validation): Correct tax calculation for multi-rate invoices

Previous logic assumed single tax rate per invoice. Now correctly
handles line items with different tax rates (0%, 5%, 8%, 10%).

Fixes #156
```

**Breaking change:**

```bash
feat(api)!: Change invoice response format

BREAKING CHANGE: Invoice API now returns items as array instead of
object keyed by line number. Clients must update parsing logic.

Migration: Replace `invoice.items[line_num]` with
`invoice.items.find(i => i.line_number === line_num)`

Closes #201
```

---

## 🎯 Project Board Usage

### GitHub Project Boards

**Columns:**

1. **Backlog** - Not yet started
2. **Todo** - Ready to work on
3. **In Progress** - Actively being worked on
4. **Review** - PR created, awaiting review
5. **Done** - Merged and completed

**Moving Issues:**

- Automatically moves based on PR status
- Manually move if working without PR
- Close issue when PR merged

**Milestones:**

- Phase 1: MVP (Week 1-2)
- Phase 2: Enhancement (Week 3)
- Phase 3: Polish & Production (Week 4)
- Post-Launch Enhancements

---

## 🔍 AI Agent GitHub Actions

### Automated Workflows

**When PR is created:**

1. Run linting (flake8, black)
2. Run unit tests (pytest)
3. Check test coverage
4. Build documentation
5. Security scan (if applicable)

**When PR is merged to develop:**

1. Run full test suite
2. Deploy to staging (if applicable)
3. Update project board
4. Close linked issues

**When PR is merged to main:**

1. Create release tag
2. Generate changelog
3. Build deployment package
4. Deploy to production (manual approval)

### Required Status Checks

**Before merging to develop:**

- [ ] All tests pass
- [ ] Code coverage > 80%
- [ ] Linting passes
- [ ] Documentation builds successfully
- [ ] At least 1 approval (if team project)

---

## 📊 Issue Lifecycle

### Typical Issue Flow

```bash
[Created] → [Triaged] → [In Progress] → [PR Created] → [Review] → [Merged] → [Closed]
```

**1. Created**

- New issue submitted
- Uses appropriate template
- Has clear description

**2. Triaged**

- Labeled appropriately
- Assigned priority
- Added to milestone
- Assigned to developer (optional)

**3. In Progress**

- Developer starts work
- Branch created from issue
- Regular updates via comments

**4. PR Created**

- Pull request opened
- Linked to issue ("Closes #123")
- CI/CD checks run

**5. Review**

- Code review performed
- Changes requested and addressed
- Approval granted

**6. Merged**

- PR merged to target branch
- Branch deleted
- Issue automatically closed (if "Closes #123" in PR)

**7. Closed**

- Verified in target branch
- Documented in changelog
- Added to release notes

---

## 🛡️ Best Practices for AI Agents

### DO ✅

1. **Always work from develop branch** (not main)
2. **Create feature branches** for each task
3. **Write clear commit messages** following conventions
4. **Link commits to issues** using "Closes #123"
5. **Keep PRs focused** - one feature/fix per PR
6. **Update tests** with code changes
7. **Update documentation** as you go
8. **Request reviews** before merging (if team)
9. **Delete branches** after merging
10. **Keep develop up-to-date** with main

### DON'T ❌

1. **Don't commit directly to main** - always use PRs
2. **Don't commit secrets** - use environment variables
3. **Don't commit large binary files** - use .gitignore
4. **Don't force push to shared branches** - use --force-with-lease carefully
5. **Don't leave stale branches** - clean up after merge
6. **Don't mix concerns** - separate features into different PRs
7. **Don't skip tests** - ensure all tests pass
8. **Don't ignore merge conflicts** - resolve immediately
9. **Don't commit commented-out code** - remove or explain
10. **Don't use generic messages** - be specific

---

## 🚨 Emergency Hotfix Process

**For critical production bugs:**

```bash
# Create hotfix branch from main (not develop)
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug

# Make minimal fix
# Test thoroughly
# Commit

git commit -m "hotfix: Fix critical bug in invoice processing

Critical issue: Invoices with missing tax fields caused system crash.

Quick fix: Add null check before tax calculation.

Closes #CRITICAL-456"

# Push and create PR to main
git push origin hotfix/critical-bug

# After merging to main, also merge to develop
git checkout develop
git pull origin main
git push origin develop
```

**Hotfix Characteristics:**

- Bypass normal flow
- Minimal changes only
- Immediate review
- Fast-track approval
- Merge to both main AND develop

---

## 📚 Additional Resources

### Git References

- [Pro Git Book](https://git-scm.com/book/en/v2)
- [GitHub Docs](https://docs.github.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Best Practices](https://sethrobertson.github.io/GitBestPractices/)

### Project-Specific

- [TECHNICAL_SPECS.md](../TECHNICAL_SPECS.md) - Technical specifications
- [AI_AGENT_INSTRUCTIONS.md](../AI_AGENT_INSTRUCTIONS.md) - Development guide
- [Mom-Project-Proposal](../Mom-Project-Proposal) - Project overview

---

## 🎓 Quick Reference Cheat Sheet

```bash
# Daily workflow
git checkout develop && git pull origin develop
git checkout -b feature/my-feature
# ... make changes ...
git add .
git commit -m "feat: Add my feature"
git push origin feature/my-feature
# ... create PR on GitHub ...

# Update feature branch with latest develop
git checkout develop && git pull origin develop
git checkout feature/my-feature
git merge develop  # or: git rebase develop

# Before creating PR
git status                    # Check what's changed
pytest tests/                 # Run tests
flake8 app/                   # Check linting
git log --oneline -5          # Review recent commits

# After PR merged
git checkout develop && git pull origin develop
git branch -d feature/my-feature
git push origin --delete feature/my-feature
```

---

**Document Version:** 1.0  
**Last Updated:** December 5, 2025  
**Maintained By:** Development Team
