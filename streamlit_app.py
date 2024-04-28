import streamlit as st
import openai, boto3, re, datetime
from io import BytesIO
from pydub import AudioSegment
from elevenlabs.client import ElevenLabs
# from elevenlabs import save

client11 = ElevenLabs(api_key=st.secrets['ELEVEN_API_KEY'])

st.set_page_config(page_title='AMI',
                   page_icon='🤖',
                   initial_sidebar_state='expanded',)

# Load environment variables
openai.api_key = st.secrets["OPENAI_API_KEY"]
openai_voices = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']
voices_list = list(client11.voices.get_all())
# print(voices_list)

# AWS S3 Bucket Name
BUCKET_NAME = "ami48" 

# # AWS S3 Client Initialization
# s3_client = boto3.client('s3')

# Connect to S3 using st.secrets
s3_client = boto3.client(
    's3',
    aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"]
)

# Initialize session state
if "create_article" not in st.session_state:
    st.session_state.create_article = False

# Functions for S3 Operations
def create_article_s3(title, bucket_name):
    file_path = f'{episode}/text/{title}.txt'
    s3_client.put_object(Bucket=bucket_name, Key=file_path, Body='')

def list_files_s3(bucket_name, directory):
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=directory)
    return [item['Key'] for item in response.get('Contents', [])]

def read_file_s3(bucket_name, file_path):
    response = s3_client.get_object(Bucket=bucket_name, Key=file_path)
    return response['Body'].read().decode('utf-8')

def read_audio_s3(bucket_name, file_path):
    response = s3_client.get_object(Bucket=bucket_name, Key=file_path)
    return response['Body'].read()

def write_file_s3(bucket_name, file_path, data):
    s3_client.put_object(Bucket=bucket_name, Key=file_path, Body=data)

def summarize(inst,text):
    # inst = '''Resume en moins de 1000 caracteres:''' 
    completion = openai.chat.completions.create(
        model='gpt-3.5-turbo-1106',
        messages= [
            {'role': 'system', 'content': inst },
            {'role': 'user', 'content': text }]
    )
    return completion.choices[0].message.content

def tts_s3(summary, audio_path, voice, bucket_name):
    # audio_path = f'{episode}/audio/' + article.replace('.txt', '.mp3')
    response = openai.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=summary
    )
    audio_data = BytesIO(response.content)
    s3_client.upload_fileobj(audio_data, bucket_name, audio_path)

def intro(episode_number):
    voice = 'frYann'
    episode = 'episode' + '{:03d}'.format(episode_number)
    intro = 'ami_{:03d}.txt'.format(episode_number)

    # Define the template
    template = '''Conseil d'ami
    episode {}
    '''
    # Initialize an empty string to hold the formatted articles
    intro_text = template.format(episode_number)
    intro_text += '\n'

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
    intro_text += 'Au programme de cet épisode:'
    intro_text += '\n\n'

    # Read the articles from the directory
    articles = list_files_s3(BUCKET_NAME, directory + '/text')
    articles = [article.split('/')[-1] for article in articles]
    # Loop through the articles and format them
    for article in articles:
        intro_text += article.replace('txt','') + '\n\n'
    # st.write(intro_text)
    # Generate audio for the content
    audio = client11.generate(
        text=intro_text,
        voice=voice,
        model="eleven_multilingual_v2"
    )
    # save(audio,f'podcast/{episode}/intro.mp3')
    st.audio(audio)
    audio_data = BytesIO(audio)
    s3_client.upload_fileobj(audio_data, BUCKET_NAME, f'{episode}/intro.mp3')

def edit(episode_number):
    episode_number = int(episode_number)
    episode = 'episode' + '{:03d}'.format(episode_number)
    # Set the directory for the episode
    directory = episode 

    # Get a list of all the audio files in the directory
    audio_files = list_files_s3(BUCKET_NAME, directory + '/audio')
    # audio_files = [file.split('/')[-1] for file in audio_files]
    
    # Download ami_generic.mp3 from S3 bucket
    s3_client.download_file(BUCKET_NAME, 'ami_generic.mp3', 'ami_generic.mp3')
    
    # Initialize an empty AudioSegment object to hold the concatenated audio
    concatenated_audio = AudioSegment.empty()

    # Add the audio to the concatenated audio
    concatenated_audio += AudioSegment.from_mp3('ami_generic.mp3')

    # Add the intro audio to the concatenated audio
    intro_audio = AudioSegment.from_mp3(BytesIO(read_audio_s3(BUCKET_NAME, f'{episode}/intro.mp3')))
    concatenated_audio += intro_audio
    # st.write(audio_files)
    # Loop through the audio files and append them to the concatenated audio
    for file in audio_files:
        concatenated_audio += AudioSegment.from_mp3('ami_generic.mp3')
        audio = AudioSegment.from_mp3(BytesIO(read_audio_s3(BUCKET_NAME, file)))
        concatenated_audio += audio

    # Export the concatenated audio to a file
    concatenated_audio.export(f'ami_{episode}.mp3', format='mp3')
    s3_client.upload_file(f'ami_{episode}.mp3', BUCKET_NAME, f'{episode}/ami_{episode}.mp3')

