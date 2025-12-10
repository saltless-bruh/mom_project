# Pull Request Template

## Description

**Summary of changes:**
[Provide a clear and concise description of what this PR does]

**Related Issue(s):**
Closes #[issue number]
Related to #[issue number]

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Refactoring (no functional changes)
- [ ] Performance improvement
- [ ] Test coverage improvement

## Phase

- [ ] Phase 1: MVP
- [ ] Phase 2: Enhancement
- [ ] Phase 3: Polish & Production
- [ ] Post-launch maintenance

## Changes Made

### Files Changed

- `path/to/file1.py` - [Description of changes]
- `path/to/file2.py` - [Description of changes]

### Key Implementation Details

- [Detail 1]
- [Detail 2]
- [Detail 3]

## Testing

### Unit Tests

- [ ] New tests added for new functionality
- [ ] Existing tests updated as needed
- [ ] All tests pass locally

**Test Coverage:**

- Previous: [X%]
- Current: [Y%]

### Integration Tests

- [ ] Integration tests added/updated
- [ ] All integration tests pass

### Manual Testing

- [ ] Tested with sample invoices
- [ ] Tested error scenarios
- [ ] Tested edge cases

**Manual Test Results:**

```bash
Test 1: [Description] - ✅ Pass / ❌ Fail
Test 2: [Description] - ✅ Pass / ❌ Fail
Test 3: [Description] - ✅ Pass / ❌ Fail
```

### Performance Testing (if applicable)

- [ ] Performance benchmarks run
- [ ] No performance regressions
- [ ] Improvements: [description]

## Code Quality Checklist

### Functionality

- [ ] Code works as intended and meets requirements
- [ ] All edge cases handled appropriately
- [ ] Error messages are clear and actionable
- [ ] No hardcoded values (configuration used)

### Code Style

- [ ] Follows PEP 8 style guidelines
- [ ] Type hints used for function signatures
- [ ] Docstrings for all public functions/classes
- [ ] No duplicate code (DRY principle followed)
- [ ] Proper separation of concerns

### Security & Privacy

- [ ] No sensitive data in logs
- [ ] Input validation implemented
- [ ] SQL injection prevention (parameterized queries)
- [ ] No secrets in code (environment variables used)
- [ ] File upload validation (if applicable)

### Documentation

- [ ] README.md updated (if user-facing changes)
- [ ] TECHNICAL_SPECS.md updated (if architecture changes)
- [ ] Inline comments for complex logic
- [ ] API documentation updated (if applicable)
- [ ] CHANGELOG.md entry added

### Performance

- [ ] No N+1 query problems
- [ ] Efficient algorithms used
- [ ] Database indexes appropriate
- [ ] Resources properly managed (files closed, connections released)
- [ ] API calls minimized/cached where appropriate

## Database Changes

- [ ] No database changes
- [ ] Schema changes (describe below)
- [ ] Migration script provided
- [ ] Backward compatible

**Schema Changes:**

```sql
-- Paste relevant SQL here
```

## API Changes

- [ ] No API changes
- [ ] New endpoints added
- [ ] Existing endpoints modified
- [ ] Breaking changes (describe below)
- [ ] API documentation updated

**Endpoint Changes:**

```bash
POST /api/new-endpoint - [Description]
PUT /api/existing-endpoint - [Changes made]
```

## Configuration Changes

- [ ] No configuration changes
- [ ] New environment variables required
- [ ] config.yaml updated
- [ ] .env.example updated

**New Environment Variables:**

```bash
NEW_VAR=description_of_purpose
```

## Dependencies

- [ ] No new dependencies
- [ ] New packages added (listed below)
- [ ] requirements.txt updated
- [ ] All dependencies compatible

**New Dependencies:**

```bash
package-name==version  # Purpose: [why needed]
```

## Screenshots/Logs

**Before:**
[Attach screenshots or paste logs showing before state]

**After:**
[Attach screenshots or paste logs showing after state]

## Breaking Changes

- [ ] No breaking changes
- [ ] Breaking changes (describe below)

**Description of breaking changes:**
[Explain what breaks and migration path for users]

## Rollback Plan

**If this PR needs to be reverted:**

1. [Step 1]
2. [Step 2]
3. [Step 3]

## Deployment Notes

**Special considerations for deployment:**

- [ ] Requires database migration
- [ ] Requires configuration update
- [ ] Requires service restart
- [ ] Requires manual steps (describe below)

**Manual Steps Required:**

```bash
1. [Step description]
2. [Step description]
```

## Post-Deployment Validation

**After deploying, verify:**

- [ ] [Check 1]
- [ ] [Check 2]
- [ ] [Check 3]

## Reviewer Notes

**Areas needing special attention:**

- [Area 1: Specific file or function needing careful review]
- [Area 2: Complex logic or algorithm]
- [Area 3: Security-sensitive code]

**Questions for reviewers:**

1. [Question about design decision]
2. [Question about implementation approach]

## Additional Context

[Any additional information that would be helpful for reviewers]

---

## Pre-Merge Checklist

- [ ] All CI checks pass
- [ ] Code review completed and approved
- [ ] Documentation updated
- [ ] Tests added and passing
- [ ] No merge conflicts
- [ ] Branch is up to date with main/develop

## Post-Merge Tasks

- [ ] Close related issues
- [ ] Update project board
- [ ] Notify stakeholders (if applicable)
- [ ] Monitor for issues in production (if applicable)

---

**PR Author:** @[github-username]  
**Reviewers:** @[reviewer1] @[reviewer2]  
**Target Branch:** main / develop / feature-branch  
**Estimated Review Time:** [small/medium/large]
