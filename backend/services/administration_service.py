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

    def export_seed_data(self, tracker: ProgressTracker) -> dict[str, Any]:
        """Exports the current database configuration to 'seed_data.json'.

        Used for persisting changes made in the UI back to source control.

        Args:
            tracker (ProgressTracker): Tracker for background task progress.

        Returns:
            Dict[str, Any]: Status and result message.

        """
        from backend.database.exporter import export_db_to_files

        tracker.start({"operation": "Export Seed Data"})
        try:
            # Use the exporter module
            tracker.update("Exporting Workflows & components...", 10)
            # By default uses settings.start_db_path which is correct for current env
            result = export_db_to_files()
            tracker.update("Export Completed", 100)

            final_res = {"status": "completed", "message": result.get("message", "Export done")}
            tracker.complete(final_res)
            return final_res
        except Exception as e:
            tracker.fail(str(e))
            raise e from e

    def rebuild_database(self, tracker: ProgressTracker) -> dict[str, Any]:
        """Rebuilds the database using 'seed_data.json'.

        Wipes existing data and re-seeds from the JSON source.

        Args:
            tracker (ProgressTracker): Tracker for background task progress.

        Returns:
            Dict[str, Any]: Status and result message.

        """
        from backend.seed.seeder import seed_database

        tracker.start({"operation": "Rebuild Database"})
        try:
            # Use the seeder internally. It will use the configured DB path from backend.config.
            # This ensures we respect the current environment (Mock vs Prod).
            tracker.update("Seeding Database", 10)
            seed_database()
            tracker.update("Seeding Completed", 100)

            result = {"status": "completed", "message": "Database rebuilt from seed_data.json"}
            tracker.complete(result)
            return result
        except Exception as e:
            tracker.fail(str(e))
            raise e from e

    def reset_mock_db(self, tracker: ProgressTracker) -> dict[str, Any]:
        """Resets the Mock database via external script.

        Args:
            tracker (ProgressTracker): Progress tracker.

        Returns:
            dict[str, Any]: Operation result.
        """
        return self._run_external_reset(tracker, "rebuild_mock_db.py", "Mock Database Reset")

    def reset_prod_db(self, tracker: ProgressTracker) -> dict[str, Any]:
        """Resets the Prod (TinyDB) database via external script.

        Args:
            tracker (ProgressTracker): Progress tracker.

        Returns:
            dict[str, Any]: Operation result.
        """
        return self._run_external_reset(tracker, "rebuild_prod_db.py", "Prod Database Reset")

    def reset_firestore(self, tracker: ProgressTracker) -> dict[str, Any]:
        """Resets the Firestore database via external script.

        Args:
            tracker (ProgressTracker): Progress tracker.

        Returns:
            dict[str, Any]: Operation result.
        """
        return self._run_external_reset(tracker, "seed_firestore.py", "Firestore Reset")

    def _run_external_reset(self, tracker: ProgressTracker, script_name: str, op_name: str) -> dict[str, Any]:
        import subprocess
        import sys

        from backend.settings import get_settings

        tracker.start({"operation": op_name})
        try:
            settings = get_settings()
            script_path = os.path.join(settings.scripts_dir, script_name)

            if not os.path.exists(script_path):
                # Fallback: try relative path from root if scripts_dir not set correctly or script moved
                script_path = os.path.join(os.getcwd(), "scripts", script_name)

            tracker.update(f"Running {script_name}...", 20)

            # Run subproces
            cmd = [sys.executable, script_path]
            # Ensure we run from project root so imports work
            cwd = settings.root_dir if hasattr(settings, "root_dir") else os.getcwd()

            result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)

            if result.returncode != 0:
                raise Exception(f"Script failed (Exit {result.returncode}): {result.stderr}")

            tracker.update("Completed", 100)
            return {"status": "completed", "message": f"{op_name} Successful", "output": result.stdout[:500]}

        except Exception as e:
            tracker.fail(str(e))
            raise e from e
