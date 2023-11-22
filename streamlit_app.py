import streamlit as st
import openai, boto3, re
from io import BytesIO

# Load environment variables
openai.api_key = st.secrets["OPENAI_API_KEY"]
voices = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']

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

def write_file_s3(bucket_name, file_path, data):
    s3_client.put_object(Bucket=bucket_name, Key=file_path, Body=data)

def summarize(text):
    inst = '''Resume en moins de 1000 caracteres:''' 
    completion = openai.chat.completions.create(
        model='gpt-3.5-turbo-1106',
        messages= [
            {'role': 'system', 'content': inst },
            {'role': 'user', 'content': text }]
    )
    return completion.choices[0].message.content

def tts_s3(summary, article, episode, voice, bucket_name):
    speech_file_path = f'{episode}/audio/' + article.replace('.txt', '.mp3')
    response = openai.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=summary
    )
    audio_data = BytesIO(response.content)
    s3_client.upload_fileobj(audio_data, bucket_name, speech_file_path)

# Streamlit app
st.title("AMI 🤖 Artificial Market Intelligence")

# User input for episode number
episode_number = st.number_input("Enter Episode Number", min_value=1, value=2, step=1)
episode = 'episode' + '{:03d}'.format(episode_number)

# Create article
if st.button("Create Article"):
        st.session_state.create_article = True
if st.session_state.create_article:
    if title := st.text_input("Enter Article title", key='title'):
        title = title.replace(':', '-').replace('Les Echos - ', '')
        title = re.sub(r'[<>:"/\\|?*]', '', title)
        create_article_s3(title, BUCKET_NAME)
        st.session_state.create_article = False

# Display articles
directory = episode
articles = list_files_s3(BUCKET_NAME, directory + '/text')
# st.write(articles)
if articles:
    article = st.selectbox("Select an Article", articles, format_func=lambda x: x.split('/')[-1].replace('.txt', ''))
    article = article.split('/')[-1]

    # Text
    file_path = f'{episode}/text/{article}'
    if file_path in articles:
        text = read_file_s3(BUCKET_NAME, file_path)
        if st.toggle("Edit Article", key='edit'):
            text = st.text_area('**Article**', text)
            write_file_s3(BUCKET_NAME, file_path, text)
        else:
            st.write(f'**Article:**',article.replace('.txt', ''))
            st.write(text)

    # Summary
    summary_path = f'{episode}/summary/{article}'
    summaries = list_files_s3(BUCKET_NAME, directory + '/summary')

    if summary_path not in summaries:
        if st.button("Summary"):
            summary = summarize(text)
            st.write(f'Summary characters: {len(summary)}')
            write_file_s3(BUCKET_NAME, summary_path, summary)
            st.write("Summary generated.")
            st.write(summary)
    else:
        st.write(f'**Summary**')
        summary = read_file_s3(BUCKET_NAME, summary_path)
        st.write(summary)

        # Audio
        audio_path = f'{episode}/audio/' + article.replace('.txt', '.mp3')
        audios = list_files_s3(BUCKET_NAME, directory + '/audio')
        if audio_path in audios:
            st.write(f'**Audio**')
            audio_url = s3_client.generate_presigned_url('get_object',
                                                        Params={'Bucket': BUCKET_NAME, 'Key': audio_path},
                                                        ExpiresIn=3600)
            st.audio(audio_url)
        else:
            voice = st.radio("Select Voice", voices)
            if st.button("TTS"):
                tts_s3(summary, article, episode, voice, BUCKET_NAME)
                st.write("Audio generated.")
                audio_url = s3_client.generate_presigned_url('get_object',
                                                            Params={'Bucket': BUCKET_NAME, 'Key': audio_path},
                                                            ExpiresIn=3600)
                st.audio(audio_url)

else:
    st.write("No articles found for the selected episode.")