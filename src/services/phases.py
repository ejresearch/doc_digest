from .llm_client import (
    extract_comprehension_pass,
    build_structural_outline,
    extract_propositions,
    derive_analytical_metadata
)

def run_phase_1(text:str)->dict:
    return extract_comprehension_pass(text)

def run_phase_2(text:str, comp:dict)->dict:
    return build_structural_outline(text, comp)

def run_phase_3(text:str, comp:dict, outline:dict)->dict:
    return extract_propositions(text, comp, outline)

def run_phase_4(comp:dict, outline:dict, props:dict, hints:dict|None=None)->dict:
    return derive_analytical_metadata(comp, outline, props, hints=hints)
