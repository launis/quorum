import asyncio
import os
from backend_v2.services.blueprint import BlueprintTransformer
from backend_v2.db.repositories.execution_repo import ExecutionRepository
from backend_v2.db.repositories.system_repo import SystemRepository
from backend_v2.db.session import async_session_maker
from backend_v2.services.pdf_generator import render_template

async def main():
    async with async_session_maker() as session:
        exec_repo = ExecutionRepository(session)
        sys_repo = SystemRepository(session)
        execution = await exec_repo.get_execution("exe_6b288e6a8e0e4af2ade5d5552b3ea7ab")
        blueprint = BlueprintTransformer(exec_repo, sys_repo)
        report_dto = await blueprint.build_report_data(execution.id, "prf_5d6e7f8091a2b3c4", "fi", None, None)
        
        # Test if preface_md is in inner_sdui_blocks
        print(f"Number of inner blocks: {len(report_dto.inner_sdui_blocks)}")
        if report_dto.inner_sdui_blocks:
            print(f"First block type: {report_dto.inner_sdui_blocks[0].block_type}")
            print(f"First block text: {getattr(report_dto.inner_sdui_blocks[0], 'text', 'No text')}")
        
        html = await render_template(
            "report_template.jinja2",
            report_data=report_dto,
            lang_code="fi"
        )
        if "Raportti tekoälytaidoistasi" in html:
            print("FOUND IN HTML!")
        else:
            print("NOT FOUND IN HTML!")
            
if __name__ == "__main__":
    asyncio.run(main())
