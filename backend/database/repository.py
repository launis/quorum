import asyncio
from abc import ABC, abstractmethod
from typing import Any

from tinydb import Query

from backend.database.wrapper import AbstractDatabase


class AbstractWorkflowRepository(ABC):
    """Universal Async Interface for Workflow Data Access.

    This replaces the old Sync/Async split. All repositories are now Async First.
    TinyDB implementations must use asyncio.to_thread internally.
    """

    # --- Components ---
    @abstractmethod
    async def get_component_by_id(self, component_id: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    async def get_component_by_name(self, name: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    async def register_component(self, component_data: dict[str, Any]):
        pass

    @abstractmethod
    async def update_component_metadata(self, name: str, module: str, component_class: str):
        pass

    @abstractmethod
    async def get_all_components(self) -> list[dict[str, Any]]:
        pass

    # --- Steps ---
    @abstractmethod
    async def get_step_by_id(self, step_id: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    async def get_all_steps(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def create_step(self, step_data: dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def update_step(self, step_id: str, updates: dict[str, Any]):
        pass

    @abstractmethod
    async def delete_step(self, step_id: str):
        pass

    # --- Workflows ---
    @abstractmethod
    async def get_workflow_by_id(self, workflow_id: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    async def create_workflow(self, workflow_data: dict[str, Any]) -> int | str:
        pass

    @abstractmethod
    async def get_all_workflows(
        self, organization_id: str | None = None, role: str | None = None
    ) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def update_workflow(self, workflow_id: str, updates: dict[str, Any]):
        pass

    @abstractmethod
    async def delete_workflow(self, workflow_id: str):
        pass

    # --- Executions ---
    @abstractmethod
    async def create_execution(self, execution_data: dict[str, Any]) -> int | str:
        pass

    @abstractmethod
    async def get_execution(self, execution_id: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    async def update_execution(self, execution_id: str, updates: dict[str, Any]):
        pass

    @abstractmethod
    async def get_all_executions(
        self, organization_id: str | None = None, user_id: str | None = None
    ) -> list[dict[str, Any]]:
        pass

    # --- Config ---
    @abstractmethod
    async def get_model_registry(self) -> dict[str, Any] | None:
        pass

    @abstractmethod
    async def get_banned_phrases(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def add_banned_phrase(self, phrase: str, **kwargs):
        pass

    @abstractmethod
    async def remove_banned_phrase(self, phrase: str):
        pass

    # --- Knowledge Base ---
    @abstractmethod
    async def get_knowledge_base_items(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def add_knowledge_base_item(self, item_data: dict[str, Any]):
        pass

    @abstractmethod
    async def clear_knowledge_base(self):
        pass

    # --- Organization Management ---
    @abstractmethod
    async def create_organization(self, org_data: dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def get_organization(self, org_id: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    async def update_organization(self, org_id: str, updates: dict[str, Any]):
        pass

    @abstractmethod
    async def list_organizations(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def delete_organization(self, org_id: str):
        pass

    @abstractmethod
    async def log_usage(self, record: Any):
        pass

    # --- System Settings (Phase 2) ---
    @abstractmethod
    async def get_system_settings(self) -> dict[str, Any]:
        """Retrieves global system settings singleton."""
        pass

    @abstractmethod
    async def update_system_settings(self, updates: dict[str, Any]):
        """Updates global system settings."""
        pass

    # --- Audit Logs ---
    @abstractmethod
    async def log_audit_event(self, entry: dict[str, Any]):
        """Persists a structured audit log entry."""
        pass

    @abstractmethod
    async def get_audit_logs(
        self,
        organization_id: str | None = None,
        actor_uid: str | None = None,
        action: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Retrieves audit logs with optional filtering."""
        pass

    # --- User Management (Organization Context) ---
    @abstractmethod
    async def get_user(self, uid: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    async def list_users(self, organization_id: str | None = None) -> list[dict[str, Any]]:
        pass

    # --- Quota Management (Phase 5) ---
    @abstractmethod
    async def get_org_usage_total(self, org_id: str, since: str | None = None) -> float:
        """Calculates total cost_usd for an organization, optionally filtered by start date (ISO)."""
        pass


class TinyDBRepository(AbstractWorkflowRepository):
    """Async-First TinyDB Repository.
    Wraps synchronous TinyDB calls in asyncio.to_thread.
    """

    def __init__(self, db_client: AbstractDatabase):
        self.db = db_client
        self.components = self.db.table("components")
        self.steps = self.db.table("steps")
        self.workflows = self.db.table("workflows")
        self.executions = self.db.table("executions")
        self.banned_phrases = self.db.table("banned_phrases")
        self.knowledge_base = self.db.table("knowledge_base")
        self.system_config = self.db.table("system_config")
        self.organizations = self.db.table("organizations")
        self.usage_logs = self.db.table("usage_logs")
        self.organizations = self.db.table("organizations")
        self.usage_logs = self.db.table("usage_logs")
        self.settings = self.db.table("settings")
        self.users = self.db.table("users")
        self.settings = self.db.table("settings")
        self.users = self.db.table("users")
        self.audit_logs = self.db.table("audit_logs")
        import logging

        self.logger = logging.getLogger(__name__)

    async def _run(self, func, *args, **kwargs):
        """Helper to run sync DB calls in thread."""
        return await asyncio.to_thread(func, *args, **kwargs)

    # --- Components ---
    async def get_component_by_id(self, component_id: str) -> dict[str, Any] | None:
        def _get():
            Q = Query()
            res = self.components.search(Q.id == component_id)
            return res[0] if res else None

        return await self._run(_get)

    async def get_component_by_name(self, name: str) -> dict[str, Any] | None:
        def _get():
            Q = Query()
            res = self.components.search(Q.name == name)
            return res[0] if res else None

        return await self._run(_get)

    async def register_component(self, component_data: dict[str, Any]):
        await self._run(self.components.insert, component_data)

    async def update_component_metadata(self, name: str, module: str, component_class: str):
        def _update():
            Q = Query()
            self.components.update({"module": module, "class": component_class}, Q.name == name)

        await self._run(_update)

    async def get_all_components(self) -> list[dict[str, Any]]:
        return await self._run(self.components.all)

    # --- Steps ---
    async def get_step_by_id(self, step_id: str) -> dict[str, Any] | None:
        def _get():
            Q = Query()
            res = self.steps.search(Q.id == step_id)
            return res[0] if res else None

        return await self._run(_get)

    async def get_all_steps(self) -> list[dict[str, Any]]:
        return await self._run(self.steps.all)

    async def create_step(self, step_data: dict[str, Any]) -> str:
        # TinyDB insert returns document ID (int), we convert to str/int
        res = await self._run(self.steps.insert, step_data)
        return str(res)

    async def update_step(self, step_id: str, updates: dict[str, Any]):
        def _update():
            Q = Query()
            self.steps.update(updates, Q.id == step_id)

        await self._run(_update)

    async def delete_step(self, step_id: str):
        def _delete():
            Q = Query()
            self.steps.remove(Q.id == step_id)

        await self._run(_delete)

    # --- Workflows ---
    async def get_workflow_by_id(self, workflow_id: str) -> dict[str, Any] | None:
        def _get():
            Q = Query()
            res = self.workflows.search(Q.id == workflow_id)
            return res[0] if res else None

        return await self._run(_get)

    async def create_workflow(self, workflow_data: dict[str, Any]) -> int | str:
        return await self._run(self.workflows.insert, workflow_data)

    async def get_all_workflows(
        self, organization_id: str | None = None, role: str | None = None
    ) -> list[dict[str, Any]]:
        def _get():
            all_wfs = self.workflows.all()

            # Root View: See EVERYTHING if filtering by system/root
            if role == "ROOT":
                return all_wfs

            # Tenant View
            filtered = []
            for wf in all_wfs:
                wf_org = wf.get("organization_id")
                is_system = wf_org is None or wf_org == "system"
                is_public = wf.get("is_public", False)

                # 1. Own Org Workflows
                if organization_id and wf_org == organization_id:
                    filtered.append(wf)

                # 2. System Workflows (Public Only, unless Root handled above)
                elif is_system and is_public:
                    filtered.append(wf)

            return filtered

        return await self._run(_get)

    async def update_workflow(self, workflow_id: str, updates: dict[str, Any]):
        def _update():
            Q = Query()
            self.workflows.update(updates, Q.id == workflow_id)

        await self._run(_update)

    async def delete_workflow(self, workflow_id: str):
        def _delete():
            Q = Query()
            self.workflows.remove(Q.id == workflow_id)

        await self._run(_delete)

    # --- Executions ---
    async def create_execution(self, execution_data: dict[str, Any]) -> int | str:
        return await self._run(self.executions.insert, execution_data)

    async def get_execution(self, execution_id: str) -> dict[str, Any] | None:
        def _get():
            Q = Query()
            res = self.executions.search(Q.execution_id == str(execution_id))
            return res[0] if res else None

        return await self._run(_get)

    async def update_execution(self, execution_id: str, updates: dict[str, Any]):
        def _update():
            Q = Query()
            self.executions.update(updates, Q.execution_id == str(execution_id))

        await self._run(_update)

    async def get_all_executions(
        self, organization_id: str | None = None, user_id: str | None = None
    ) -> list[dict[str, Any]]:
        def _get():
            all_execs = self.executions.all()

            # 1. Tenant Filter
            if organization_id:
                all_execs = [e for e in all_execs if e.get("organization_id") == organization_id]

            # 2. User Filter (Member Role)
            if user_id:
                all_execs = [e for e in all_execs if e.get("user_id") == user_id]

            return all_execs

        return await self._run(_get)

    # --- Config ---
    async def get_model_registry(self) -> dict[str, Any] | None:
        def _get():
            Q = Query()
            res = self.system_config.search(Q.type == "model_registry")
            return res[0] if res else None

        return await self._run(_get)

    async def get_banned_phrases(self) -> list[dict[str, Any]]:
        return await self._run(self.banned_phrases.all)

    async def add_banned_phrase(self, phrase: str, **kwargs):
        def _add():
            existing = self.banned_phrases.search(Query().phrase == phrase)
            if not existing:
                data = {"phrase": phrase}
                data.update(kwargs)
                return self.banned_phrases.insert(data)

        await self._run(_add)

    async def remove_banned_phrase(self, phrase: str):
        def _remove():
            self.banned_phrases.remove(Query().phrase == phrase)

        await self._run(_remove)

    # --- Knowledge Base ---
    async def get_knowledge_base_items(self) -> list[dict[str, Any]]:
        return await self._run(self.knowledge_base.all)

    async def add_knowledge_base_item(self, item_data: dict[str, Any]):
        await self._run(self.knowledge_base.insert, item_data)

    async def clear_knowledge_base(self):
        await self._run(self.knowledge_base.truncate)

    # --- Organization Management ---
    async def create_organization(self, org_data: dict[str, Any]) -> str:
        # For simplicity, we assume org_data already has 'id' or we let TinyDB trigger one.
        # But our ABC expects a string return ID.
        result = await self._run(self.organizations.insert, org_data)
        return str(result)

    async def get_organization(self, org_id: str) -> dict[str, Any] | None:
        def _get():
            Q = Query()
            res = self.organizations.search(Q.id == org_id)
            return res[0] if res else None

        return await self._run(_get)

    async def update_organization(self, org_id: str, updates: dict[str, Any]):
        def _update():
            Q = Query()
            self.organizations.update(updates, Q.id == org_id)

        await self._run(_update)

    async def list_organizations(self) -> list[dict[str, Any]]:
        return await self._run(self.organizations.all)

    async def delete_organization(self, org_id: str):
        def _delete():
            Q = Query()
            self.organizations.remove(Q.id == org_id)

        await self._run(_delete)

    async def delete_org_data(self, org_id: str):
        """Cascading delete for organization data (Workflows, Executions)."""

        def _delete_data():
            # 1. Delete Workflows
            self.workflows.remove(Query().organization_id == org_id)
            # 2. Delete Executions
            self.executions.remove(Query().organization_id == org_id)

        await self._run(_delete_data)

    async def get_org_usage_total(self, org_id: str, since: str | None = None) -> float:
        def _calc():
            # Filter by Org
            logs = self.usage_logs.search(Query().org_id == org_id)
            total = 0.0
            for log in logs:
                if since:
                    if log.get("timestamp", "") < since:
                        continue
                total += float(log.get("cost_usd", 0.0))
            return total

        return await self._run(_calc)

    async def log_usage(self, record: Any):
        """Logs usage record to the database."""
        # TinyDB stores dicts, so we dump the model.
        # record is expected to be a Pydantic model (UsageRecord)
        data = record.model_dump()
        await self._run(self.usage_logs.insert, data)

    # --- System Settings ---
    async def get_system_settings(self) -> dict[str, Any]:
        def _get():
            # Singleton: ID=1 or just the first record
            res = self.settings.all()
            if res:
                return res[0]
            # Default empty, caller handles defaults
            return {}

        return await self._run(_get)

    async def update_system_settings(self, updates: dict[str, Any]):
        def _update():
            # Check existence
            existing = self.settings.all()
            if not existing:
                self.settings.insert(updates)
            else:
                # Update the first one
                doc_id = existing[0].doc_id
                self.settings.update(updates, doc_ids=[doc_id])

        await self._run(_update)

    # --- Audit Logs ---
    async def log_audit_event(self, entry: dict[str, Any]):
        self.logger.debug(f"REPO: log_audit_event called with {entry}")
        await self._run(self.audit_logs.insert, entry)

    async def get_audit_logs(
        self,
        organization_id: str | None = None,
        actor_uid: str | None = None,
        action: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        def _get():
            # TinyDB doesn't do complex querying efficiently, so we filter in Python for now.
            # In a real DB we'd index this.
            all_logs = self.audit_logs.all()

            self.logger.debug(
                f"REPO: get_audit_logs found {len(all_logs)} entries. Requested: org={organization_id}, action={action}"
            )
            if len(all_logs) > 0:
                self.logger.debug(f"REPO: last log: {all_logs[-1]}")

            # Filter
            filtered = []
            for log in all_logs:
                if organization_id and log.get("organization_id") != organization_id:
                    continue
                if actor_uid and log.get("actor_uid") != actor_uid:
                    continue
                if action and log.get("action") != action:
                    continue
                filtered.append(log)

            # Sort by timestamp desc (newest first)
            filtered.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
            return filtered[:limit]

        return await self._run(_get)

    # --- User Management ---
    async def get_user(self, uid: str) -> dict[str, Any] | None:
        def _get():
            Q = Query()
            # Assuming 'uid' is the key in users table
            res = self.users.search(Q.uid == uid)
            return res[0] if res else None

        return await self._run(_get)

    async def list_users(self, organization_id: str | None = None) -> list[dict[str, Any]]:
        def _list():
            if organization_id:
                return self.users.search(Query().organization_id == organization_id)
            return self.users.all()

        return await self._run(_list)


# Backward compatibility alias
WorkflowRepository = TinyDBRepository
