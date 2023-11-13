from moviepy.editor import AudioFileClip

# Replace 'your_audio.mp3' with the path to your audio file
audio_path = 'voice/newVoice.mp3'
audio = AudioFileClip(audio_path)

# Length of the audio in seconds
audio_length = audio.duration

# Duration of each chunk in seconds (1 minute = 60 seconds)
chunk_duration = 60

# Loop to create audio chunks
for start_time in range(0, int(audio_length), chunk_duration):
    end_time = min(start_time + chunk_duration, audio_length)
    audio_chunk = audio.subclip(start_time, end_time)

    # Create a filename for each chunk
    chunk_filename = f'voice/newVoice_chunk_{start_time//60}-{end_time//60}.mp3'
    
    # Write the audio chunk to a file
    audio_chunk.write_audiofile(chunk_filename, codec='libmp3lame')
