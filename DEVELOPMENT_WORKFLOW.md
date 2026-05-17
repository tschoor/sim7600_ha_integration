# AI Development & Workflow Guidelines

## 1. Git Workflow: Git Flow
All development MUST strictly adhere to the [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/) branching model:
- `main`: Production-ready code.
- `develop`: Integration branch for features.
- `feature/*`: Feature development.
- `release/*`: Release preparation.
- `hotfix/*`: Emergency patches.

## 2. CI/CD Pipeline (GitHub Actions)
The following automated pipeline stages are executed via GitHub Actions on every push and PR:
1. **Build & Install:** Validate dependency installation.
2. **Static Code Analysis:** Linting and code quality (using `ruff`).
3. **Type Checking:** Strict type verification (using `mypy`).
4. **Vulnerability Check:** Dependency scanning (using `safety`).
5. **License Check:** Compliance audit of third-party dependencies (using `pip-licenses`).
6. **Testing:** Full execution of the `pytest` suite.
7. **Snapshot Release:** Automated creation of pre-releases for `develop` and `feature/*` branches.

These steps are handled by GitHub Actions and no longer require manual agent intervention.

## 3. Development Standards
- **Validation:** No code change is complete without passing tests.
- **Automation:** Pipeline steps are automated via GitHub Actions to ensure consistency and reliability.
- **Reporting:** All successful validations should trigger an automated PR creation.
- **Git Synchronization:** Always perform a `git push` (and `git pull --rebase` if necessary) after completing work on a branch to keep the remote repository and local environment synchronized according to Git Flow.

## 4. Automation & Verification
- **GitHub Actions:** Primary orchestrator for CI/CD.
- **HACS:** Integration versions are automatically updated via snapshot releases on non-production branches.
- **Pipeline Monitoring:** Every code push must be followed by monitoring the GitHub Actions run. Use `gh run list` or the GitHub UI to verify success.
- **Autonomous Recovery:** In case of CI failure, the agent must autonomously analyze logs, identify the root cause, and propose a fix using Plan Mode. A task is only complete when the CI pipeline is green.
