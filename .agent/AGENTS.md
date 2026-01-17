# Project Rules for AI Agents

Welcome to the Maccabipedia MediaWiki Bot project. To maintain a clean and efficient workspace, all AI agents must follow these rules:

## 1. File Placement (CRITICAL)
- **Do NOT** create temporary scripts, debug tools, or data reports in the root directory.
- Use the **`.agents-temp/`** directory for all such files.
- Core project files (like `requirements.txt`, `.gitignore`, or main entry points) should remain in the root or their designated project folders.

## 2. Documentation
- Every new script created must include a docstring at the top explaining:
  - What the script does.
  - How to run it.
  - Any specific dependencies or inputs required.

## 3. Workflows
- Check the `.agent/workflows/` directory for any pre-defined procedures before starting complex tasks.

## 4. Automation & Data Integrity Best Practices
- **Zero Tolerance for Silent Failures**: Treat every discrepancy as an exception. Verify counts against source of truth (e.g., wiki category size vs. processed list) before assuming completeness.
- **Interactive Verification**: For fuzzy matching or data correction, prefer interactive scripts that cache user decisions (Human-in-the-Loop) over automated guessing.

## 5. Project Specific Coding Standards
- **URL Formatting**: Mccaabipedia URLs must be `https://www.maccabipedia.co.il/Page_Title_With_Underscores`. Do not use `index.php?title=...`.
