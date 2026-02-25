import re

with open("backend/api/routes/config/workflows.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Imports
content = content.replace('from tinydb import Query', '')

# 2. get_steps
content = content.replace('def get_steps(db: DatabaseDep) -> list[StepDefinition]:', 'async def get_steps(repository: RepositoryDep) -> list[StepDefinition]:')
content = content.replace('steps = db.table("steps").all()', 'steps = await repository.get_all_steps()')

# 3. create_step
content = content.replace('def create_step(step: StepDefinition, db: DatabaseDep) -> StepDefinition:', 'async def create_step(step: StepDefinition, repository: RepositoryDep) -> StepDefinition:')
create_step_old = """        table = db.table("steps")
        if table.search(Query().id == step.id):
            raise ConflictError(message="Resource conflict", details={"error_code": "STEP_ID_EXISTS"})

        doc = step.model_dump(exclude={"component", "execution_config"})
        table.insert(doc)"""
create_step_new = """        if await repository.get_step_by_id(step.id):
            raise ConflictError(message="Resource conflict", details={"error_code": "STEP_ID_EXISTS"})

        doc = step.model_dump(exclude={"component", "execution_config"})
        await repository.create_step(doc)"""
content = content.replace(create_step_old, create_step_new)

# 4. update_step
content = content.replace('def update_step(step_id: str, step: StepDefinition, db: DatabaseDep) -> StepDefinition:', 'async def update_step(step_id: str, step: StepDefinition, repository: RepositoryDep) -> StepDefinition:')
update_step_old = """        table = db.table("steps")
        if not table.search(Query().id == step_id):
            raise ResourceNotFoundError("Step", step_id, details={"error_code": "STEP_NOT_FOUND"})

        # Prevent ID change collision
        if step.id != step_id and table.contains(Query().id == step.id):
            raise ConflictError(message="New Step ID already exists", details={"id": step.id})

        doc = step.model_dump(exclude={"component", "execution_config"})

        if step.id == step_id:
            table.update(doc, Query().id == step_id)
        else:
            table.remove(Query().id == step_id)
            table.insert(doc)"""
update_step_new = """        existing = await repository.get_step_by_id(step_id)
        if not existing:
            raise ResourceNotFoundError("Step", step_id, details={"error_code": "STEP_NOT_FOUND"})

        # Prevent ID change collision
        if step.id != step_id and await repository.get_step_by_id(step.id):
            raise ConflictError(message="New Step ID already exists", details={"id": step.id})

        doc = step.model_dump(exclude={"component", "execution_config"})

        if step.id == step_id:
            await repository.update_step(step_id, doc)
        else:
            await repository.delete_step(step_id)
            await repository.create_step(doc)"""
content = content.replace(update_step_old, update_step_new)

# 5. delete_step
content = content.replace('def delete_step(step_id: str, db: DatabaseDep) -> StepDeleteResponse:', 'async def delete_step(step_id: str, repository: RepositoryDep) -> StepDeleteResponse:')
delete_step_old = """        # 1. Check Existence
        table = db.table("steps")
        if not table.search(Query().id == step_id):
            raise ResourceNotFoundError("Step", step_id, details={"error_code": "STEP_NOT_FOUND"})

        # 2. Integrity Check: Workflow Usage
        workflows = db.table("workflows").all()
        used_in = []
        for wf in workflows:
            if step_id in wf.get("steps", []) or step_id in wf.get("sequence", []):
                used_in.append(wf.get("name", wf["id"]))

        if used_in:
            raise ConflictError(message="Resource conflict", details={"error_code": "STEP_IN_USE", "used_in": used_in})

        # 3. Delete
        table.remove(Query().id == step_id)"""
delete_step_new = """        # 1. Check Existence
        if not await repository.get_step_by_id(step_id):
            raise ResourceNotFoundError("Step", step_id, details={"error_code": "STEP_NOT_FOUND"})

        # 2. Integrity Check: Workflow Usage
        workflows = await repository.get_all_workflows()
        used_in = []
        for wf in workflows:
            if step_id in wf.get("steps", []) or step_id in wf.get("sequence", []):
                used_in.append(wf.get("name", wf.get("id")))

        if used_in:
            raise ConflictError(message="Resource conflict", details={"error_code": "STEP_IN_USE", "used_in": used_in})

        # 3. Delete
        await repository.delete_step(step_id)"""
content = content.replace(delete_step_old, delete_step_new)


# 6. update_workflow
content = content.replace('def update_workflow(wf_id: str, update: WorkflowConfigUpdate, db: DatabaseDep) -> WorkflowConfigDefinition:', 'async def update_workflow(wf_id: str, update: WorkflowConfigUpdate, repository: RepositoryDep) -> WorkflowConfigDefinition:')
update_wf_old = """        Workflow = Query()
        table = db.table("workflows")

        if not table.search(Workflow.id == wf_id):
            raise ResourceNotFoundError("Workflow", wf_id, details={"error_code": "WORKFLOW_NOT_FOUND"})

        update_data: dict[str, Any] = {}
        if update.steps is not None:
            update_data["steps"] = update.steps
        if update.sequence is not None:
            update_data["sequence"] = update.sequence
        if update.description:
            update_data["description"] = update.description
        if update.default_model_mapping is not None:
            update_data["default_model_mapping"] = update.default_model_mapping

        if not update_data:
            raise AppException(
                message="No update data provided",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": "NO_UPDATE_DATA"},
            )

        steps_to_check = update.steps if update.steps else update.sequence
        if steps_to_check:
            valid_steps = {s["id"] for s in db.table("steps").all()}
            for item in steps_to_check:
                sid = item if isinstance(item, str) else item.get("id")
                if sid and sid not in valid_steps:
                    raise AppException(
                        message=f"Step '{sid}' not found",
                        status_code=status.HTTP_400_BAD_REQUEST,
                        details={"error_code": "INVALID_STEP_ID"},
                    )

        table.update(update_data, Workflow.id == wf_id)
        # Fetch updated to return full object
        updated_doc = table.get(Workflow.id == wf_id)
        if not updated_doc:
            raise AppException(message="Failed to fetch after update", status_code=500)"""
update_wf_new = """        existing = await repository.get_workflow_by_id(wf_id)

        if not existing:
            raise ResourceNotFoundError("Workflow", wf_id, details={"error_code": "WORKFLOW_NOT_FOUND"})

        update_data = {}
        if update.steps is not None:
            update_data["steps"] = update.steps
        if update.sequence is not None:
            update_data["sequence"] = update.sequence
        if update.description:
            update_data["description"] = update.description
        if update.default_model_mapping is not None:
            update_data["default_model_mapping"] = update.default_model_mapping

        if not update_data:
            raise AppException(
                message="No update data provided",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": "NO_UPDATE_DATA"},
            )

        steps_to_check = update.steps if update.steps else update.sequence
        if steps_to_check:
            all_steps = await repository.get_all_steps()
            valid_steps = {s["id"] for s in all_steps}
            for item in steps_to_check:
                sid = item if isinstance(item, str) else item.get("id")
                if sid and sid not in valid_steps:
                    raise AppException(
                        message=f"Step '{sid}' not found",
                        status_code=status.HTTP_400_BAD_REQUEST,
                        details={"error_code": "INVALID_STEP_ID"},
                    )

        await repository.update_workflow(wf_id, update_data)
        # Fetch updated to return full object
        updated_doc = await repository.get_workflow_by_id(wf_id)
        if not updated_doc:
            raise AppException(message="Failed to fetch after update", status_code=500)"""
content = content.replace(update_wf_old, update_wf_new)

# 7. create_workflow
content = content.replace('def create_workflow(workflow: WorkflowConfigCreate, db: DatabaseDep) -> WorkflowConfigDefinition:', 'async def create_workflow(workflow: WorkflowConfigCreate, repository: RepositoryDep) -> WorkflowConfigDefinition:')
create_wf_old = """        Workflow = Query()
        table = db.table("workflows")

        if table.search(Workflow.id == workflow.id):
            raise ConflictError(message="Resource conflict", details={"error_code": "WORKFLOW_ID_EXISTS"})

        new_wf = workflow.model_dump()
        if workflow.sequence:
            valid_steps = {s["id"] for s in db.table("steps").all()}
            for step_id in workflow.sequence:
                if step_id not in valid_steps:
                    raise AppException(
                        message=f"Step '{step_id}' not found",
                        status_code=status.HTTP_400_BAD_REQUEST,
                        details={"error_code": "INVALID_STEP_ID"},
                    )

        table.insert(new_wf)"""
create_wf_new = """        if await repository.get_workflow_by_id(workflow.id):
            raise ConflictError(message="Resource conflict", details={"error_code": "WORKFLOW_ID_EXISTS"})

        new_wf = workflow.model_dump()
        if workflow.sequence:
            all_steps = await repository.get_all_steps()
            valid_steps = {s["id"] for s in all_steps}
            for step_id in workflow.sequence:
                if step_id not in valid_steps:
                    raise AppException(
                        message=f"Step '{step_id}' not found",
                        status_code=status.HTTP_400_BAD_REQUEST,
                        details={"error_code": "INVALID_STEP_ID"},
                    )

        await repository.create_workflow(new_wf)"""
content = content.replace(create_wf_old, create_wf_new)

# 8. delete_workflow
content = content.replace('def delete_workflow(wf_id: str, db: DatabaseDep) -> ConfigWorkflowDeleteResponse:', 'async def delete_workflow(wf_id: str, repository: RepositoryDep) -> ConfigWorkflowDeleteResponse:')
del_wf_old = """        Workflow = Query()
        table = db.table("workflows")
        if not table.search(Workflow.id == wf_id):
            raise ResourceNotFoundError("Workflow", wf_id, details={"error_code": "WORKFLOW_NOT_FOUND"})
        table.remove(Workflow.id == wf_id)"""
del_wf_new = """        if not await repository.get_workflow_by_id(wf_id):
            raise ResourceNotFoundError("Workflow", wf_id, details={"error_code": "WORKFLOW_NOT_FOUND"})
        await repository.delete_workflow(wf_id)"""
content = content.replace(del_wf_old, del_wf_new)

# 9. validate_flow
content = content.replace('async def validate_flow(\n    workflow: WorkflowConfigCreate, db: DatabaseDep, registry: RegistryDep\n) -> ValidationReportResponse:', 'async def validate_flow(\n    workflow: WorkflowConfigCreate, repository: RepositoryDep, registry: RegistryDep\n) -> ValidationReportResponse:')
content = content.replace('all_steps_config = db.table("steps").all()', 'all_steps_config = await repository.get_all_steps()')


with open("backend/api/routes/config/workflows.py", "w", encoding="utf-8") as f:
    f.write(content)
