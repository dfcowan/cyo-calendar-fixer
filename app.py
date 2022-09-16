import requests
import re
from io import BytesIO, StringIO
from flask import Flask, request, jsonify, send_file
app = Flask(__name__)

@app.route('/getcal', methods=['GET'])
def respond():
    response = {}

    # Retrieve the contest from url parameter
    contest = request.args.get("contest", None)
    error = False
    # For debugging
    # print(f"got contest {contest}")
    # Check if user sent a contest at all
    if not contest:
        response["ERROR"] = "no contest found, please send a contest."
        error = True
    # Check if the user entered a number
    elif not(str(contest).isdigit()):
        response["ERROR"] = "contest must be numeric."
        error = True


    # Retrieve the team from url parameter
    team = request.args.get("team", None)
    # For debugging
    # print(f"got team {team}")
    # Check if user sent a team at all
    if not team:
        response["ERROR"] = "no team found, please send a team."
        error = True
    # Check if the user entered a number
    elif not(str(team).isdigit()):
        response["ERROR"] = "team must be numeric."
        error = True

    # Retrieve the prefix from url parameter
    prefix = request.args.get("prefix", None)
    # For debugging
    # print(f"got prefix {prefix}")
    # Check if user sent a prefix at all
    if not prefix:
        prefix = ""

    if error:
        return jsonify(response)

    x = requests.get(f"http://archsacyo.sportspilot.com/Scheduler/public/synccalendar.aspx?contest={contest}&team={team}")

    rep = x.text
    rep = re.sub("St. Mark[^\)]*\)", "", rep)
    rep = re.sub("Game:\d*: ", prefix + " ", rep)
    rep = re.sub(" VS ", "", rep)

    # print(rep)

    # Return the response in json format
    return send_file(BytesIO(bytes(rep, 'utf8')), mimetype="text/calendar", as_attachment=True, download_name="cyo.ics")

# A welcome message to test our server
@app.route('/')
def index():
    return "<h1>Welcome to our server !!</h1>"

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)





