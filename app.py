import sys
from flask import Flask, request
from risk.models import *
import json
import random

pass_prob = float(sys.argv[2])


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
#    print r
    me = r['you']
    game = r['game']
    available_actions = me['available_actions']
    print available_actions
    if "choose_country" in available_actions:
        countries = game['countries']
        unoccupied = [c for c in countries if countries[c]['owner'] == 'none']
        country_choice = random.choice(unoccupied)
        response = {"action":"choose_country", "data":country_choice}
        print "choose: %s" % country_choice
        return json.dumps(response)
    elif "deploy_troops" in available_actions:
        troops_to_deploy = me['troops_to_deploy']
        name = me['name']
        countries = game['countries']
        my_countries = [c for c in countries if countries[c]['owner'] == name]
        deploy_orders = {}
        print troops_to_deploy
        for _ in range(troops_to_deploy):
            c = random.choice(my_countries)
            deploy_orders[c] = deploy_orders.setdefault(c,0) + 1
        response = {"action":"deploy_troops", "data":deploy_orders}
        print "deploy orders: %s" % deploy_orders
        return json.dumps(response)
    elif "attack" in available_actions:
        name = me['name']
        countries = game['countries']
        countries_obj = [board.countries[c] for c in countries]
        my_countries = [c for c in countries if countries[c]['owner'] == name]
        my_countries_obj = [board.countries[c] for c in my_countries]
        possible_attacks = [(c1,c2)
                            for c1 in my_countries_obj
                            for c2 in c1.border_countries
                            if countries[c1.name]['troops'] > 1 
                            and countries[c2.name]['owner'] != name]
        if not possible_attacks or random.random() < pass_prob:
            response = {"action":"end_attack_phase"}
            print "ended attack phase"
            return json.dumps(response)
        attacking_country, defending_country = random.choice(possible_attacks)
        attacking_troops = min(3, countries[attacking_country.name]['troops']-1)
        moving_troops = random.randint(0,max(0,countries[attacking_country.name]['troops']-4))
        data = {'attacking_country':attacking_country.name,
                'defending_country':defending_country.name,
                'attacking_troops':attacking_troops,
                'moving_troops':moving_troops}
        response = {'action':'attack', 'data':data}
        print json.dumps(response)
        print "attacking %s from %s with %s troops" % (defending_country.name,
                                                       attacking_country.name,
                                                       attacking_troops)
        return json.dumps(response)
    elif "reinforce" in available_actions:
        print "ended turn"
        response = {"action":"end_turn"}
        return json.dumps(response)
    elif "spend_cards" in available_actions:
        print me['cards']
        cards = [board.cards[c['country_name']] for c in me['cards']]
        combos = itertools.combinations(cards,3)
        potential_sets = [c for c in combos if c[0].is_set_with(c[1],c[2])]
        trade_in = random.choice(potential_sets)
        trade_in = [c.country_name for c in trade_in]
        response = {'action':'spend_cards', 'data':trade_in}
        print "traded in cards %s" % trade_in
        return json.dumps(response)
    print "something broke"
    return ''

if __name__ == '__main__':
    port = int(sys.argv[1])
    app.run(debug=True, host="0.0.0.0", port=port)
