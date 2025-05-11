from flask import Flask, render_template, request, redirect, url_for # type: ignore
# import requests
import os
import sys
import urllib.parse

app = Flask(__name__)
app.debug = True
conversations = [
    {"id": 1, "conversation_name": "None"}
]

users = [
    {"first_name": "Enter", "last_name": "Name"}
]

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/welcome", methods=["GET", "POST"])
def welcome():
    if request.method == "POST":
        result = request.form 
        users[0] = {
            "first_name": result.get("first_name", ""),
            "last_name": result.get("last_name", "")
            }
        conversations[0] = {
            "id": 1,
            "conversation_name": result.get("conversation_name", "")
        }
        name = f"{users[0]['first_name']}"
        print(users[0], file=sys.stderr)
        print(conversations[0], file=sys.stderr)
        return render_template("welcome.html", result=result, name=name)
    return render_template("welcome.html", result={})
    # return redirect(url_for('success', name=user)) use redirect like this to send to different endpoint
    
@app.route("/join_conversation", methods=["GET"])
def join_conversation():
    user = f"{users[0]['first_name']} {users[0]['last_name']}"
    conv = conversations[0]['conversation_name']
    # redirect_url = f"http://transcriber-service:8002/start?user={urllib.parse.quote(user)}&conv={urllib.parse.quote(conv)}"
    redirect_url = f"http://localhost:8002/start?user={urllib.parse.quote(user)}&conv={urllib.parse.quote(conv)}"
    return redirect(redirect_url)



if __name__ == '__main__':
    app.run(debug=True, port=5005)
