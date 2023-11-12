# %% AMI
from dotenv import load_dotenv
from pathlib import Path
import os,openai

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

episode_number = 2
# episode_number = int(episode_number)
episode = 'episode' + '{:03d}'.format(episode_number)
# Set the directory for the episode
directory = 'podcast/' + episode 
articles = os.listdir(f'podcast/{episode}/text')
article = articles[1]
print(article)

# %% OpenAI summary
if not os.path.exists(f'podcast/{episode}/summary'):
    os.mkdir(f'podcast/{episode}/summary')
# Read the text from the file
with open(f'podcast/{episode}/text/' + article, 'r',encoding='utf-8') as f:
    text = f.read()

summary = summarize(text)
print(f'Summary characters: {len(summary)}')
summary = article.replace('.txt', '\n')+summary
# Write the summary string to the file
with open(f'podcast/{episode}/summary/' + article, 'w', encoding='utf-8') as f:
    f.write(summary)

# %% OpenAI TTS
if not os.path.exists(f'podcast/{episode}/audio'):
    os.mkdir(f'podcast/{episode}/audio')
voices = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']
voice = voices[1]
# Read the text from the file
with open(f'podcast/{episode}/summary/' + article, 'r',encoding='utf-8') as f:
    summary = f.read()

speech_file_path = Path(f'podcast/{episode}/audio/' + article.replace('.txt', '.mp3'))
response = openai.audio.speech.create(
  model="tts-1",
  voice=voice,
  input=summary
)
response.stream_to_file(speech_file_path)
print(f'Audio file saved to {speech_file_path}')
