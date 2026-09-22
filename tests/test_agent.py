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


def test_calculate_target_movement_uses_elapsed_time_and_stops_at_attack_range() -> None:
    agent = make_agent(1, config.RED, 0)

    target_movement = agent.calculate_target_movement(
        pygame.Vector2(100, 0), 0.5
    )
    assert target_movement.x == config.AGENT_SPEED * 0.5

    target_movement = agent.calculate_target_movement(
        pygame.Vector2(100, 0), 4.0
       )
    assert target_movement.x == 100 - config.ATTACK_RANGE


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

    assert agent.find_nearest_enemy([farther, dead, nearest]) is nearest


def test_calculate_separation_pushes_agent_away_from_neighbor() -> None:
    agent = make_agent(1, config.RED, 0)
    neighbor1 = make_agent(2, config.RED, 1)
    neighbor2 = make_agent(3, config.RED, 2)

    separation = agent.calculate_separation(
        [agent, neighbor1,neighbor2]
        )

    assert abs(
        separation.length()
        - config.MAX_SEPARATION_SPEED
    ) < 1e-6

def test_facing_direction_updates_only_for_non_zero_movement() -> None:
    agent = make_agent(1, config.RED, 0)

    agent.update_facing_direction(pygame.Vector2(0, 4))
    assert agent.facing_direction == pygame.Vector2(0, 1)

    agent.update_facing_direction(pygame.Vector2())
    assert agent.facing_direction == pygame.Vector2(0, 1)