import streamlit as st
import openai
import base64
from PIL import Image



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

        Output Format:
        [Story Segment]
        
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
    


def rewrite_story(context):
    """Generate an interactive story based on image context"""
    try:
        prompt = f"""Rewrite this with the given requirements: {context}.
        
        Requirements:
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
