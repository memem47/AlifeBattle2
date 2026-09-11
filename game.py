from __future__ import annotations

import pygame

import config
from agent import Agent


class Game:
    def __init__(self) -> None:
        self.agents: list[Agent] = []
        self.winner: str | None = None
        self.battle_finished = False
        self.reset()

    def reset(self) -> None:
        self.agents = []
        self.winner = None
        self.battle_finished = False

        for team, start_x, column_direction in (
            (config.RED, config.RED_START_X, 1),
            (config.BLUE, config.BLUE_START_X, -1),
        ):
            for index in range(config.TEAM_SIZE):
                row = index // 2
                column = index % 2
                position = pygame.Vector2(
                    start_x + column_direction * column * config.COLUMN_SPACING,
                    config.START_Y + row * config.ROW_SPACING,
                )
                self.agents.append(Agent(len(self.agents), team, position))

    def update(self, dt: float) -> None:
        if self.battle_finished:
            return

        dt = min(max(0.0, dt), config.MAX_DT)
        living_agents = self.get_living_agents()

        for agent in living_agents:
            agent.update_cooldown(dt)

        for agent in living_agents:
            agent.target = agent.find_nearest_enemy(living_agents)

        positions = {agent.id: agent.position.copy() for agent in living_agents}
        target_positions = {
            agent.id: agent.target.position.copy()
            for agent in living_agents
            if agent.target is not None
        }
        planned_positions = {}

        for agent in living_agents:
            if agent.id in target_positions:
                agent.move_toward(
                    target_positions[agent.id],
                    dt,
                    start_position=positions[agent.id],
                )
            planned_positions[agent.id] = agent.position.copy()

        for agent in living_agents:
            agent.position = planned_positions[agent.id]

        attacks = []
        for agent in living_agents:
            if agent.target is not None and agent.can_attack(agent.target):
                attacks.append((agent, agent.target, config.ATTACK_DAMAGE))

        for attacker, target, damage in attacks:
            target.take_damage(damage)
            attacker.start_attack_cooldown()

        self.check_battle_result()

    def get_living_agents(self, team: str | None = None) -> list[Agent]:
        return [
            agent
            for agent in self.agents
            if agent.is_alive() and (team is None or agent.team == team)
        ]

    def check_battle_result(self) -> None:
        red_alive = bool(self.get_living_agents(config.RED))
        blue_alive = bool(self.get_living_agents(config.BLUE))

        if red_alive and blue_alive:
            return

        self.battle_finished = True
        if red_alive:
            self.winner = config.RED
        elif blue_alive:
            self.winner = config.BLUE
        else:
            self.winner = config.DRAW