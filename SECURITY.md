# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability within **Molavi Web Intelligence Engine (MWIE)**, please report it responsibly:

- **Email:** `contact@molavi.pro`
- Please provide detailed reproduction steps and affected components.
- Do not disclose vulnerabilities publicly until a patch has been published.

## Responsible Crawling & SSRF Protection

MWIE includes native Server-Side Request Forgery (SSRF) protections:
- Private, loopback, and reserved IP ranges (RFC 1918, RFC 5737, RFC 4291) are blocked by default.
- Robots.txt rules and domain rate-limiting are enforced by default.
- Users are responsible for configuring target allowlists when deploying MWIE within internal corporate networks.
