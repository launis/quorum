from typing import Any, Optional, Type
from backend.agents.base import BaseAgent
from backend.state import WorkflowState
from backend.schemas import XAIReport
from pydantic import BaseModel

class XAIReporterAgent(BaseAgent):
    """
    XAI-Raportoija-agentti (XAI Reporter Agent).
    """
    def construct_user_prompt(self, state: WorkflowState) -> str:
        # Reporter needs the final verdict and scores
        judge_output = state.step_8_judge.model_dump_json(indent=2) if state.step_8_judge else "N/A"
        
        # Get Example
        example_text = self.get_schema_example(XAIReport)

        return f"""
        TASK: Generate a human-readable report.

        {example_text}

        INPUT DATA (TUOMIO JA PISTEET):
        ---
        {judge_output}
        ---
        """

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return XAIReport

    def get_system_instruction(self) -> str:
        return """
        You are the XAI Reporter Agent. Your task is to generate the content for a structured report.
        
        CRITICAL INSTRUCTIONS FOR JSON FIELDS:
        1. 'executive_summary': A concise text summary of the audit. Do NOT use structural headers (like '##', '###' or 'Results'). Do NOT repeat the detailed scores list here (they are displayed separately).
        2. 'detailed_analysis': A list of sections analyzing the performance. 
           - Do NOT create a section called 'Pisteytys', 'Scores', 'Results', or 'Yhteenveto', as these are covered elsewhere.
           - Focus on qualitative analysis: Strengths, Weaknesses, Insights, and Recommendations.
        3. 'final_verdict': A short concluding statement.
        
        Output must be a valid JSON object matching the XAIReport schema. Do not output Markdown formatting for the *structure* of the report, only for the *content* (e.g., bolding specific words is okay).
        """

    def _update_state(self, state: WorkflowState, response_data: Any) -> WorkflowState:
        try:
            state.step_9_reporter = XAIReport(**response_data)
        except Exception as e:
            print(f"[XAIReporterAgent] State update failed: {e}")
            raise e
        return state

    def generate_jinja2_report(self, state: WorkflowState) -> WorkflowState:
        """
        Generates a formatted markdown report (interpreting 'jinja2' loosely as 'template rendering').
        Includes scores explicitly.
        """
        print("[XAIReporterAgent] Generating formatted report...")
        
        report = state.step_9_reporter
        judge = state.step_8_judge
        
        if not report:
            print("[XAIReporterAgent] No report data to format.")
            return state

        # Start building Markdown
        md = f"### XAI-Raportti: Kognitiivinen Auditointi\n\n"
        md += f"**Päiväys:** {state.start_time.strftime('%Y-%m-%d %H:%M')}\n\n"
        
        md += f"#### 1. Johdon Yhteenveto\n"
        # Clean potential headers from executive summary if LLM ignored instructions
        clean_summary = report.executive_summary.replace("##", "").replace("###", "")
        md += f"{clean_summary}\n\n"
        
        # Add Scores explicitly if available
        if judge and judge.pisteet:
            md += "#### 2. Pisteytys (BARS 1-4)\n"
            
            p = judge.pisteet
            
            # Helper to format score row
            def format_score(title, score_obj):
                if not score_obj: return ""
                stars = "★" * score_obj.arvosana + "☆" * (4 - score_obj.arvosana)
                return f"**{title}:** {score_obj.arvosana}/4 {stars}\n\n_{score_obj.perustelu}_\n\n"

            if p.analyysi_ja_prosessi:
                md += format_score("Analyysi ja Prosessin Tehokkuus", p.analyysi_ja_prosessi)
            if p.arviointi_ja_argumentaatio:
                md += format_score("Arviointi ja Argumentaatio", p.arviointi_ja_argumentaatio)
            if p.synteesi_ja_luovuus:
                md += format_score("Synteesi ja Luovuus", p.synteesi_ja_luovuus)
        
        md += f"#### 3. Yksityiskohtainen Analyysi (XAI)\n"
        for section in report.detailed_analysis:
            # Filter out redundant sections
            if any(x in section.title.lower() for x in ['piste', 'score', 'tulokset', 'results', 'verdict', 'tuomio']):
                continue
            
            md += f"**{section.title}**\n\n"
            md += f"{section.content}\n\n"
            if section.visualizations:
                md += "**Havainnollistukset:**\n"
                for v in section.visualizations:
                    md += f"- {v}\n"
                md += "\n"
        
        md += f"#### 4. Lopullinen Tuomio\n"
        md += f"**Tuomio:** {report.final_verdict}\n"
        md += f"**Luottamustaso:** {report.confidence_score}\n"
        
        # Save to state
        state.xai_report_formatted = md
        print("[XAIReporterAgent] Formatted report saved to state.")
        
        return state
