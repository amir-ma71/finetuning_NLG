from flask import Flask, Blueprint, request, jsonify
from werkzeug.exceptions import HTTPException
import json
from GPT2_Sentiment_topic_TxtGen_En import GPT2_Sentiment

# bp = Blueprint('sentiment_topic_text_generation', __name__)
app = Flask(__name__)

gpt2 = GPT2_Sentiment()
model = gpt2.load_finetuneModel()


# @app.errorhandler(HTTPException)
# def handle_exception(e):
#     response = e.get_response()
#     response.data = json.dumps({
#         "code": e.code,
#         "name": e.name,
#         "description": e.description,
#     })
#     response.content_type = "application/json"
#     return response


@app.route('/TxtGen', methods=['POST'])
def text_generationAPI():
    data = request.get_json(force=True)
    if not data:
        return jsonify({'code': 400, 'name': 'Bad Request', 'description': 'The request body are empty!'}), 400
    if 'text' not in data:
        return jsonify(
            {'code': 400, 'name': 'Bad Request', 'description': 'The "text" field not found in request body'}), 400
    else:
        begin_texts = data['text']
    if 'sentiment' not in data:
        return jsonify(
            {'code': 400, 'name': 'Bad Request', 'description': 'The "sentiment" field not found in request body'}), 400
    else:
        sentiment = data['sentiment']
    if 'topic' not in data:
        return jsonify(
            {'code': 400, 'name': 'Bad Request', 'description': 'The "topic" field not found in request body'}), 400
    else:
        topic = data['topic']
    if 'dialect' not in data:
        return jsonify(
            {'code': 400, 'name': 'Bad Request', 'description': 'The "dialect" field not found in request body'}), 400
    else:
        dialect = data['dialect']

    text_num = data['text_num'] if 'text_num' in data else 5
    result = gpt2.generate_newTexts(model, texts=begin_texts, sent_label=sentiment, topic_label=topic,
                                    dialect_label=dialect, texts_num=text_num)
    return jsonify(result), 200


# app.register_blueprint(bp, url_prefix='/v1')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# /v1/TxtGen/
# {
#      "sentiment": "positive",
#      "topic":"political",
#      "text_num": 5,
#      "text": ["today", "Zahra and her husband", "Iran", "Joe Biden tells"]
# }

# http://localhost:5000/v1/TxtGen
