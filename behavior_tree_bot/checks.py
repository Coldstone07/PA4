

def if_neutral_planet_available(state):
    return any(state.neutral_planets())

def if_enemy_planet_available(state):
    return any(state.enemy_planets())


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())


def have_sufficient_defenses(state):

    min_defense_mult = 8
    valid_planets = {}
    if len(state.not_my_planets()) <= 0:
        return False, valid_planets
    for planet in state.my_planets():
        if planet.num_ships > planet.growth_rate * min_defense_mult:
            valid_planets[planet] = planet.num_ships - (planet.growth_rate * min_defense_mult)
    if len(valid_planets) > 0:
        return True, valid_planets
    else:
        return False, valid_planets


def multiple_planets_owned(state):
    if len(state.my_planets()) > 1:
        return True
    else:
        return False


def enemy_fleets_attacking(state):
    for fleet in state.enemy_fleets():
        for planet in state.my_planets():
            if fleet.destination_planet == planet.ID:
                return True
    return False
