from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import asyncio
import json
import base64
from io import BytesIO
from PIL import Image
import io

# Import your existing clinic AI functionality
from pydantic_ai_expert import clinic_ai_expert, ClinicAIDeps, load_knowledge_base
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize clients and load knowledge base
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
knowledge_base = load_knowledge_base()

# Store conversation history (in production, use a proper database)
conversation_history = {}

# Add logging to debug environment variables and knowledge base
print("🔍 Checking environment variables...")
print(f"OPENAI_API_KEY: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Missing'}")

print("\n📚 Checking knowledge base...")
if not knowledge_base.get("treatments") and not knowledge_base.get("pages"):
    print("⚠️  Warning: Knowledge base is empty. Please check combined_database_newest.json file.")
else:
    treatment_count = len(knowledge_base.get("treatments", []))
    page_count = len(knowledge_base.get("pages", []))
    print(f"✅ Knowledge base loaded: {treatment_count} treatments, {page_count} pages")

@app.route('/')
def index():
    """Serve the main HTML page with the chatbot widget"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages from the frontend"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get or create conversation history for this session
        session_id = request.headers.get('X-Session-ID', 'default')
        if session_id not in conversation_history:
            conversation_history[session_id] = []
        
        # Run the AI agent in a separate thread to handle async operations
        import asyncio
        import threading
        from concurrent.futures import ThreadPoolExecutor
        
        def run_ai_agent():
            """Run the AI agent in a new event loop"""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                print(f"🤖 Processing query: '{user_message}'")
                
                # Prepare dependencies
                deps = ClinicAIDeps(
                    knowledge_base=knowledge_base,
                    openai_client=openai_client
                )
                
                # Run the agent with the user's message
                result = loop.run_until_complete(clinic_ai_expert.run(
                    user_message,
                    deps=deps,
                    message_history=conversation_history[session_id]
                ))
                
                # Extract the response text (only from assistant messages, not system prompts)
                response_text = ""
                for message in result.new_messages():
                    if hasattr(message, 'parts'):
                        for part in message.parts:
                            if hasattr(part, 'content') and part.part_kind == 'text':
                                response_text += part.content
                
                # Clean up the response - remove any system prompt content
                if "You are an expert consultant" in response_text:
                    # Find where the actual response starts
                    start_idx = response_text.find("Tell me about")
                    if start_idx != -1:
                        response_text = response_text[start_idx:]
                
                # Update conversation history
                conversation_history[session_id].extend(result.new_messages())
                
                print(f"✅ AI response generated: {len(response_text)} characters")
                return response_text
            except Exception as e:
                print(f"❌ Error in AI agent: {e}")
                import traceback
                traceback.print_exc()
                raise e
            finally:
                loop.close()
        
        # Run the AI agent in a thread pool
        with ThreadPoolExecutor() as executor:
            future = executor.submit(run_ai_agent)
            response_text = future.result(timeout=60)  # 60 second timeout
        
        return jsonify({
            'message': response_text,
            'sources': []  # You can add sources here if available
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'message': 'Entschuldigung, es gab einen Fehler bei der Verarbeitung Ihrer Anfrage. Bitte versuchen Sie es erneut.',
            'sources': []
        }), 500

@app.route('/api/analyze-image', methods=['POST'])
def analyze_image():
    """Handle image uploads for skin analysis"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Read and process the image
        image_data = file.read()
        
        # For now, return a placeholder response
        # In a real implementation, you would:
        # 1. Save the image to storage
        # 2. Use AI vision models to analyze the skin
        # 3. Return detailed analysis results
        
        analysis_result = (
            "Ich habe Ihr Hautbild analysiert. Basierend auf dem Bild kann ich folgende Beobachtungen machen:\n\n"
            "• Hauttyp: Normal bis Mischhaut\n"
            "• Empfohlene Behandlungen: HydraFacial, LaseMD\n"
            "• Pflegeempfehlungen: Feuchtigkeitspflege, Sonnenschutz\n\n"
            "Für eine detaillierte Analyse und personalisierte Behandlungsempfehlungen "
            "vereinbaren Sie bitte einen Termin in unserer Praxis."
        )
        
        return jsonify({
            'status': 'success',
            'message': analysis_result
        })
        
    except Exception as e:
        print(f"Error in image analysis: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Fehler bei der Bildanalyse. Bitte versuchen Sie es erneut.'
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint for Render.com"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False) 