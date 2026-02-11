"""Administration Service for backend management."""

import os

from backend.database.repository import AbstractWorkflowRepository
from backend.schemas.admin import AdminOperationResponse
from backend.services.progress import ProgressTracker


class AdministrationService:
    """Coordinates administrative tasks like database exporting and rebuilding."""

    def __init__(self, repository: AbstractWorkflowRepository):
        """Initializes the service with a repository instance.

        Args:
            repository (AbstractWorkflowRepository): The data access layer.

        """
        self.repository = repository

    async def export_seed_data(self, tracker: ProgressTracker) -> AdminOperationResponse:
        """Exports the current database configuration to 'seed_data.json'.

        Used for persisting changes made in the UI back to source control.

        Args:
            tracker (ProgressTracker): Tracker for background task progress.

        Returns:
            AdminOperationResponse: Status and result message.

        """
        from backend.database.exporter import export_db_to_files

        await tracker.start({"operation": "Export Seed Data"})
        try:
            # Use the exporter module
            await tracker.update("Exporting Workflows & components...", 10)
            # By default uses settings.start_db_path which is correct for current env
            result = export_db_to_files()
            await tracker.update("Export Completed", 100)

            final_res = AdminOperationResponse(status="completed", message=result.get("message", "Export done"))
            await tracker.complete(final_res.model_dump())
            return final_res
        except Exception as e:
            await tracker.fail(str(e))
            raise e from e

    async def rebuild_database(self, tracker: ProgressTracker) -> AdminOperationResponse:
        """Rebuilds the database using 'seed_data.json'.

        Wipes existing data and re-seeds from the JSON source.

        Args:
            tracker (ProgressTracker): Tracker for background task progress.

        Returns:
            AdminOperationResponse: Status and result message.

        """
        from backend.seed.seeder import seed_database

        await tracker.start({"operation": "Rebuild Database"})
        try:
            # Use the seeder internally. It will use the configured DB path from backend.config.
            # This ensures we respect the current environment (Mock vs Prod).
            await tracker.update("Seeding Database", 10)
            seed_database()
            await tracker.update("Seeding Completed", 100)

            from backend.services.localization import LocalizationService
            result = AdminOperationResponse(status="completed", message=LocalizationService.translate("DB_REBUILT"))
            await tracker.complete(result.model_dump())
            return result
        except Exception as e:
            await tracker.fail(str(e))
            raise e from e

    async def reset_mock_db(self, tracker: ProgressTracker) -> AdminOperationResponse:
        """Resets the Mock database via external script.

        Args:
            tracker (ProgressTracker): Progress tracker.

        Returns:
            AdminOperationResponse: Operation result.
        """
        return await self._run_external_reset(tracker, "rebuild_mock_db.py", "Mock Database Reset")

    async def reset_prod_db(self, tracker: ProgressTracker) -> AdminOperationResponse:
        """Resets the Prod (TinyDB) database via external script.

        Args:
            tracker (ProgressTracker): Progress tracker.

        Returns:
            AdminOperationResponse: Operation result.
        """
        return await self._run_external_reset(tracker, "rebuild_prod_db.py", "Prod Database Reset")

    async def reset_firestore(self, tracker: ProgressTracker) -> AdminOperationResponse:
        """Resets the Firestore database via external script.

        Args:
            tracker (ProgressTracker): Progress tracker.

        Returns:
            AdminOperationResponse: Operation result.
        """
        return await self._run_external_reset(tracker, "seed_firestore.py", "Firestore Reset")

    async def _run_external_reset(
        self, tracker: ProgressTracker, script_name: str, op_name: str
    ) -> AdminOperationResponse:
        import asyncio
        import sys

        from backend.settings import get_settings

        await tracker.start({"operation": op_name})
        try:
            settings = get_settings()
            script_path = os.path.join(settings.scripts_dir, script_name)

            if not os.path.exists(script_path):
                # Fallback: try relative path from root if scripts_dir not set correctly or script moved
                script_path = os.path.join(os.getcwd(), "scripts", script_name)

            await tracker.update(f"Running {script_name}...", 20)

            # Run subprocess asynchronously
            # Ensure we run from project root so imports work
            cwd = settings.root_dir if hasattr(settings, "root_dir") else os.getcwd()

            # Using asyncio.create_subprocess_exec for non-blocking execution
            process = await asyncio.create_subprocess_exec(
                sys.executable, script_path, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=cwd
            )

            # Wait for completion
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode().strip()
                raise Exception(f"Script failed (Exit {process.returncode}): {error_msg}")

            await tracker.update("Completed", 100)
            return AdminOperationResponse(
                status="completed", message=f"{op_name} Successful", output=stdout.decode()[:500]
            )

        except Exception as e:
            await tracker.fail(str(e))
            raise e from e
