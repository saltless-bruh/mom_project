---
description: AI Agent Onboarding - Required Reading Before Starting Work
applyTo: '**/*'
alwaysApply: true
---

# AI Agent Onboarding Instructions

**CRITICAL: Read this first before starting any work on this project.**

This is the Mom's Accounting Automation System (MAAS) - an invoice data entry automation project for a Vietnamese accountant. Your work directly impacts a real person's daily workflow and family time.

---

## 🚨 MANDATORY PRE-WORK CHECKLIST

Before implementing ANY feature, fix, or change:

### 1. Read Technical Specifications
**File:** `/TECHNICAL_SPECS.md` (project root)

**You MUST read:**
- Section 2: Component specifications for the area you're working on
- Section 3: Configuration management
- Section 4: Error handling strategy
- Section 9: Appendix A & B (Tech stack and file structure)

**Why:** This ensures you understand the architecture, data models, and patterns already established.

### 2. Read GitHub Workflow Guide
**File:** `/.github/GITHUB_WORKFLOW.md`

**You MUST read:**
- Branching & Pull Request Workflow section
- Commit Message Guidelines
- Issue Lifecycle section

**Why:** This ensures your PRs and commits follow project conventions.

### 3. Read Contributing Guidelines
**File:** `/CONTRIBUTING.md` (project root)

**You MUST read:**
- Code Style section (PEP 8, Black, Type hints)
- Testing Guidelines section
- Code Review Checklist

**Why:** This ensures code quality and consistency.

### 4. Use GitHub Templates
**Location:** `/.github/ISSUE_TEMPLATE/`

**Available templates:**
- `bug_report.md` - For reporting bugs
- `feature_request.md` - For requesting features  
- `phase_task.md` - For tracking implementation tasks

**When to use:**
- Creating issues: Use appropriate template
- Creating PRs: Use `/.github/pull_request_template.md`

**Why:** Consistent issue/PR format ensures all necessary information is captured.

---

## 📂 SPEC FOLDER WORKFLOW

**CRITICAL: Always work with the spec folder before and during implementation.**

### Before Starting Any Work:

1. **Read spec/Requirements.md:**
   - Find the requirement(s) related to your task
   - Understand functional and non-functional requirements
   - Note the priority (P0, P1, P2)
   - Identify acceptance criteria

2. **Read spec/Design.md:**
   - Understand architectural decisions
   - Review component design
   - Check design patterns to use
   - Verify data flow and interactions

3. **Check spec/Tasks.md:**
   - Find your task in the task list
   - Read all sub-tasks and features
   - Understand task dependencies
   - Verify prerequisites are complete

### During Implementation:

1. **Track Progress in spec/Tasks.md:**
   - Mark sub-task as you start: leave `[]` as is
   - Implement the sub-task
   - Verify implementation matches requirements
   - Mark complete: change `[]` to `[x]`

2. **Verify Features Completeness:**
   - Before marking parent task complete, check ALL child items
   - Verify every feature is implemented
   - Run tests to confirm functionality
   - **Do NOT mark parent task complete if any child is incomplete**

3. **Update Documentation:**
   - If you add/change features, update spec/Requirements.md
   - If you change architecture, update spec/Design.md
   - Always update spec/Tasks.md checkboxes

### After Completing Task:

1. **Final Verification Checklist:**
   - [ ] All sub-tasks marked `[x]`
   - [ ] All features implemented and tested
   - [ ] Requirements met (check spec/Requirements.md)
   - [ ] Design patterns followed (check spec/Design.md)
   - [ ] Tests written and passing
   - [ ] Documentation updated

2. **Mark Task Complete:**
   - Change parent task: `[] Task-X.` → `[x] Task-X.`
   - Commit changes to spec/Tasks.md
   - Update task status summary in Tasks.md

---

## 📋 WORKFLOW FOR IMPLEMENTING FEATURES

### Step 1: Review Requirements
```
1. Read the user's request carefully
2. Check spec/Requirements.md for related requirements
3. Check spec/Design.md for architectural context
4. Check spec/Tasks.md for task definition
5. Check TECHNICAL_SPECS.md for detailed specifications
6. Check if similar functionality exists
7. Identify which components are affected
```