# Streamlit app
st.sidebar.title("Conseil d'ami 🤖")

password = st.sidebar.text_input('Enter password', type='password')
if password == st.secrets['PASSWORD']:

    # User input for episode number
    episode_number = st.sidebar.number_input("Enter Episode Number", min_value=1, value=2, step=1)
    episode = 'episode' + '{:03d}'.format(episode_number)

    # Create article
    if st.sidebar.button("Create Article"):
            st.session_state.create_article = True
    if st.session_state.create_article:
        if title := st.sidebar.text_input("Enter Article title", key='title'):
            title = title.replace(':', '-').replace('Les Echos - ', '')
            title = re.sub(r'[<>:"/\\|?*]', '', title)
            create_article_s3(title, BUCKET_NAME)
            st.session_state.create_article = False

    # Display articles
    directory = episode
    articles = list_files_s3(BUCKET_NAME, directory + '/text')
    # st.write(articles)
    if articles:
        article = st.sidebar.selectbox("Select an Article", articles, format_func=lambda x: x.split('/')[-1].replace('.txt', ''))
        article = article.split('/')[-1]

        # Text
        file_path = f'{episode}/text/{article}'
        if file_path in articles:
            text = read_file_s3(BUCKET_NAME, file_path)
            if st.sidebar.toggle("Edit Article", key='edit'):
                text = st.text_area('**Article**', text)
                write_file_s3(BUCKET_NAME, file_path, text)
            else:
                st.write(f'**Article:**',article.replace('.txt', ''))
                st.write(text)

        # Summary
        summary_path = f'{episode}/summary/{article}'

        with st.sidebar.expander("Summary"):
            inst = st.text_area("Enter Instructions", value='Resume en moins de 4000 caracteres:')
            if st.button("Summary"):
                summary = summarize(inst,text)
                # st.write(f'Summary characters: {len(summary)}')
                write_file_s3(BUCKET_NAME, summary_path, summary)
                # st.write("Summary generated.")
        
        summaries = list_files_s3(BUCKET_NAME, directory + '/summary')

        if summary_path in summaries:
            st.write(f'**Summary**')
            summary = read_file_s3(BUCKET_NAME, summary_path)
            st.write(summary)
            
            # Audio
            audio_path = f"{episode}/audio/{article.replace('.txt', '.mp3')}"

            with st.sidebar.expander("Text to Speech"):
                voice = st.radio("Select Voice", openai_voices)
                if st.button("TTS"):
                    tts_s3(summary, audio_path, voice, BUCKET_NAME)
                    # st.write("Audio generated.")
            
            audios = list_files_s3(BUCKET_NAME, directory + '/audio')

            if audio_path in audios:
                st.write(f'**Audio**')
                audio_url = s3_client.generate_presigned_url('get_object',
                                                            Params={'Bucket': BUCKET_NAME, 'Key': audio_path},
                                                            ExpiresIn=3600)
                st.audio(audio_url)

        # Generate intro
        with st.sidebar.expander("Generate Episode"):
            if st.button("Generate Intro"):
                intro(episode_number)
            intro_path = f"{episode}/intro.mp3"
            if intro_path in list_files_s3(BUCKET_NAME, episode):
                if st.button("Generate Episode"):
                    edit(episode_number)
                    st.write("Episode generated.")
        if f'{episode}/ami_{episode}.mp3' in list_files_s3(BUCKET_NAME, episode):
            st.sidebar.write(f'**Episode podcast**')
            episode_url = s3_client.generate_presigned_url('get_object',
                                                        Params={'Bucket': BUCKET_NAME, 'Key': f'{episode}/ami_{episode}.mp3'},
                                                        ExpiresIn=3600)
            st.sidebar.audio(episode_url)

    else:
        st.write("No articles found for the selected episode.")