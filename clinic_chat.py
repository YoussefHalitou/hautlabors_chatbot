#!/usr/bin/env python3
"""
Interactive chat interface for the Haut Labor Oldenburg clinic AI agent
Run this to have a conversation about treatments and services.
"""

import asyncio
from pydantic_ai_expert import clinic_ai_expert, ClinicAIDeps, load_knowledge_base
from dotenv import load_dotenv
from openai import AsyncOpenAI
import os

load_dotenv()

async def interactive_chat():
    # Setup dependencies
    knowledge_base = load_knowledge_base()
    openai_client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    deps = ClinicAIDeps(knowledge_base=knowledge_base, openai_client=openai_client)
    
    print("🏥 Haut Labor Oldenburg Clinic AI Assistant")
    print("=" * 50)
    print("Ask me anything about treatments, procedures, or services!")
    print("Type 'quit' or 'exit' to end the conversation.")
    print("Type 'help' for example questions.")
    print("-" * 50)
    
    # Check if knowledge base loaded successfully
    if not knowledge_base.get("treatments") and not knowledge_base.get("pages"):
        print("⚠️  Warning: Knowledge base is empty. Please check combined_database_newest.json file.")
    else:
        treatment_count = len(knowledge_base.get("treatments", []))
        page_count = len(knowledge_base.get("pages", []))
        print(f"✅ Knowledge base loaded: {treatment_count} treatments, {page_count} pages")
    
    while True:
        user_input = input("\n💬 You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Thank you for using the Haut Labor clinic assistant!")
            break
        
        if user_input.lower() == 'help':
            print("\n📋 Example questions you can ask:")
            print("• What treatments are available for wrinkle reduction?")
            print("• Tell me about Morpheus8 treatments")
            print("• What is the cost of Botox treatments?")
            print("• Can you explain the HydraFacial procedure?")
            print("• What treatments are specifically available for men?")
            print("• How do I book an appointment?")
            print("• Tell me about Dr. Lara Pfahl")
            print("• What are the contact details?")
            print("• List all treatments by category")
            continue
        
        if not user_input:
            continue
        
        try:
            print("\n🤖 Assistant: ", end="")
            result = await clinic_ai_expert.run(user_input, deps=deps)
            print(result.data)
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again or contact the clinic directly for more information.")

if __name__ == "__main__":
    asyncio.run(interactive_chat())
