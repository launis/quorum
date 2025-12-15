from typing import Any, Optional, Type, Dict
from backend.agents.base import BaseAgent
from backend.models.state import WorkflowState
from pydantic import BaseModel, Field
import logging
import re

logger = logging.getLogger(__name__)

class TextMetrics(BaseModel):
    word_count: int = Field(..., description="Total number of words")
    sentence_count: int = Field(..., description="Total number of sentences")
    avg_sentence_length: float = Field(..., description="Average words per sentence")
    lexical_diversity: float = Field(..., description="Unique words divided by total words (0-1)")
    capitalization_ratio: float = Field(..., description="Ratio of uppercase letters to total letters")

class ProfilerAnalysis(BaseModel):
    """
    Schema for the Profiler (Psychologist) Agent.
    Analyzes intent, tone, and biases.
    """
    intentio_analyysi: str = Field(..., description="Analysis of the writer's hidden intent/motive")
    tunnetila_ja_savy: str = Field(..., description="Analysis of emotional state and tone")
    tunnistetut_vinoumat: list[str] = Field(..., description="List of detected cognitive biases")
    psykologinen_profiili: str = Field(..., description="Summary of the writer's psychological profile")
    manipulaatio_yritykset: str = Field(..., description="Detection of any manipulation or sarcasm")
    
    # Python-calculated metrics injected here for the LLM to review/explain
    teksti_metriikka: Optional[Dict[str, Any]] = Field(None, description="Objective metrics calculated by Python hook")

class ProfilerAgent(BaseAgent):
    """
    Profiloija (Psychologist) Agent.
    Step 2.5: Analyzes the 'human' side of the input: intent, biases, tone.
    """

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return ProfilerAnalysis
        
    def get_user_prompt_template(self) -> str:
        return "Analyze the following text for intent, tone, and cognitive biases."

    def _update_state(self, state: WorkflowState, response_data: Any) -> WorkflowState:
        # We can store this in a new field in WorkflowState (needs to be added dynamically or uses aux_data if strict checking)
        # Assuming we will update WorkflowState model or use 'aux_data' for now to avoid breaking Pydantic models immediately.
        # But 'ProfilerAnalysis' is a nice structured object.
        # Let's attach it to 'aux_data' first, or we can add 'step_profiler' to State. 
        # For now, let's use aux_data to be safe without refactoring State model yet, 
        # OR we can assume dynamic attribute assignment works if we allow it.
        # SAFE BET: aux_data['profiler_analysis']
        
        # However, to be a "First Class Citizen", we'd ideally want state.step_profiler.
        # Since I cannot easily change `backend/models/state.py` without seeing it and potentially breaking things,
        # I will store it in `aux_data` AND try to set it as an attribute if possible.
        
        analysis = ProfilerAnalysis(**response_data)
        state.aux_data['step_profiler'] = analysis.model_dump()
        return state

    # --- PYTHON HOOKS ---

    def analyze_text_metrics(self, state: WorkflowState) -> WorkflowState:
        """
        PRE-HOOK: Calculates objective text metrics from the input history/product.
        Injects these into the system prompt context via aux_data, 
        so the LLM sees the hard numbers.
        """
        logger.info("[ProfilerAgent] Running analyze_text_metrics hook...")
        
        # 1. Get Text to Analyze
        text = state.inputs.history_text + "\n" + state.inputs.product_text
        if not text.strip():
            logger.warning("[ProfilerAgent] No text to analyze.")
            return state

        # 2. Calculate Metrics
        words = re.findall(r'\b\w+\b', text.lower())
        word_count = len(words)
        
        sentences = re.split(r'[.!?]+', text)
        sentences = [s for s in sentences if s.strip()]
        sentence_count = len(sentences)
        
        avg_sent_len = word_count / sentence_count if sentence_count > 0 else 0
        
        unique_words = set(words)
        lex_diversity = len(unique_words) / word_count if word_count > 0 else 0
        
        caps = sum(1 for c in text if c.isupper())
        total_chars = sum(1 for c in text if c.isalpha())
        cap_ratio = caps / total_chars if total_chars > 0 else 0
        
        metrics = TextMetrics(
            word_count=word_count,
            sentence_count=sentence_count,
            avg_sentence_length=round(avg_sent_len, 2),
            lexical_diversity=round(lex_diversity, 2),
            capitalization_ratio=round(cap_ratio, 2)
        )
        
        logger.info(f"[ProfilerAgent] Metrics calculated: {metrics}")
        
        # 3. Inject into State (aux_data)
        # The prompt template for Profiler will need to include {{PROFILER_METRICS}} or similar,
        # OR we rely on the Engine's variable injection if we conform to it.
        # For now, we store it in aux_data. 
        # To make the LLM see it, we might need a custom `construct_user_prompt` or 
        # ensure the prompt template uses {{PROFILER_METRICS}}.
        
        state.aux_data['profiler_metrics'] = metrics.model_dump()
        
        return state
        
    def get_user_prompt_template(self) -> str:
        # Override to show we use metrics
        return "Analyze the text. Metrics: {{PROFILER_METRICS}}"
