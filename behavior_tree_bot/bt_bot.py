#!/usr/bin/env python
#

"""
// There is already a basic strategy in place here. You can use it as a
// starting point, or you can throw it out entirely and replace it with your
// own.
"""
import logging, traceback, sys, os, inspect
logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from behavior_tree_bot.behaviors import *
from behavior_tree_bot.checks import *
from behavior_tree_bot.bt_nodes import Selector, Sequence, Action, Check, Tautology_Sequence, Tautology_Selector

from planet_wars import PlanetWars, finish_turn
# You have to improve this tree or create an entire new one that is capable
# of winning against all the 5 opponent bots
def setup_behavior_tree():
    # Top-down construction of behavior tree
    #root = Sequence(name='High Level Ordering of Strategies')

    root = Sequence(name='High Level Ordering of Strategies')
    neutral_claiming = Tautology_Selector(name='Neutral Planet Claiming Strategies')
    offensive_strategies = Tautology_Selector(name='Offensive Strategies')
    defensive_strategies = Tautology_Sequence(name='Defensive Strategies')

    priority_attack_strategy = Sequence(name='Priority Attack Strategy')
    sufficient_defenses_check = Check(have_sufficient_defenses)
    p_attack = Action(priority_attack)
    priority_attack_strategy.child_nodes = [sufficient_defenses_check, p_attack]

    offensive_plan = Sequence(name='Basic Offensive Strategy')
    largest_fleet_check = Check(have_largest_fleet)
    attack = Action(attack_weakest_enemy_planet)
    offensive_plan.child_nodes = [largest_fleet_check, attack]

    spread_sequence = Sequence(name='Spread Strategy')
    neutral_planet_check = Check(if_neutral_planet_available)
    spread_action = Action(spread_to_weakest_neutral_planet)
    spread_sequence.child_nodes = [neutral_planet_check, spread_action]

    high_value_neutral_attack_plan = Sequence(name='High Value Neutral Target Strategy')
    high_value_neutral_attack = Action(spread_to_high_value_neutral_planet)
    high_value_neutral_attack_plan.child_nodes = [neutral_planet_check, high_value_neutral_attack]

    close_neutral_strategy = Sequence(name='Capture Close Neutral Strategy')
    close_neutral_action = Action(capture_close_neutral_planets)
    close_neutral_strategy.child_nodes = [neutral_planet_check.copy(), close_neutral_action]

    pulse_strategy = Sequence(name='Pulse Strategy')
    multiple_planets = Check(multiple_planets_owned)
    pulse_action = Action(pulse_defense)
    pulse_strategy.child_nodes = [multiple_planets, pulse_action]

    smart_closest_enemy_strategy = Sequence(name='Smart Attack Closest Enemy Strategy')
    enemy_planet_check = Check(if_enemy_planet_available)
    smart_closest_enemy_action = Action(capture_closest_enemy_planet_smart)
    smart_closest_enemy_strategy.child_nodes = [multiple_planets, enemy_planet_check, smart_closest_enemy_action]

    dumb_closest_enemy_strategy = Sequence(name='Dumb Attack Closest Enemy Strategy')
    enemy_planet_check = Check(if_enemy_planet_available)
    dumb_closest_enemy_action = Action(capture_closest_enemy_planet_dumb)
    dumb_closest_enemy_strategy.child_nodes = [multiple_planets, enemy_planet_check, dumb_closest_enemy_action]



    joint_capture_neutral_strategy = Sequence(name='Joint Capture Neutral Planet Strategy')
    joint_capture_neutral_action = Action(joint_capture_close_neutral_planet)

    joint_capture_neutral_strategy.child_nodes = [neutral_planet_check.copy(), multiple_planets.copy(), joint_capture_neutral_action]



    neutral_claiming.child_nodes = [close_neutral_strategy,  high_value_neutral_attack_plan, spread_sequence, joint_capture_neutral_strategy]
    offensive_strategies.child_nodes = [smart_closest_enemy_strategy, dumb_closest_enemy_strategy, offensive_plan]
    defensive_strategies.child_nodes = [pulse_strategy]
    root.child_nodes = [neutral_claiming, defensive_strategies, offensive_strategies]






    #root.child_nodes = [high_value_neutral_attack_plan, spread_sequence, offensive_plan, attack.copy()]
    #root.child_nodes = [priority_attack_strategy]

    # root.child_nodes = [high_value_neutral_attack_plan, spread_sequence, offensive_plan, attack.copy()]
    # root.child_nodes = [priority_attack_strategy]


    logging.info('\n' + root.tree_to_string())
    return root

# You don't need to change this function
def do_turn(state):
    behavior_tree.execute(planet_wars)

if __name__ == '__main__':
    logging.basicConfig(filename=__file__[:-3] + '.log', filemode='w', level=logging.DEBUG)

    behavior_tree = setup_behavior_tree()
    try:
        map_data = ''
        while True:
            current_line = input()
            if len(current_line) >= 2 and current_line.startswith("go"):
                planet_wars = PlanetWars(map_data)
                do_turn(planet_wars)
                finish_turn()
                map_data = ''
            else:
                map_data += current_line + '\n'

    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
    except Exception:
        traceback.print_exc(file=sys.stdout)
        logging.exception("Error in bot.")
