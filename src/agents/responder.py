"""
Response Generator (LLM-based).

Maps the signal produced by the Discovery agent to one of four
simplified response archetypes, then uses the configured LLM client
(e.g., Ollama, Claude) to build a contextual, natural reply.

Archetypes (from Project.md):
  1. data_drop        – share a specific metric or data point
  2. pattern_spotter  – highlight a trend or correlation
  3. question_answer  – directly answer a question about analytics
  4. polite_correction – gently correct a misconception or suggest a better tool
"""

import logging
from src.agents.llm_client import get_llm_client
from src.prompts import RESPONDER_SYSTEM_PROMPT

logger = logging.getLogger("responder")
llm = get_llm_client()

def _pick_archetype(signal: dict) -> str:
    """
    Choose the best-fit archetype based on signal characteristics.

    Rules (evaluated in priority order):
      1. If the user asks a question → question_answer
      2. If a competitor is mentioned → polite_correction
      3. If multiple keyword categories hit → pattern_spotter
      4. Default → data_drop
    """
    if signal["is_question"]:
        return "question_answer"

    if "competitor_mentions" in signal["categories"]:
        return "polite_correction"

    if len(signal["categories"]) > 1:
        return "pattern_spotter"

    return "data_drop"


async def generate_reply(signal: dict) -> str:
    """
    Generate an LLM-based reply string for the given signal,
    injecting the chosen archetype into the prompt context.
    """
    archetype = _pick_archetype(signal)
    
    # Prepare context for the LLM
    keywords_list = [m["keyword"] for m in signal["keywords"]]
    user_prompt = f"""[Target Message Context]
Author: {signal['author']}
Message: "{signal['text']}"
Matched Keywords: {keywords_list}
Desired Strategy (Archetype): {archetype}

Please generate the reply message (just the raw response text) adhering to the system rules and matching the desired strategy."""

    logger.info("Archetype=%s for message by %s (score=%d). Requesting LLM generation...",
                archetype, signal["author"], signal["score"])
                
    reply = await llm.generate_response(RESPONDER_SYSTEM_PROMPT, user_prompt)
    return reply
