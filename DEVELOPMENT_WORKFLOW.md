# AI Development & Workflow Guidelines

## 1. Git Workflow: Git Flow
All development MUST strictly adhere to the [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/) branching model:
- `main`: Production-ready code.
- `develop`: Integration branch for features.
- `feature/*`: Feature development.
- `release/*`: Release preparation.
- `hotfix/*`: Emergency patches.

## 2. CI/CD Pipeline (GitHub Actions)
Every PR MUST pass the following automated pipeline stages:
1. **Build:** Validate project compilation/dependency installation.
2. **Static Code Analysis:** Linting and code quality (using `ruff`).
3. **Vulnerability Check:** Dependency scanning (e.g., `safety` or GitHub Dependabot).
4. **License Check:** Ensure compliance of third-party dependencies.
5. **Testing:** Full execution of the `pytest` suite.
6. **Package:** Prepare build artifacts.

## 3. Development Standards
- **Validation:** No code change is complete without passing tests.
- **Automation:** Use specialized agents to manage specific pipeline tasks.
- **Reporting:** All successful validations should trigger an automated PR creation.

## 4. Specialized Agents
The following dedicated agents handle specific workflow domains:
- `workflow_engineer`: Orchestrates the CI/CD pipeline and Git Flow compliance.
- `qa_agent`: Manages test suite execution, coverage reporting, and validation.
- `security_compliance_agent`: Performs vulnerability scans and license audits.
- `release_manager`: Handles versioning, changelog generation, and PR lifecycle management.
