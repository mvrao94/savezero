# Security Policy

## Supported Versions

SaveZero is currently in early development. Security updates will be provided for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Security Considerations

### Credentials and Authentication

- **SaveZero never asks for your Instagram password**
- Authentication is handled through your Chrome browser session
- Session data is stored locally in `~/.savezero_session` (or custom `CHROME_USER_DATA_DIR`)
- No credentials are transmitted to third parties

### Local Execution

- SaveZero runs entirely on your local machine
- All automation happens through your local Chrome instance
- No data is sent to external servers (except Instagram's official API endpoints)

### Instagram Rate Limiting

- SaveZero includes built-in rate limiting to reduce risk of account restrictions
- However, **we cannot guarantee that Instagram won't restrict your account**
- Use at your own discretion and risk

### Data Privacy

- SaveZero does not collect, store, or transmit any personal data
- Logs are stored locally in `instagram_cleaner.log`
- No analytics or telemetry

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please report it responsibly.

### How to Report

**Do NOT open a public GitHub issue for security vulnerabilities.**

Instead, please email security concerns to:

**venki_bobby1994@yahoo.com**

Include in your report:

1. **Description** of the vulnerability
2. **Steps to reproduce** the issue
3. **Potential impact** of the vulnerability
4. **Suggested fix** (if you have one)
5. **Your contact information** for follow-up

### What to Expect

- **Acknowledgment**: We'll acknowledge receipt of your report within 48 hours
- **Investigation**: We'll investigate and assess the severity within 7 days
- **Updates**: We'll keep you informed of our progress
- **Fix Timeline**: Critical issues will be addressed as quickly as possible
- **Credit**: With your permission, we'll credit you in the security advisory

### Scope

Security issues in scope:

- Authentication bypass or credential exposure
- Remote code execution vulnerabilities
- Privilege escalation
- Data leakage or privacy violations
- Dependency vulnerabilities with exploits

Out of scope:

- Issues requiring physical access to the user's machine
- Social engineering attacks
- Instagram's own platform vulnerabilities
- DoS attacks on the user's local environment

## Security Best Practices for Users

1. **Review the code**: SaveZero is open source — inspect it before running
2. **Use a dedicated Chrome profile**: Don't use your main profile for automation
3. **Start small**: Test on a small collection first
4. **Monitor for action blocks**: Stop immediately if Instagram shows warnings
5. **Keep dependencies updated**: Run `pip install --upgrade -r requirements.txt` regularly
6. **Use on trusted networks**: Avoid running on public Wi-Fi
7. **Backup important saved posts**: Screenshot or note any posts you want to keep

## Known Limitations

- SaveZero cannot guarantee that Instagram won't restrict your account
- Rate limiting is best-effort, not foolproof
- Action block detection is based on known indicators and may not catch all cases
- Instagram's platform changes may break functionality

## Dependency Security

We regularly review dependencies for known vulnerabilities. To check for security issues in dependencies:

```bash
pip install safety
safety check -r requirements.txt
```

## Updates and Patches

- Security updates will be released as soon as possible
- Critical vulnerabilities will be patched within 48 hours when possible
- Users will be notified via GitHub releases and security advisories

## Responsible Disclosure

We follow coordinated vulnerability disclosure practices and request that security researchers:

- Allow reasonable time for us to fix issues before public disclosure
- Make a good faith effort to avoid privacy violations and data destruction
- Do not exploit vulnerabilities beyond what's necessary to demonstrate the issue

Thank you for helping keep SaveZero and its users safe!
