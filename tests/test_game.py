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
    assert len(game.get_living_agents(config.RED)) == config.TEAM_SIZE
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

def test_update_stores_team_command_movement_direction() -> None:
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


def test_agents_continue_team_command_movement_inside_attack_range(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        config,
        "MAX_SEPARATION_SPEED",
        0.0,
    )

    game = Game()

    red = make_agent(1, config.RED, 0)
    blue = make_agent(
        2,
        config.BLUE,
        config.ATTACK_RANGE,
    )
    game.agents = [red, blue]

    red_start_x = red.position.x
    blue_start_x = blue.position.x

    game.update(1 / 60)

    assert red.position.x > red_start_x
    assert blue.position.x < blue_start_x

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


def test_agents_move_by_team_command_not_toward_enemy() -> None:
    game = Game()

    red = Agent(
        0,
        config.RED,
        pygame.Vector2(300, 200),
    )
    blue = Agent(
        1,
        config.BLUE,
        pygame.Vector2(100, 200),
    )

    game.agents = [red, blue]

    red_start_x = red.position.x
    blue_start_x = blue.position.x

    game.update(0.1)

    assert red.position.x > red_start_x
    assert blue.position.x < blue_start_x

def test_agents_attack_after_command_movement_enters_attack_range(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        config,
        "MAX_SEPARATION_SPEED",
        0.0,
    )

    game = Game()

    dt = min(1 / 60, config.MAX_DT)

    start_distance = (
        config.ATTACK_RANGE
        + config.AGENT_SPEED * dt
    )

    red = make_agent(
        1,
        config.RED,
        0,
    )
    blue = make_agent(
        2,
        config.BLUE,
        start_distance,
    )
    game.agents = [red, blue]

    red_start_hp = red.hp
    blue_start_hp = blue.hp

    game.update(dt)

    assert red.hp == red_start_hp - config.ATTACK_DAMAGE
    assert blue.hp == blue_start_hp - config.ATTACK_DAMAGE

def test_local_attack_target_selects_nearest_enemy_in_range() -> None:
    game = Game()

    red = make_agent(1, config.RED, 0)
    nearest = make_agent(
        2,
        config.BLUE,
        config.ATTACK_RANGE * 0.4,
    )
    farther = make_agent(
        3,
        config.BLUE,
        config.ATTACK_RANGE * 0.8,
    )

    game.agents = [
        red,
        farther,
        nearest,
    ]

    game.update(0)

    assert red.target is nearest

def test_enemy_outside_attack_range_is_not_targeted() -> None:
    game = Game()

    red = make_agent(1, config.RED, 0)
    blue = make_agent(
        2,
        config.BLUE,
        config.ATTACK_RANGE
        + config.DISTANCE_EPSILON
        + 1,
    )

    game.agents = [red, blue]

    game.update(0)

    assert red.target is None
    assert blue.target is None

def test_dead_enemy_is_not_local_attack_target() -> None:
    game = Game()

    red = make_agent(1, config.RED, 0)
    dead_blue = make_agent(
        2,
        config.BLUE,
        config.ATTACK_RANGE / 2,
        hp=0,
    )

    game.agents = [red, dead_blue]

    game.update(0)

    assert red.target is None

def test_teams_start_with_advance_command() -> None:
    game = Game()

    assert (
        game.team_commands[config.RED]
        == Game.COMMAND_ADVANCE
    )
    assert (
        game.team_commands[config.BLUE]
        == Game.COMMAND_ADVANCE
    )

def test_toggle_team_command_changes_only_selected_team() -> None:
    game = Game()

    game.toggle_team_command(config.RED)

    assert (
        game.team_commands[config.RED]
        == Game.COMMAND_HOLD
    )
    assert (
        game.team_commands[config.BLUE]
        == Game.COMMAND_ADVANCE
    )

    game.toggle_team_command(config.RED)

    assert (
        game.team_commands[config.RED]
        == Game.COMMAND_ADVANCE
    )

def test_reset_restores_team_commands_to_advance() -> None:
    game = Game()

    game.toggle_team_command(config.RED)
    game.toggle_team_command(config.BLUE)

    assert (
        game.team_commands[config.RED]
        == Game.COMMAND_HOLD
    )
    assert (
        game.team_commands[config.BLUE]
        == Game.COMMAND_HOLD
    )

    game.reset()

    assert (
        game.team_commands[config.RED]
        == Game.COMMAND_ADVANCE
    )
    assert (
        game.team_commands[config.BLUE]
        == Game.COMMAND_ADVANCE
    )

def test_hold_stops_commanded_forward_movement() -> None:
    game = Game()

    red = make_agent(
        1,
        config.RED,
        100,
    )
    blue = make_agent(
        2,
        config.BLUE,
        500,
    )

    game.agents = [red, blue]

    game.toggle_team_command(config.RED)

    red_start_position = red.position.copy()
    blue_start_x = blue.position.x

    game.update(0.1)

    assert red.position == red_start_position
    assert blue.position.x < blue_start_x

def test_hold_preserves_separation_movement() -> None:
    game = Game()

    red1 = Agent(
        1,
        config.RED,
        pygame.Vector2(100, 100),
    )
    red2 = Agent(
        2,
        config.RED,
        pygame.Vector2(
            100 + config.SEPARATION_DISTANCE / 2,
            100,
        ),
    )
    blue = Agent(
        3,
        config.BLUE,
        pygame.Vector2(500, 100),
    )

    game.agents = [red1, red2, blue]

    game.toggle_team_command(config.RED)

    red1_start = red1.position.copy()
    red2_start = red2.position.copy()

    game.update(0.1)

    assert (
        red1.position != red1_start
        or red2.position != red2_start
    )