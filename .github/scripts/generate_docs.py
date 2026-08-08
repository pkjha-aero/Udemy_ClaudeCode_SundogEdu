#!/usr/bin/env python3
"""Generate documentation using Claude API."""

import os
import sys
from pathlib import Path

from anthropic import Anthropic

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


def read_project_files() -> str:
    """Read relevant project files for documentation context."""
    content = []
    base_path = Path("radiocalico")

    files_to_read = [
        "CLAUDE.md",
        "README.md",
        "app/routes.py",
        "app/models.py",
        "requirements.txt",
    ]

    for file_path in files_to_read:
        full_path = base_path / file_path
        if full_path.exists():
            try:
                with open(full_path, "r") as f:
                    file_content = f.read()
                    content.append(f"=== {file_path} ===\n{file_content}\n")
            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}")

    return "\n".join(content)


def generate_documentation() -> str:
    """Use Claude to generate documentation."""
    client = Anthropic()

    project_content = read_project_files()

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        system="""You are a technical documentation expert. Generate comprehensive, clear documentation.
Focus on:
1. Clear explanations of functionality
2. Setup and installation instructions
3. API endpoint documentation
4. Database schema overview
5. Development guidelines

Format the output as markdown.""",
        messages=[
            {
                "role": "user",
                "content": f"""Please generate comprehensive documentation for this project based on the files provided:

{project_content}

Generate:
1. API Documentation
2. Database Schema
3. Development Setup Guide
4. Project Architecture Overview""",
            }
        ],
    )

    return message.content[0].text


def save_documentation(docs: str):
    """Save generated documentation to file."""
    docs_dir = Path("radiocalico/docs")
    docs_dir.mkdir(exist_ok=True)

    output_file = docs_dir / "API.md"
    with open(output_file, "w") as f:
        f.write(docs)

    print(f"Documentation saved to {output_file}")


def main():
    """Main function."""
    if not ANTHROPIC_API_KEY:
        print("Error: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    print("Generating documentation with Claude...")
    docs = generate_documentation()

    print("\n=== Generated Documentation ===")
    print(docs[:500] + "..." if len(docs) > 500 else docs)
    print("=" * 30)

    print("\nSaving documentation...")
    save_documentation(docs)


if __name__ == "__main__":
    main()
