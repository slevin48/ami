from moviepy.editor import VideoFileClip
# Replace 'your_video.mp4' with the path to your video file
# video_path = 'your_video.mp4'
video = VideoFileClip(video_path)

# Extract audio from the video
audio = video.audio

# Replace 'extracted_audio.mp3' with the desired output audio file name
audio.write_audiofile('voice/newVoice.mp3')
