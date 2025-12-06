from typing import Optional, List, Dict, Any, Literal, Union
from pydantic import BaseModel, Field
from datetime import datetime
from backend.schemas import (
    TaintedData, 
    TodistusKartta, 
    ArgumentaatioAnalyysi,
    LogiikkaAuditointi, 
    KausaalinenAuditointi,
    PerformatiivisuusAuditointi, 
    EtiikkaJaFakta,
    TuomioJaPisteet, 
    XAIReport
)

class InputData(BaseModel):
    """Raakadata, joka tulee käyttäjältä."""
    history_text: str
    product_text: str
    reflection_text: str
    # Optional bibliography context
    bibliography_context: Optional[List[str]] = None

class WorkflowState(BaseModel):
    """
    Tämä on "Blackboard". Se elää muistissa koko ajon ajan.
    Kaikki agentit lukevat tästä ja kirjoittavat tähän.
    """
    # Metadata
    execution_id: str
    start_time: datetime = Field(default_factory=datetime.now)
    current_step_name: str = "init"
    
    # Syötteet (Read-only agenteille)
    inputs: InputData
    
    # Agenttien tulosteet (Alussa None, täyttyvät matkan varrella)
    step_1_guard: Optional[TaintedData] = None
    step_2_analyst: Optional[TodistusKartta] = None
    step_3_logician: Optional[ArgumentaatioAnalyysi] = None
    step_4_falsifier: Optional[LogiikkaAuditointi] = None
    step_5_overseer: Optional[EtiikkaJaFakta] = None
    step_6_causal: Optional[KausaalinenAuditointi] = None
    step_7_detector: Optional[PerformatiivisuusAuditointi] = None
    step_8_judge: Optional[TuomioJaPisteet] = None
    step_9_reporter: Optional[XAIReport] = None

    # Formatted output
    xai_report_formatted: Optional[str] = None

    # Apumuuttujat (esim. hakutulokset, jotka eivät ole skeemassa)
    aux_data: Dict[str, Any] = Field(default_factory=dict)