### Step 2: Plan Implementation
```
1. Review Section 2 of TECHNICAL_SPECS.md for affected components
2. Check file structure (TECHNICAL_SPECS.md Appendix B)
3. Identify files to create/modify
4. Plan test strategy
```

### Step 3: Create/Update Issue
```
1. Use appropriate template from ISSUE_TEMPLATE/
2. Link to related issues
3. Add appropriate labels (phase-1, backend, etc.)
4. Include technical details
```

### Step 4: Create Branch
```
1. Follow naming convention from GITHUB_WORKFLOW.md
2. Branch from 'develop' (not main)
3. Use format: feature/description or bugfix/issue-number-description
```

### Step 5: Implement
```
1. Follow code style from CONTRIBUTING.md
2. Write tests (pytest) alongside code
3. Add type hints to all functions
4. Include docstrings (Google style)
5. Update documentation if needed
```

### Step 6: Test & Validate
```
1. Run: pytest tests/
2. Run: flake8 app/
3. Run: black app/
4. Ensure coverage > 80%
5. Manual testing with sample data
```

### Step 7: Create Pull Request
```
1. Use pull_request_template.md
2. Fill out ALL sections completely
3. Link related issues ("Closes #123")
4. Add screenshots/logs if relevant
5. Request review if team project
```

---

## 🎯 PROJECT-SPECIFIC RULES

### Data Privacy & Security
- **NEVER commit sensitive data** (invoice PDFs, vendor names, amounts)
- **NEVER commit .env files** with API keys
- **ALWAYS anonymize** test data
- **ALWAYS use environment variables** for secrets

### Vietnamese Language Support
- Test with Vietnamese text (UTF-8 encoding)
- Gemini 2.0 Flash is optimized for Vietnamese OCR
- UI should support Vietnamese characters
- Log messages can be English (for debugging)

### Safety First
- **NEVER implement auto-save** in ACSoft automation
- **ALWAYS require human confirmation** before final save
- **ALWAYS take screenshots** during automation (audit trail)
- **ALWAYS validate** extracted data before automation

### Testing Requirements
- **Unit tests required** for all business logic
- **Integration tests required** for API endpoints
- **Manual testing required** for ACSoft automation
- **Test with diverse invoice formats** (see tests/fixtures/)

---

### 📚 QUICK REFERENCE

### File Locations
```
/TECHNICAL_SPECS.md                                        → System architecture & detailed specs
/spec/Requirements.md                                      → Functional & non-functional requirements
/spec/Design.md                                            → System design & architecture decisions
/spec/Tasks.md                                             → Implementation task tracking (checkbox format)
/README.md                                                 → User documentation
/CONTRIBUTING.md                                           → Development guidelines
/.github/GITHUB_WORKFLOW.md                                → Git/GitHub workflow
/.github/instructions/AI_AGENT_INSTRUCTIONS.instructions.md → Detailed dev guide (phase tasks)
/.github/instructions/AI_AGENT_ONBOARDING.instructions.md  → This file (onboarding checklist)
/.github/ISSUE_TEMPLATE/                                   → Issue templates
/.github/pull_request_template.md                          → PR template
/CHANGELOG.md                                              → Version history
/docs/                                                     → Organized documentation (coming soon)
```

### Code Standards
```python
# Type hints required
def process_invoice(pdf_path: str) -> Invoice:
    pass

# Docstrings required (Google style)
"""Extract data from invoice PDF.

Args:
    pdf_path: Absolute path to PDF file
    
Returns:
    Invoice object with extracted data
    
Raises:
    PDFProcessingError: If processing fails
"""

# Error handling required
try:
    result = gemini_client.extract(pdf_path)
except GeminiAPIError as e:
    logger.error(f"Extraction failed: {e}")
    raise
```

### Commit Message Format
```
feat(component): Add new feature
fix(component): Fix bug
docs: Update documentation
test(component): Add tests
refactor(component): Refactor code
```

