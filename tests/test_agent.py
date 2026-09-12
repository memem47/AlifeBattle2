import pygame

import config
from agent import Agent


def make_agent(agent_id: int, team: str, x: float, y: float = 0) -> Agent:
    return Agent(agent_id, team, pygame.Vector2(x, y))


def test_take_damage_and_death() -> None:
    agent = make_agent(1, config.RED, 0)

    agent.take_damage(20)
    assert agent.hp == 80
    assert agent.is_alive()

    agent.take_damage(80)
    assert agent.hp == 0
    assert not agent.is_alive()


def test_move_toward_uses_elapsed_time_and_stops_at_attack_range() -> None:
    agent = make_agent(1, config.RED, 0)

    agent.move_toward(pygame.Vector2(100, 0), 0.5)
    assert agent.position.x == config.AGENT_SPEED * 0.5

    agent.move_toward(pygame.Vector2(100, 0), 3.0)
    assert agent.position.x == 88


def test_attack_range_and_cooldown() -> None:
    attacker = make_agent(1, config.RED, 0)
    target = make_agent(2, config.BLUE, config.ATTACK_RANGE)

    assert attacker.is_in_attack_range(target)
    assert attacker.can_attack(target)

    attacker.start_attack_cooldown()
    assert not attacker.can_attack(target)
    attacker.update_cooldown(config.ATTACK_INTERVAL)
    assert attacker.can_attack(target)


def test_attack_range_allows_small_floating_point_error() -> None:
    attacker = make_agent(1, config.RED, 0)
    target = make_agent(
        2,
        config.BLUE,
        config.ATTACK_RANGE + config.DISTANCE_EPSILON / 2,
    )

    assert attacker.is_in_attack_range(target)


def test_find_nearest_living_enemy() -> None:
    agent = make_agent(1, config.RED, 0)
    nearest = make_agent(2, config.BLUE, 10)
    farther = make_agent(3, config.BLUE, 20)
    dead = make_agent(4, config.BLUE, 1)
    dead.take_damage(config.AGENT_HP)

    assert agent.find_nearest_enemy([agent, farther, dead, nearest]) is nearest


def test_calculate_separation_pushes_agent_away_from_neighbor() -> None:
    agent = make_agent(1, config.RED, 0)
    neighbor = make_agent(2, config.RED, config.AGENT_RADIUS)

    separation = agent.calculate_separation([agent, neighbor])

    assert separation.x < 0
    assert separation.y == 0