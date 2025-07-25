from __future__ import annotations as _annotations

from dataclasses import dataclass
from dotenv import load_dotenv
import logfire
import asyncio
import json
import os
import re
from typing import List, Dict, Any, Optional

from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.models.openai import OpenAIModel
from openai import AsyncOpenAI

load_dotenv()

llm = os.getenv('LLM_MODEL', 'gpt-4o-mini')
model = OpenAIModel(llm)

logfire.configure(send_to_logfire='if-token-present')

@dataclass
class ClinicAIDeps:
    knowledge_base: Dict[str, Any]
    openai_client: AsyncOpenAI

def load_system_prompt():
    """Load system prompt from external file."""
    try:
        with open('system_prompt.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print("⚠️  system_prompt.txt not found, using default prompt")
        return """
You are the official AI assistant for Hautlabor, the practice of Dr. med. Lara Pfahl in Oldenburg. 
Your primary source of truth for all information related to treatments, procedures, and the practice itself 
is the knowledge base provided in the context. Your core mission is to educate potential patients based on 
official information and guide them towards booking a personal consultation.

You have access to comprehensive information about:
- Dr. med. Lara Pfahl (Gynecologist specialized in minimally invasive aesthetic treatments)
- Over 30 different aesthetic treatments including:
  * Botox/Faltenrelaxan treatments
  * Dermal fillers (Hyaluron-Filler)
  * Laser treatments (CO2 Laser, LaseMD, Lumecca)
  * Radiofrequency treatments (Morpheus8, Ultherapy)
  * Body contouring (Sculptra, Radiesse, Lipolyse)
  * Skin treatments (HydraFacial, Skinbooster, Vampirlifting)
  * Hair removal and PRP therapy
  * Specialized treatments for men
  * Aesthetic gynecology

Always search the knowledge base first to find relevant information.
Provide detailed, accurate information about treatments, procedures, expected results, and aftercare.
Maintain a professional, knowledgeable tone while being helpful and informative.

If you cannot find specific information in the knowledge base, be honest about it and suggest contacting 
the clinic directly for a personal consultation.

Always respond in German using formal "Sie" address.
"""

def load_knowledge_base():
    """Load knowledge base from JSON file."""
    try:
        with open('combined_database_newest.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️  combined_database_newest.json not found")
        return {"treatments": [], "pages": []}
    except json.JSONDecodeError as e:
        print(f"⚠️  Error parsing JSON: {e}")
        return {"treatments": [], "pages": []}

system_prompt = load_system_prompt()

clinic_ai_expert = Agent(
    model,
    system_prompt=system_prompt,
    deps_type=ClinicAIDeps,
    retries=2
)

def search_treatments(knowledge_base: Dict[str, Any], query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Search treatments in the knowledge base based on query."""
    query_lower = query.lower()
    treatments = knowledge_base.get("treatments", [])
    results = []
    
    for treatment in treatments:
        score = 0
        
        # Check treatment name
        if query_lower in treatment.get("treatment_name", "").lower():
            score += 10
            
        # Check category
        if query_lower in treatment.get("category", "").lower():
            score += 5
            
        # Check tags
        for tag in treatment.get("tags", []):
            if query_lower in tag.lower():
                score += 3
                
        # Check content description
        content = treatment.get("content", {})
        if isinstance(content, dict):
            description = content.get("description", "")
            if query_lower in description.lower():
                score += 2
                
            # Check mechanism
            mechanism = content.get("mechanism", "")
            if query_lower in mechanism.lower():
                score += 2
                
            # Check FAQs
            faqs = content.get("faq", []) or content.get("faqs", [])
            for faq in faqs:
                if isinstance(faq, dict):
                    question = faq.get("question", "")
                    answer = faq.get("answer", "")
                    if query_lower in question.lower() or query_lower in answer.lower():
                        score += 1
        
        if score > 0:
            results.append((score, treatment))
    
    # Sort by score and return top results
    results.sort(key=lambda x: x[0], reverse=True)
    return [treatment for score, treatment in results[:max_results]]

def search_pages(knowledge_base: Dict[str, Any], query: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """Search pages in the knowledge base based on query."""
    query_lower = query.lower()
    pages = knowledge_base.get("pages", [])
    results = []
    
    for page in pages:
        score = 0
        
        # Check page title
        if query_lower in page.get("page_title", "").lower():
            score += 10
            
        # Check page subtitle
        if query_lower in page.get("page_subtitle", "").lower():
            score += 5
            
        # Check sections
        for section in page.get("sections", []):
            if isinstance(section, dict):
                title = section.get("title", "")
                content = section.get("content", "")
                if query_lower in title.lower():
                    score += 3
                if content and query_lower in content.lower():
                    score += 2
        
        if score > 0:
            results.append((score, page))
    
    # Sort by score and return top results
    results.sort(key=lambda x: x[0], reverse=True)
    return [page for score, page in results[:max_results]]

@clinic_ai_expert.tool
async def search_knowledge_base(ctx: RunContext[ClinicAIDeps], user_query: str) -> str:
    """
    Search the knowledge base for relevant information about treatments, procedures, and clinic information.
    
    Args:
        ctx: The context containing the knowledge base
        user_query: The user's question or query about treatments, procedures, or clinic services
        
    Returns:
        A formatted string containing the most relevant information from the knowledge base
    """
    try:
        knowledge_base = ctx.deps.knowledge_base
        
        # Search treatments and pages
        treatment_results = search_treatments(knowledge_base, user_query, max_results=3)
        page_results = search_pages(knowledge_base, user_query, max_results=2)
        
        if not treatment_results and not page_results:
            return "Ich konnte keine spezifischen Informationen zu Ihrer Anfrage in unserer Wissensdatenbank finden. Für eine individuelle Beratung empfehle ich Ihnen ein persönliches Gespräch mit Dr. med. Lara Pfahl."
        
        formatted_results = []
        
        # Format treatment results
        for treatment in treatment_results:
            content = treatment.get("content", {})
            result = f"""
## {treatment.get("treatment_name", "Behandlung")}
**Kategorie:** {treatment.get("category", "Nicht spezifiziert")}
**Tags:** {", ".join(treatment.get("tags", []))}

**Beschreibung:**
{content.get("description", "Keine Beschreibung verfügbar.")}

**Funktionsweise:**
{content.get("mechanism", "Keine Informationen zur Funktionsweise verfügbar.")}
"""
            
            # Add details if available
            details = content.get("details", {})
            if details:
                result += f"""
**Behandlungsdetails:**
- Dauer: {details.get("duration", "Nicht spezifiziert")}
- Ausfallzeit: {details.get("downtime", "Nicht spezifiziert")}
- Haltbarkeit: {details.get("durability", "Nicht spezifiziert")}
"""
                
                # Add cost information if available
                cost = details.get("cost", {})
                if cost and cost.get("base_price"):
                    result += f"- Kosten: ab {cost.get('base_price')} {cost.get('currency', 'EUR')}\n"
            
            # Add doctor citation if available
            doctor_citation = content.get("doctor_citation")
            if doctor_citation:
                if isinstance(doctor_citation, dict):
                    quote = doctor_citation.get("quote", "")
                    doctor_name = doctor_citation.get("doctor_name", "Dr. med. Lara Pfahl")
                elif isinstance(doctor_citation, str):
                    quote = doctor_citation
                    doctor_name = "Dr. med. Lara Pfahl"
                
                if quote:
                    result += f'\n> "{quote}" - {doctor_name}\n'
            
            formatted_results.append(result)
        
        # Format page results
        for page in page_results:
            result = f"""
## {page.get("page_title", "Seite")}
{page.get("page_subtitle", "")}

"""
            # Add relevant sections
            for section in page.get("sections", [])[:2]:  # Limit to first 2 sections
                if isinstance(section, dict):
                    result += f"**{section.get('title', '')}**\n"
                    if section.get('content'):
                        result += f"{section.get('content')}\n\n"
            
            formatted_results.append(result)
        
        return "\n\n---\n\n".join(formatted_results)
        
    except Exception as e:
        print(f"Error searching knowledge base: {e}")
        return "Es gab einen Fehler beim Durchsuchen der Wissensdatenbank. Bitte kontaktieren Sie uns direkt für weitere Informationen."

@clinic_ai_expert.tool
async def get_treatment_details(ctx: RunContext[ClinicAIDeps], treatment_name: str) -> str:
    """
    Get detailed information about a specific treatment.
    
    Args:
        ctx: The context containing the knowledge base
        treatment_name: Name of the treatment to get details for
        
    Returns:
        Detailed information about the treatment
    """
    try:
        knowledge_base = ctx.deps.knowledge_base
        treatments = knowledge_base.get("treatments", [])
        
        # Find the treatment
        target_treatment = None
        for treatment in treatments:
            if treatment_name.lower() in treatment.get("treatment_name", "").lower():
                target_treatment = treatment
                break
        
        if not target_treatment:
            return f"Ich konnte keine Informationen zur Behandlung '{treatment_name}' finden. Bitte überprüfen Sie den Namen oder fragen Sie nach einer ähnlichen Behandlung."
        
        content = target_treatment.get("content", {})
        
        result = f"""
# {target_treatment.get("treatment_name")}

**Kategorie:** {target_treatment.get("category")}
**Behandlungsarten:** {", ".join(target_treatment.get("tags", []))}

## Beschreibung
{content.get("description", "Keine Beschreibung verfügbar.")}

## Funktionsweise
{content.get("mechanism", "Keine Informationen zur Funktionsweise verfügbar.")}
"""
        
        # Add details
        details = content.get("details", {})
        if details:
            result += f"""
## Behandlungsdetails
- **Dauer:** {details.get("duration", "Nicht spezifiziert")}
- **Ausfallzeit:** {details.get("downtime", "Nicht spezifiziert")}
- **Haltbarkeit:** {details.get("durability", "Nicht spezifiziert")}
"""
            
            cost = details.get("cost", {})
            if cost and cost.get("base_price"):
                result += f"- **Kosten:** ab {cost.get('base_price')} {cost.get('currency', 'EUR')}\n"
        
        # Add procedure steps
        procedure_steps = content.get("procedure_steps", [])
        if procedure_steps:
            result += "\n## Behandlungsablauf\n"
            if isinstance(procedure_steps, list):
                for i, step in enumerate(procedure_steps, 1):
                    result += f"{i}. {step}\n"
            else:
                result += procedure_steps
        
        # Add FAQ
        faqs = content.get("faq", []) or content.get("faqs", [])
        if faqs:
            result += "\n## Häufig gestellte Fragen\n"
            for faq in faqs[:3]:  # Limit to first 3 FAQs
                if isinstance(faq, dict):
                    question = faq.get("question", "")
                    answer = faq.get("answer", "")
                    result += f"**{question}**\n{answer}\n\n"
        
        return result
        
    except Exception as e:
        print(f"Error getting treatment details: {e}")
        return "Es gab einen Fehler beim Abrufen der Behandlungsdetails."

@clinic_ai_expert.tool
async def list_treatments_by_category(ctx: RunContext[ClinicAIDeps], category: str = "") -> str:
    """
    List all treatments, optionally filtered by category.
    
    Args:
        ctx: The context containing the knowledge base
        category: Optional category to filter by (e.g., "Gesicht", "Körper", "Männer")
        
    Returns:
        List of treatments in the specified category or all treatments
    """
    try:
        knowledge_base = ctx.deps.knowledge_base
        treatments = knowledge_base.get("treatments", [])
        
        if category:
            treatments = [t for t in treatments if t.get("category", "").lower() == category.lower()]
        
        if not treatments:
            return f"Keine Behandlungen gefunden{f' in der Kategorie {category}' if category else ''}."
        
        result = f"## Behandlungen{f' - {category}' if category else ''}\n\n"
        
        # Group by category
        categories = {}
        for treatment in treatments:
            cat = treatment.get("category", "Sonstige")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(treatment)
        
        for cat, cat_treatments in categories.items():
            result += f"### {cat}\n"
            for treatment in cat_treatments:
                name = treatment.get("treatment_name", "Unbekannte Behandlung")
                tags = ", ".join(treatment.get("tags", []))
                result += f"- **{name}**"
                if tags:
                    result += f" ({tags})"
                result += "\n"
            result += "\n"
        
        return result
        
    except Exception as e:
        print(f"Error listing treatments: {e}")
        return "Es gab einen Fehler beim Abrufen der Behandlungsliste."
