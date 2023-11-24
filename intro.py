# %%
from elevenlabs import generate, save, voices, set_api_key
from dotenv import load_dotenv
import os, datetime
load_dotenv()
set_api_key(os.getenv('ELEVENLABS_KEY'))
voices_list = list(voices())
# print(voices_list)
voice = 'frYann'
episode_number = 4
episode = 'episode' + '{:03d}'.format(episode_number)
intro = 'ami_{:03d}.txt'.format(episode_number)

# %%
# Define the template
template = '''Conseil d'ami
episode {}
'''
# Initialize an empty string to hold the formatted articles
intro_text = template.format(episode_number)
intro_text += '\n'

# %%
# Get the current date
current_date = datetime.datetime.now()

# Format the date as date & month
formatted_date = current_date.strftime("%d")
formatted_month = current_date.strftime("%B")
# Create a lookup table for English to French month names
month_lookup = {
    "January": "janvier",
    "February": "février",
    "March": "mars",
    "April": "avril",
    "May": "mai",
    "June": "juin",
    "July": "juillet",
    "August": "août",
    "September": "septembre",
    "October": "octobre",
    "November": "novembre",
    "December": "décembre"
}

# Print the formatted date
# print(formatted_date,month_lookup[formatted_month])
intro_text += f'{formatted_date} {month_lookup[formatted_month]}'
intro_text += '\n\n'

# %%
intro_text += 'Au programme de cet épisode:'
intro_text += '\n\n'

# Read the articles from the directory
articles = os.listdir(f'podcast/{episode}/text')

# Loop through the articles and format them
for article in articles:
    intro_text += article.replace('txt','') + '\n'
# %% Generate intro
# Write the text in intro file
with open(f'podcast/{episode}/' + intro, 'w',encoding='utf-8') as f:
    f.write(intro_text)

# %% Generate intro
# Read the text from the file
with open(f'podcast/{episode}/' + intro, 'r',encoding='utf-8') as f:
    text = f.read()

# Generate audio for the content
audio = generate(
    text=text,
    voice=voice,
    model="eleven_multilingual_v2"
)

save(audio,f'podcast/{episode}/intro.mp3')