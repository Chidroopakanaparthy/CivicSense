# Contributing to CivicSense

Thank you for your interest in improving CivicSense! As an impartial election assistant, we maintain high standards for code quality and neutrality.

## Code of Conduct
By participating in this project, you agree to maintain strict political neutrality. CivicSense does not endorse or criticize any candidates or parties.

## Development Process

1. **Fork and Branch**: Create a feature branch from `main`.
2. **Type Hinting**: All Python code must use strict type hints.
3. **TypeScript**: Frontend components must be strictly typed and accessible.
4. **Testing**: 
   - New backend features require Pytest coverage.
   - UI changes require Jest component tests.
5. **Accessibility**: All UI components must pass basic WCAG 2.1 checks (use `aria-label` and semantic HTML).

## Pull Request Guidelines
- Provide a clear description of the changes.
- Ensure all CI/CD checks (GitHub Actions) pass.
- Update the `README.md` if adding new features.

## Security
If you find a security vulnerability, please report it via the issue tracker using the "Security" label. Never post API keys or sensitive data in PRs.
