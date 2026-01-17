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
