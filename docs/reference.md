# API Reference

## Core Engine
The core logic of the generic, data-driven workflow engine.

::: backend.engine
    options:
      heading_level: 3

## Agents
Provides the foundational logic for agents, including interactions with Large Language Models (LLMs).

::: backend.agents.base
    options:
      heading_level: 3

## Data Handling and Seeding
Modules responsible for loading, parsing, and seeding data into the system.

::: backend.data_handler
    options:
      heading_level: 3

::: backend.seeder
    options:
      heading_level: 3

## Database
Provides the abstraction layer for all database interactions.

::: src.database.client
    options:
      heading_level: 3

## Schemas
Defines the Pydantic models and data schemas used throughout the application.

::: backend.schemas
    options:
      heading_level: 3

## Hooks (Functional Logic)
Contains the deterministic Python functions (hooks) that are executed by the workflow engine at specific stages.

::: backend.hooks
    options:
      heading_level: 3

## API
The main FastAPI application, defining API endpoints and server configuration.

::: backend.main
    options:
      heading_level: 3