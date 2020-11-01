import sys
import heapq
sys.path.insert(0, '../')
from planet_wars import issue_order
import logging, traceback, sys, os, inspect


def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)

def priority_attack(state):
    temp = 8
    valid_planets = {}
    for planet in state.my_planets():
        if planet.num_ships > planet.growth_rate * temp:
            valid_planets[planet] = planet.num_ships - (planet.growth_rate * temp)
    order_issued = False
    planet_priorities = []
    min_defense_mult = 4
    order_list = []
    expenditures = {}
    for planet in state.enemy_planets():
        heapq.heappush(planet_priorities, (
        (planet.num_ships + (planet.growth_rate * min_defense_mult)) / (planet.growth_rate * 0.25
                                                                        ), planet, planet.num_ships + planet.growth_rate * min_defense_mult))
    for planet in state.neutral_planets():
        heapq.heappush(planet_priorities, (
        (planet.num_ships + (planet.growth_rate * min_defense_mult)) / planet.growth_rate, planet, planet.num_ships + planet.growth_rate * min_defense_mult))
    if not planet_priorities:
        order_issued = False
        return order_issued
    target = heapq.heappop(planet_priorities)
    attacking_planets = {}
    for source_planet in valid_planets.keys():
        if valid_planets[source_planet] - target[2] >= 0:
            attacking_planets[source_planet] = target[2]
            target = (target[0], target[1], 0)
        else:
            attacking_planets[source_planet] = valid_planets[source_planet]
            target = (target[0], target[1], target[2] - valid_planets[source_planet])
        if target[2] <= 0:
            order_issued = True
            for attacker in attacking_planets.keys():
                issue_order(state, source_planet.ID, target[1].ID, attacking_planets[attacker])
                if attacker in expenditures:
                    expenditures[attacker] += attacking_planets[attacker]
                else:
                    expenditures[attacker] = attacking_planets[attacker]
            if len(planet_priorities ) > 0:
                target = heapq.heappop(planet_priorities)
                attacking_planets.clear()
            else:
                break
    return order_issued










