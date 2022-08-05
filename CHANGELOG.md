# Release Timeline

Interlock-Bouncer uses [Semantic Versioning](https://semver.org/).

Given a version number MAJOR.MINOR.PATCH, we increment:

- MAJOR when we make incompatible API changes,
- MINOR when we add functionality in a backwards-compatible manner, and
- PATCH when we make backwards-compatible bug fixes.

## Upcoming

- Recommended allowlist
- Options to deal with shortened URLs
- Weekly reports to admin

## 1 series

#### DONE 1.0.0

This version is the minimum viable Discord bot, with the following features:

- Client-side allowlist
- Admins can add to allowlist
- Logging for URLs scanned and percent malicious
- Backend leverages blockhashing to scan novel URLs
