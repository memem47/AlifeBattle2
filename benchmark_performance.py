from __future__ import annotations

import argparse
import statistics
import time

import config
from game import Game


DEFAULT_TEAM_SIZE = [50, 100, 250, 500]
DEFAULT_SIMULATION_SECONDS = 5.0
DEFAULT_REPEATS = 3

SIMULATION_DT = 1.0 / 60.0
BENCHMARK_SEED = 0

def run_benchmark(
        team_size: int,
        simulation_seconds: float,
) -> float:
    """Return simulation updates per real second."""
    config.TEAM_SIZE = team_size
    config.RANDOM_SEED = BENCHMARK_SEED

    game = Game()

    frame_count = int(simulation_seconds / SIMULATION_DT)

    start = time.perf_counter()

    for _ in range(frame_count):
        game.update(SIMULATION_DT)

    elapsed = time.perf_counter() - start

    return frame_count / elapsed

def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--sizes",
        nargs="+",
        type=int,
        default=DEFAULT_TEAM_SIZE,
    )
    
    parser.add_argument(
        "--seconds",
        type=float,
        default=DEFAULT_SIMULATION_SECONDS,
    )

    parser.add_argument(
        "--repeats",
        type=int,
        default=DEFAULT_REPEATS,
    )

    args = parser.parse_args()

    original_team_size = config.TEAM_SIZE
    original_seed = config.RANDOM_SEED

    try:
        print()
        print("AlifeBattle performance benchmark")
        print(
            f"Simulation duration: {args.seconds:.1f} s "
            f"per run"
        )
        print(
            f"Repeats: {args.repeats} "
        )
        print()

        print(
            f"{'Team Size':>10} "
            f"{'Agents':>10} "
            f"{'Sim FPS':>12}"
        )

        print("-" * 36)

        for team_size in args.sizes:
            results: list[float] = []

            for _ in range(args.repeats):
                simulation_fps = run_benchmark(
                    team_size=team_size,
                    simulation_seconds=args.seconds,
                )
                results.append(simulation_fps)

            average_fps = statistics.mean(results)

            print(
                f"{team_size:>10} "
                f"{team_size * 2:>10} "
                f"{average_fps:>12.1f}"
            )
    finally:
        config.TEAM_SIZE = original_team_size
        config.RANDOM_SEED = original_seed

if __name__ == "__main__":
    main()