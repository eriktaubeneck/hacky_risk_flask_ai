import sys
from flask import Flask
from risk.models import *

board, card_lookup = models.import_board_data('./risk/board_graph.json')

app = Flask(__name__)

@app.route("/status")
def status():
    print 'got status check'
    return ''

@app.route("/not_turn")
def not_turn():
    print 'got board'
    return ''


if __name__ == '__main__':
    port = int(sys.argv[1])
    app.run(debug=True, host="0.0.0.0", port=port)
