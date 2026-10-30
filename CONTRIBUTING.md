# Contributing

1. Open an issue describing the feature or correction.
2. Keep workflows generic unless a feature is explicitly technology-specific. Put SAP CAP, SAP Commerce OCC, Java, or Node.js guidance in clearly labeled sections.
3. Do not add credentials, production logs, customer data, or internal URLs to examples.
4. Update `manifest/features.json` whenever you add, remove, or rename an installable file.
5. Add tests for helper scripts and validate copied files with `python scripts/install.py --dry-run`.
6. Run `python -m unittest discover -s tests -v` before submitting a change.
7. Update the README or feature docs when usage changes.
