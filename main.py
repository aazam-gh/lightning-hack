import streamlit as st
from PIL import Image
import assemblyai as aai
from functions import encode_image_to_base64, analyze_image, generate_interactive_story, generate_conclusion, rewrite_story


aai.settings.api_key = st.secrets["ASSEMBLY_API_KEY"]
transcriber = aai.Transcriber()
config = aai.TranscriptionConfig()

# Set page configuration
st.set_page_config(
    page_title="VisualQuest - The Interactive Story Adventure",
    page_icon="📖",
    layout="wide"
)

# Initialize session state for story interaction
if 'story_history' not in st.session_state:
    st.session_state.story_history = []
if 'current_story_state' not in st.session_state:
    st.session_state.current_story_state = None
if 'choices' not in st.session_state:
    st.session_state.choices = []
if 'choice_count' not in st.session_state:  # Add choice counter
    st.session_state.choice_count = 0
if 'choice_limit' not in st.session_state:
    st.session_state.choice_limit = 5

# Main Streamlit App
st.title("📖 VisualQuest - Interactive Story Adventure")

# Sidebar for story controls
st.sidebar.header("Story Adventure")
# Clear Chat Button
if st.sidebar.button("Clear Chat 🧹"):
    st.session_state.story_history = []
    st.session_state.current_story_state = None
    st.session_state.choices = []
    st.session_state.choice_count = 0  # Reset choice counter

# Image Upload Section
uploaded_file = st.sidebar.file_uploader("Choose an image to start your adventure...", type=['png', 'jpg', 'jpeg'])

# Main story display area
story_container = st.container()

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.sidebar.image(image, caption="Your Story Begins!", use_container_width=True)
    
    choice_limit = st.sidebar.number_input(
    "Number of choices in your adventure:",
    min_value=2,
    max_value=10,
    value=st.session_state.choice_limit,
    step=1,
    help="Choose how many decisions you want to make in your adventure (1-20)"
)
    
    if choice_limit != st.session_state.choice_limit:
        st.session_state.choice_limit = choice_limit


    # Start Adventure Button
    if st.sidebar.button("Create your story! ✨") and not st.session_state.story_history:
        # Reset session state
        st.session_state.story_history = []
        st.session_state.choices = []
        st.session_state.choice_count = 0  # Reset choice counter
        
        # Analyze image and generate first story segment
        image_base64 = encode_image_to_base64(uploaded_file)
        image_context = analyze_image(image_base64)
        
        # Generate first story segment
        first_story = generate_interactive_story(context=image_context)
        first_story_rewrite = rewrite_story(context=first_story)
        
        # Update session state
        st.session_state.story_history.append(first_story_rewrite)
        st.session_state.current_story_state = first_story_rewrite
        
with story_container:
    if st.session_state.story_history:
        # Show story history
        st.subheader("Your Adventure")
        for idx, story_part in enumerate(st.session_state.story_history, 1):
            st.markdown(f"\n{story_part}")
        
        # Only show input if we haven't reached the choices yet
        if st.session_state.choice_count < choice_limit:
            st.subheader("What will you do?")
            audio_value = st.audio_input("Speak out your next move!")
            continue_button = st.button("Continue Your Journey")

            if continue_button and audio_value:

                audio_file = audio_value
                transcript = transcriber.transcribe(audio_file, config)

                if transcript.status == aai.TranscriptStatus.error:
                    print(f"Transcription failed: {transcript.error}")
                    exit(1)

                # Increment choice counter
                st.session_state.choice_count += 1
                
                # Append user input to story history
                st.session_state.story_history.append(f"**Your decision:** {transcript.text}")
                
                # Generate next story segment or conclusion based on choice count
                if st.session_state.choice_count < choice_limit:
                    next_story = generate_interactive_story(context=transcript.text)
                    next_story_rewrite = rewrite_story(context=next_story)
                else:
                    next_story_rewrite = generate_conclusion(context=transcript.text)

                    st.success("🎉 Congratulations! You've reached the end of your adventure!")
                
                # Update session state
                st.session_state.story_history.append(next_story_rewrite)
                st.session_state.current_story_state = next_story_rewrite
                
                # Rerun app to update display
                st.rerun()
        
        # Show restart button when story is complete
        if st.session_state.choice_count == choice_limit:
            if st.button("Start a New Adventure! 🔄"):
                st.session_state.story_history = []
                st.session_state.current_story_state = None
                st.session_state.choices = []
                st.session_state.choice_count = 0
                st.rerun()

# Styling
st.markdown("""
    <style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 10px;
    }
    .stRadio>div {
        padding: 15px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("Powered by SambaNova AI")