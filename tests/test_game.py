import pygame

import config
from agent import Agent
from game import Game


def make_agent(agent_id: int, team: str, x: float, hp: float = config.AGENT_HP) -> Agent:
    agent = Agent(agent_id, team, pygame.Vector2(x, 0))
    agent.hp = hp
    return agent


def test_reset_creates_two_deterministic_teams() -> None:
    game = Game()

    assert len(game.agents) == 20
    assert len(game.get_living_agents(config.RED)) == config.TEAM_SIZE
    assert len(game.get_living_agents(config.BLUE)) == config.TEAM_SIZE
    assert game.agents[0].position == pygame.Vector2(config.RED_START_X, config.START_Y)


def test_nearest_target_and_dead_target_exclusion() -> None:
    game = Game()
    red = make_agent(1, config.RED, 0)
    nearest = make_agent(2, config.BLUE, 10)
    farther = make_agent(3, config.BLUE, 20)
    dead = make_agent(4, config.BLUE, 1, hp=0)
    game.agents = [red, farther, dead, nearest]

    game.update(0)

    assert red.target is nearest


def test_red_wins_when_blue_is_dead() -> None:
    game = Game()
    red = make_agent(1, config.RED, 0)
    blue = make_agent(2, config.BLUE, 20, hp=0)
    game.agents = [red, blue]

    game.check_battle_result()

    assert game.battle_finished
    assert game.winner == config.RED


def test_both_teams_dead_result_in_draw() -> None:
    game = Game()
    game.agents = [
        make_agent(1, config.RED, 0, hp=0),
        make_agent(2, config.BLUE, 20, hp=0),
    ]

    game.check_battle_result()

    assert game.battle_finished
    assert game.winner == config.DRAW


def test_simultaneous_attacks_kill_both_agents() -> None:
    game = Game()
    red = make_agent(1, config.RED, 0, hp=config.ATTACK_DAMAGE)
    blue = make_agent(2, config.BLUE, config.ATTACK_RANGE, hp=config.ATTACK_DAMAGE)
    game.agents = [red, blue]

    game.update(0)

    assert not red.is_alive()
    assert not blue.is_alive()
    assert game.winner == config.DRAW