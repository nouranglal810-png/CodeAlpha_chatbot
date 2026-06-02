"""
====================================================
 Smart Chatbot Server  —  CodeAlpha Internship
====================================================
Flask web server that connects the chatbot engine
to the web-based UI.

Routes:
  GET  /      — Serves the chat interface
  POST /chat  — Receives user message, returns bot response
====================================================
"""

from flask import Flask, render_template, request, jsonify
from chatbot_engine import get_response

app = Flask(__name__)


@app.route("/")
def home():
    """Serve the main chat interface."""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """
    API endpoint for chat messages.
    Expects JSON: {"message": "user text"}
    Returns JSON: {"response": "bot reply", "source": "pattern|wikipedia|web"}
    """
    try:
        data = request.get_json()
        user_message = data.get("message", "")

        # Get response from chatbot engine
        result = get_response(user_message)

        return jsonify(result)

    except Exception as e:
        return jsonify({
            "response": "Oops! Something went wrong. Please try again.",
            "source": "error"
        }), 500


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  SmartBot Server is running!")
    print("  Open http://localhost:5000 in your browser")
    print("=" * 50 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
