from flask import Flask, request, jsonify
import speech_recognition as spr
from translate import Translator
from pydub import AudioSegment
from flask_cors import CORS
from io import BytesIO

app = Flask(__name__)
CORS(app)

def recognize(input_audio_file):
    # Convert audio file to wav using Pydub
    audio = AudioSegment.from_file(input_audio_file)
    
    # Convert AudioSegment to bytes
    buffer = BytesIO()
    audio.export(buffer, format="wav")
    buffer.seek(0)
    

    recognizer = spr.Recognizer()
    text = ""  # Initialize text variable to return it even in case of exceptions

    with spr.AudioFile(buffer) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language='ur-PK')
        except spr.UnknownValueError:
            text = "Speech recognition could not understand the audio"
        except spr.RequestError as e:
            text = f"Error during speech recognition: {e}"

    return text

def translate_urdu_to_english(text):
    translator = Translator(to_lang="en", from_lang="ur")
    translated_text = translator.translate(text)
    return translated_text

@app.route('/recognize', methods=['POST'])
def api_recognize():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.endswith('.wav'):
        text = recognize(file)
        return jsonify({"recognized_text": text})
    else:
        return jsonify({"error": "Unsupported file format"}), 400

@app.route('/translate', methods=['POST'])
def api_translate():
    if not request.json or 'text' not in request.json:
        return jsonify({"error": "No text provided"}), 400
    text = request.json['text']
    translated_text = translate_urdu_to_english(text)
    return jsonify({"translated_text": translated_text})

if __name__ == '__main__':
    app.run(debug=True)
