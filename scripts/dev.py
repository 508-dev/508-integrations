#!/usr/bin/env python3

import subprocess
import sys


def run_command(command: str, description: str) -> bool:
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {description} completed successfully")
        if result.stdout.strip():
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/dev.py <command>")
        print("Commands:")
        print("  install    - Install dependencies")
        print("  dev        - Run development server")
        print("  lint       - Run linting")
        print("  format     - Format code")
        print("  typecheck  - Run type checking")
        print("  test       - Run tests")
        print("  test-cov   - Run tests with coverage")
        print("  check-all  - Run all checks (lint, format, typecheck, test)")
        print("  hooks      - Install pre-commit hooks")
        print("  hooks-run  - Run pre-commit hooks on all files")
        sys.exit(1)

    command = sys.argv[1]

    if command == "install":
        run_command("uv pip install -e .[dev]", "Installing dependencies")

    elif command == "dev":
        run_command(
            "uvicorn src.main:app --reload --host 0.0.0.0 --port 5080",
            "Starting development server",
        )

    elif command == "lint":
        success = run_command("ruff check src tests", "Running linter")
        if not success:
            sys.exit(1)

    elif command == "format":
        run_command("ruff format src tests", "Formatting code")

    elif command == "typecheck":
        success = run_command("mypy src", "Running type checker")
        if not success:
            sys.exit(1)

    elif command == "test":
        success = run_command("pytest", "Running tests")
        if not success:
            sys.exit(1)

    elif command == "test-cov":
        success = run_command(
            "pytest --cov=src --cov-report=html --cov-report=term",
            "Running tests with coverage",
        )
        if not success:
            sys.exit(1)

    elif command == "check-all":
        print("🔍 Running all checks...")
        checks = [
            ("ruff check src tests", "Linting"),
            ("ruff format --check src tests", "Format checking"),
            ("mypy src", "Type checking"),
            ("pytest", "Testing"),
        ]

        failed = []
        for cmd, desc in checks:
            if not run_command(cmd, desc):
                failed.append(desc)

        if failed:
            print(f"\n❌ Failed checks: {', '.join(failed)}")
            sys.exit(1)
        else:
            print("\n✅ All checks passed!")

    elif command == "hooks":
        run_command("pre-commit install", "Installing pre-commit hooks")

    elif command == "hooks-run":
        run_command(
            "pre-commit run --all-files", "Running pre-commit hooks on all files"
        )

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
