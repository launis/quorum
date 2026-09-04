"""Unit tests for StudioLexiconService."""

from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.exceptions import PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import SystemOrganizations, TokenData, UserRole
from backend_v2.models.enums import SystemConfigID
from backend_v2.models.v2_core import (
    LexiconConfigPayload,
    LexiconSuggestionListDTO,
    SystemConfigPerformativeLexicons,
)
from backend_v2.services.studio.lexicon_service import StudioLexiconService
from backend_v2.tests.fakes.in_memory_repositories import InMemorySystemRepository


@pytest.fixture
def mock_system_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def lexicon_service(mock_system_repo: AsyncMock) -> StudioLexiconService:
    return StudioLexiconService(system_repo=mock_system_repo)


@pytest.fixture
def admin_token() -> TokenData:
    return TokenData(
        id="usr_admin",
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        email="admin@example.com",
        role=UserRole.ADMIN,
    )


@pytest.mark.asyncio
async def test_get_performative_lexicons_config_success(
    lexicon_service: StudioLexiconService, mock_system_repo: AsyncMock
) -> None:
    mock_system_repo.get_system_config.return_value = SystemConfigPerformativeLexicons(
        id=SystemConfigID.PERFORMATIVE_LEXICONS.value,
        lexicon_configs={
            "en": LexiconConfigPayload(language_code="en", language_name="English", words=["synergy", "delve"]),
            "fi": LexiconConfigPayload(language_code="fi", language_name="Finnish", words=["synergia"]),
        },
    )
    result = await lexicon_service.get_performative_lexicons_config()
    assert result.id == SystemConfigID.PERFORMATIVE_LEXICONS.value
    assert "en" in result.lexicon_configs
    assert result.lexicon_configs["en"].words == ["synergy", "delve"]


@pytest.mark.asyncio
async def test_get_performative_lexicons_config_not_found(
    lexicon_service: StudioLexiconService, mock_system_repo: AsyncMock
) -> None:
    mock_system_repo.get_system_config.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await lexicon_service.get_performative_lexicons_config()


@pytest.mark.asyncio
async def test_save_performative_lexicons_config(
    lexicon_service: StudioLexiconService,
    mock_system_repo: AsyncMock,
    admin_token: TokenData,
) -> None:
    config = SystemConfigPerformativeLexicons(
        id=SystemConfigID.PERFORMATIVE_LEXICONS.value,
        lexicon_configs={
            "en": LexiconConfigPayload(language_code="en", language_name="English", words=["pivot"]),
        },
    )
    mock_system_repo.get_system_config.return_value = config
    saved = await lexicon_service.save_performative_lexicons_config(admin_token, config)
    assert saved.lexicon_configs["en"].words == ["pivot"]
    mock_system_repo.update_performative_lexicons.assert_called_once_with(config)


@pytest.mark.asyncio
async def test_discover_new_performative_phrases(
    lexicon_service: StudioLexiconService,
) -> None:
    expected = LexiconSuggestionListDTO(suggested_phrases=["unprecedented trajectory", "game changer"])
    with patch("backend_v2.services.studio.lexicon_service.LLMTaskExecutor.execute_structured_task") as mock_exec:
        mock_exec.return_value = (expected, None)
        with patch("backend_v2.services.studio.lexicon_service.LLMClient.from_strategy") as mock_client:
            mock_client.return_value = AsyncMock()
            result = await lexicon_service.discover_new_performative_phrases("en")
            assert result.suggested_phrases == ["unprecedented trajectory", "game changer"]


@pytest.mark.asyncio
async def test_translate_performative_phrases_empty_en(
    lexicon_service: StudioLexiconService, mock_system_repo: AsyncMock
) -> None:
    mock_system_repo.get_system_config.return_value = None
    result = await lexicon_service.translate_performative_phrases("fi")
    assert result.suggested_phrases == []


@pytest.mark.asyncio
async def test_translate_performative_phrases_with_en_lexicon(
    lexicon_service: StudioLexiconService, mock_system_repo: AsyncMock
) -> None:
    config = SystemConfigPerformativeLexicons(
        id=SystemConfigID.PERFORMATIVE_LEXICONS.value,
        lexicon_configs={
            "en": LexiconConfigPayload(language_code="en", language_name="English", words=["synergy", "pivot"]),
        },
    )
    mock_system_repo.get_system_config.return_value = config
    expected = LexiconSuggestionListDTO(suggested_phrases=["synergia", "suunnanmuutos"])

    with patch("backend_v2.services.studio.lexicon_service.LLMTaskExecutor.execute_structured_task") as mock_exec:
        mock_exec.return_value = (expected, None)
        with patch("backend_v2.services.studio.lexicon_service.LLMClient.from_strategy") as mock_client:
            mock_client.return_value = AsyncMock()
            result = await lexicon_service.translate_performative_phrases("fi")
            assert result.suggested_phrases == ["synergia", "suunnanmuutos"]


@pytest.mark.asyncio
async def test_in_memory_save_performative_lexicons_roundtrip(admin_token: TokenData) -> None:
    """Tests saving performative lexicons using InMemorySystemRepository."""
    system_repo = InMemorySystemRepository()
    service = StudioLexiconService(system_repo=system_repo)

    config_id = SystemConfigID.PERFORMATIVE_LEXICONS.value
    initial_config = SystemConfigPerformativeLexicons(
        id=config_id,
        lexicon_configs={
            "en": LexiconConfigPayload(language_code="en", language_name="English", words=["buzzword"]),
        },
    )
    await system_repo.update_performative_lexicons(initial_config)

    updated_config = initial_config.model_copy(
        update={
            "lexicon_configs": {
                "en": LexiconConfigPayload(
                    language_code="en",
                    language_name="English",
                    words=["buzzword", "synergy", "paradigm shift"],
                )
            }
        }
    )

    saved = await service.save_performative_lexicons_config(admin_token, updated_config)
    assert saved.id == config_id
    assert len(saved.lexicon_configs["en"].words) == 3

    fetched = await service.get_performative_lexicons_config()
    assert fetched.id == config_id
    assert len(fetched.lexicon_configs["en"].words) == 3

    # Assert zero "cfg_performative_lexicons" documents exist
    legacy_doc = await system_repo.get_system_config("cfg_performative_lexicons")
    assert legacy_doc is None


@pytest.mark.asyncio
async def test_save_performative_lexicons_unauthorized_token_raises_permission_denied() -> None:
    """Tests that non-system token cannot save performative lexicons."""
    system_repo = InMemorySystemRepository()
    service = StudioLexiconService(system_repo=system_repo)
    unauthorized_token = TokenData(
        id="usr_normal111111111",
        organization_id="org_tenant_1",
        email="user@example.com",
        role=UserRole.MEMBER,
    )
    config = SystemConfigPerformativeLexicons(
        id=SystemConfigID.PERFORMATIVE_LEXICONS.value,
        lexicon_configs={},
    )
    with pytest.raises(PermissionDeniedError):
        await service.save_performative_lexicons_config(unauthorized_token, config)
