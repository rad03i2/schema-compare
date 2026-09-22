# Security Policy

## Supported version
The latest version on `main` is supported.

## Security model
Schema Compare opens SQLite inputs in read-only mode and does not execute schema SQL. It performs no network requests and collects no telemetry. Database paths and schema definitions can still be sensitive; treat JSON/text reports accordingly.

## Reporting
Please report suspected vulnerabilities privately through GitHub's security reporting features when available. Do not publish sensitive database contents in an issue.
