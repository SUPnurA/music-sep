from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from spleeter.separator import Separator

app = Flask(__name__)
CORS(app)
FILEPATH={}

@app.route('/split-audio', methods=['POST'])
def split_audio():
    if 'file' not in request.files:
        return 'No file uploaded', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No file selected', 400
    
    if file:
        file.save(file.filename)
        output_dir = './output'
        separator = Separator('spleeter:4stems')
        separator.separate_to_file(file.filename, output_dir)

        # Get the base URL of the server
        server_url = request.host_url
        global FILEPATH
        FILEPATH = {
                       "vocals":os.path.join(server_url, 'audio', f"{os.path.splitext(file.filename)[0]}", 'vocals.wav').replace('\\', '/'),
                       "bass":os.path.join(server_url, 'audio', f"{os.path.splitext(file.filename)[0]}", 'bass.wav').replace('\\', '/'),
                       "drums":os.path.join(server_url, 'audio', f"{os.path.splitext(file.filename)[0]}", 'drums.wav').replace('\\', '/'),
                       'other':os.path.join(server_url, 'audio', f"{os.path.splitext(file.filename)[0]}", 'other.wav').replace('\\', '/')
                    }

        # Return URLs for each stem file, replacing backslashes with forward slashes
        return jsonify(success=True,
                       vocals=os.path.join(server_url, 'audio', f"{os.path.splitext(file.filename)[0]}", 'vocals.wav').replace('\\', '/'),
                       bass=os.path.join(server_url, 'audio', f"{os.path.splitext(file.filename)[0]}", 'bass.wav').replace('\\', '/'),
                       drums=os.path.join(server_url, 'audio', f"{os.path.splitext(file.filename)[0]}", 'drums.wav').replace('\\', '/'),
                       other=os.path.join(server_url, 'audio', f"{os.path.splitext(file.filename)[0]}", 'other.wav').replace('\\', '/'))

    return 'Unknown error', 500

@app.route('/audio/<path:filename>')
def download_file(filename):
    return send_file(os.path.join('./output', filename), as_attachment=True)

@app.route('/playback-urls', methods=['GET'])
def get_playback_urls():
    try:
        global FILEPATH
        data = FILEPATH
        if data is None:
            return jsonify(success=False, message='No JSON body found in the request')

        vocalsurl = data['vocals']
        bassurl = data['bass']
        drumsurl = data['drums']
        otherurl = data['other']

        # Return the URLs as a JSON response
        return jsonify(success=True,
                       vocalsurl=vocalsurl,
                       bassurl=bassurl,
                       drumsurl=drumsurl,
                       otherurl=otherurl)
    except Exception as e:
        print(f"Error getting playback URLs: {e}")
        return jsonify(success=False)
       



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')