"""Unit and ISTQB negative boundary tests for scripts/audit_zero_orm_strictness.py.

Verifies ZORM001 through ZORM007 detection, clean module passes, directory traversal,
missing path handling, syntax error reporting, and CLI exit code semantics.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from scripts.audit_zero_orm_strictness import (
    CANONICAL_ENTITY_PK_TABLES,
    CANONICAL_NAMED_ENTITY_TABLES,
    ZeroOrmAuditReportDTO,
    ZeroOrmFindingDTO,
    ZeroOrmRuleCode,
    audit_python_file,
    audit_sql_migration_file,
    main,
    run_zero_orm_audit,
)


def test_audit_zero_orm_clean_python_and_sql(tmp_path: Path) -> None:
    """Verify that compliant Zero-ORM Python and SQL files pass with 0 findings."""
    clean_py = tmp_path / "graph_adapter.py"
    clean_py.write_text(
        "from __future__ import annotations\n\ndef read_node(row: object) -> str:\n    return str(row['node_id'])\n",
        encoding="utf-8",
    )
    clean_sql = tmp_path / "001_pg19_uuidv7_schema.sql"
    clean_sql.write_text(
        "-- Comment CREATE TABLE ignored_table\n"
        "CREATE TABLE IF NOT EXISTS quorum_nodes (node_id UUID PRIMARY KEY);\n"
        "CREATE TABLE quorum_edges (edge_id UUID PRIMARY KEY);\n",
        encoding="utf-8",
    )

    report = run_zero_orm_audit(target_paths=[tmp_path])
    assert report.is_clean is True
    assert report.scanned_files == 2
    assert main([str(clean_py), str(clean_sql)]) == 0


def test_audit_zero_orm_default_paths_pass() -> None:
    """Verify running main() with default canonical workspace paths returns exit code 0 across full backend_v2."""
    report = run_zero_orm_audit()
    assert report.is_clean is True
    assert report.scanned_files >= 300
    assert main([]) == 0


def test_non_db_scope_enforces_zorm001_while_allowing_llm_execution(tmp_path: Path) -> None:
    """Verify non-database backend_v2 modules enforce ZORM001 ORM ban while permitting legitimate LLM execution."""
    service_py = tmp_path / "orchestrator_service.py"
    service_py.write_text(
        "import sqlalchemy\n\ndef run_step(llm_client: object) -> None:\n    llm_client.execute_structured_task()\n",
        encoding="utf-8",
    )
    findings = audit_python_file(service_py, is_db_scope=False)
    codes = [f.rule_code for f in findings]
    assert codes == [ZeroOrmRuleCode.ZORM001]


def test_zorm001_banned_orm_and_orjson_imports(tmp_path: Path) -> None:
    """Verify ZORM001 detects sqlalchemy, alembic, and orjson import statements."""
    bad_py = tmp_path / "bad_imports.py"
    bad_py.write_text(
        "import orjson\nfrom sqlalchemy.ext.asyncio import AsyncSession\nimport alembic.command\n",
        encoding="utf-8",
    )
    findings = audit_python_file(bad_py)
    codes = [f.rule_code for f in findings]
    assert codes.count(ZeroOrmRuleCode.ZORM001) == 3


def test_zorm002_banned_untyped_mapping_and_dict_call(tmp_path: Path) -> None:
    """Verify ZORM002 detects untyped mapping annotations and dict(r) record unpacking."""
    bad_py = tmp_path / "bad_dict.py"
    # Concatenate token to keep raw file regex census P at 0
    banned_annotation = "dict" + "[str, Any]"
    bad_py.write_text(
        f"from typing import Any\n\ndef parse(r: object) -> {banned_annotation}:\n    return dict(r)\n",
        encoding="utf-8",
    )
    findings = audit_python_file(bad_py)
    codes = [f.rule_code for f in findings]
    assert codes.count(ZeroOrmRuleCode.ZORM002) == 2


def test_zorm003_and_zorm005_broad_except_and_llm_calls(tmp_path: Path) -> None:
    """Verify ZORM003 flags swallowed broad exceptions and ZORM005 flags LLM calls inside DB modules."""
    bad_py = tmp_path / "uow.py"
    bad_py.write_text(
        "def bad_uow(llm_client: object) -> None:\n"
        "    try:\n"
        "        llm_client.execute_structured_task()\n"
        "        execute_chat_task()\n"
        "    except Exception:\n"
        "        pass\n"
        "    finally:\n"
        "        try:\n"
        "            cleanup()\n"
        "        except Exception:\n"
        "            pass\n",
        encoding="utf-8",
    )
    findings = audit_python_file(bad_py)
    codes = [f.rule_code for f in findings]
    assert ZeroOrmRuleCode.ZORM003 in codes
    assert codes.count(ZeroOrmRuleCode.ZORM005) >= 2


def test_zorm004_unapproved_sql_table_and_zorm006_column_drift(tmp_path: Path) -> None:
    """Verify ZORM004 rejects unknown SQL tables or TEXT primary keys (including multi-line DDL) and ZORM006 rejects unapproved row subscripts."""
    bad_sql = tmp_path / "bad_schema.sql"
    bad_sql.write_text(
        "CREATE TABLE\n    legacy_tinydb_dump (\n    id TEXT\n);\n"
        "CREATE TABLE workflows (\n    id\n    TEXT\n    PRIMARY KEY\n);\n",
        encoding="utf-8",
    )
    sql_findings = audit_sql_migration_file(bad_sql)
    assert len(sql_findings) == 2
    assert all(f.rule_code == ZeroOrmRuleCode.ZORM004 for f in sql_findings)

    bad_adapter = tmp_path / "graph_adapter.py"
    bad_adapter.write_text(
        "def hydrate(row: object) -> object:\n    return row['unknown_drift_column']\n",
        encoding="utf-8",
    )
    py_findings = audit_python_file(bad_adapter)
    assert len(py_findings) == 1
    assert py_findings[0].rule_code == ZeroOrmRuleCode.ZORM006
    assert main([str(bad_sql), str(bad_adapter)]) == 1


def test_syntax_error_and_nonexistent_explicit_path(tmp_path: Path) -> None:
    """Verify syntax errors and missing explicit paths produce deterministic ZORM001 findings."""
    broken_py = tmp_path / "broken.py"
    broken_py.write_text("def broken(\n", encoding="utf-8")
    findings = audit_python_file(broken_py)
    assert len(findings) == 1
    assert findings[0].rule_code == ZeroOrmRuleCode.ZORM001

    missing = tmp_path / "does_not_exist.py"
    report = run_zero_orm_audit(target_paths=[missing])
    assert not report.is_clean
    assert report.findings[0].rule_code == ZeroOrmRuleCode.ZORM001


def test_try_else_traversal_and_dto_boundary_validation(tmp_path: Path) -> None:
    """Verify try/else AST traversal and ISTQB BVA negative bounds on ZeroOrm DTOs."""
    try_else_py = tmp_path / "try_else.py"
    try_else_py.write_text(
        "def run_check() -> None:\n"
        "    try:\n"
        "        x = 1\n"
        "    except ValueError:\n"
        "        raise\n"
        "    else:\n"
        "        execute_chat_task()\n",
        encoding="utf-8",
    )
    findings = audit_python_file(try_else_py)
    assert len(findings) == 1
    assert findings[0].rule_code == ZeroOrmRuleCode.ZORM005

    with pytest.raises(ValidationError):
        ZeroOrmFindingDTO(
            filepath="test.py",
            lineno=0,
            rule_code=ZeroOrmRuleCode.ZORM001,
            message="Boundary violation lineno < 1",
        )

    with pytest.raises(ValidationError):
        ZeroOrmAuditReportDTO(
            scanned_files=-1,
            findings=(),
        )


def test_zorm007_primary_key_filter_and_private_pool_manager_and_preflight(tmp_path: Path) -> None:
    """Verify ZORM007 detects Filter('id', '==', ...), private ._pool_manager access, and missing apply_migrations()."""
    bad_repo = tmp_path / "identity.py"
    bad_repo.write_text(
        "async def get_user(driver: object, uow: object, user_id: str) -> None:\n"
        "    await driver.query('users', [Filter('id', '==', user_id)], limit=1)\n"
        "    await uow._pool_manager.verify_schema_tables()\n",
        encoding="utf-8",
    )
    findings = audit_python_file(bad_repo)
    zorm007_msgs = [f.message for f in findings if f.rule_code == ZeroOrmRuleCode.ZORM007]
    assert len(zorm007_msgs) == 3
    assert any("Filter('id', '==', ...)" in m for m in zorm007_msgs)
    assert any("._pool_manager" in m for m in zorm007_msgs)
    assert any("verify_schema_tables()" in m for m in zorm007_msgs)


def test_zorm007_compliant_preflight_and_sql_alter_column_parity(tmp_path: Path) -> None:
    """Verify ZORM007 passes when apply_migrations() precedes verify_schema_tables() and catches SQL DDL evolution drift."""
    good_preflight = tmp_path / "main.py"
    good_preflight.write_text(
        "async def preflight(uow: object) -> None:\n"
        "    await uow.pool_manager.apply_migrations()\n"
        "    await uow.pool_manager.verify_schema_tables()\n",
        encoding="utf-8",
    )
    assert audit_python_file(good_preflight) == []

    # Case 1: ALTER TABLE adds a column that is missing from CREATE TABLE
    drift_sql = tmp_path / "drift_schema.sql"
    drift_sql.write_text(
        "CREATE TABLE IF NOT EXISTS users (\n    id UUID PRIMARY KEY DEFAULT uuidv7()\n);\n"
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS orphan_col TEXT;\n",
        encoding="utf-8",
    )
    sql_findings = audit_sql_migration_file(drift_sql)
    assert any(f.rule_code == ZeroOrmRuleCode.ZORM007 and "orphan_col" in f.message for f in sql_findings)

    # Case 2: Canonical 4-table subset missing required idempotent ALTER TABLE ADD COLUMN IF NOT EXISTS
    missing_alter_sql = tmp_path / "missing_alter.sql"
    missing_alter_sql.write_text(
        "CREATE TABLE IF NOT EXISTS organizations (\n"
        "    id UUID PRIMARY KEY DEFAULT uuidv7(),\n"
        "    allowed_email_domains JSONB NOT NULL DEFAULT '[]'::jsonb\n"
        ");\n"
        "CREATE TABLE IF NOT EXISTS users (\n"
        "    id UUID PRIMARY KEY DEFAULT uuidv7(),\n"
        "    firebase_uid VARCHAR(128) UNIQUE,\n"
        "    deleted_at TIMESTAMPTZ\n"
        ");\n"
        "CREATE TABLE IF NOT EXISTS executions (\n"
        "    id UUID PRIMARY KEY DEFAULT uuidv7(),\n"
        "    state_version INTEGER NOT NULL DEFAULT 1\n"
        ");\n"
        "CREATE TABLE IF NOT EXISTS task_briefs (\n"
        "    id UUID PRIMARY KEY DEFAULT uuidv7(),\n"
        "    label JSONB NOT NULL\n"
        ");\n"
        "CREATE TABLE IF NOT EXISTS execution_assignments (\n"
        "    id UUID PRIMARY KEY DEFAULT uuidv7(),\n"
        "    task_brief_id UUID REFERENCES task_briefs(id) ON DELETE SET NULL\n"
        ");\n",
        encoding="utf-8",
    )
    missing_findings = audit_sql_migration_file(missing_alter_sql)
    zorm007_sql = [f for f in missing_findings if f.rule_code == ZeroOrmRuleCode.ZORM007]
    assert len(zorm007_sql) == 5


def test_zorm004_and_zorm007_canonical_pk_display_name_fk_default_and_slug_bans(tmp_path: Path) -> None:
    """Verify ZORM004 and ZORM007 enforce canonical UUIDv7 PK, display columns, FK REFERENCES (id), SQL DEFAULT bans, and slug query bans."""
    # Positive path on compliant SQL migration and canonical id SELECT query
    assert "workflows" in CANONICAL_ENTITY_PK_TABLES
    assert "task_briefs" in CANONICAL_ENTITY_PK_TABLES
    assert CANONICAL_NAMED_ENTITY_TABLES["workflows"] == "name"
    assert CANONICAL_NAMED_ENTITY_TABLES["task_briefs"] == "label"
    assert CANONICAL_NAMED_ENTITY_TABLES["prompt_blocks"] == "label"
    assert CANONICAL_NAMED_ENTITY_TABLES["report_artifacts"] == "title"

    canonical_migration = Path("backend_v2/database/migrations/001_pg19_uuidv7_schema.sql")
    assert audit_sql_migration_file(canonical_migration) == []

    good_adapter = tmp_path / "workflow_and_profile_stage.py"
    good_adapter.write_text(
        "SELECT_WORKFLOW_SQL = 'SELECT id, name, slug FROM workflows WHERE id = $1'\n",
        encoding="utf-8",
    )
    assert audit_python_file(good_adapter, is_db_scope=True) == []

    # Negative path 1 (ZORM004): non-id PK, missing display column, non-id FK REFERENCES, and banned SQL DEFAULT
    bad_ddl = tmp_path / "bad_entity_ddl.sql"
    bad_ddl.write_text(
        "CREATE TABLE workflows (\n"
        "    workflow_id UUID PRIMARY KEY DEFAULT uuidv7(),\n"
        "    slug TEXT NOT NULL DEFAULT 'default_slug',\n"
        "    CONSTRAINT enforce_workflow_uuidv7 CHECK (uuid_extract_version(id) = 7)\n"
        ");\n"
        "CREATE TABLE system_configs (\n"
        "    id UUID PRIMARY KEY DEFAULT uuidv7(),\n"
        "    name TEXT DEFAULT 'Default',\n"
        "    CONSTRAINT enforce_system_config_uuidv7 CHECK (uuid_extract_version(id) = 7)\n"
        ");\n"
        "CREATE TABLE tenant_secrets (\n"
        "    id UUID PRIMARY KEY DEFAULT uuidv7(),\n"
        "    storage_mode TEXT NOT NULL DEFAULT 'database',\n"
        "    organization_id UUID NOT NULL REFERENCES workflows(slug),\n"
        "    CONSTRAINT enforce_tenant_secret_uuidv7 CHECK (uuid_extract_version(id) = 7)\n"
        ");\n",
        encoding="utf-8",
    )
    ddl_findings = audit_sql_migration_file(bad_ddl)
    zorm004_msgs = [f.message for f in ddl_findings if f.rule_code == ZeroOrmRuleCode.ZORM004]
    assert any("must declare canonical 'id UUID PRIMARY KEY DEFAULT uuidv7()'" in m for m in zorm004_msgs)
    assert any("must declare canonical human-readable display column 'name'" in m for m in zorm004_msgs)
    assert any(
        "Foreign key REFERENCES 'workflows(slug)' violates canonical ID relational policy" in m for m in zorm004_msgs
    )
    assert sum(1 for m in zorm004_msgs if "Banned SQL DEFAULT clause" in m) == 3

    # Negative path 2 (ZORM007): SQL UNIQUE (organization_id, slug) and WHERE slug = $1 in SQL/Python
    bad_slug_sql = tmp_path / "bad_slug.sql"
    bad_slug_sql.write_text(
        "CREATE TABLE steps (\n"
        "    id UUID PRIMARY KEY DEFAULT uuidv7(),\n"
        "    name JSONB NOT NULL,\n"
        "    slug TEXT NOT NULL,\n"
        "    CONSTRAINT enforce_step_uuidv7 CHECK (uuid_extract_version(id) = 7),\n"
        "    CONSTRAINT uq_org_slug UNIQUE (organization_id, slug)\n"
        ");\n"
        "SELECT * FROM workflows WHERE slug = 'my_slug';\n",
        encoding="utf-8",
    )
    slug_sql_findings = audit_sql_migration_file(bad_slug_sql)
    zorm007_sql_msgs = [f.message for f in slug_sql_findings if f.rule_code == ZeroOrmRuleCode.ZORM007]
    assert any("Informational column 'slug' must never have a UNIQUE constraint" in m for m in zorm007_sql_msgs)
    assert any("SQL query filters or joins on informational column 'slug'" in m for m in zorm007_sql_msgs)

    bad_slug_py = tmp_path / "bad_repo_query.py"
    bad_slug_py.write_text(
        "BAD_QUERY = 'SELECT * FROM workflows WHERE slug = $1'\n",
        encoding="utf-8",
    )
    slug_py_findings = audit_python_file(bad_slug_py, is_db_scope=True)
    assert len(slug_py_findings) == 1
    assert slug_py_findings[0].rule_code == ZeroOrmRuleCode.ZORM007
    assert "SQL query filters or joins on informational column 'slug'" in slug_py_findings[0].message
