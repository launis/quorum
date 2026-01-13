"""Verify AAS-2026 Agent Compliance."""

import logging
import os
import sys

# Ensure backend can be imported
sys.path.append(os.getcwd())

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verifier")


def verify_exception_signature():
    """Verify AgentExecutionError signature matches Echo Protocol."""
    try:
        from backend.exceptions import AgentExecutionError

        e = AgentExecutionError(detail="TEST_CODE", original_error=ValueError("foo"))
        # Check compatibility with Echo Protocol expectations
        if e.details.get("error_code") == "TEST_CODE" and "foo" in e.details.get("original_error", ""):
            logger.info("PASS: AgentExecutionError signature verified.")
        else:
            logger.error(f"FAIL: AgentExecutionError details mismatch: {e.details}")
            sys.exit(1)
    except Exception as e:
        logger.error(f"FAIL: Could not instantiate AgentExecutionError: {e}")
        sys.exit(1)


def verify_imports():
    """Verify all agents can be imported."""
    agents = [
        "backend.agents.base",
        "backend.agents.guard",
        "backend.agents.judge",
        "backend.agents.coach",
        "backend.agents.analyst",
        "backend.agents.archivist",
        "backend.agents.critics",
        "backend.agents.interaction",
        "backend.agents.logician",
        "backend.agents.panel",
        "backend.agents.profiler",
        "backend.agents.xai",
    ]
    for agent_module in agents:
        try:
            __import__(agent_module)
            logger.info(f"PASS: Imported {agent_module}")
        except Exception as e:
            logger.error(f"FAIL: Failed to import {agent_module}: {e}")
            sys.exit(1)


def main():
    """Run verification suite."""
    logger.info("Starting AAS-2026 Agent Verification...")
    verify_exception_signature()
    verify_imports()
    logger.info("ALL CHECKS PASSED.")


if __name__ == "__main__":
    main()
