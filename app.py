from flask import Flask, render_template, request
from google.cloud import texttospeech
from google.auth.exceptions import DefaultCredentialsError

app = Flask(__name__)

def get_credentials():
    try:
        from google.auth import default
        credentials, _ = default()
        return credentials
    except DefaultCredentialsError:
        return None

def create_client():
    credentials = get_credentials()
    if credentials:
        return texttospeech.TextToSpeechClient(credentials=credentials)
    else:
        return None

client = create_client()

def text_to_speech(text):
    if client:
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="ta-IN", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        return response.audio_content
    else:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    audio_url = None
    if request.method == 'POST':
        text = request.form['couplet']
        audio_content = text_to_speech(text)
        if audio_content:
            with open('static/audio.mp3', 'wb') as audio_file:
                audio_file.write(audio_content)
            audio_url = '/audio'

    return render_template('index.html', audio_url=audio_url)

@app.route('/audio')
def audio():
    return app.send_static_file('audio.mp3')

if __name__ == '__main__':
    app.run(debug=True)
