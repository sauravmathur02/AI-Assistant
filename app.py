from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_session import Session
import json
from dotenv import load_dotenv

from message_handler import handle_message
from services.state_service import (
    set_mute,
    get_mute,
    set_knowledge_mode
)

# -------------------------------------------------
# App setup
# -------------------------------------------------

load_dotenv()

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# -------------------------------------------------
# Dummy user system (demo only)
# -------------------------------------------------

users = {
    "admin": "admin123",
    "test": "test123"
}

# -------------------------------------------------
# Routes
# -------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username] == password:
            session["user"] = username
            return redirect(url_for("home"))

        return "Invalid credentials. Please try again."

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users:
            return "Username already exists."

        users[username] = password
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route("/")
def home():
    if "user" in session:
        return render_template("index.html")
    return redirect(url_for("login"))


# -------------------------------------------------
# API endpoints
# -------------------------------------------------

@app.route("/api/message", methods=["POST"])
def message():
    if "user" not in session:
        return jsonify({"response": "Unauthorized"}), 401

    user_message = request.json.get("message", "")
    response_message = handle_message(user_message, None)
    return jsonify({"response": response_message})


@app.route("/api/toggle_mute", methods=["POST"])
def toggle_mute():
    new_state = request.json.get("mute", False)
    set_mute(new_state)
    return jsonify({"is_muted": new_state})


@app.route("/api/toggle_knowledge", methods=["POST"])
def toggle_knowledge():
    is_on = request.json.get("on", False)
    set_knowledge_mode(is_on)
    return jsonify({"knowledge_mode": is_on})


@app.route("/api/stop_speech", methods=["POST"])
def stop_speech():
    # Speech is async + queued, no hard stop needed
    return jsonify({"status": "speech handled asynchronously"})

@app.route("/api/get_mute", methods=["GET"])
def api_get_mute():
    from services.state_service import get_mute
    return jsonify({"is_muted": get_mute()})

# -------------------------------------------------
# Run
# -------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
