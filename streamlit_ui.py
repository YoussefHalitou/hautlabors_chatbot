from __future__ import annotations
from typing import Literal, TypedDict
import asyncio
import os

import streamlit as st
import json
import logfire

# Configure Streamlit page
st.set_page_config(
    page_title="Haut Labor Oldenburg - AI Consultant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)
from supabase import Client
from openai import AsyncOpenAI

# Import all the message part classes
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    SystemPromptPart,
    UserPromptPart,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
    RetryPromptPart,
    ModelMessagesTypeAdapter
)
from pydantic_ai_expert import clinic_ai_expert, ClinicAIDeps

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
supabase: Client = Client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

# Configure logfire to suppress warnings (optional)
logfire.configure(send_to_logfire='never')

class ChatMessage(TypedDict):
    """Format of messages sent to the browser/API."""

    role: Literal['user', 'model']
    timestamp: str
    content: str


def display_message_part(part):
    """
    Display a single part of a message in the Streamlit UI.
    Customize how you display system prompts, user prompts,
    tool calls, tool returns, etc.
    """
    # system-prompt
    if part.part_kind == 'system-prompt':
        with st.chat_message("system"):
            st.markdown(f"**System**: {part.content}")
    # user-prompt
    elif part.part_kind == 'user-prompt':
        with st.chat_message("user"):
            st.markdown(part.content)
    # text
    elif part.part_kind == 'text':
        with st.chat_message("assistant"):
            st.markdown(part.content)          


async def run_agent_with_streaming(user_input: str):
    """
    Run the agent with streaming text for the user_input prompt,
    while maintaining the entire conversation in `st.session_state.messages`.
    """
    # Prepare dependencies
    deps = ClinicAIDeps(
        supabase=supabase,
        openai_client=openai_client
    )

    # Run the agent in a stream
    async with clinic_ai_expert.run_stream(
        user_input,
        deps=deps,
        message_history= st.session_state.messages[:-1],  # pass entire conversation so far
    ) as result:
        # We'll gather partial text to show incrementally
        partial_text = ""
        message_placeholder = st.empty()

        # Render partial text as it arrives
        async for chunk in result.stream_text(delta=True):
            partial_text += chunk
            message_placeholder.markdown(partial_text)

        # Now that the stream is finished, we have a final result.
        # Add new messages from this run, excluding user-prompt messages
        filtered_messages = [msg for msg in result.new_messages() 
                            if not (hasattr(msg, 'parts') and 
                                    any(part.part_kind == 'user-prompt' for part in msg.parts))]
        st.session_state.messages.extend(filtered_messages)

        # Add the final response to the messages
        st.session_state.messages.append(
            ModelResponse(parts=[TextPart(content=partial_text)])
        )


async def main():
    st.title("🏥 Haut Labor Oldenburg - AI Consultant")
    st.write("Ask me anything about aesthetic treatments, procedures, and services at Haut Labor Oldenburg clinic in Germany.")
    
    # Sidebar with clinic information
    with st.sidebar:
        st.header("📍 Clinic Information")
        st.write("**Haut Labor Oldenburg**")
        st.write("Dr. Larisa Pfahl - Gynecologist")
        st.write("Specialized in minimally invasive aesthetic treatments")
        
        st.divider()
        
        st.header("📞 Contact")
        st.write("**Phone:** +49 (0) 157 834 488 90")
        st.write("**Email:** info@haut-labor.de")
        
        st.divider()
        
        st.header("💡 Example Questions")
        example_questions = [
            "What treatments are available for wrinkle reduction?",
            "Tell me about Morpheus8 treatments",
            "What is the cost of Botox treatments?",
            "Can you explain the HydraFacial procedure?",
            "What treatments are specifically available for men?",
            "Tell me about Dr. Larisa Pfahl",
            "How do I book an appointment?",
            "What are the laser hair removal options?"
        ]
        
        for question in example_questions:
            if st.button(question, key=f"example_{hash(question)}"):
                st.session_state.example_question = question
                st.rerun()
                
        st.divider()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", key="clear_chat"):
            st.session_state.messages = []
            st.rerun()

    # Initialize chat history in session state if not present
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Show welcome message if no messages yet
    if len(st.session_state.messages) == 0:
        st.info("👋 Welcome to Haut Labor Oldenburg! I'm here to help you learn about our aesthetic treatments and services. Feel free to ask me anything or click on the example questions in the sidebar.")
        
        # Display treatment categories
        st.subheader("🎆 Our Treatment Categories")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**💆 Facial Treatments**")
            st.write("• Botox/Faltenrelaxan")
            st.write("• Dermal Fillers")
            st.write("• HydraFacial")
            st.write("• Morpheus8")
            st.write("• Ultherapy")
            
        with col2:
            st.write("**✨ Laser Treatments**")
            st.write("• CO2 Laser")
            st.write("• LaseMD")
            st.write("• Lumecca")
            st.write("• Hair Removal")
            
        with col3:
            st.write("**👨 Specialized Services**")
            st.write("• Treatments for Men")
            st.write("• Body Contouring")
            st.write("• Aesthetic Gynecology")
            st.write("• Skin Analysis")

    # Display all messages from the conversation so far
    # Each message is either a ModelRequest or ModelResponse.
    # We iterate over their parts to decide how to display them.
    for msg in st.session_state.messages:
        if isinstance(msg, ModelRequest) or isinstance(msg, ModelResponse):
            for part in msg.parts:
                display_message_part(part)

    # Check if an example question was clicked
    if "example_question" in st.session_state:
        user_input = st.session_state.example_question
        del st.session_state.example_question
    else:
        # Chat input for the user
        user_input = st.chat_input("What questions do you have about our aesthetic treatments?")

    if user_input:
        # We append a new request to the conversation explicitly
        st.session_state.messages.append(
            ModelRequest(parts=[UserPromptPart(content=user_input)])
        )
        
        # Display user prompt in the UI
        with st.chat_message("user"):
            st.markdown(user_input)

        # Display the assistant's partial response while streaming
        with st.chat_message("assistant"):
            # Actually run the agent now, streaming the text
            await run_agent_with_streaming(user_input)


if __name__ == "__main__":
    asyncio.run(main())
