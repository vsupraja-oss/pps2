#!/usr/bin/env python3
"""Code explainer AI tool using Google Gemini API."""

import argparse
import os
import sys
import textwrap
from typing import Optional

import requests

API_BASE = "https://generativelanguage.googleapis.com/v1beta2"
DEFAULT_MODEL = "models/gemini-pro"
DEFAULT_LANG = "python"


class GeminiClient:
    def __init__(self, api_key: str, model: str = DEFAULT_MODEL):
        if not api_key:
            raise ValueError(
                "Google API key is required. Set the GOOGLE_API_KEY environment variable."
            )
        self.api_key = api_key
        self.model = model

    def request(self, prompt: str) -> str:
        url = f"{API_BASE}/{self.model}:generateText"
        payload = {"prompt": {"text": prompt}}
        response = requests.post(url, params={"key": self.api_key}, json=payload, timeout=60)

        if response.status_code != 200:
            raise RuntimeError(
                f"Gemini API error {response.status_code}: {response.text}"
            )

        data = response.json()
        if isinstance(data, dict):
            if "candidates" in data and data["candidates"]:
                return "".join(
                    candidate.get("content", "") for candidate in data["candidates"]
                )
            if "output" in data:
                output = data["output"]
                if isinstance(output, dict) and "text" in output:
                    return output["text"]

        raise RuntimeError(f"Unexpected Gemini response format: {data}")

    def explain_code(self, code: str, lang: str) -> str:
        prompt = textwrap.dedent(
            f"""
            Explain this {lang} code line by line and identify any syntax issues.
            Provide a clear numbered explanation with references to each line.

            {code}
            """
        )
        return self.request(prompt)

    def check_syntax(self, code: str, lang: str) -> str:
        prompt = textwrap.dedent(
            f"""
            Inspect this {lang} code for syntax errors only.
            If there are no syntax errors, reply exactly: No syntax errors found.
            If there are errors, list each one with the offending line.

            {code}
            """
        )
        return self.request(prompt)

    def generate_code(self, requirement: str, lang: str) -> str:
        prompt = textwrap.dedent(
            f"""
            Generate {lang} code for the following requirement.
            Return only the code snippet and no extra explanation.

            Requirement:
            {requirement}
            """
        )
        return self.request(prompt)


def resolve_code_input(code: Optional[str], file_path: Optional[str]) -> str:
    if code and file_path:
        raise ValueError("Specify either --code or --file, not both.")
    if file_path:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        with open(file_path, "r", encoding="utf-8") as handle:
            return handle.read()
    if code:
        return code
    raise ValueError("Provide code with --code or a file path with --file.")


def local_python_syntax_check(code: str) -> str:
    try:
        compile(code, "<input>", "exec")
        return "Local Python syntax check: no errors detected."
    except SyntaxError as exc:
        return f"Local Python syntax error: {exc.msg} at line {exc.lineno}: {exc.text.strip() if exc.text else ''}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Code explainer AI tool using Google Gemini API"
    )

    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Gemini model name (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--lang",
        default=DEFAULT_LANG,
        help="Programming language for explanation, generation, and syntax checking.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    explain = subparsers.add_parser("explain", help="Explain code line by line.")
    explain.add_argument("--code", help="Inline code to explain.")
    explain.add_argument("--file", help="Path to a code file to explain.")

    check = subparsers.add_parser("check", help="Detect syntax errors in code.")
    check.add_argument("--code", help="Inline code to check.")
    check.add_argument("--file", help="Path to a code file to check.")

    generate = subparsers.add_parser("generate", help="Generate code from a requirement.")
    generate.add_argument("--requirement", required=True, help="Coding requirement to generate code for.")

    all_cmd = subparsers.add_parser(
        "all",
        help="Run explanation, syntax check, and optional code generation in one command.",
    )
    all_cmd.add_argument("--code", help="Inline code to process.")
    all_cmd.add_argument("--file", help="Path to a code file to process.")
    all_cmd.add_argument(
        "--requirement",
        help="Optional requirement for code generation.",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    api_key = os.getenv("GOOGLE_API_KEY")

    try:
        client = GeminiClient(api_key=api_key, model=args.model)

        if args.command == "explain":
            code = resolve_code_input(args.code, args.file)
            print(client.explain_code(code, args.lang).strip())
            return 0

        if args.command == "check":
            code = resolve_code_input(args.code, args.file)
            print(client.check_syntax(code, args.lang).strip())
            if args.lang.lower() == "python":
                print(local_python_syntax_check(code))
            return 0

        if args.command == "generate":
            print(client.generate_code(args.requirement, args.lang).strip())
            return 0

        if args.command == "all":
            code = resolve_code_input(args.code, args.file)
            print("=== Explanation ===")
            print(client.explain_code(code, args.lang).strip())
            print("\n=== Syntax Check ===")
            print(client.check_syntax(code, args.lang).strip())
            if args.lang.lower() == "python":
                print(local_python_syntax_check(code))
            if args.requirement:
                print("\n=== Generated Code ===")
                print(client.generate_code(args.requirement, args.lang).strip())
            return 0

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
