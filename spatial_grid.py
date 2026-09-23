from __future__ import annotations

import pygame

import config
from agent import Agent

Cell = tuple[int, int]
SpatialGrid = dict[Cell, list[Agent]]

def position_to_cell(position: pygame.Vector2) -> Cell:
    cell_size = config.SPATIAL_GRID_CELL_SIZE

    return (
        int(position.x // cell_size), 
        int(position.y // cell_size),
    )

def build_spatial_grid(
        agents: list[Agent],
        positions: dict[int, pygame.Vector2],
) -> SpatialGrid:
    grid: SpatialGrid = {}

    for agent in agents:
        cell = position_to_cell(positions[agent.id])

        if cell not in grid:
            grid[cell] = []
            
        grid[cell].append(agent)

    return grid

def get_neighbor_candidates(
        grid: SpatialGrid,
        position: pygame.Vector2,
) -> list[Agent]:
    cell_x, cell_y = position_to_cell(position)

    candidates: list[Agent] = []

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            cell = (cell_x + dx, cell_y + dy)
            candidates.extend(grid.get(cell, []))

    return candidates