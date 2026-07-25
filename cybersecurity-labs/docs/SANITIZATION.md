# Sanitization Guide

Make a copy of evidence before sanitizing it. Preserve the original only in
secure local storage; publish the sanitized copy.

Replace sensitive values consistently:

| Sensitive value | Safe replacement |
| --- | --- |
| Person name | `[USER-01]` |
| Username | `[ACCOUNT-01]` |
| Email | `analyst@example.invalid` |
| Private IP | `192.0.2.10` or a documented lab-only address |
| Public IP | `[PUBLIC-IP-REDACTED]` |
| Hostname | `LAB-WIN-01` |
| Domain | `example.invalid` |
| Token or key | `[SECRET-REMOVED]` |
| File path with a real name | `/home/labuser/...` |

Use the documentation ranges `192.0.2.0/24`, `198.51.100.0/24`, and
`203.0.113.0/24` for published examples. Use `.example`, `.invalid`, or
`.test` domains. Never invent a replacement that could identify a real
person or reachable host.

Before committing:

```bash
git diff --cached
git status
```

Review images manually. Search text files for email addresses, home paths,
public IP addresses, tokens, cookies, and authorization headers.

