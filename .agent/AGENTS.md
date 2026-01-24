# Project Rules for AI Agents

Welcome to the Maccabipedia MediaWiki Bot project. This file is the **primary source of truth** for all agent behavior and coding standards.

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
- Check the `.agent/workflows/` directory for any procedures. Most workflow files will point back to this file for general best practices.

## 4. Automation & Data Integrity Best Practices
- **Zero Tolerance for Silent Failures**: Treat every discrepancy as an exception. Verify counts against source of truth (e.g., wiki category size vs. processed list).
- **Let Exceptions Propagate (Fail Fast)**: Do **NOT** silence exceptions with empty `try/except` blocks (catch and do nothing). Let the script crash so errors are visible.
- **Handle Edge Cases**: proactively identify and handle potential edge cases (e.g., missing data, network timeouts, invalid wiki syntax).
- **Interactive Verification**: For fuzzy matching or data correction, prefer interactive scripts that cache user decisions (Human-in-the-Loop).

## 5. Coding Standards & Naming
- **Readable Names**: Naming conventions must prioritize readability and clarity. Avoid overly cryptic abbreviations.
- **Python Style**: Follow PEP 8 (snake_case for functions/variables, PascalCase for classes).
- **URL Formatting**: Maccabipedia URLs must be `https://www.maccabipedia.co.il/Page_Title_With_Underscores`. Do not use `index.php?title=...`.

## 6. Environment & Tools
- **Shell Preference**: Use **`cmd`** for command-line operations instead of PowerShell. Avoid PowerShell-specific syntax (like `$env:VAR` or backtick line continuations) and use standard CMD syntax (`^` for line continuation).
