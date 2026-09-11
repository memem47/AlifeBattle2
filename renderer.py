import pygame

import config
from game import Game
from agent import Agent


def draw_agent(screen: pygame.Surface, agent: Agent) -> None:
    color = config.RED_COLOR if agent.team == config.RED else config.BLUE_COLOR
    pygame.draw.circle(
        screen,
        color,
        (round(agent.position.x), round(agent.position.y)),
        config.AGENT_RADIUS,
    )


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

    for agent in game.get_living_agents():
        draw_agent(screen, agent)

    draw_hud(screen, game)