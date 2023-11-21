import streamlit as st
import os
import openai
from pathlib import Path

# Load environment variables
openai.api_key = st.secrets["OPENAI_API_KEY"]
voices = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']

# Functions
def summarize(text):
    inst = '''Resume en moins de 1000 caracteres:''' 
    completion = openai.chat.completions.create(
        model='gpt-3.5-turbo-1106',
        messages= [
            {'role': 'system', 'content': inst },
            {'role': 'user', 'content': text }]
    )
    return completion.choices[0].message.content

def tts(summary, article, episode, voice):
    speech_file_path = Path(f'podcast/{episode}/audio/' + article.replace('.txt', '.mp3'))
    response = openai.audio.speech.create(
    model="tts-1",
    voice=voice,
    input=summary
    )
    response.stream_to_file(speech_file_path)
    # return response.content

# Streamlit app
st.title("Podcast Generator")

# User input for episode number
episode_number = st.number_input("Enter Episode Number", min_value=1, value=2, step=1)
episode = 'episode' + '{:03d}'.format(episode_number)

# Display articles
directory = 'podcast/' + episode 
if os.path.exists(directory):
    articles = os.listdir(directory + '/text')
    article = st.selectbox("Select an Article", articles)
    
    # Summary
    if not os.path.exists(f'podcast/{episode}/summary/{article}'):
        if st.button("Summary"):
            if not os.path.exists(f'podcast/{episode}/summary'):
                os.mkdir(f'podcast/{episode}/summary')
            # Read the text from the file
            with open(f'podcast/{episode}/text/{article}', 'r',encoding='utf-8') as f:
                text = f.read()
            summary = summarize(text)
            st.write(f'Summary characters: {len(summary)}')
            # summary = article.replace('.txt', '\n')+summary
            # Write the summary string to the file
            with open(f'podcast/{episode}/summary/{article}', 'w', encoding='utf-8') as f:
                f.write(summary)
            st.write("Summary generated.")
            st.write(summary)
    else:
        with open(f'podcast/{episode}/summary/{article}', 'r',encoding='utf-8') as f:
            summary = f.read()
        st.write(summary)


        # Audio
        if os.path.exists(f'podcast/{episode}/audio/' + article.replace('.txt', '.mp3')): 
            with open(f'podcast/{episode}/audio/' + article.replace('.txt', '.mp3'), 'rb') as f:
                audio = f.read()
            st.audio(audio)
        else:
            voice = st.radio("Select Voice", voices)
            if st.button("TTS"):
                if not os.path.exists(f'podcast/{episode}/audio'):
                    os.mkdir(f'podcast/{episode}/audio')
                # Read the text from the file
                with open(f'podcast/{episode}/summary/{article}', 'r', encoding='utf-8') as f:
                    summary = f.read()
                summary = article.replace('.txt', '\n') + summary
                tts(summary, article, episode, voice)
                st.write("Audio generated.")
                with open(f'podcast/{episode}/audio/' + article.replace('.txt', '.mp3'), 'rb') as f:
                    audio = f.read()
                st.audio(audio)

else:
    st.write("No articles found for the selected episode.")
    if st.button("Create Episode"):
        os.mkdir(directory)
        os.mkdir(directory + '/text')
        st.write("Episode directory created.")
