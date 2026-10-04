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
    scale = agent.size_scale

    points = (
        center + direction * config.TRIANGLE_FRONT * scale,
        center - direction * config.TRIANGLE_REAR * scale
          + side * config.TRIANGLE_HALF_WIDTH * scale,
        center - direction * config.TRIANGLE_REAR * scale
          - side * config.TRIANGLE_HALF_WIDTH * scale,
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

    death_marker_radius = max(
        1, round(config.DEATH_MARKER_RADIUS * agent.size_scale)
    )
    pygame.draw.circle(
        screen, color, center, death_marker_radius
    )


def draw_hud(
    screen: pygame.Surface,
    game: Game,
    fps: float,
) -> None:
    font = pygame.font.Font(None, 30)

    red_count = len(game.get_living_agents(config.RED))
    blue_count = len(game.get_living_agents(config.BLUE))

    if game.battle_finished:
        status = (
            f"{game.winner.upper()} WINS"
            if game.winner != config.DRAW
            else "DRAW"
        )
        status += f"    FPS: {fps:.1f}    Press R to restart"
    else:
        status = (
            f"Red: {red_count}    "
            f"Blue: {blue_count}    "
            f"FPS: {fps:.1f}"
        )

    red_command = (
        f"Red Command: {game.team_commands[config.RED]} [A]"
    )
    blue_command = (
        f"Blue Command: {game.team_commands[config.BLUE]} [B]"
    )

    lines = [
        status,
        red_command,
        blue_command,
    ]

    for index, line in enumerate(lines):
        text = font.render(
            line,
            True,
            config.TEXT_COLOR,
        )
        screen.blit(
            text,
            (20, 20 + index * 28),
        )

def draw_spatial_grid(screen: pygame.Surface) -> None:
    cell_size = int(config.SPATIAL_GRID_CELL_SIZE)

    for x in range(0, config.SCREEN_WIDTH + 1, cell_size):
        pygame.draw.line(
            screen, 
            config.SPATIAL_GRID_COLOR, 
            (x, 0), 
            (x, config.SCREEN_HEIGHT),
        )

    for y in range(0, config.SCREEN_HEIGHT + 1, cell_size):
        pygame.draw.line(
            screen, 
            config.SPATIAL_GRID_COLOR, 
            (0, y), 
            (config.SCREEN_WIDTH, y),
        )

def draw_game(screen: pygame.Surface, game: Game, fps: float) -> None:
    screen.fill(config.BACKGROUND_COLOR)

    if config.SHOW_SPATIAL_GRID:
        draw_spatial_grid(screen)

    for agent in game.agents:
        if not agent.is_alive():
            draw_agent(screen, agent)

    for agent in game.agents:
        if agent.is_alive():
            draw_agent(screen, agent)

    draw_hud(screen, game, fps)
