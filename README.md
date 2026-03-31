# Code Explainer AI Tool

A simple Python CLI tool that explains code line by line, generates code from requirements, and identifies syntax errors using the Google Gemini API.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set your Gemini API key:

- macOS / Linux:
  ```bash
  export GOOGLE_API_KEY="YOUR_API_KEY"
  ```
- Windows PowerShell:
  ```powershell
  $env:GOOGLE_API_KEY = "YOUR_API_KEY"
  ```

## Usage

### Explain code from a file

```bash
python app.py explain --file sample/example.py --lang python
```

### Explain inline code

```bash
python app.py explain --code "print('Hello, world!')" --lang python
```

### Check syntax errors

```bash
python app.py check --file sample/example.py --lang python
```

### Generate code from a requirement

```bash
python app.py generate --requirement "Create a Python function that validates an email address." --lang python
```

### Run all actions together

```bash
python app.py all --file sample/example.py --requirement "Create a Python CLI tool that reverses strings." --lang python
```

## Notes

- The tool uses the `GOOGLE_API_KEY` environment variable to authenticate with the Gemini API.
- `app.py` supports the `--lang` option to describe which programming language should be used in prompts.
