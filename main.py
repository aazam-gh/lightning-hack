import streamlit as st
import openai
import base64
from PIL import Image
import io

# Set page configuration
st.set_page_config(
    page_title="Interactive Story Adventure",
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

# Get API key from secrets
samba = st.secrets["SAMBA_API_KEY"]

# Initialize OpenAI client
client = openai.OpenAI(
    api_key=samba,
    base_url="https://api.sambanova.ai/v1",
)

def encode_image_to_base64(image_file):
    """Convert uploaded image to base64 string"""
    if image_file is not None:
        bytes_data = image_file.getvalue()
        base64_string = base64.b64encode(bytes_data).decode('utf-8')
        return base64_string
    return None

def analyze_image(image_base64):
    """Analyze the image using Vision Model"""
    image_prompt = """
    You have been provided with an image submitted by a user. Your task is to analyze and describe the image, providing as much detail as possible about its content, composition, and overall aesthetic.

    Image Description: Provide a brief summary of the image's content, including any notable objects, scenes, or figures.

    Composition Analysis: Analyze the image's composition, discussing the use of:
    Color palette and color harmony
    Lighting and shadows
    Negative space and composition balance

    Aesthetic Analysis: Discuss the image's overall aesthetic, including:
    Mood and atmosphere
    Emotional resonance
    Style and genre (e.g., realistic, abstract, surreal)
    """
    try:
        response = client.chat.completions.create(
            model='Llama-3.2-90B-Vision-Instruct',
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": image_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error analyzing image: {str(e)}"

def generate_interactive_story(context):
    """Generate an interactive story based on image context"""
    try:
        prompt = f"""Create an interactive, branching narrative based on this story: {context}.
        
        Requirements:
        - Generate a story segment of 3-4 paragraphs
        - Make sure it is engaging, descriptive, and immersive, using vivid language and sensory details to bring it to life. 
        - Use a narrative voice that is engaging, with a tone that is exciting and suspenseful.
        - Provide exactly 3 distinct choices for the user to progress the story
        - Each choice should lead to a different potential narrative path
        - Maintain narrative coherence with previous choices if provided

        Output Format:
        [Story Segment]
        
        CHOICES:
        1. [First Choice Description]
        2. [Second Choice Description]
        3. [Third Choice Description]
        """

        response = client.chat.completions.create(
            model='Meta-Llama-3.2-3B-Instruct',
            messages=[
                {
                    "role": "system",
                    "content": prompt
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating interactive story: {str(e)}"

def generate_conclusion(context):
    """Generate the conclusion of the story based on context"""
    try:
        prompt = f"""Create a satisfactory conclusion to the story based on the context.
                    Make sure it is engaging, descriptive, and immersive, using vivid language and sensory details to bring it to life. 
                    Use a narrative voice that is engaging, with a tone that is exciting and suspenseful.
                    At the end thank the user for engaging with the story.
                    Context: {context}
        """

        response = client.chat.completions.create(
            model='Meta-Llama-3.2-3B-Instruct',
            messages=[
                {
                    "role": "system",
                    "content": prompt
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating conclusion: {str(e)}"

# Main Streamlit App
st.title("📖 Interactive Story Adventure")

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
    min_value=1,
    max_value=20,
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
        first_story = generate_interactive_story(image_context)
        
        # Update session state
        st.session_state.story_history.append(first_story)
        st.session_state.current_story_state = first_story

with story_container:
    if st.session_state.story_history:
        # Show story history
        st.subheader("Your Adventure")
        for idx, story_part in enumerate(st.session_state.story_history, 1):
            st.markdown(f"\n{story_part}")
        
        # Only show input if we haven't reached the choices yet
        if st.session_state.choice_count < choice_limit:
            st.subheader("What will you do?")
            user_input = st.text_input("Enter your decision:", key="user_choice_input")
            continue_button = st.button("Continue Your Journey")

            if continue_button and user_input.strip():
                # Increment choice counter
                st.session_state.choice_count += 1
                
                # Append user input to story history
                st.session_state.story_history.append(f"**Your decision:** {user_input.strip()}")
                
                # Generate next story segment or conclusion based on choice count
                if st.session_state.choice_count < choice_limit:
                    next_story = generate_interactive_story(context=user_input.strip())
                else:
                    next_story = generate_conclusion(context=user_input.strip())
                    st.success("🎉 Congratulations! You've reached the end of your adventure!")
                
                # Update session state
                st.session_state.story_history.append(next_story)
                st.session_state.current_story_state = next_story
                
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