### Branch Naming
```
feature/gemini-extraction
bugfix/42-validation-error
docs/update-readme
test/add-integration-tests
```

---

## ⚠️ COMMON MISTAKES TO AVOID

### ❌ DON'T DO THIS:
1. Commit directly to `main` branch
2. Skip reading TECHNICAL_SPECS.md
3. Write code without tests
4. Use generic commit messages ("fix bug", "update code")
5. Hardcode values (use config.yaml instead)
6. Ignore type hints
7. Skip docstrings
8. Commit sensitive data
9. Implement auto-save in ACSoft automation
10. Mix multiple features in one PR

### ✅ DO THIS:
1. Always branch from `develop`
2. Read relevant sections of TECHNICAL_SPECS.md first
3. Write tests alongside code (TDD approach)
4. Use conventional commit format
5. Use configuration files for all settings
6. Add type hints to all functions
7. Write clear docstrings
8. Use .gitignore for sensitive files
9. Always require human confirmation
10. Keep PRs focused on single feature/fix

---

## 🎓 LEARNING RESOURCES

**Before starting work, review:**
1. **TECHNICAL_SPECS.md** - Sections 1-4 (Architecture, Components, Config, Error Handling)
2. **CONTRIBUTING.md** - Code Style, Testing, Git Guidelines sections
3. **GITHUB_WORKFLOW.md** - Entire document (it's your GitHub bible)
4. **/.github/instructions/AI_AGENT_INSTRUCTIONS.instructions.md** - Phase-specific tasks and detailed patterns

**Phase-specific guidance:**
- **Phase 1 (MVP):** Read `/.github/instructions/AI_AGENT_INSTRUCTIONS.instructions.md` Phase 1 section
- **Phase 2 (Enhancement):** Read Phase 2 section + review Phase 1 code
- **Phase 3 (Polish):** Read Phase 3 section + full codebase review

---

## 🚀 READY TO START?

**Before writing any code, answer these questions:**

1. ✅ Have I read the relevant section of TECHNICAL_SPECS.md?
2. ✅ Have I checked GITHUB_WORKFLOW.md for git conventions?
3. ✅ Have I reviewed CONTRIBUTING.md for code standards?
4. ✅ Do I know which template to use for issues/PRs?
5. ✅ Have I identified which files need to be created/modified?
6. ✅ Have I planned my test strategy?
7. ✅ Do I understand the safety requirements (no auto-save)?
8. ✅ Have I checked .gitignore to avoid committing sensitive data?

**If you answered YES to all questions above, you're ready to code! 🎉**

**If you answered NO to any question, STOP and read the relevant documentation first.**

---

## 📞 NEED HELP?

**For questions about:**
- **Architecture:** Check TECHNICAL_SPECS.md Section 1-2
- **Code style:** Check CONTRIBUTING.md Code Style section
- **Git workflow:** Check GITHUB_WORKFLOW.md
- **Testing:** Check CONTRIBUTING.md Testing section
- **Specific components:** Check TECHNICAL_SPECS.md Section 2 (detailed specs)
- **Configuration:** Check TECHNICAL_SPECS.md Section 3
- **Error handling:** Check TECHNICAL_SPECS.md Section 4

**Still stuck?**
- Search existing issues for similar problems
- Check logs/maas.log for error details
- Create issue with "question" label using templates

---

## 🎯 PROJECT CONTEXT REMINDER

**User:** Mom (non-technical Vietnamese accountant)  
**Goal:** Save 3-5 hours per day of manual invoice data entry  
**Critical Success Factors:**
- Safety (human review required)
- Reliability (comprehensive error handling)
- Privacy (all data stays local)
- Ease of use (non-technical user)

**Your code directly impacts:**
- Mom's daily workload and stress level
- Time available for family responsibilities  
- Business capacity and growth potential
- Work-life balance and wellbeing

**Code with care, test thoroughly, document clearly. Every line matters! ❤️**

---

**Document Version:** 1.0  
**Last Updated:** December 5, 2025  
**Status:** Active - Always read before starting work
