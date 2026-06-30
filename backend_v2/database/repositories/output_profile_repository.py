"""Repository for OutputProfile."""

from backend_v2.database.repositories.base import BaseRepository
from backend_v2.models.domain.output_profile import OutputProfile


class OutputProfileRepository(BaseRepository):
    """Repository for managing Output Profiles."""

    async def get_profile(self, profile_id: str) -> OutputProfile | None:
        """Fetch an output profile by ID.

        Args:
            profile_id: The ID of the profile.

        Returns:
            The OutputProfile model or None if not found.
        """
        data = await self.driver.get("output_profiles", profile_id)
        if not data:
            return None

        return OutputProfile.model_validate(data, strict=False)

    async def save_profile(self, profile: OutputProfile) -> None:
        """Save an output profile to the database.

        Args:
            profile: The profile to save.
        """
        await self.driver.upsert("output_profiles", profile.model_dump(mode="json", exclude_none=True), profile.id)
