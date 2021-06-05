from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import os
import json

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


def map_to_indo(response):
    with open('labels_indo.json') as l_indo:
        labels_indo = json.load(l_indo)
    with open('labels_english.json') as l_eng:
        labels_english = json.load(l_eng)

    dict_labels = dict(zip(labels_english, labels_indo))
    relevant_labels_indo = [dict_labels.get(label, None) for label in response]
    relevant_labels_indo = [label.lower() for label in relevant_labels_indo if label is not None]
    return relevant_labels_indo


def get_relevan_recipes(labels_indo):
    relevant_recipes = []
    with open('resep.json') as file:
        recipes = json.load(file)

    for recipe in recipes:
        count = len(set(recipe['bahan']) & set(labels_indo))
        if count > 0:
            recipe['count'] = count
            relevant_recipes.append(recipe)
    ordered_relevant_recipes = sorted(relevant_recipes, key=lambda item: item.get("count"), reverse=True)
    return ordered_relevant_recipes


@app.route('/detect', methods=['POST'])
def detect_image():
    file = request.files['image'].stream.read()
    client = setup_boto()
    labels = detect(client, file)
    labels_indo = map_to_indo(labels)
    recipes = get_relevan_recipes(labels_indo)
    response = dict(labels=labels_indo, recipes=recipes, raw_labels=labels)
    return jsonify(response)


@app.route('/')
def index():
    return "<h1>Welcome to our server !!</h1>"


if __name__ == '__main__':
    app.run(threaded=True, port=port)
