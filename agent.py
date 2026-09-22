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
        self.facing_direction = pygame.Vector2(1, 0)
        self.hp = config.AGENT_HP
        self.attack_cooldown = 0.0
        self.target: Agent | None = None

    def is_alive(self) -> bool:
        return self.hp > 0

    def update_cooldown(self, dt: float) -> None:
        self.attack_cooldown = max(0.0, self.attack_cooldown - dt)

    def update_facing_direction(self, movement: pygame.Vector2) -> None:
        if movement.length_squared() > config.DISTANCE_EPSILON**2:
            self.facing_direction = movement.normalize()

    def find_nearest_enemy(self, enemies: list[Agent]) -> Agent | None:
        nearest_enemy = None
        nearest_distance = inf

        for enemy in enemies:
            if not enemy.is_alive():
                continue

            offset = self.position - enemy.position
            distance_squared = offset.length_squared()
            if distance_squared < nearest_distance:
                nearest_enemy = enemy
                nearest_distance = distance_squared

        return nearest_enemy

    def calculate_target_movement(
        self,
        target_position: pygame.Vector2,
        dt: float,
        start_position: pygame.Vector2 | None = None,
    ) -> pygame.Vector2:
        position = (
            self.position 
            if start_position is None 
            else pygame.Vector2(start_position)
        )

        direction = pygame.Vector2(target_position) - position
        distance = direction.length()

        if distance <= config.ATTACK_RANGE:
            return pygame.Vector2()
        
        movement_distance = min(
            config.AGENT_SPEED * dt, 
            distance - config.ATTACK_RANGE,
        )

        if movement_distance <= 0:
            return pygame.Vector2()
        
        return direction.normalize() * movement_distance

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

            overlap_ratio = (
                config.SEPARATION_DISTANCE - distance
            ) / config.SEPARATION_DISTANCE

            separation += direction * overlap_ratio

        if separation.length_squared() > 1.0:
            separation = separation.normalize()

        return separation * config.MAX_SEPARATION_SPEED

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