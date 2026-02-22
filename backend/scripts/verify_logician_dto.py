import logging

from backend.agents.logician import LogicianAgent
from backend.models.domain.logician import LogicianOutput, LogicianOutputDTO

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verify_dto_inheritance():
    """Verify that LogicianOutput inherits correct fields."""
    logger.info("Verifying LogicianOutput inheritance...")

    # 1. Instantiate DTO
    dto_data = {
        "thought_process": "Thinking...",
        "conclusion": "Therefore...",
        "confidence_score": 0.9,
        "logician_data": {
            "toulmin_analysis": [{"id": "1", "claim": "Claim 1", "data": "Data 1", "warrant": "Warrant 1"}],
            "cognitive_level": {
                "bloom_level": "BLOOM_ANALYZING",
                "strategic_depth": "STRAT_HIGH",
                "bloom_score": 4.0,
                "strategic_score": 3.0,
            },
            "walton_scheme": {"identified_scheme": "Expert Opinion", "critical_questions": ["Is he an expert?"]},
            "toulmin_score": 5.0,
        },
    }

    dto = LogicianOutputDTO.model_validate(dto_data)
    logger.info("✅ LogicianOutputDTO instantiated successfully.")

    # 2. Instantiate Domain Model (Authority)
    # Provide system metadata
    domain_args = dto.model_dump()
    domain_args["metadata"] = {
        "luontiaika": "2026-02-19T12:00:00Z",
        "agentti": "LogicianAgent",
        "suoritus_ymparisto": "TEST",
    }
    domain_args["semanttinen_tarkistussumma"] = "checksum123"

    domain_model = LogicianOutput(**domain_args)
    logger.info("✅ LogicianOutput (Domain) instantiated successfully.")

    assert domain_model.metadata is not None
    assert domain_model.logician_data.toulmin_score == 5.0
    assert domain_model.metadata.agentti == "LogicianAgent"
    logger.info("✅ Fields verified.")


def verify_agent_schema():
    """Verify Agent uses DTO schema."""
    logger.info("Verifying LogicianAgent schema...")
    assert LogicianAgent.DTO_SCHEMA == LogicianOutputDTO
    assert LogicianAgent.OUTPUT_SCHEMA == LogicianOutput
    logger.info("✅ Agent schemas correct.")


if __name__ == "__main__":
    verify_dto_inheritance()
    verify_agent_schema()
