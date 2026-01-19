import asyncio
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.hooks.reporting import generate_report
from backend.models.domain import (
    AitousEpaily,
    CoachingPlan,
    EettinenHavainto,
    EtiikkaJaFakta,
    MestaruusPoikkeama,
    Pisteet,
    PisteetKriteeri,
    TuomioJaPisteet,
    XAIReport,
)
from backend.models.state import InputData, WorkflowState

# Mock class removed as CoachingPlan now supports V2 fields.


def get_base_fields():
    return {
        "metadata": {"luontiaika": "2026-01-15T12:00:00Z", "agentti": "TestAgent", "vaihe": 1, "versio": "2.0"},
        "metodologinen_loki": "Log",
        "edellisen_vaiheen_validointi": "Valid",
        "semanttinen_tarkistussumma": "Hash123",
    }


async def verify_report_generation():
    print("🚀 Starting V2 Report Verification...")

    base = get_base_fields()

    # 1. Create Mock State
    # Using standard initialization to verify Pydantic compliance.
    state = WorkflowState(
        execution_id="test_v2_verification",
        inputs=InputData(history_text="Test History", product_text="Test Product", reflection_text="Test Reflection"),
        step_xai=XAIReport(
            **base,
            executive_summary="Executive Summary Text",
            final_verdict="Active Driver",
            confidence_score=0.95,
            analysis_strengths="Strong logic.",
            analysis_weaknesses="None.",
            analysis_opportunities="Keep going.",
            analysis_recommendations="No changes.",
        ),
        step_results={
            "step_coach": CoachingPlan(
                **base,
                kannustava_palaute="Good job!",
                kehityskohteet_konkreettisesti=[],
                lopputuloksen_kehitysehdotukset=[],
                lahdeluettelo=[],
                # V2 Fields - Now Supported!
                analyysi_haasteista="User needs more structure (V2 Style).",
                toimenpiteet=["Use TOULMIN model", "Define clear goals"],
                motivaatio="Better logic leads to better results.",
            ),
            "step_judge": TuomioJaPisteet(
                **base,
                konfliktin_ratkaisut=[],
                mestaruus_poikkeama=MestaruusPoikkeama(tunnistettu=False, perustelu=""),
                aitous_epaily=AitousEpaily(automaattinen_lippu=False, viesti_hitl_lle=""),
                pisteet=Pisteet(analyysi=PisteetKriteeri(arvosana=3, perustelu="Good")),
                kriittiset_havainnot_yhteenveto=[],
            ),
            "step_overseer": EtiikkaJaFakta(
                **base,
                eettiset_havainnot=[
                    EettinenHavainto(tyyppi="Haitallinen sisältö", vakavuus="Varoitus", kuvaus="Minor bias detected.")
                ],
                faktantarkistus_rfi=[],
            ),
        }
    )

    # 2. Run Reporting Hook
    try:
        updated_state = generate_report(state)
        report_md = updated_state.xai_report_formatted

        print("\n✅ Report Generated Successfully!")
        print("-" * 40)
        # print(report_md)
        print("-" * 40)

        # 3. Verify Key Sections
        checks = {
            "Coaching Plan Header": "## 3b. Valmennussuunnitelma (Coaching Plan)" in report_md,
            "Generic Coaching Header": "Valmennussuunnitelma" in report_md,
            "Coaching Content": "User needs more structure (V2 Style)." in report_md,
            "Ethical Issues Header": "## 4. Eettiset Havainnot" in report_md,
            "Ethical Content": "Minor bias detected." in report_md,
        }

        all_passed = True
        for name, passed in checks.items():
            status = "PASS" if passed else "FAIL"
            print(f"[{status}] {name}")
            if not passed:
                all_passed = False

        print("\n--- FULL REPORT MARKDOWN ---")
        # Write to file to bypass terminal issues
        with open("report_debug.md", "w", encoding="utf-8") as f:
            f.write(report_md)
        print("Report written to report_debug.md")
        print("----------------------------")

        if all_passed:
            print("\n🎉 ALL CHECKS PASSED. V2 Report logic is working (Data-Layer Mismatch Noted).")
        else:
            print("\n❌ SOME CHECKS FAILED.")

    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        if hasattr(e, "json"):
            print(e.json())
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    import asyncio

    asyncio.run(verify_report_generation())
