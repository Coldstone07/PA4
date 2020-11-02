import sys
import heapq
sys.path.insert(0, '../')
from planet_wars import issue_order
from math import floor, ceil
import logging, traceback, sys, os, inspect


def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    #if len(state.my_fleets()) >= 2 * len(state.my_planets()):
    #    return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        if strongest_planet.num_ships * 5 / 10 > (weakest_planet.num_ships + (state.distance(strongest_planet.ID, weakest_planet.ID) * weakest_planet.growth_rate)):
            return issue_order(state, strongest_planet.ID, weakest_planet.ID, weakest_planet.num_ships + (state.distance(strongest_planet.ID, weakest_planet.ID) * weakest_planet.growth_rate) + 1)
        else:
            return False


def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    #if len(state.my_fleets()) >= 2 * len(state.my_planets()):
        #return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        #return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)
        if strongest_planet.num_ships * 5 / 10 >= weakest_planet.num_ships + 1:
            return issue_order(state, strongest_planet.ID, weakest_planet.ID, weakest_planet.num_ships + 1)
        return False

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

def spread_to_high_value_neutral_planet(state):
    #if len(state.my_fleets()) >= 2 * len(state.my_planets()):
        #return False
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)
    if strongest_planet is None:
        return False
    target_list = []
    for planet in state.neutral_planets():
        if not incoming_my_fleets(state, planet.ID) and not incoming_enemy_fleets(state, planet.ID):
            target_list.append(planet)
    if len(target_list) > 0:
        best_target = None
        best_value = 0
        for planet in target_list:
            if (((planet.growth_rate / (planet.num_ships + 1)) / state.distance(strongest_planet.ID, planet.ID)) > best_value) and (strongest_planet.num_ships * 5.5/10 > (planet.num_ships)):
                best_target = planet
                best_value = (planet.growth_rate / (planet.num_ships + 1)) / state.distance(strongest_planet.ID, planet.ID)
        if best_value == 0:
            return False
        return issue_order(state, strongest_planet.ID, best_target.ID, best_target.num_ships + 1)
    else:
        return False


def incoming_enemy_fleets(state, planetID):
    for fleet in state.enemy_fleets():
        if fleet.destination_planet == planetID:
            return True
    return False

def incoming_my_fleets(state, planetID):
    for fleet in state.my_fleets():
        if fleet.destination_planet == planetID:
            return True
    return False

def pulse_defense(state):
    for source_planet in state.my_planets():
        fleet_size = floor(source_planet.num_ships / (20 * (len(state.my_planets()) - 1)))
        if fleet_size > 0:
            for destination_planet in state.my_planets():
                if source_planet.ID != destination_planet.ID:
                    issue_order(state, source_planet.ID, destination_planet.ID, fleet_size)
    return True

def capture_close_neutral_planets(state):
    max_dist = 5
    min_ratio = 1
    success = False
    for source_planet in state.my_planets():
        target = None
        weakest_defense = 999
        for destination_planet in state.neutral_planets():
            if state.distance(source_planet.ID, destination_planet.ID) < max_dist:
                if destination_planet.num_ships < weakest_defense:
                    target = destination_planet
                    weakest_defense = destination_planet.num_ships
                    logging.exception(weakest_defense)
        if target is not None:
            if target.num_ships <= source_planet.num_ships * min_ratio:
                if not incoming_my_fleets(state, target.ID) and not incoming_enemy_fleets(state, target.ID):
                    issue_order(state, source_planet.ID, target.ID, target.num_ships + 1)
                    success = True
    return success

def capture_closest_enemy_planet_smart(state):
    max_frac = 3/4
    success = False
    closest_dist = 999
    closest_planet = None
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)
    if strongest_planet is None:
        return False
    for planet in state.enemy_planets():
        if state.distance(strongest_planet.ID, planet.ID) < closest_dist:
            closest_dist = state.distance(strongest_planet.ID, planet.ID)
            closest_planet = planet
    if not incoming_my_fleets(state, closest_planet.ID):
        req_ships = closest_planet.num_ships + 1 + closest_planet.growth_rate * state.distance(strongest_planet.ID, closest_planet.ID)
        if strongest_planet.num_ships * max_frac > req_ships:
            issue_order(state, strongest_planet.ID, closest_planet.ID, req_ships)
            success = True
    return success

def capture_closest_enemy_planet_dumb(state):
    max_frac = 3/4
    success = False
    closest_dist = 999
    closest_planet = None
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)
    if strongest_planet is None:
        return False
    for planet in state.enemy_planets():
        if state.distance(strongest_planet.ID, planet.ID) < closest_dist:
            closest_dist = state.distance(strongest_planet.ID, planet.ID)
            closest_planet = planet
    if not incoming_my_fleets(state, closest_planet.ID):
        if strongest_planet.num_ships * max_frac > closest_planet.num_ships + 1:
            issue_order(state, strongest_planet.ID, closest_planet.ID, closest_planet.num_ships + 1)
            success = True
    return success

def joint_capture_close_neutral_planet(state):
    success = False
    average_dist_dict = {}
    max_fleet_fraction = 1/20
    for destination_planet in state.neutral_planets():
        total_dist = 0
        for source_planet in state.my_planets():
            total_dist += state.distance(source_planet.ID, destination_planet.ID)
        average_dist_dict[total_dist / len(state.my_planets())] = destination_planet
    while len(average_dist_dict) > 0:
        closest_dist = min(average_dist_dict, key=average_dist_dict.get)
        closest_planet = average_dist_dict[closest_dist]
        available_ships = 0
        if not incoming_my_fleets(state, closest_planet.ID) and not incoming_enemy_fleets(state, closest_planet.ID):
            for planet in state.my_planets():
                available_ships += planet.num_ships
            if available_ships * max_fleet_fraction >= closest_planet.num_ships:
                success = True
                for source_planet in state.my_planets():
                    issue_order(state, source_planet.ID, closest_planet.ID, ceil((source_planet.num_ships / available_ships) * (closest_planet.num_ships + 1)))
                break
            else:
                average_dist_dict.pop(closest_dist)
        else:
            average_dist_dict.pop(closest_dist)
    return success






