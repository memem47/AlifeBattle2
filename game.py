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

        for team, start_x in (
            (config.RED, config.RED_START_X),
            (config.BLUE, config.BLUE_START_X),
        ):
            team_positions: list[pygame.Vector2] = []
            for _ in range(config.TEAM_SIZE):
                position = self._random_start_position(
                    random_generator,
                    start_x,
                    team_positions,
                )
                team_positions.append(position)
                agent = Agent(len(self.agents), team, position)
                
                self.agents.append(agent)

    def _random_start_position(
        self,
        random_generator: random.Random,
        start_x: float,
        existing_positions: list[pygame.Vector2],
    ) -> pygame.Vector2:
        for _ in range(100):
            position = pygame.Vector2(
                start_x
                + random_generator.uniform(
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

        self._update_cooldowns(living_agents, dt)
        self._select_targets(living_agents)

        positions = self._snapshot_positions(living_agents)
        target_positions = {
            agent.id: agent.target.position.copy()
            for agent in living_agents
            if agent.target is not None
        }

        planned_positions = self._plan_movements(
            living_agents,
            positions,
            target_positions,
            dt,
        )
        self._apply_movements(living_agents, planned_positions)

        self._resolve_attacks(living_agents)

        self.check_battle_result()

    def get_living_agents(self, team: str | None = None) -> list[Agent]:
        return [
            agent
            for agent in self.agents
            if agent.is_alive() and (team is None or agent.team == team)
        ]

    def _update_cooldowns(self, living_agents: list[Agent], dt: float) -> None:
        for agent in living_agents:
            agent.update_cooldown(dt)

    def _select_targets(self, living_agents: list[Agent]) -> None:
        for agent in living_agents:
            agent.target = agent.find_nearest_enemy(living_agents)

    def _snapshot_positions(self, living_agents: list[Agent]) -> dict[int, pygame.Vector2]:
        positions = {agent.id: agent.position.copy() for agent in living_agents}
        return positions

    def _plan_movements(
        self,
        living_agents: list[Agent],
        positions: dict[int, pygame.Vector2],
        target_positions: dict[int, pygame.Vector2],
        dt: float,
    ) -> dict[int, pygame.Vector2]:
        planned_positions: dict[int, pygame.Vector2] = {}
        for agent in living_agents:
            start_position = positions[agent.id]
            planned_position = start_position.copy()
            reaches_attack_range = False

            if agent.id in target_positions:
                target_position = target_positions[agent.id]
                target_direction = target_position - start_position
                target_distance = target_direction.length()
                if target_distance > 0:
                    max_advance = max(0.0, target_distance - config.ATTACK_RANGE)
                    move_distance = min(config.AGENT_SPEED * dt, max_advance)
                    reaches_attack_range = move_distance >= max_advance
                    if move_distance > 0:
                        planned_position = start_position + (
                            target_direction.normalize() * move_distance
                        )

            separation = agent.calculate_separation(living_agents, positions)
            planned_position += separation * dt

            if agent.id in target_positions:
                target_position = target_positions[agent.id]
                base_target_distance = start_position.distance_to(target_position)
                target_distance = planned_position.distance_to(target_position)
                if (
                    (base_target_distance <= config.ATTACK_RANGE or reaches_attack_range)
                    and target_distance > config.ATTACK_RANGE
                ):
                    direction = planned_position - target_position
                    planned_position = target_position + direction.normalize() * (
                        config.ATTACK_RANGE - config.DISTANCE_EPSILON
                    )

            planned_positions[agent.id] = planned_position
        return planned_positions

    def _apply_movements(
        self,
        living_agents: list[Agent],
        planned_positions: dict[int, pygame.Vector2],
    ) -> None:
        for agent in living_agents:
            movement = planned_positions[agent.id] - agent.position
            agent.update_facing_direction(movement)
            agent.position = planned_positions[agent.id]

    def _resolve_attacks(self, living_agents: list[Agent]) -> None:
        attacks = []
        for agent in living_agents:
            if agent.target is not None and agent.can_attack(agent.target):
                attacks.append((agent, agent.target, config.ATTACK_DAMAGE))

        for attacker, target, damage in attacks:
            target.take_damage(damage)
            attacker.start_attack_cooldown()

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