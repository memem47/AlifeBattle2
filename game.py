from __future__ import annotations

import random

import pygame

import config
from agent import Agent
from spatial_grid import (
    SpatialGrid,
    build_spatial_grid,
    get_neighbor_candidates,
)

class Game:

    TEAM_MOVE_DIRECTIONS = {
        config.RED: pygame.Vector2(1, 0),
        config.BLUE: pygame.Vector2(-1, 0),
    }

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

        positions = self._snapshot_positions(living_agents)

        movement_grid = build_spatial_grid(
            living_agents, 
            positions,
        )

        planned_positions = self._plan_movements(
            living_agents,
            positions,
            movement_grid,
            dt,
        )

        self._apply_movements(
            living_agents, 
            planned_positions,
        )

        attack_positions = self._snapshot_positions(living_agents)

        attack_grid = build_spatial_grid(
            living_agents, 
            attack_positions,
        )

        self._select_local_attack_targets(
            living_agents,
            attack_grid,
        )

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

    def _snapshot_positions(self, living_agents: list[Agent]) -> dict[int, pygame.Vector2]:
        positions = {agent.id: agent.position.copy() for agent in living_agents}
        return positions

    def _plan_movements(
        self,
        living_agents: list[Agent],
        positions: dict[int, pygame.Vector2],
        spatial_grid: SpatialGrid,
        dt: float,
    ) -> dict[int, pygame.Vector2]:
        planned_positions: dict[int, pygame.Vector2] = {}

        for agent in living_agents:
            start_position = positions[agent.id]
            
            command_direction = self.TEAM_MOVE_DIRECTIONS[agent.team]
            command_movement = agent.calculate_command_movement(
                command_direction,
                dt,
            )

            neighbor_candidates = get_neighbor_candidates(
                spatial_grid,
                start_position,
            )
            separation = agent.calculate_separation(
                neighbor_candidates,
                positions,
            )
            
            planned_position = (
                start_position
                + command_movement
                + separation * dt
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

    def _select_local_attack_targets(
        self,
        living_agents: list[Agent],
        spatial_grid: SpatialGrid,
    ) -> None:
        attack_range_squared = (
            config.ATTACK_RANGE + config.DISTANCE_EPSILON
        ) ** 2

        for agent in living_agents:
            agent.target = None

            candidates = get_neighbor_candidates(
                spatial_grid,
                agent.position,
            )

            nearest_enemy = None
            nearest_distance_squared = float("inf")

            for candidate in candidates:
                if candidate is agent:
                    continue

                if candidate.team == agent.team:
                    continue

                dx = agent.position.x - candidate.position.x
                dy = agent.position.y - candidate.position.y
                distance_squared = dx * dx + dy * dy

                if distance_squared > attack_range_squared:
                    continue

                if distance_squared < nearest_distance_squared:
                    nearest_enemy = candidate
                    nearest_distance_squared = distance_squared

            agent.target = nearest_enemy