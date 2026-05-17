# SIM7600 Home Assistant Integration

This file contains the architectural standards, conventions, and workflows for this repository.

## Architecture
- **Framework:** Home Assistant integration (HACS-compatible).
- **Core Logic:** Located in `custom_components/sim7600/`.
- **Async:** All I/O operations must be performed asynchronously to prevent blocking the Home Assistant event loop.

## Standards
- **Language:** Python 3.12+.
- **Typing:** Strict type hinting is required for all modules.
- **Linting/Formatting:** `ruff` is the primary tool for linting and formatting.
- **Testing:** `pytest` is used for all testing. Ensure new features or bug fixes have corresponding tests in the `tests/` directory.

## Development Workflow
1. **Research:** Explore codebase using `grep_search` and `glob`.
2. **Strategy:** Plan changes before execution.
3. **Execution:** 
   - Apply changes surgically.
   - Run existing tests and add new ones to verify.
   - Run `ruff check .` and `pytest` to validate.
4. **Validation:** Always verify correctness via tests and linting before considering a task complete.
5. **Synchronization:** Perform a Git synchronization (push/pull) according to Git Flow after work is completed.
