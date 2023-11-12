from pydub import AudioSegment
import os
import sys

def edit(episode_number):
    episode_number = int(episode_number)
    episode = 'episode' + '{:03d}'.format(episode_number)
    # Set the directory for the episode
    directory = 'podcast/' + episode 

    # Get a list of all the audio files in the directory
    audio_files = [f for f in os.listdir(directory+ '/audio/') if f.endswith('.mp3')]

    # Initialize an empty AudioSegment object to hold the concatenated audio
    concatenated_audio = AudioSegment.empty()

    # Add the audio to the concatenated audio
    concatenated_audio += AudioSegment.from_mp3('ami_generic.mp3')

    # Add the intro audio to the concatenated audio
    intro_audio = AudioSegment.from_mp3(directory + '/intro.mp3')
    concatenated_audio += intro_audio

    # Loop through the audio files and append them to the concatenated audio
    for file in audio_files:
        concatenated_audio += AudioSegment.from_mp3('ami_generic.mp3')
        audio = AudioSegment.from_mp3(directory + '/audio/' + file)
        concatenated_audio += audio

    # Export the concatenated audio to a file
    concatenated_audio.export(directory + f'/ami_{episode}.mp3', format='mp3')

if __name__ == '__main__':
    episode_number = sys.argv[1]
    # episode_number = input("Enter episode number: ")
    # episode_number = 1
    edit(episode_number)
