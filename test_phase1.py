#!/usr/bin/env python3
"""
Quick test flight: Phase 1 Outline & Unit Extraction
Tests the NEW Phase 1 prompt on actual chapter content
"""

import sys
import json
import os
from pathlib import Path
from docx import Document
from openai import OpenAI

# Set up path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from services.prompts import get_phase_1_prompts

# Simple logging
def log(msg):
    print(f"[TEST] {msg}")


def extract_docx_text(file_path: str) -> str:
    """Extract text from .docx file."""
    doc = Document(file_path)
    paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
    text = '\n'.join(paragraphs)
    log(f"Extracted {len(paragraphs)} paragraphs, {len(text)} characters")
    return text


def test_phase_1(file_path: str):
    """Test Phase 1 extraction on a real chapter."""

    log(f"Testing Phase 1 on: {file_path}")

    # Extract text
    log("Extracting text from .docx...")
    text = extract_docx_text(file_path)

    # For very large files, truncate for testing
    MAX_LENGTH = 30000  # ~30K characters for faster testing
    if len(text) > MAX_LENGTH:
        log(f"Text is {len(text)} chars, truncating to {MAX_LENGTH} for test")
        text = text[:MAX_LENGTH]

    # Get Phase 1 prompts
    log("Generating Phase 1 prompts...")
    prompts = get_phase_1_prompts(text)

    log(f"System prompt length: {len(prompts['system_prompt'])} chars")
    log(f"User prompt length: {len(prompts['user_prompt'])} chars")

    # Call LLM
    log("Calling OpenAI GPT-4o...")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")

    client = OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompts['system_prompt']},
                {"role": "user", "content": prompts['user_prompt']}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        result_text = response.choices[0].message.content
        result = json.loads(result_text)

        log("✅ Phase 1 extraction successful!")

        content_units = result.get('content_units', [])
        log(f"Extracted {len(content_units)} content units")

        # Show summary
        print("\n" + "="*80)
        print("PHASE 1 TEST RESULTS")
        print("="*80)
        print(f"\nTotal content units extracted: {len(content_units)}\n")

        # Show hierarchy
        print("HIERARCHICAL STRUCTURE:")
        print("-" * 80)
        for unit in content_units:
            indent = "  " * unit.get('depth_level', 0)
            unit_type = unit.get('unit_type', 'unknown')
            unit_id = unit.get('unit_id', 'unknown')
            section = unit.get('section') or unit.get('chapter', '')
            snippet = unit.get('text_snippet', '')[:80] + "..."
            keywords = unit.get('keywords', [])

            print(f"{indent}[{unit_type}] {unit_id} - {section}")
            print(f"{indent}  📝 {snippet}")
            print(f"{indent}  🔑 Keywords: {', '.join(keywords[:5])}")
            print()

        # Save full output
        output_file = Path(__file__).parent / "test_phase1_output.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)

        print(f"\n✅ Full output saved to: {output_file}")
        print("="*80)

        return result

    except Exception as e:
        log(f"❌ Phase 1 extraction failed: {e}")
        raise


if __name__ == "__main__":
    file_path = "/Users/elle_jansick/Desktop/01 YOUR FOUR WORLDS - from DMC v25.docx"

    try:
        result = test_phase_1(file_path)
        print("\n🎉 Test flight successful!")
    except Exception as e:
        print(f"\n❌ Test flight failed: {e}")
        sys.exit(1)
