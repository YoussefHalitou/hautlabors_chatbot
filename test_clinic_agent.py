#!/usr/bin/env python3
"""
Test script for the Haut Labor Oldenburg clinic AI agent
This demonstrates how the agent can provide detailed information about treatments
based on the scraped clinic website data.
"""

import asyncio
from pydantic_ai_expert import clinic_ai_expert, ClinicAIDeps
from dotenv import load_dotenv
from supabase import create_client, Client
from openai import AsyncOpenAI
import os

load_dotenv()

async def test_clinic_agent():
    # Setup dependencies
    supabase: Client = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_SERVICE_KEY')
    )
    openai_client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    deps = ClinicAIDeps(supabase=supabase, openai_client=openai_client)
    
    # Test queries
    test_queries = [
        "What treatments are available for wrinkle reduction?",
        "Tell me about Dr. Larisa Pfahl and her qualifications",
        "What is the cost of Botox treatments?",
        "Can you explain the HydraFacial procedure?",
        "What treatments are specifically available for men?",
        "How do I book an appointment?",
        "What are the opening hours and contact information?",
        "Tell me about laser hair removal treatments"
    ]
    
    print("🏥 Haut Labor Oldenburg Clinic AI Agent Test")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 40)
        
        try:
            result = await clinic_ai_expert.run(query, deps=deps)
            print(f"Response: {result.data}")
        except Exception as e:
            print(f"Error: {e}")
        
        print()

if __name__ == "__main__":
    asyncio.run(test_clinic_agent())
