# %% AMI translated
from dotenv import load_dotenv
from pathlib import Path
import os, openai, re

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Functions
def summarize(text):
    inst = '''Resume l'article suivant en moins de 1000 caracteres:''' 
    completion = openai.chat.completions.create(
        model='gpt-3.5-turbo-1106',
        messages= [
            {'role': 'system', 'content': inst },
            {'role': 'user', 'content': text }]
    )
    return completion.choices[0].message.content

def translate(text):
    inst = '''Translate the text to English''' 
    completion = openai.chat.completions.create(
        model='gpt-3.5-turbo-1106',
        messages= [
            {'role': 'system', 'content': inst },
            {'role': 'user', 'content': text }]
    )
    return completion.choices[0].message.content

episode_number = 3
# episode_number = int(episode_number)
episode = 'episode' + '{:03d}'.format(episode_number)
# Set the directory for the episode
directory = 'podcast/' + episode 
articles = os.listdir(f'podcast/{episode}/text')

for i, article in enumerate(articles):
    print(f"Iteration {i}: {article}")

    # OpenAI translate
    if not os.path.exists(f'podcast/{episode}/translation'):
        os.mkdir(f'podcast/{episode}/translation')
    # Read the text from the file
    with open(f'podcast/{episode}/summary/' + article, 'r',encoding='utf-8') as f:
        text = f.read()

    translation = translate(text)
    print(f'Translation characters: {len(translation)}')
    title_en = translate(article.replace('.txt', ''))
    title_en = re.sub(r'[<>:"/\\|?*]', '', title_en)
    print(f'Translated title: {title_en}')
    translation = title_en+'\n'+translation
    # Write the summary string to the file
    with open(f'podcast/{episode}/translation/' + title_en + '.txt', 'w', encoding='utf-8') as f:
        f.write(translation)

    # OpenAI TTS
    if not os.path.exists(f'podcast/{episode}/audio_en'):
        os.mkdir(f'podcast/{episode}/audio_en')
    voices = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']
    voice = voices[i % 6]
    print(f'Voice: {voice}')
    # # Read the text from the file
    # with open(f'podcast/{episode}/translation/' + title_en, 'r',encoding='utf-8') as f:
    #     translation = f.read()

    speech_file_path = Path(f'podcast/{episode}/audio_en/' + title_en + '.mp3')
    response = openai.audio.speech.create(
    model="tts-1",
    voice=voice,
    input=translation
    )
    response.stream_to_file(speech_file_path)
    print(f'Audio file saved to {speech_file_path}')

# %% Intro Elevenlabs
from elevenlabs import generate, save, voices, set_api_key
set_api_key(os.getenv('ELEVENLABS_KEY'))

intro = 'ami_en_{:03d}.txt'.format(episode_number)

# Define the template
template = '''
AMI episode {}

Monday november 13th

For this episode:

'''

# Read the articles from the directory
articles = os.listdir(f'podcast/{episode}/translation')

# Initialize an empty string to hold the formatted articles
intro_text = template.format(episode_number)

# Loop through the articles and format them
for article in articles:
    intro_text += article.replace('txt','') + '\n'

# Write the output to a file
with open(f'podcast/{episode}/' + intro, 'w', encoding='utf-8') as f:
    f.write(intro_text)

# Generate intro
voices_list = list(voices())
# print(voices_list)
voice = 'enYann'

# Generate audio for the content
audio = generate(
    text=intro_text,
    voice=voice,
    model="eleven_multilingual_v2"
)

save(audio,f'podcast/{episode}/intro_en.mp3')

# %% Edit audio
from pydub import AudioSegment
import os

def edit(episode_number):
    episode_number = int(episode_number)
    episode = 'episode' + '{:03d}'.format(episode_number)
    # Set the directory for the episode
    directory = 'podcast/' + episode 

    # Get a list of all the audio files in the directory
    audio_files = [f for f in os.listdir(directory+ '/audio_en/') if f.endswith('.mp3')]

    # Initialize an empty AudioSegment object to hold the concatenated audio
    concatenated_audio = AudioSegment.empty()

    # Add the audio to the concatenated audio
    concatenated_audio += AudioSegment.from_mp3('ami_generic.mp3')

    # Add the intro audio to the concatenated audio
    intro_audio = AudioSegment.from_mp3(directory + '/intro_en.mp3')
    concatenated_audio += intro_audio

    # Loop through the audio files and append them to the concatenated audio
    for file in audio_files:
        concatenated_audio += AudioSegment.from_mp3('ami_generic.mp3')
        audio = AudioSegment.from_mp3(directory + '/audio_en/' + file)
        concatenated_audio += audio

    # Export the concatenated audio to a file
    concatenated_audio.export(directory + f'/ami_{episode}_en.mp3', format='mp3')

edit(episode_number)
