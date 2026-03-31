import asyncio
from pathlib import Path

from pydantic import BaseModel, ConfigDict
from unittest.mock import patch, AsyncMock

# V2: pymupdf4llm is used in production via InputProcessingHook
import pymupdf4llm 
from backend_v2.models.v2_core import ExpectedInput
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler
from backend_v2.services.chat_parser import ChatParserService
from backend_v2.llm.client import LLMClient

from dotenv import load_dotenv
load_dotenv()

class DummyConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    model_name: str = "vertex_ai/gemini-2.5-flash"
    provider: str = "vertex_ai"
    temperature: float = 0.0
    default_max_tokens: int = 15000
    is_active: bool = True
    tpm_limit: int = 4000000
    rpm_limit: int = 5
    supports_grounding: bool = False
    api_key: str | None = None

async def mock_from_strategy(*args, **kwargs):
    return LLMClient(config=DummyConfig())


async def run_demo() -> None:
    print("🚀 [1/3] Luetaan Sitra-tiedostot docs\\datat -kansiosta...")
    doc_dir = Path("docs/datat")
    reflektio_file = doc_dir / "Reflektiodokumentti sitra.pdf"
    chat_file = doc_dir / "keskusteluhistoria SITRA.pdf"

    if not reflektio_file.exists() or not chat_file.exists():
        print("❌ Virhe: Sitran PDF-tiedostoja ei löydy polusta:", doc_dir.absolute())
        return

    print("🧩 [2/3] Ajetaan The Eager Extraction (Pymupdf4llm)...")
    
    # 1. Normaalidokumentti
    md_reflektio = pymupdf4llm.to_markdown(str(reflektio_file.absolute()))
    
    # 2. Chat Log -dokumentin raaka teksti PyMuPDFllä 
    # (Tuotannossa InputProcessingHook ajaa tämän ChatParserServicen läpi The English-Only Mandaten kera)
    md_chat_raw = pymupdf4llm.to_markdown(str(chat_file.absolute()))
    
    # Otetaan demonstraation vuoksi vain rajallinen osa chatista, koska koko PDF maksaa turhaan rahaa.
    md_chat_truncated = md_chat_raw[:5000]

    print("🤖 [3/4] Ajetaan ChatParserService LLM-siistiminen (gemini-2.5-flash)...")
    # Mockataan from_strategy hakemaan meidän lokaali konfiguraatio tietokannan sijaan.
    with patch('backend_v2.services.chat_parser.LLMClient.from_strategy', side_effect=mock_from_strategy):
        parser = ChatParserService()
        try:
            chat_dto = await parser.parse_pasted_chat(md_chat_truncated, repository=None)
            
            # Formatoidaan DTO -> puhdas Markdown
            formatted_lines = []
            for turn in chat_dto.conversation:
                role = getattr(turn, 'role', 'Unknown')
                text = getattr(turn, 'content', '')
                formatted_lines.append(f"**{role}**: {text}")
            
            md_chat = "\n\n".join(formatted_lines) + "\n\n... [TRUNCATED FOR DEMO] ..."
        except Exception as e:
            print("❌ ChatParser epäonnistui (Tarkista .env OPENAI_API_KEY):", str(e))
            return

    # Kuvitteellinen Step-malli The English-Only Mandate -toteutuksella ja Pydantic Strict-täydennyksillä!
    expected_inputs = [
        ExpectedInput.model_validate({
            "input_key": "reflektio", 
            "required": True,
            "description": {"translations": {"en": "desc"}, "default_locale": "en"},
            "ai_description": "[STRICT: ENGLISH ONLY] Analyze the structural logic of the user's explicit written reflections.", 
            "input_modes": ["file"],
            "is_chat_history": False,
            "label": {"translations": {"en": "Reflection Document"}, "default_locale": "en"}
        }),
        ExpectedInput.model_validate({
            "input_key": "chat", 
            "required": True,
            "description": {"translations": {"en": "desc"}, "default_locale": "en"},
            "ai_description": "[STRICT: ENGLISH ONLY] Extract and structure the cognitive patterns exhibited by the user during interactive chat.", 
            "input_modes": ["file"],
            "is_chat_history": True,
            "label": {"translations": {"en": "Chat History"}, "default_locale": "en"}
        })
    ]

    print("🧠 [4/4] Kompiloidaan LLM-konteksti puskurista läpi PromptCompilerin...")
    compiler = PromptCompiler()
    
    processed_inputs = {
        "reflektio": md_reflektio,
        "chat": md_chat
    }

    mappings = {
        "TARGET_REFLECTION_DATA": "$inputs.reflektio",
        "TARGET_CHAT_DATA": "$inputs.chat"
    }
    
    prompt = compiler.build_xml_context(
        input_mappings=mappings,
        state_data={"inputs": processed_inputs}, 
        target_locale="fi",
        expected_inputs=expected_inputs
    )

    # Luodaan feikki-matriiseilla aito mallinnus arvioinnista
    criteria = [
        {
            "id": "matriisi_1",
            "type": "criteria",
            "title": {"translations": {"en": "Critical Analysis"}, "default_locale": "en"},
            "system_instruction": {"translations": {"en": "Evaluate the depth of critical thinking based on the provided rubric."}, "default_locale": "en"},
            "critical_directive": {"translations": {"en": "You MUST penalize superficial thinking."}, "default_locale": "en"},
            "matrix": [
                {"score": 1, "label": "Poor", "description": "Fails to meet basic standards.", "critical_directive": {"translations": {"en": "Immediate failure."}, "default_locale": "en"}},
                {"score": 5, "label": "Excellent", "description": "Mastery of critical thinking.", "critical_directive": {"translations": {"en": "Requires concrete evidence."}, "default_locale": "en"}}
            ]
        }
    ]

    print("🧩 [5/5] Luodaan The Universal Mandate System Prompt (Matriisit)...")
    system_prompt = compiler.compile_xml_rubrics(
        criteria=criteria,
        target_locale="en"
    )

    out_file = Path("demo_render_output.md")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("# Epic 12: LLM Prompt Context Demo\n\n")
        f.write("## 1. Järjestelmän Säännöt ja Matriisit (SYSTEM PROMPT)\n")
        f.write("Aito PromptCompiler XML tuotos arviointikriteereistä:\n\n---\n")
        f.write(system_prompt + "\n\n")
        
        f.write("## 2. Injektoidut Datalähteet (USER PROMPT)\n")
        f.write("Aito PromptCompiler XML tuotos asetetuilla The English-Only Mandate injektioilla:\n\n---\n")
        f.write(prompt)
    
    print(f"✅ VALMIS! Generoitu LLM Prompt tallennettiin: {out_file.absolute()}")


if __name__ == "__main__":
    asyncio.run(run_demo())
