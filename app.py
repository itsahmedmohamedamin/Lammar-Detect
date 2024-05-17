from flask import Flask, request, jsonify, render_template
import boto3
import uuid
import requests
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

@app.route('/')
def index():
    welcome_message = "Welcome to the Image Uploader"
    return render_template('index.html', message=welcome_message)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    category = request.form.get('category')

    if file:
        random_name = f"{uuid.uuid4().hex}.jpg"

        try:
            s3_client.upload_fileobj(
                file,
                BUCKET_NAME,
                random_name,
            )
            print(random_name)
            # Assume the bucket is public, construct the URL
            file_url = f"https://{BUCKET_NAME}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{random_name}"

            # # Construct the URL for the external API
            url = f"http://54.237.242.84/process_request/{random_name}_{category}"
            response = requests.get(url,json={})
            print(url)
            link = response.json()['link']
            

        except Exception as e:
            return jsonify({'error': str(e)}), 500

        return jsonify({
            'message': 'File uploaded successfully',
            'random_name': random_name,
            'category': category,
            'link': link
        }), 200

    return jsonify({'error': 'Something went wrong'}), 500

if __name__ == '__main__':
    app.run(debug=True)
