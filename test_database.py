#!/usr/bin/env python3
"""
Test script to verify Supabase database connection and RAG functionality
"""

import asyncio
import os
from dotenv import load_dotenv
from supabase import Client
from openai import AsyncOpenAI

# Load environment variables
load_dotenv()

async def test_database_connection():
    """Test the Supabase database connection"""
    print("🔍 Testing Supabase Database Connection")
    print("=" * 50)
    
    # Check environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    print(f"SUPABASE_URL: {'✅ Set' if supabase_url else '❌ Missing'}")
    print(f"SUPABASE_SERVICE_KEY: {'✅ Set' if supabase_key else '❌ Missing'}")
    print(f"OPENAI_API_KEY: {'✅ Set' if openai_key else '❌ Missing'}")
    
    if not all([supabase_url, supabase_key, openai_key]):
        print("\n❌ Missing environment variables. Please check your .env file.")
        return False
    
    try:
        # Initialize clients
        supabase = Client(supabase_url, supabase_key)
        openai_client = AsyncOpenAI(api_key=openai_key)
        
        print("\n✅ Clients initialized successfully")
        
        # Test Supabase connection
        print("\n🔍 Testing Supabase connection...")
        result = supabase.table('site_pages').select('id, title, url').limit(1).execute()
        
        if result.data:
            print(f"✅ Database connection successful. Found {len(result.data)} records in sample.")
            print(f"Sample record: {result.data[0]['title']}")
        else:
            print("⚠️  Database connected but no records found in site_pages table.")
        
        # Test OpenAI connection
        print("\n🔍 Testing OpenAI connection...")
        test_embedding = await openai_client.embeddings.create(
            model="text-embedding-3-small",
            input="test query"
        )
        print(f"✅ OpenAI connection successful. Embedding dimensions: {len(test_embedding.data[0].embedding)}")
        
        # Test RAG functionality
        print("\n🔍 Testing RAG functionality...")
        query_embedding = test_embedding.data[0].embedding
        
        rag_result = supabase.rpc(
            'match_site_pages',
            {
                'query_embedding': query_embedding,
                'match_count': 3,
                'filter': {}
            }
        ).execute()
        
        if rag_result.data:
            print(f"✅ RAG functionality working. Found {len(rag_result.data)} relevant documents.")
            for i, doc in enumerate(rag_result.data[:2]):
                print(f"  {i+1}. {doc['title']} (similarity: {doc.get('similarity', 'N/A'):.3f})")
        else:
            print("⚠️  RAG query returned no results.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing database connection: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_ai_expert():
    """Test the AI expert system"""
    print("\n🤖 Testing AI Expert System")
    print("=" * 50)
    
    try:
        from pydantic_ai_expert import clinic_ai_expert, ClinicAIDeps
        
        # Initialize dependencies
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        supabase = Client(supabase_url, supabase_key)
        openai_client = AsyncOpenAI(api_key=openai_key)
        
        deps = ClinicAIDeps(
            supabase=supabase,
            openai_client=openai_client
        )
        
        # Test a simple query
        test_query = "Tell me about Botox treatments"
        print(f"Testing query: '{test_query}'")
        
        result = await clinic_ai_expert.run(
            test_query,
            deps=deps
        )
        
        # Extract response
        response_text = ""
        for message in result.new_messages():
            if hasattr(message, 'parts'):
                for part in message.parts:
                    if hasattr(part, 'content'):
                        response_text += part.content
        
        print(f"✅ AI Expert response: {response_text[:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ Error testing AI expert: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("🏥 Testing Haut Labor AI System Database Integration")
    print("=" * 60)
    
    # Test database connection
    db_ok = await test_database_connection()
    
    if db_ok:
        # Test AI expert
        ai_ok = await test_ai_expert()
        
        print("\n" + "=" * 60)
        print("📊 Test Results:")
        print(f"Database Connection: {'✅ PASS' if db_ok else '❌ FAIL'}")
        print(f"AI Expert System: {'✅ PASS' if ai_ok else '❌ FAIL'}")
        
        if db_ok and ai_ok:
            print("\n🎉 All tests passed! Your AI system is ready to use.")
        else:
            print("\n⚠️  Some tests failed. Check the configuration.")
    else:
        print("\n❌ Database connection failed. Cannot test AI expert.")

if __name__ == "__main__":
    asyncio.run(main()) 