from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from uuid import uuid4
from chat import ask_question
import os
import sys
import elastic_transport

app = Flask(__name__, static_folder="../frontend/build", static_url_path="/")
CORS(app)

print("ELASTIC_TRANSPORT_DEBUG: ", os.getenv("ELASTIC_TRANSPORT_DEBUG"))
if os.getenv("ELASTIC_TRANSPORT_DEBUG").lower() == "true":
    print("Elastic transport debug logging ENABLED.")
    elastic_transport.debug_logging()
elif os.getenv("ELASTIC_TRANSPORT_DEBUG").lower() == "false":
    print("Elastic transport debug logging DISABLED.")
else:
    print("** ELASTIC_TRANSPORT_DEBUG not set correctly. Defaulting to DISABLED. **")


@app.route("/")
def api_index():
    return app.send_static_file("index.html")


@app.route("/api/chat", methods=["POST"])
def api_chat():
    request_json = request.get_json()
    question = request_json.get("question")
    if question is None:
        return jsonify({"msg": "Missing question from request JSON"}), 400

    session_id = request.args.get("session_id", str(uuid4()))
    return Response(ask_question(question, session_id), mimetype="text/event-stream")


@app.cli.command()
def create_index():
    """Create or re-create the Elasticsearch index."""
    basedir = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(f"{basedir}/../")

    from data import index_data

    index_data.main()


if __name__ == "__main__":
    app.run(port=3001, debug=True)
