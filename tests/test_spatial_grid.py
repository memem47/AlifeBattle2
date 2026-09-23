import pygame

import config
from spatial_grid import build_spatial_grid, get_neighbor_candidates, position_to_cell
from agent import Agent

def make_agent(
        agent_id: int,
        x: float,
        y: float,
) -> Agent:
    return Agent(
        agent_id=agent_id,
        team=config.RED,
        position=pygame.Vector2(x, y),
    )



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

def test_build_spatial_grid_groups_agents_by_cell() -> None:
    cell_size = config.SPATIAL_GRID_CELL_SIZE

    agent1 = make_agent(agent_id=1, x=1, y=1)
    agent2 = make_agent(agent_id=2, x=cell_size - 1, y=cell_size - 1)
    agent3 = make_agent(agent_id=3, x=cell_size + 1, y=1)

    agents = [agent1, agent2, agent3]

    positions = {
        agent.id: agent.position.copy()
        for agent in agents
    }

    grid = build_spatial_grid(agents, positions)

    assert grid[(0, 0)] == [agent1, agent2]
    assert grid[(1, 0)] == [agent3]

def test_build_spatial_grid_uses_position_snapshot() -> None:
    cell_size = config.SPATIAL_GRID_CELL_SIZE

    agent = make_agent(1, 1, 1)

    positions = {
        agent.id: pygame.Vector2(cell_size + 1, 1)
    }

    grid = build_spatial_grid([agent], positions)

    assert (1, 0) in grid
    assert grid[(1, 0)] == [agent]

def test_get_neighbor_candidates_uses_current_and_adjacent_cells() -> None:
    cell_size = config.SPATIAL_GRID_CELL_SIZE

    center = make_agent(1, 1, 1)
    right = make_agent(2, cell_size + 1, 1)
    diagonal = make_agent(3, cell_size + 1, cell_size + 1)
    far = make_agent(4, cell_size * 2 + 1, 1)

    agents = [center, right, diagonal, far]

    positions = {
        agent.id: agent.position.copy()
        for agent in agents
    }

    grid = build_spatial_grid(agents, positions)

    candidates = get_neighbor_candidates(
        grid,
        positions[center.id],
    )

    candidate_ids = {agent.id for agent in candidates}

    assert center.id in candidate_ids
    assert right.id in candidate_ids
    assert diagonal.id in candidate_ids
    assert far.id not in candidate_ids

def test_get_neighbor_candidates_returns_empty_list_for_empty_grid() -> None:
    candidates = get_neighbor_candidates(
        {},
        pygame.Vector2(10, 10),
    )
    
    assert candidates == []