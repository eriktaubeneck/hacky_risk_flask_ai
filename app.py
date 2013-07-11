import sys
from flask import Flask, request
from risk.models import *
import json
import random

board = import_board_data('./risk/board_graph.json')

app = Flask(__name__)

@app.route("/status")
def status():
    print 'got status check'
    return ''

@app.route("/not_turn")
def not_turn():
    print 'got board'
    return ''

@app.route('/turn', methods=['POST'])
def turn():
    r = json.loads(request.form['risk'])
    available_actions = r['you']['available_actions']
    if "choose_country" in available_actions:
        countries = r['game']['countries']
        unoccupied = [c for c in countries if not countries[c]['owner']]
        country_choice = random.choice(unoccupied)
        response = {"action":"choose_country", "data":country_choice}
        print "choose: %s" % country_choice
        return json.dumps(response)
    return ''

if __name__ == '__main__':
    port = int(sys.argv[1])
    app.run(debug=True, host="0.0.0.0", port=port)
