# Lab 07: Safe Phishing-Email Analysis

## Objective

Analyze a fully synthetic email, identify warning signs, and write a safe
triage recommendation without opening links or attachments.

## Safety boundary

Use only `../samples/safe-phishing-sample.eml`. Its domain is non-resolving and
its URL is defanged. Do not send the message, activate the URL, submit
credentials, or upload real organizational email to public analysis services.

## Setup

Run the local metadata helper:

```bash
python3 ../tools/eml_summary.py ../samples/safe-phishing-sample.eml
```

The program reads the local message and displays selected headers, attachment
names, authentication-result text, and defanged URL indicators. It makes no
network requests.

## Procedure

1. Verify the sender display name and actual address.
2. Review `Reply-To`, `Message-ID`, and `Authentication-Results`.
3. Identify urgency, unexpected context, and requests for action.
4. List attachment names without opening them. This sample has none.
5. Record defanged indicators exactly as displayed.
6. Decide whether to classify the message as benign, suspicious, or malicious,
   and explain the evidence and uncertainty.

## Expected observations

The sample intentionally includes urgency, a generic organizational pretext,
a failed SPF result, no DKIM result, and a defanged non-resolving URL.
Authentication failure alone is not proof of phishing; evaluate the whole
message.

## Deliverable

Write a triage note with:

- Classification and confidence
- Header and content indicators
- Recommended user action
- Safe escalation and preservation steps
- One limitation of static email analysis

## Cleanup

No cleanup is required. Do not replace the sample with a real message in Git.

