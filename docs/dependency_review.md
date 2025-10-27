# Dependency Review

This document lists the core dependencies of the SATCN pipeline and provides guidelines for reviewing them.

## Core Dependencies

| Library | Current Version | Purpose | Last Reviewed | Notes |
|---|---|---|---|---|
| language-tool-python | 2.9.4 | Grammar correction | 2025-10-27 | Implemented in "safe mode" using a conservative, hardcoded set of rule IDs to prevent unintended semantic changes and to avoid interfering with Markdown syntax. |
| pyspellchecker | 0.8.3 | Spelling correction | 2025-10-27 | |
| ebooklib | 0.20 | EPUB parsing and generation | 2025-10-27 | |
| beautifulsoup4 | 4.14.2 | HTML parsing | 2025-10-27 | |
| markdown | 3.9 | Markdown parsing | 2025-10-27 | |
| pytest | 8.4.2 | Testing | 2025-10-27 | |

## Review Process

These dependencies should be reviewed quarterly to ensure that they are up-to-date and that there are no known security vulnerabilities. The review process should include:

1. Checking the project's documentation for any changes or updates.
2. Checking the project's issue tracker for any known issues.
3. Checking the project's security advisories for any known vulnerabilities.

After the review is complete, the "Last Reviewed" date in this document should be updated.
