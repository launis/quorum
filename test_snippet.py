
def test_prompt_compiler_architectural_integrity() -> None:
    """Suojelee arkkitehtuuria vahinkopoistoilta ja "salaa poistamisilta".
    Varmistaa, että molemmat evaluointistrategiat pysyvät olemassa.
    """
    from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler

    msg1 = "CRITICAL: build_dynamic_schema on SALAA POISTETTU! Tämä rikkoo XAI-laajennukset ja 3D-matriisit."
    assert hasattr(PromptCompiler, "build_dynamic_schema"), msg1

    msg2 = (
        "CRITICAL: build_blind_evaluation_schema on SALAA POISTETTU! "
        "Tämä rikkoo Epic 20 Phase 7 sokeiden kokeilujen arkkitehtuurin."
    )
    assert hasattr(PromptCompiler, "build_blind_evaluation_schema"), msg2
