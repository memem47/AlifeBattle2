import pygame
import pytest

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


def test_calculate_command_movement_uses_elapsed_time_and_normalized_direction() -> None:
    agent = make_agent(1, config.RED, 0)

    movement = agent.calculate_command_movement(
        pygame.Vector2(1, 0), 
        0.5,
    )
    assert movement == pygame.Vector2(
        config.AGENT_SPEED * 0.5,
        0,
    )

    movement = agent.calculate_command_movement(
        pygame.Vector2(10, 0), 
        0.5,
    )
    assert movement == pygame.Vector2(
        config.AGENT_SPEED * 0.5,
        0,
    )

def test_calculate_command_movement_returns_zero_for_zero_direction() -> None:
    agent = make_agent(1, config.RED, 0)

    movement = agent.calculate_command_movement(
        pygame.Vector2(),
        0.5,
    )

    assert movement == pygame.Vector2()


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

def test_agent_size_scale_controls_visual_and_physical_radius() -> None:
    normal = Agent(
        1,
        config.RED,
        pygame.Vector2(),
    )

    large = Agent(
        2,
        config.RED,
        pygame.Vector2(),
        size_scale=1.5,
    )

    assert normal.visual_radius == pytest.approx(
        config.DEFAULT_AGENT_VISUAL_RADIUS
    )
    assert normal.physical_radius == pytest.approx(
        config.DEFAULT_AGENT_PHYSICAL_RADIUS
    )

    assert large.visual_radius == pytest.approx(
        normal.visual_radius * 1.5
    )
    assert large.physical_radius == pytest.approx(
        normal.physical_radius * 1.5
    )

def test_physical_radius_is_smaller_than_visual_radius() -> None:
    agent = Agent(
        1,
        config.RED,
        pygame.Vector2(),
    )

    assert agent.physical_radius < agent.visual_radius