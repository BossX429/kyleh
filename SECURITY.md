# Copilot Security and Workflow Restrictions

This repository enforces the following rules for GitHub Copilot and automated agents:

- **Task Assignment:** Only users with write access can assign tasks to Copilot. Comments from users without write access are ignored by the agent.
- **Access Token Permissions:** Copilot’s access tokens only allow pushes to branches prefixed with `copilot/`. Copilot cannot push to `main` or `master`.
- **Credential Scope:** Copilot can only perform simple push operations; it cannot run arbitrary Git commands like `git push` directly.
- **Workflow Runs:** GitHub Actions workflows triggered by Copilot are paused until a user with write access reviews and approves them via the "Approve and run workflows" button.
- **Pull Request Approvals:** The user who requested Copilot to create a pull request cannot approve it, maintaining branch protection and required approval rules.

For more details, see GitHub documentation on [Copilot security controls](https://docs.github.com/en/copilot).
