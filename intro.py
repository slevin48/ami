from elevenlabs import generate, save, voices, set_api_key
from dotenv import load_dotenv
import os
load_dotenv()
set_api_key(os.getenv('ELEVENLABS_KEY'))
voices_list = list(voices())
# print(voices_list)
voice = 'Yann'
episode_number = 2
episode = 'episode' + '{:03d}'.format(episode_number)
intro = 'ami_{:03d}.txt'.format(episode_number)
# Read the text from the file
with open(f'podcast/{episode}/' + intro, 'r',encoding='utf-8') as f:
    text = f.read()

voice = 'Yann'

# Generate audio for the content
audio = generate(
    text=text,
    voice=voice,
    model="eleven_multilingual_v2"
)

save(audio,f'podcast/{episode}/intro.mp3')