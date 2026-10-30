---
name: logging-advisor
description: Recommend where, what, and at which level to log in application code. Use when adding, reviewing, or improving application logging.
---

# Logging Advisor

## Goal
Recommend useful, low-noise logging that supports troubleshooting and operational visibility while respecting the project's existing logging framework and conventions.

## Workflow
1. Detect the language, framework, logging library, and existing conventions from the repository. Do not assume SLF4J, Log4j, Logback, or a Node logger unless evidence supports it.
2. Trace the selected method's control flow and identify meaningful boundaries: external calls, persistence, business state transitions, retries, validation failures, and exception handling.
3. Recommend logging only where it adds diagnostic or business-operational value. Avoid logging every method entry/exit by default.
4. Choose levels using this guidance, adjusted to local conventions:
   - ERROR: operation failed and requires attention or could not be recovered at this layer.
   - WARN: unexpected but handled/recoverable condition, degraded behavior, retry, or suspicious input.
   - INFO: significant business operation or lifecycle event that operators need to follow.
   - DEBUG: detailed diagnostic context useful during troubleshooting, normally not enabled in production.
5. Include safe correlation identifiers (request ID, correlation ID, business ID) only when appropriate and permitted.
6. Avoid duplicate exception logging. Log an exception once at the layer that can add meaningful context and handle/report it.
7. Avoid noisy logs in tight loops, excessive payload dumps, and repeated messages from multiple layers.
8. Never log passwords, tokens, cookies, authorization headers, private keys, full payment details, or unnecessary personal data.

## Output
For each recommendation provide:
- File and method / approximate line
- Level
- Example statement using the project's actual logging API
- Reason and operational value
- Any data-safety consideration

Separate high-value recommendations from optional DEBUG additions. Do not edit source code unless the user explicitly requests implementation. When asked to implement, make the smallest changes and preserve the existing logging API.
