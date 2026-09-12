from __future__ import annotations

from math import inf

import pygame

import config


class Agent:
    def __init__(
        self,
        agent_id: int,
        team: str,
        position: pygame.Vector2,
    ) -> None:
        self.id = agent_id
        self.team = team
        self.position = pygame.Vector2(position)
        self.hp = config.AGENT_HP
        self.attack_cooldown = 0.0
        self.target: Agent | None = None

    def is_alive(self) -> bool:
        return self.hp > 0

    def update_cooldown(self, dt: float) -> None:
        self.attack_cooldown = max(0.0, self.attack_cooldown - dt)

    def find_nearest_enemy(self, agents: list[Agent]) -> Agent | None:
        nearest_enemy = None
        nearest_distance = inf

        for enemy in agents:
            if not enemy.is_alive() or enemy.team == self.team:
                continue

            distance = self.position.distance_to(enemy.position)
            if distance < nearest_distance:
                nearest_enemy = enemy
                nearest_distance = distance

        return nearest_enemy

    def move_toward(
        self,
        target_position: pygame.Vector2,
        dt: float,
        start_position: pygame.Vector2 | None = None,
    ) -> None:
        position = self.position if start_position is None else pygame.Vector2(start_position)
        direction = pygame.Vector2(target_position) - position
        distance = direction.length()
        maximum_distance = max(0.0, distance - config.ATTACK_RANGE)
        movement_distance = min(config.AGENT_SPEED * dt, maximum_distance)

        if distance == 0 or movement_distance == 0:
            self.position = position
            return

        self.position = position + direction.normalize() * movement_distance

    def calculate_separation(
        self,
        agents: list[Agent],
        positions: dict[int, pygame.Vector2] | None = None,
    ) -> pygame.Vector2:
        position = self.position if positions is None else positions[self.id]
        separation = pygame.Vector2()

        for other in agents:
            if other is self or not other.is_alive():
                continue

            other_position = (
                other.position if positions is None else positions[other.id]
            )
            offset = position - other_position
            distance = offset.length()
            if distance >= config.SEPARATION_DISTANCE:
                continue

            if distance <= config.DISTANCE_EPSILON:
                direction = pygame.Vector2(
                    1 if self.id < other.id else -1,
                    0,
                )
            else:
                direction = offset.normalize()

            separation += direction * (
                config.SEPARATION_DISTANCE - distance
            )

        if separation.length_squared() == 0:
            return separation

        return separation.normalize() * config.SEPARATION_STRENGTH

    def is_in_attack_range(self, target: Agent) -> bool:
        return (
            self.position.distance_to(target.position)
            <= config.ATTACK_RANGE + config.DISTANCE_EPSILON
        )

    def can_attack(self, target: Agent) -> bool:
        return (
            self.is_alive()
            and target.is_alive()
            and self.attack_cooldown <= 0.0
            and self.is_in_attack_range(target)
        )

    def start_attack_cooldown(self) -> None:
        self.attack_cooldown = config.ATTACK_INTERVAL

    def take_damage(self, damage: float) -> None:
        self.hp = max(0, self.hp - damage)