# Cybersecurity Labs

A beginner-friendly collection of defensive cybersecurity exercises for an
authorized home lab. The labs emphasize observation, documentation, and safe
analysis rather than exploitation.

## Safety and authorization

Only use these exercises on systems you own or have explicit permission to
test. Keep vulnerable machines and scanners on an isolated host-only or
internal network. Never scan a school, workplace, public, or internet-facing
system without written authorization.

Before each lab:

1. Identify the systems in scope.
2. Confirm that you own them or have permission.
3. Record the allowed time window and activity.
4. Take a virtual-machine snapshot when appropriate.
5. Remove names, usernames, public IP addresses, email addresses, tokens, and
   other sensitive data before publishing results.

See [Lab Rules](docs/LAB_RULES.md) and [Sanitization Guide](docs/SANITIZATION.md).
When this folder is ready to join the main portfolio, follow
[Add This Section to CyberLaunch](docs/ADD_TO_REPOSITORY.md).

## Lab environment

Recommended:

- A computer with at least 8 GB RAM and 20 GB free disk space
- VirtualBox, VMware Fusion, UTM, or another local hypervisor
- One Windows evaluation VM and one Linux VM
- Docker Desktop or Docker Engine for the container lab
- Python 3.10 or newer for the included helper tools
- Nmap for the discovery and vulnerability-observation labs

Use an isolated network such as `192.168.56.0/24`. The documentation uses
reserved example addresses only; replace them with addresses from your own
private lab.

## Labs

| Lab | Topic | Outcome |
| --- | --- | --- |
| 01 | [Private-lab network discovery](01-network-discovery/README.md) | Build an authorized device inventory |
| 02 | [Windows log analysis](02-windows-log-analysis/README.md) | Review sign-in and process events |
| 03 | [Linux log analysis](03-linux-log-analysis/README.md) | Identify authentication patterns |
| 04 | [Basic vulnerability scanning](04-vulnerability-scanning/README.md) | Document exposed services safely |
| 05 | [Docker lab setup](05-docker-lab/README.md) | Create and verify an isolated web service |
| 06 | [File integrity monitoring](06-file-integrity-monitoring/README.md) | Detect authorized file changes |
| 07 | [Phishing-email analysis](07-phishing-email-analysis/README.md) | Examine a harmless synthetic message |
| 08 | [Incident-response documentation](08-incident-response/README.md) | Produce a defensible incident timeline |

## Repository layout

```text
cybersecurity-labs/
├── README.md
├── docs/             Shared safety and sanitization guidance
├── templates/        Reusable lab and incident reports
├── samples/          Synthetic, publication-safe example data
├── tools/            Small defensive helper programs
└── 01-...08-.../     Individual lab instructions
```

## Using a lab

1. Read the entire lab and its safety boundary.
2. Copy `templates/lab-report.md` into the lab folder as `REPORT.md`.
3. Record your scope before running any command.
4. Perform the exercise only inside the authorized environment.
5. Compare your observations with the sanitized examples.
6. Remove sensitive information using `docs/SANITIZATION.md`.
7. Commit the completed report without raw private data.

## Included helper tools

No third-party Python packages are required.

```bash
python3 tools/file_integrity.py --help
python3 tools/auth_log_summary.py --help
python3 tools/eml_summary.py --help
```

The tools default to local files and do not transmit data.

## Portfolio guidance

Publish the method, sanitized findings, lessons learned, and remediation
ideas. Do not publish credentials, live targets, private student data,
unredacted logs, proprietary files, or screenshots containing personal
information.

## Status

Version 1.0 provides eight guided defensive labs, reusable reporting
templates, safe sample artifacts, and three local analysis helpers.
