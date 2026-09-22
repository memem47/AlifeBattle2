import pygame

import config
from spatial_grid import position_to_cell

def test_position_to_cell() -> None:
    cell_size = config.SPATIAL_GRID_CELL_SIZE

    assert position_to_cell(
        pygame.Vector2(0, 0)
    ) == (0, 0)
    
    assert position_to_cell(
        pygame.Vector2(cell_size - 1, cell_size - 1)
    ) == (0, 0)

    assert position_to_cell(
        pygame.Vector2(cell_size, 0)
    ) == (1, 0)

    assert position_to_cell(
        pygame.Vector2(cell_size * 2, cell_size * 3)
    ) == (2, 3)
