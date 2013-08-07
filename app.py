import sys
import os
from flask import Flask, request
from risk.models import *
import json
import random

pass_prob = os.environ.get('PASS_PROB') or 0.0
pass_prob = float(pass_prob)

app = Flask(__name__)

def unpack_json(r):
    board = import_board_data('./risk/board_graph.json')
    me_data = r['you']
    game = r['game']
    me = Player(me_data['name'])
    me.earned_cards_this_turn = me_data['earned_cards_this_turn']
    me.is_eliminated = me_data['is_eliminated']
    me.troops_to_deploy = me_data['troops_to_deploy']
    me.available_actions = me_data['available_actions']
    me.countries = [board.countries[c] for c in me_data['countries']]
    me.cards = [board.cards[c['country_name']] for c in me_data['cards']]
    players = {n:Player(n) for n in game['players'] if n != me.name}
    players[me.name] = me
    players['none'] = None
    for country_name in game['countries']:
        board.countries[country_name].owner = players[game['countries'][country_name]['owner']]
        board.countries[country_name].troops = game['countries'][country_name]['troops']
    return me, players, board

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
    r = json.loads(request.data)
    me, players, board = unpack_json(r['risk'])
    print me.available_actions
    if "choose_country" in me.available_actions:
        unoccupied = [c for c in board.countries.values() if not c.owner]
        country_choice = random.choice(unoccupied)
        response = {"action":"choose_country", "data":country_choice.name}
        print "choose: %s" % country_choice
        return json.dumps(response)
    elif "deploy_troops" in me.available_actions:
        troops_to_deploy = me.troops_to_deploy
        deploy_orders = {}
        for _ in range(troops_to_deploy):
            c = random.choice(me.countries)
            deploy_orders[c.name] = deploy_orders.setdefault(c.name,0) + 1
        response = {"action":"deploy_troops", "data":deploy_orders}
        print "deploy orders: %s" % deploy_orders
        return json.dumps(response)
    elif "attack" in me.available_actions:
        possible_attacks = [(c1,c2)
                            for c1 in me.countries
                            for c2 in c1.border_countries
                            if c1.troops > 1 
                            and c2 not in me.countries]
        if not possible_attacks or random.random() < pass_prob:
            response = {"action":"end_attack_phase"}
            print "ended attack phase"
        else:
            attacking_country, defending_country = random.choice(possible_attacks)
            attacking_troops = min(3, attacking_country.troops-1)
            moving_troops = random.randint(0,max(0,attacking_country.troops-4))
            data = {'attacking_country':attacking_country.name,
                    'defending_country':defending_country.name,
                    'attacking_troops':attacking_troops,
                    'moving_troops':moving_troops}
            response = {'action':'attack', 'data':data}
            print "attacking %s from %s with %s troops" % (defending_country.name,
                                                           attacking_country.name,
                                                           attacking_troops)
        return json.dumps(response)
    elif "reinforce" in me.available_actions:
        reinforce_countries = [(c1,c2) for c1 in me.countries
                                for c2 in c1.border_countries
                                if c1.troops > 1
                                and c2 in me.countries]
        if not reinforce_countries:
            print "ended turn"
            response = {"action":"end_turn"}
            return json.dumps(response)
        (origin_country,destination_country) = random.choice(reinforce_countries)
        moving_troops = random.randint(1,origin_country.troops-1)
        print "reinforced %s from %s with %s troops" % (origin_country.name, destination_country.name, moving_troops)
        response = {'action':'reinforce', 'data':{'origin_country':origin_country.name,
                                                  'destination_country':destination_country.name,
                                                  'moving_troops':moving_troops}}
        return json.dumps(response)
    elif "spend_cards" in me.available_actions:
        combos = itertools.combinations(me.cards,3)
        potential_sets = [c for c in combos if c[0].is_set_with(c[1],c[2])]
        trade_in = random.choice(potential_sets)
        trade_in = [c.country_name for c in trade_in]
        response = {'action':'spend_cards', 'data':trade_in}
        print "traded in cards %s" % trade_in
        return json.dumps(response)
    print "something broke"
    return ''

