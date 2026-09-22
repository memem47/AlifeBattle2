from __future__ import annotations

import pygame

import config

Cell = tuple[int, int]

def position_to_cell(position: pygame.Vector2) -> Cell:
    cell_size = config.SPATIAL_GRID_CELL_SIZE

    return (
        int(position.x // cell_size), 
        int(position.y // cell_size),
    )