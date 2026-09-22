import pygame

import config
from agent import Agent
from game import Game
from renderer import draw_agent, draw_game, get_agent_color, get_triangle_points


def make_agent(hp: float, team: int = config.RED) -> Agent:
    agent = Agent(1, team, pygame.Vector2(50, 50))
    agent.hp = hp
    return agent


def test_health_colors_have_three_levels_per_team() -> None:
    assert get_agent_color(make_agent(100, config.RED)) == config.RED_HEALTHY_COLOR
    assert get_agent_color(make_agent(60, config.RED)) == config.RED_DAMAGED_COLOR
    assert get_agent_color(make_agent(30, config.RED)) == config.RED_CRITICAL_COLOR
    assert get_agent_color(make_agent(100, config.BLUE)) == config.BLUE_HEALTHY_COLOR
    assert get_agent_color(make_agent(60, config.BLUE)) == config.BLUE_DAMAGED_COLOR
    assert get_agent_color(make_agent(30, config.BLUE)) == config.BLUE_CRITICAL_COLOR


def test_triangle_points_follow_facing_direction() -> None:
    agent = make_agent(100)
    agent.facing_direction = pygame.Vector2(0, 1)

    points = get_triangle_points(agent)

    assert points[0] == (50, 62)


def test_dead_agent_is_drawn_as_a_team_colored_circle() -> None:
    pygame.init()
    screen = pygame.Surface((100, 100))
    agent = make_agent(0)

    draw_agent(screen, agent)

    assert screen.get_at((50, 50))[:3] == config.RED_DEATH_MARKER_COLOR
    pygame.quit()


def test_living_agent_is_drawn_over_dead_agent_at_same_position() -> None:
    pygame.init()
    screen = pygame.Surface((100, 100))
    dead_agent = make_agent(0)
    living_agent = make_agent(100)
    living_agent.team = config.BLUE
    game = Game()
    game.agents = [living_agent, dead_agent]

    draw_game(screen, game, fps=60)

    assert screen.get_at((50, 50))[:3] == config.BLUE_HEALTHY_COLOR
    pygame.quit()