"""Administration Service for backend management."""

import os
from typing import Any

from backend.database.repository import AbstractWorkflowRepository
from backend.services.progress import ProgressTracker


class AdministrationService:
    """Coordinates administrative tasks like database exporting and rebuilding."""

    def __init__(self, repository: AbstractWorkflowRepository):
        """Initializes the service with a repository instance.

        Args:
            repository (AbstractWorkflowRepository): The data access layer.

        """
        self.repository = repository

    async def export_seed_data(self, tracker: ProgressTracker) -> dict[str, Any]:
        """Exports the current database configuration to 'seed_data.json'.

        Used for persisting changes made in the UI back to source control.

        Args:
            tracker (ProgressTracker): Tracker for background task progress.

        Returns:
            Dict[str, Any]: Status and result message.

        """
        from backend.database.exporter import export_db_to_files

        await tracker.start({"operation": "Export Seed Data"})
        try:
            # Use the exporter module
            await tracker.update("Exporting Workflows & components...", 10)
            # By default uses settings.start_db_path which is correct for current env
            result = export_db_to_files()
            await tracker.update("Export Completed", 100)

            final_res = {"status": "completed", "message": result.get("message", "Export done")}
            await tracker.complete(final_res)
            return final_res
        except Exception as e:
            await tracker.fail(str(e))
            raise e from e

    async def rebuild_database(self, tracker: ProgressTracker) -> dict[str, Any]:
        """Rebuilds the database using 'seed_data.json'.

        Wipes existing data and re-seeds from the JSON source.

        Args:
            tracker (ProgressTracker): Tracker for background task progress.

        Returns:
            Dict[str, Any]: Status and result message.

        """
        from backend.seed.seeder import seed_database

        await tracker.start({"operation": "Rebuild Database"})
        try:
            # Use the seeder internally. It will use the configured DB path from backend.config.
            # This ensures we respect the current environment (Mock vs Prod).
            await tracker.update("Seeding Database", 10)
            seed_database()
            await tracker.update("Seeding Completed", 100)

            result = {"status": "completed", "message": "Database rebuilt from seed_data.json"}
            await tracker.complete(result)
            return result
        except Exception as e:
            await tracker.fail(str(e))
            raise e from e

    async def reset_mock_db(self, tracker: ProgressTracker) -> dict[str, Any]:
        """Resets the Mock database via external script.

        Args:
            tracker (ProgressTracker): Progress tracker.

        Returns:
            dict[str, Any]: Operation result.
        """
        return await self._run_external_reset(tracker, "rebuild_mock_db.py", "Mock Database Reset")

    async def reset_prod_db(self, tracker: ProgressTracker) -> dict[str, Any]:
        """Resets the Prod (TinyDB) database via external script.

        Args:
            tracker (ProgressTracker): Progress tracker.

        Returns:
            dict[str, Any]: Operation result.
        """
        return await self._run_external_reset(tracker, "rebuild_prod_db.py", "Prod Database Reset")

    async def reset_firestore(self, tracker: ProgressTracker) -> dict[str, Any]:
        """Resets the Firestore database via external script.

        Args:
            tracker (ProgressTracker): Progress tracker.

        Returns:
            dict[str, Any]: Operation result.
        """
        return await self._run_external_reset(tracker, "seed_firestore.py", "Firestore Reset")

    async def _run_external_reset(self, tracker: ProgressTracker, script_name: str, op_name: str) -> dict[str, Any]:
        import subprocess
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

            # Run subproces
            cmd = [sys.executable, script_path]
            # Ensure we run from project root so imports work
            cwd = settings.root_dir if hasattr(settings, "root_dir") else os.getcwd()

            # Using run_in_executor to avoid blocking event loop would be better, but sticking to subprocess.run for now
            # as it was sync. But since we are async def, we block the loop.
            # Strictly speaking we should offload this. But for now, fixing Mypy.
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)

            if result.returncode != 0:
                raise Exception(f"Script failed (Exit {result.returncode}): {result.stderr}")

            await tracker.update("Completed", 100)
            return {"status": "completed", "message": f"{op_name} Successful", "output": result.stdout[:500]}

        except Exception as e:
            await tracker.fail(str(e))
            raise e from e
