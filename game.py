from __future__ import annotations

import random

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
        random_generator = random.Random(config.RANDOM_SEED)

        for team, start_x, column_direction in (
            (config.RED, config.RED_START_X, 1),
            (config.BLUE, config.BLUE_START_X, -1),
        ):
            team_positions: list[pygame.Vector2] = []
            for _ in range(config.TEAM_SIZE):
                position = self._random_start_position(
                    random_generator,
                    start_x,
                    column_direction,
                    team_positions,
                )
                team_positions.append(position)
                agent = Agent(len(self.agents), team, position)
                agent.attack_cooldown = random_generator.uniform(
                    0.0, config.ATTACK_INTERVAL
                )
                self.agents.append(agent)

    def _random_start_position(
        self,
        random_generator: random.Random,
        start_x: float,
        column_direction: int,
        existing_positions: list[pygame.Vector2],
    ) -> pygame.Vector2:
        for _ in range(100):
            position = pygame.Vector2(
                start_x
                + column_direction
                * random_generator.uniform(
                    -config.START_X_VARIATION, config.START_X_VARIATION
                ),
                random_generator.uniform(config.START_Y_MIN, config.START_Y_MAX),
            )
            if all(
                position.distance_to(existing) >= config.INITIAL_MIN_DISTANCE
                for existing in existing_positions
            ):
                return position

        return position

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
            separation = agent.calculate_separation(living_agents, positions)
            planned_position = agent.position + separation * dt
            if agent.id in target_positions:
                target_position = target_positions[agent.id]
                base_target_distance = agent.position.distance_to(target_position)
                target_distance = planned_position.distance_to(target_position)
                if (
                    base_target_distance > config.ATTACK_RANGE
                    and target_distance > base_target_distance
                ):
                    away_direction = (agent.position - target_position).normalize()
                    outward_speed = separation.dot(away_direction)
                    if outward_speed > 0:
                        separation -= away_direction * outward_speed
                        planned_position = agent.position + separation * dt
                        target_distance = planned_position.distance_to(target_position)
                if (
                    base_target_distance <= config.ATTACK_RANGE
                    and target_distance > config.ATTACK_RANGE
                ):
                    direction = planned_position - target_position
                    planned_position = target_position + direction.normalize() * (
                        config.ATTACK_RANGE - config.DISTANCE_EPSILON
                    )
            planned_positions[agent.id] = planned_position

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