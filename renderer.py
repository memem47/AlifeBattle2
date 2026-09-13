import pygame

import config
from game import Game
from agent import Agent


def get_agent_color(agent: Agent) -> tuple[int, int, int]:
    health_ratio = agent.hp / config.AGENT_HP
    if agent.team == config.RED:
        colors = (
            config.RED_HEALTHY_COLOR,
            config.RED_DAMAGED_COLOR,
            config.RED_CRITICAL_COLOR,
        )
    else:
        colors = (
            config.BLUE_HEALTHY_COLOR,
            config.BLUE_DAMAGED_COLOR,
            config.BLUE_CRITICAL_COLOR,
        )

    if health_ratio > 2 / 3:
        return colors[0]
    if health_ratio > 1 / 3:
        return colors[1]
    return colors[2]


def get_triangle_points(agent: Agent) -> list[tuple[int, int]]:
    direction = agent.facing_direction.normalize()
    side = pygame.Vector2(-direction.y, direction.x)
    center = agent.position
    points = (
        center + direction * config.TRIANGLE_FRONT,
        center - direction * config.TRIANGLE_REAR + side * config.TRIANGLE_HALF_WIDTH,
        center - direction * config.TRIANGLE_REAR - side * config.TRIANGLE_HALF_WIDTH,
    )
    return [(round(point.x), round(point.y)) for point in points]


def draw_agent(screen: pygame.Surface, agent: Agent) -> None:
    center = (round(agent.position.x), round(agent.position.y))
    if agent.is_alive():
        pygame.draw.polygon(screen, get_agent_color(agent), get_triangle_points(agent))
        return

    color = (
        config.RED_DEATH_MARKER_COLOR
        if agent.team == config.RED
        else config.BLUE_DEATH_MARKER_COLOR
    )
    pygame.draw.circle(screen, color, center, config.DEATH_MARKER_RADIUS)


def draw_hud(screen: pygame.Surface, game: Game) -> None:
    font = pygame.font.Font(None, 30)
    red_count = len(game.get_living_agents(config.RED))
    blue_count = len(game.get_living_agents(config.BLUE))
    status = f"Red: {red_count}    Blue: {blue_count}"

    if game.battle_finished:
        status = f"{game.winner.upper()} WINS" if game.winner != config.DRAW else "DRAW"
        status += "    Press R to restart"

    text = font.render(status, True, config.TEXT_COLOR)
    screen.blit(text, (20, 20))


def draw_game(screen: pygame.Surface, game: Game) -> None:
    screen.fill(config.BACKGROUND_COLOR)

    for agent in game.agents:
        if not agent.is_alive():
            draw_agent(screen, agent)

    for agent in game.agents:
        if agent.is_alive():
            draw_agent(screen, agent)

    draw_hud(screen, game)