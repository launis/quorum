# API Reference

## Core Engine

The core logic of the Generic Workflow Engine.

::: src.engine.orchestrator
    options:
      heading_level: 3

::: src.engine.executor
    options:
      heading_level: 3

::: src.engine.llm_handler
    options:
      heading_level: 3

## Data Handling & Seeding

Modules responsible for loading, parsing, and seeding data.

::: src.data_handler
    options:
      heading_level: 3

::: src.seeder
    options:
      heading_level: 3

## Database

Abstraction layer for database interactions.

::: src.database.client
    options:
      heading_level: 3

## Components & Registry

Registries for mapping JSON configuration to Python code.

::: src.components.hook_registry
    options:
      heading_level: 3

::: src.models.schema_registry
    options:
      heading_level: 3

## Hooks (Functional Logic)

Deterministic Python functions called by the engine.

::: src.components.hooks.search
    options:
      heading_level: 3

::: src.components.hooks.calculations
    options:
      heading_level: 3

::: src.components.hooks.parsing
    options:
      heading_level: 3

::: src.components.hooks.sanitization
    options:
      heading_level: 3

::: src.components.hooks.reporting
    options:
      heading_level: 3

## API

FastAPI application structure.

::: src.api.server
    options:
      heading_level: 3
