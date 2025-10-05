# Import necessary libraries
import streamlit as st
from litellm import completion
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

def clear_state():
    """
    Function to reset the Streamlit session state.
    This clears the user input and the enhanced prompt, effectively
    resetting the entire application to its initial state.
    """
    st.session_state.user_prompt = ""
    st.session_state.enhanced_prompt = None

def main():
    """
    Main function to run the Streamlit application.
    This app serves as a prompt enhancer and a multi-LLM generator.
    
    WORKFLOW:
    1. User enters a basic prompt idea
    2. App enhances the prompt using selected LLM (Gemini/Groq/OpenRouter)
    3. Enhanced prompt is displayed to user
    4. User can then generate final output using any of the available LLMs
    """

    # --- STEP 1: PAGE CONFIGURATION ---
    # Configure the Streamlit page with title, icon, and layout settings
    st.set_page_config(
        page_title="Prompt Enhancer & Generator",
        page_icon="✨",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # --- STEP 2: CUSTOM STYLING ---
    # Add custom CSS styles to make the application visually appealing
    st.markdown("""
        <style>
            body { color: #333; }
            .stApp { background-color: #f0f2f6; }
            .stButton > button {
                background-color: #4CAF50; color: white; border-radius: 20px;
                border: none; padding: 10px 20px; transition: background-color 0.3s;
            }
            .stButton > button:hover { background-color: #45a049; }
            .stTextArea textarea {
                border-radius: 10px; border: 1px solid #ddd; background-color: #fff;
            }
            .stMarkdown h1, .stMarkdown h2 { color: #2c3e50; }
            .response-container {
                background-color: #ffffff; border-left: 5px solid #4CAF50;
                padding: 20px; border-radius: 10px; margin-top: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .llm-output-container {
                background-color: #f9f9f9; border-left: 5px solid #007bff;
                padding: 20px; border-radius: 10px; margin-top: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            /* Custom CSS to style the selectbox for prompt enhancement */
            div[data-baseweb="select"] > div {
                background-color: white !important;
                color: black !important;
            }
            /* This targets the text within the selectbox after a selection is made */
            div[data-baseweb="select"] > div > div > div > div > div {
                color: black !important;
            }  
        </style>
    """, unsafe_allow_html=True)

    # --- STEP 3: HEADER AND TITLE ---
    # Display the main title and description of the application
    st.title("🚀 AI Prompt Enhancer & Generator")
    st.markdown("Enter a simple idea, and let AI transform it into a **concise and powerful** prompt.")

    # --- STEP 4: API KEY SETUP ---
    # Retrieve API keys from environment variables
    # These keys are needed for different LLM providers
    google_api_key = os.getenv("GOOGLE_API_KEY")          # For Gemini models
    groq_api_key = os.getenv("GROQ_API_KEY")              # For Groq models  
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")  # For OpenRouter models

    # Set API keys in environment for LiteLLM to use
    # LiteLLM automatically picks up these environment variables
    if google_api_key:
        os.environ["GOOGLE_API_KEY"] = google_api_key
    if groq_api_key:
        os.environ["GROQ_API_KEY"] = groq_api_key
    if openrouter_api_key:
        os.environ["OPENROUTER_API_KEY"] = openrouter_api_key

    # --- STEP 5: PROMPT ENHANCEMENT SECTION ---
    # This section handles the first part of the workflow: enhancing user's basic prompt
    with st.form(key='prompt_enhancer_form'):
        
        # Define available LLMs for prompt enhancement with their LiteLLM model identifiers
        enhancement_llm_options = {
            "Google Gemini": "gemini/gemini-2.5-flash",        # Google's Gemini model
            "Groq": "groq/llama-3.1-8b-instant",               # Groq's Llama model
            "OpenRouter": "openrouter/meta-llama/llama-3.1-8b-instruct:free"  # OpenRouter's free Llama model
        }
        
        # Create dropdown for LLM selection
        selected_enhancement_llm = st.selectbox(
            "Select an LLM for Prompt Enhancement:",
            options=list(enhancement_llm_options.keys()),
            key='enhancement_llm_select',
            help="Choose which AI model will enhance your prompt"
        )
        
        # Create text area for user input
        user_prompt = st.text_area(
            "Enter your prompt idea here:",
            height=150,
            key='user_prompt',
            placeholder="e.g., 'I want to test a landing page, and I need a few test cases'",
            help="Enter a simple description of what you want to accomplish"
        )

        # Create two columns for buttons (Enhance and Clear)
        col1, col2 = st.columns([1, 1])

        with col1:
            submit_enhance_button = st.form_submit_button(label="✨ Enhance My Prompt")
        with col2:
            # Clear button resets the entire application state
            st.form_submit_button(label="🔄 Clear", on_click=clear_state)

    # --- STEP 6: PROMPT ENHANCEMENT LOGIC ---
    # This executes when user clicks "Enhance My Prompt" button
    if submit_enhance_button and user_prompt:
        
        # Get the LiteLLM model identifier for the selected LLM
        selected_model = enhancement_llm_options[selected_enhancement_llm]
        
        # STEP 6.1: API KEY VALIDATION
        # Check if the required API key is available for the selected model
        api_key_available = True
        error_message = ""
        
        if "gemini" in selected_model and not google_api_key:
            api_key_available = False
            error_message = "🚨 Google API Key not found! Please add your key to a `.env` file: `GOOGLE_API_KEY='Your-API-Key-Here'`"
        elif "groq" in selected_model and not groq_api_key:
            api_key_available = False
            error_message = "🚨 Groq API Key not found! Please add your key to a `.env` file: `GROQ_API_KEY='Your-Groq-Key-Here'`"
        elif "openrouter" in selected_model and not openrouter_api_key:
            api_key_available = False
            error_message = "🚨 OpenRouter API Key not found! Please add your key to a `.env` file: `OPENROUTER_API_KEY='Your-OpenRouter-Key-Here'`"
        
        # Stop execution if API key is missing
        if not api_key_available:
            st.error(error_message)
            st.stop()

        # STEP 6.2: SYSTEM PROMPT DEFINITION
        # Define the instructions for the LLM on how to enhance prompts
        system_prompt = """As an expert prompt engineering assistant, your task is to refine a user's simple prompt into a concise yet powerful one.
Your goal is to be brief but effective. Enhance the user's request by adding only the most essential context, a clear persona, and a specific desired output format.
Avoid verbosity and filler words. The final prompt should be direct and to the point.

Your response should begin with a friendly greeting: "Hello friend, here is a better prompt for you:" """

        # STEP 6.3: API CALL TO ENHANCE PROMPT
        try:
            with st.spinner("Crafting the perfect prompt..."):
                # Make API call using LiteLLM's completion function
                response = completion(
                    model=selected_model,                    # The LLM model to use
                    messages=[                               # Conversation format
                        {"role": "system", "content": system_prompt},  # Instructions for the AI
                        {"role": "user", "content": user_prompt}       # User's original prompt
                    ],
                    temperature=0.7                          # Creativity level (0.0 = focused, 1.0 = creative)
                )
                
                # Extract the enhanced prompt from the API response
                enhanced_prompt = response.choices[0].message.content
            
            # STEP 6.4: STORE AND DISPLAY ENHANCED PROMPT
            # Store the enhanced prompt in session state for later use
            st.session_state.enhanced_prompt = enhanced_prompt
            
            # Display the enhanced prompt to the user
            st.markdown("## 🌟 Your Enhanced Prompt")
            st.markdown(f'<div class="response-container">{enhanced_prompt}</div>', unsafe_allow_html=True)

        except Exception as e:
            # Handle any errors that occur during the API call
            st.error(f"An error occurred: {e}")
            st.info("Please check your API key and network connection. Also, ensure the LLM API is enabled for your project.")

    # --- STEP 7: FINAL OUTPUT GENERATION SECTION ---
    # This section handles the second part: using the enhanced prompt to generate final output
    st.markdown("---")  # Visual separator
    st.markdown("## 🤖 Generate Final Output")
    st.markdown("Use the enhanced prompt to get a real result from the LLM of your choice.")

    # Only show this section if an enhanced prompt exists
    if 'enhanced_prompt' in st.session_state and st.session_state.enhanced_prompt:
        
        with st.form(key='llm_selection_form'):
            
            # STEP 7.1: DEFINE AVAILABLE LLMS FOR FINAL GENERATION
            # Same models as enhancement, but user can choose a different one
            llm_options = {
                "Google Gemini": "gemini/gemini-2.5-flash",
                "Groq": "groq/llama-3.1-8b-instant", 
                "OpenRouter": "openrouter/meta-llama/llama-3.1-8b-instruct:free"
            }
            
            # STEP 7.2: LLM SELECTION DROPDOWN
            selected_llm = st.selectbox(
                "Select an LLM to generate the final result:",
                options=list(llm_options.keys()),
                help="Choose which AI model will process your enhanced prompt"
            )
            
            # STEP 7.3: TEMPERATURE CONTROL SLIDER
            # Allow user to control creativity/randomness of the output
            temperature = st.slider(
                "Temperature (creativity level):",
                min_value=0.0,        # Most focused/deterministic
                max_value=1.0,        # Most creative/random
                value=0.7,            # Default balanced setting
                step=0.1,
                help="Lower values = more focused and consistent, Higher values = more creative and varied"
            )
            
            # STEP 7.4: GENERATE BUTTON
            submit_generate_button = st.form_submit_button(label=f"🚀 Generate with {selected_llm}")
            
        # STEP 7.5: FINAL OUTPUT GENERATION LOGIC
        if submit_generate_button:
            
            # Get the model identifier for the selected LLM
            selected_model = llm_options[selected_llm]
            enhanced_prompt_text = st.session_state.enhanced_prompt
            
            # STEP 7.6: API KEY VALIDATION FOR FINAL GENERATION
            # Same validation logic as the enhancement step
            api_key_available = True
            error_message = ""
            
            if "gemini" in selected_model and not google_api_key:
                api_key_available = False
                error_message = "🚨 Google API Key not found! Please add your key to a `.env` file: `GOOGLE_API_KEY='Your-API-Key-Here'`"
            elif "groq" in selected_model and not groq_api_key:
                api_key_available = False
                error_message = "🚨 Groq API Key not found! Please add your key to a `.env` file: `GROQ_API_KEY='Your-Groq-Key-Here'`"
            elif "openrouter" in selected_model and not openrouter_api_key:
                api_key_available = False
                error_message = "🚨 OpenRouter API Key not found! Please add your key to a `.env` file: `OPENROUTER_API_KEY='Your-OpenRouter-Key-Here'`"
            
            # Stop if API key is missing
            if not api_key_available:
                st.error(error_message)
                st.stop()
            
            # STEP 7.7: API CALL FOR FINAL GENERATION
            try:
                with st.spinner(f"Generating result using {selected_llm}..."):
                    # Make API call with the enhanced prompt
                    response = completion(
                        model=selected_model,                               # Selected LLM model
                        messages=[                                          # Simple user message format
                            {"role": "user", "content": enhanced_prompt_text}  # The enhanced prompt as user input
                        ],
                        temperature=temperature                             # User-selected creativity level
                    )
                    
                    # Extract the final response from API
                    final_response = response.choices[0].message.content
                    
                    # STEP 7.8: DISPLAY FINAL RESULT
                    st.markdown("### ✨ Final Result")
                    st.markdown(f'<div class="llm-output-container">{final_response}</div>', unsafe_allow_html=True)
                    
            except Exception as e:
                # Handle any errors during final generation
                st.error(f"An error occurred: {e}")
                st.info("Please check your API key, model ID, or network connection.")
                
    else:
        # Show this message if no enhanced prompt is available
        st.info("Please enhance your prompt first before generating a final result.")

# --- STEP 8: APPLICATION INITIALIZATION ---
if __name__ == "__main__":
    # Initialize session state variables if they don't exist
    # This ensures the app works correctly on first load
    if 'enhanced_prompt' not in st.session_state:
        st.session_state.enhanced_prompt = None
    if 'user_prompt' not in st.session_state:
        st.session_state.user_prompt = ""
    
    # Start the main application
    main()