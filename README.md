# Artificial Market Intelligence 🤖

https://github.com/slevin48/ami/assets/12418115/6d12b2dd-b349-48be-bdf9-4efafae4e0bf

## Summary

```python
def summarize(text):
    inst = '''Resume l'article suivant en moins de 1000 caracteres:''' 
    completion = openai.chat.completions.create(
        model='gpt-3.5-turbo-1106',
        messages= [
            {'role': 'system', 'content': inst },
            {'role': 'user', 'content': text }]
    )
    return completion.choices[0].message.content

```

## Text to Speech

```python
def text_to_speech(text, voice='fable'):
    speech_file_path = Path(f'podcast/{episode}/audio/' + article.replace('.txt', '.mp3'))
    response = openai.audio.speech.create(
    model="tts-1",
    voice=voice,
    input=summary
    )
    response.stream_to_file(speech_file_path)
    return response.result
```

## Translation

[translate_log.txt](translate_log.txt) contains the log of the translation process:
```
Iteration 0: Les embauches de cadres marquent le pas mais résistent toujours.txt
Translation characters: 459
Translated title: The hiring of executives is slowing down but still holding steady.
Voice: alloy
Audio file saved to podcast\episode003\audio_en\The hiring of executives is slowing down but still holding steady..mp3
Iteration 1: Nikki Haley joue sa carte dans la primaire républicaine.txt
Translation characters: 629
Translated title: Nikki Haley is playing her hand in the Republican primary.
Voice: echo
Audio file saved to podcast\episode003\audio_en\Nikki Haley is playing her hand in the Republican primary..mp3
Iteration 2: Nucléaire - les petits réacteurs essuient un revers aux Etats-Unis.txt
Translation characters: 465
Translated title: Nuclear - small reactors suffer a setback in the United States
Voice: fable
Audio file saved to podcast\episode003\audio_en\Nuclear - small reactors suffer a setback in the United States.mp3
Iteration 3: Présidentielle américaine 2024 - Donald Trump fait la course en tête.txt
Translation characters: 509
Translated title: 2024 American Presidential Election - Donald Trump in the lead
Voice: onyx
Audio file saved to podcast\episode003\audio_en\2024 American Presidential Election - Donald Trump in the lead.mp3
Iteration 4: Trump II - le même en pire.txt
Translation characters: 525
Translated title: Trump II - the same but worse
Voice: nova
Audio file saved to podcast\episode003\audio_en\Trump II - the same but worse.mp3
Iteration 5: « Je suis devenu président grâce à ma marque », se vante Trump à son procès.txt
Translation characters: 488
Translated title: I became president because of my brand, boasts Trump at his trial.
Voice: shimmer
Audio file saved to podcast\episode003\audio_en\I became president because of my brand, boasts Trump at his trial..mp3
```
