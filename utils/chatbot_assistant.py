"""
Chatbot assistant for the GeneHack AMR application powered by OpenAI's GPT models.
"""
import json
import os
from typing import List, Dict, Any, Optional
from openai import OpenAI

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# System prompt that defines the chatbot's behavior and capabilities
SYSTEM_PROMPT = """
You are GeneHack Assistant, an AI expert in antimicrobial resistance (AMR) genomics.
You analyze genetic data and provide insights on:
1. Gene functions and their role in antimicrobial resistance
2. Protein structures and their significance
3. Resistance mechanisms for different antibiotics
4. Interpretation of AMR analysis results
5. Potential research directions and clinical implications

Current analysis data will be provided in JSON format. Use this data when answering questions.
Keep your responses scientifically accurate but understandable to researchers and healthcare professionals.
If you're unsure about something, acknowledge the limitations rather than making up information.

For any clinical advice, emphasize that your suggestions are for research purposes only and should be 
validated by proper clinical testing and medical professionals.
"""

def initialize_chat_history() -> List[Dict[str, str]]:
    """
    Initialize a new chat history with just the system message.
    
    Returns:
        List of message dictionaries
    """
    return [{"role": "system", "content": SYSTEM_PROMPT}]

def add_analysis_context(chat_history: List[Dict[str, str]], analysis_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Add the current analysis data to the chat history as context.
    
    Args:
        chat_history: Current chat history
        analysis_data: Dictionary containing genes, proteins, resistance data
        
    Returns:
        Updated chat history with analysis context
    """
    # Convert analysis data to a readable format for the model
    context = json.dumps(analysis_data, indent=2)
    
    # Create a context message for the assistant
    context_message = {
        "role": "system", 
        "content": f"Here is the current analysis data:\n```json\n{context}\n```\nUse this information to answer the user's questions."
    }
    
    # Add context to chat history (after system message, before any other messages)
    if len(chat_history) > 1:
        return [chat_history[0], context_message] + chat_history[1:]
    else:
        return chat_history + [context_message]

def chat_with_assistant(
    chat_history: List[Dict[str, str]], 
    user_message: str
) -> Dict[str, Any]:
    """
    Send a message to the OpenAI assistant and get a response.
    
    Args:
        chat_history: Current chat history including system and user messages
        user_message: The user's new message
        
    Returns:
        Dictionary with response text and updated chat history
    """
    if not OPENAI_API_KEY:
        return {
            "response": "Error: OpenAI API key is not configured. Please add your API key to the environment variables.",
            "chat_history": chat_history
        }
    
    # Add user message to chat history
    chat_history.append({"role": "user", "content": user_message})
    
    try:
        # Call the OpenAI API with gpt-4o model
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=chat_history,
            temperature=0.7,
            max_tokens=800
        )
        
        # Extract the assistant's message
        assistant_message = response.choices[0].message.content
        
        # Add the assistant's response to the chat history
        chat_history.append({"role": "assistant", "content": assistant_message})
        
        return {
            "response": assistant_message,
            "chat_history": chat_history
        }
    
    except Exception as e:
        error_message = f"Error communicating with OpenAI: {str(e)}"
        return {
            "response": error_message,
            "chat_history": chat_history
        }

def generate_analysis_suggestions(analysis_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Generate suggested questions and research directions based on the analysis.
    
    Args:
        analysis_data: Dictionary containing genes, proteins, resistance data
        
    Returns:
        Dictionary with suggested questions and research directions
    """
    if not OPENAI_API_KEY:
        return {
            "suggested_questions": [
                "What are the most common resistance mechanisms in this sample?",
                "Which antibiotics should be avoided based on this analysis?",
                "What are the key resistance genes identified?",
                "How do these genes confer resistance?"
            ],
            "research_directions": [
                "Investigate the prevalence of these resistance genes in your region",
                "Test alternative antibiotics not affected by these mechanisms",
                "Compare this resistance profile with clinical outcomes"
            ]
        }
    
    try:
        # Prepare the analysis data
        context = json.dumps(analysis_data, indent=2)
        
        # Create system prompt for suggestions
        suggestion_prompt = f"""
        Please analyze the following antimicrobial resistance data and generate:
        1. Five suggested questions a researcher might want to ask about this data
        2. Three potential research directions based on these results
        
        Data:
        ```json
        {context}
        ```
        
        Return your response in JSON format as follows:
        {{
            "suggested_questions": ["question1", "question2", ...],
            "research_directions": ["direction1", "direction2", ...]
        }}
        """
        
        # Call the OpenAI API
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": suggestion_prompt}],
            temperature=0.7,
            max_tokens=800,
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        suggestions = json.loads(response.choices[0].message.content)
        return suggestions
    
    except Exception as e:
        # Return default suggestions if there's an error
        return {
            "suggested_questions": [
                "What are the most common resistance mechanisms in this sample?",
                "Which antibiotics should be avoided based on this analysis?",
                "What are the key resistance genes identified?",
                "How do these genes confer resistance?"
            ],
            "research_directions": [
                "Investigate the prevalence of these resistance genes in your region",
                "Test alternative antibiotics not affected by these mechanisms",
                "Compare this resistance profile with clinical outcomes"
            ]
        }

def summarize_key_findings(analysis_data: Dict[str, Any]) -> str:
    """
    Generate a concise summary of the key findings from the analysis.
    
    Args:
        analysis_data: Dictionary containing genes, proteins, resistance data
        
    Returns:
        Summary text of key findings
    """
    if not OPENAI_API_KEY:
        return "OpenAI API key is not configured. Please add your API key to use this feature."
    
    try:
        # Prepare the analysis data
        context = json.dumps(analysis_data, indent=2)
        
        # Create system prompt for summary
        summary_prompt = f"""
        Please analyze the following antimicrobial resistance data and create a concise summary (250 words max)
        highlighting the key findings, focusing on:
        
        1. The most significant resistance genes and mechanisms
        2. Antibiotics that would be most and least effective
        3. Any unusual or noteworthy patterns
        
        Data:
        ```json
        {context}
        ```
        """
        
        # Call the OpenAI API
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": summary_prompt}],
            temperature=0.5,
            max_tokens=400
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Error generating summary: {str(e)}"