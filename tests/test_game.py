import pygame

import config
from agent import Agent
from game import Game


def make_agent(agent_id: int, team: str, x: float, hp: float = config.AGENT_HP) -> Agent:
    agent = Agent(agent_id, team, pygame.Vector2(x, 0))
    agent.hp = hp
    return agent


def test_reset_creates_two_teams_with_reproducible_random_positions(monkeypatch) -> None:
    monkeypatch.setattr(config, "RANDOM_SEED", 0)
    game = Game()
    first_positions = [agent.position.copy() for agent in game.agents]
    game.reset()
    second_positions = [agent.position.copy() for agent in game.agents]
    
    assert len(game.agents) == config.TEAM_SIZE * 2
    assert len(game.get_living_agents(config.RED)) == 
    assert len(game.get_living_agents(config.BLUE)) == config.TEAM_SIZE
    assert first_positions == second_positions
    assert all(agent.attack_cooldown == 0 for agent in game.agents)
    assert all(
        config.RED_START_X - config.START_X_VARIATION <= agent.position.x
        <= config.RED_START_X + config.START_X_VARIATION
        for agent in game.get_living_agents(config.RED)
    )
    assert all(
        config.BLUE_START_X - config.START_X_VARIATION <= agent.position.x
        <= config.BLUE_START_X + config.START_X_VARIATION
        for agent in game.get_living_agents(config.BLUE)
    )
    for team in (config.RED, config.BLUE):
        team_agents = game.get_living_agents(team)
        for index, agent in enumerate(team_agents):
            assert all(
                agent.position.distance_to(other.position)
                >= config.INITIAL_MIN_DISTANCE
                for other in team_agents[index + 1 :]
            )

    red_positions = [agent.position for agent in game.get_living_agents(config.RED)]
    blue_positions = [agent.position for agent in game.get_living_agents(config.BLUE)]
    assert max(position.x for position in red_positions) < min(
        position.x for position in blue_positions
    )


def test_deeded_battle_completes_after_agents_reach_attack_range(
        monkeypatch,
) -> None:
    monkeypatch.setattr(config, "RANDOM_SEED", 0)
    game = Game()

    for _ in range(1800):
        game.update(1 / 60)
        if game.battle_finished:
            break

    assert game.battle_finished
    assert game.winner in (config.RED, config.BLUE, config.DRAW)


def test_default_seed_does_not_stall_at_attack_range(monkeypatch) -> None:
    monkeypatch.setattr(config, "RANDOM_SEED", 1)
    game = Game()

    for _ in range(6000):
        game.update(1 / 60)
        if game.battle_finished:
            break

    assert game.battle_finished


def test_nearest_target_and_dead_target_exclusion() -> None:
    game = Game()
    red = make_agent(1, config.RED, 0)
    nearest = make_agent(2, config.BLUE, 10)
    farther = make_agent(3, config.BLUE, 20)
    dead = make_agent(4, config.BLUE, 1, hp=0)
    game.agents = [red, farther, dead, nearest]

    game.update(0)

    assert red.target is nearest


def test_target_changes_to_nearest_enemy_each_update() -> None:
    game = Game()

    red = make_agent(1, config.RED, 0)
    farther = make_agent(2, config.BLUE, 30)
    nearer = make_agent(3, config.BLUE, 10)

    red.target = farther
    game.agents = [red, farther, nearer]

    game.update(0)

    assert red.target is nearer


def test_update_stores_final_movement_direction() -> None:
    game = Game()
    red = make_agent(1, config.RED, 0)
    blue = make_agent(2, config.BLUE, 100)
    game.agents = [red, blue]

    game.update(0.5)

    assert red.facing_direction == pygame.Vector2(1, 0)
    assert blue.facing_direction == pygame.Vector2(-1, 0)


def test_dead_agent_keeps_position_and_is_excluded_from_update() -> None:
    game = Game()
    red = make_agent(1, config.RED, 0)
    dead_blue = make_agent(2, config.BLUE, 10, hp=0)
    dead_position = dead_blue.position.copy()
    game.agents = [red, dead_blue]

    game.update(0.5)

    assert dead_blue.position == dead_position
    assert red.target is None


def test_agents_keep_separation_inside_attack_range_without_oscillation() -> None:
    game = Game()
    red = make_agent(1, config.RED, 0)
    blue = make_agent(2, config.BLUE, config.ATTACK_RANGE)
    game.agents = [red, blue]

    game.update(1 / 60)
    first_positions = [agent.position.copy() for agent in game.agents]
    game.update(1 / 60)

    assert [agent.position for agent in game.agents] == first_positions
    assert red.position.distance_to(blue.position) >= config.ATTACK_RANGE


def test_separation_does_not_change_direction_at_long_range() -> None:
    game = Game()
    red = make_agent(1, config.RED, 0)
    blue = make_agent(2, config.BLUE, 100)
    nearby_ally = make_agent(3, config.RED, 30)
    game.agents = [red, blue, nearby_ally]

    game.update(1 / 60)

    assert red.facing_direction == pygame.Vector2(1, 0)


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