#!/usr/bin/env python3
"""
Quick test of Phase 2 section-by-section extraction
"""
import sys
sys.path.insert(0, '/Users/elle_jansick/doc_digester')

from src.services.llm_client import run_phase_2
from src.models import Phase1Comprehension, Section

# Sample text
sample_text = """
Introduction to Art History

Art history is the study of visual arts throughout human history. It examines paintings, sculptures, and architecture. Art historians analyze style, context, and cultural significance. The discipline emerged in the 18th century.

Methods of Analysis

Art historians use formal analysis to examine visual elements. They also employ iconography to decode symbolic meaning. Contextual analysis considers historical and social factors. These methods provide comprehensive understanding.
"""

# Create Phase 1 output
phase1 = Phase1Comprehension(
    summary="Overview of art history and analysis methods",
    sections=[
        Section(unit_id='1.1', title='Introduction to Art History', level=1, parent_unit_id=None),
        Section(unit_id='1.2', title='Methods of Analysis', level=1, parent_unit_id=None)
    ],
    key_entities=[],
    keywords=[]
)

print("=" * 60)
print("Testing Phase 2 Section-by-Section Extraction")
print("=" * 60)

try:
    # This will make REAL API calls to OpenAI
    print("\nProcessing 2 sections with REAL LLM calls...")
    print("(This will cost ~$0.02-0.05)")

    phase2 = run_phase_2(sample_text, "test", phase1)

    print(f"\n✓ SUCCESS!")
    print(f"  - Extracted {len(phase2.propositions)} propositions")
    print(f"  - Synthesized {len(phase2.key_takeaways)} takeaways")

    if len(phase2.propositions) > 0:
        print(f"\n  Sample proposition:")
        print(f"    [{phase2.propositions[0].proposition_id}] {phase2.propositions[0].proposition_text}")
        print(f"    Bloom: {phase2.propositions[0].bloom_level}")

    print("\n✓ System is working correctly!")

except Exception as e:
    print(f"\n✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
