import functions_framework
import requests
import re
import ssl
from collections import Counter
from io import BytesIO, StringIO
from flask import Flask, request, jsonify, send_file
from requests.adapters import HTTPAdapter

class LegacyCipherAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        # Create a custom SSL context
        context = ssl.create_default_context()
        
        # Manually enable the specific legacy RSA ciphers the server needs
        legacy_ciphers = (
            'AES256-GCM-SHA384:AES128-GCM-SHA256:'
            'AES256-SHA256:AES128-SHA256:AES256-SHA:AES128-SHA'
        )
        context.set_ciphers(legacy_ciphers)
        
        kwargs['ssl_context'] = context
        return super(LegacyCipherAdapter, self).init_poolmanager(*args, **kwargs)

@functions_framework.http
def hello_http(request):
   """HTTP Cloud Function.
   Args:
       request (flask.Request): The request object.
       <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
   Returns:
       The response text, or any set of values that can be turned into a
       Response object using `make_response`
       <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
   
   request_json = request.get_json(silent=True)
   request_args = request.args

   if request_json and 'name' in request_json:
       name = request_json['name']
   elif request_args and 'name' in request_args:
       name = request_args['name']
   else:
       name = 'World'
   return 'Hello {}!'.format(name)
   """

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

   # Create a session and mount the adapter
   session = requests.Session()
   session.mount('https://', LegacyCipherAdapter())
   
   x = session.get(f"https://archsacyo.sportspilot.com/Scheduler/public/synccalendar.aspx?contest={contest}&team={team}")

   rep = x.text

   stmarkteams = re.findall("St. Mark[^\)]*\)", rep)
   if not stmarkteams:
       stmarkteams = re.findall("ST MARK[^\)]*\)", rep)
   if stmarkteams:
       most_common = Counter(stmarkteams).most_common()[0][0]
       most_common = most_common.replace("(", "\(")
       most_common = most_common.replace(")", "\)")
       rep = re.sub(most_common, "", rep)

   rep = re.sub("Game:\d*: ", "", rep)
   rep = re.sub("SUMMARY: *VS", "SUMMARY: @", rep)
   rep = re.sub("SUMMARY:", "SUMMARY: " + prefix, rep)
   rep = re.sub("VS", "", rep)
   rep = re.sub("  ", " ", rep)

   # Return the response in ics format
   return send_file(BytesIO(bytes(rep, 'utf8')), mimetype="text/calendar", as_attachment=True, download_name="cyo.ics")
   
   # print(rep)
   # return rep

