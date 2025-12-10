# AI Agent Instructions for MAAS Project

This document provides context, guidelines, and rules for AI agents working on the Mom's Accounting Automation System (MAAS).

## 🧠 Project Context

- **Goal**: Automate invoice data entry for a non-technical user ("Mom") on Windows.
- **Core Value**: Simplicity, Reliability, Privacy (Local-first).
- **Key Flow**: PDF Invoice -> Gemini OCR -> Validation -> Human Review -> Desktop Automation (ACSoft).

## 🛠️ Technology Stack

- **Language**: Python 3.9+
- **Web Framework**: FastAPI
- **GUI Automation**: PyWinAuto (Windows specific)
- **AI/OCR**: Google Gemini 2.0 Flash
- **Database**: SQLite (via SQLAlchemy or raw SQL depending on implementation)
- **Testing**: Pytest

## 📝 Coding Standards

### Style & Formatting

- Follow **PEP 8** guidelines.
- Use **Black** for code formatting (max-line-length: 100).
- Use **Isort** for import sorting.
- **Docstrings**: Required for all public modules, classes, and functions (Google style).

### Type Safety

- **Strict Type Hinting**: All function signatures must have type hints.
- Use `logging` instead of `print` statements.

### Error Handling

- Use custom exceptions where appropriate.
- Fail gracefully—remember the user is non-technical. If an error occurs, provide a readable message.

## 🏗️ Architecture Guidelines

- **Directory Structure**:
  - `app/api`: API Routes/Controllers.
  - `app/services`: Business logic (PDF extraction, validation, automation).
  - `app/models`: Pydantic models and Database schemas.
  - `app/utils`: Helper functions.
- **Separation of Concerns**: Keep automation logic (PyWinAuto) separate from API logic.

## 🧪 Testing Guidelines

- Write **Unit Tests** for all new logic (`tests/`).
- **Mock External Calls**: Never call real Gemini API or ACSoft during tests; use mocks.
- Run `pytest` to verify changes before confirming.

## 🚀 Workflow for Changes

1. **Understand**: Read the file/context first.
2. **Plan**: Propose the change.
3. **Implement**: Write code with type hints and docs.
4. **Verify**: Run `pytest` or check syntax.
