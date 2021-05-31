from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import os

app = Flask(__name__)
CORS(app)
access_key_id = os.environ.get("ACCESS_KEY_ID")
secret_access_key = os.environ.get("SECRET_ACCESS_KEY")
port = int(os.environ.get("PORT", 5000))


def setup_boto():
    return boto3.client('rekognition',
                        aws_access_key_id=access_key_id,
                        aws_secret_access_key=secret_access_key,
                        region_name='us-east-2')


def detect(client, file):
    response = client.detect_labels(
        Image={
            'Bytes': file
        },
        MaxLabels=10,
    )
    labels = response['Labels']
    results = []
    for label in labels:
        if label['Confidence'] >= 50:
            results.append(label['Name'])
    return results


@app.route('/detect', methods=['POST'])
def coba():
    file = request.files['image'].stream.read()
    client = setup_boto()
    response = detect(client, file)
    return jsonify(response)


@app.route('/')
def index():
    return "<h1>Welcome to our server !!</h1>"


if __name__ == '__main__':
    app.run(threaded=True, port=port)

