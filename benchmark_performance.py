from __future__ import annotations

import argparse
import cProfile
import json
import platform
import pstats
import statistics
import time
from datetime import datetime
from pathlib import Path

import config
from game import Game


DEFAULT_TEAM_SIZE = [50, 100, 250, 500]
DEFAULT_SIMULATION_SECONDS = 3.0
DEFAULT_REPEATS = 3

SIMULATION_DT = 1.0 / 60.0
BENCHMARK_SEED = 0

RESULT_PATH = Path("temp/benchmark_latest.json")

def create_game(team_size: int) -> Game:
    config.TEAM_SIZE = team_size
    config.RANDOM_SEED = BENCHMARK_SEED
    return Game()

def run_updates(
        game: Game,
        simulation_seconds: float,
) -> int:
    update_count = int(simulation_seconds / SIMULATION_DT)

    for _ in range(update_count):
        if game.battle_finished:
            raise RuntimeError(
                "Battle finished before the benchmark workload completed."
            )
        game.update(SIMULATION_DT)

    return update_count


def run_benchmark_once(
        team_size: int,
        simulation_seconds: float,
) -> float:

    game = create_game(team_size)

    start = time.perf_counter()

    update_count = run_updates(
        game,
        simulation_seconds,
    )

    elapsed = time.perf_counter() - start

    return update_count / elapsed

def benchmark_team_size(
        team_size: int,
        simulation_seconds: float,
        repeats: int,
) -> dict:
    results = [
        run_benchmark_once(
            team_size,
            simulation_seconds,
        )
        for _ in range(repeats)
    ]

    mean_fps = statistics.mean(results)

    return {
        "team_size": team_size,
        "total_agents": team_size * 2,
        "sim_fps": mean_fps,
        "ms_per_update": 1000.0 / mean_fps,
    }

def load_previous_result() -> dict | None:
    if not RESULT_PATH.exists():
        return None

    try:
        return json.loads(
            RESULT_PATH.read_text(encoding="utf-8")
        )
    except(json.JSONDecodeError, OSError):
        return None

def settings_are_comparable(
        previous: dict,
        simulation_seconds: float,
        repeats: int,
) -> bool:
    return (
        previous.get("simulation_seconds") == simulation_seconds
        and previous.get("repeats") == repeats
        and previous.get("seed") == BENCHMARK_SEED
        and previous.get("simulation_dt") == SIMULATION_DT
    )

def print_benchmark_results(
        current_results: list[dict],
        previous: dict | None,
        comparable: bool,
) -> None:
    previous_by_size = {}

    if previous is not None:
        previous_by_size = {
            item["team_size"]: item
            for item in previous.get("benchmarks", [])
        }

    print()
    print("Performance results")
    print()

    print(
        f"{'Team':>8} "
        f"{'Agents':>8} "
        f"{'Sim FPS':>12} "
        f"{'Previous':>12} "
        f"{'Change':>10}"
    )
    print("-" * 56)

    for result in current_results:
        previous_result = previous_by_size.get(
            result["team_size"]
        )

        previous_text = "-"
        change_text = "-"

        if previous_result is not None:
            previous_fps = previous_result["sim_fps"]
            previous_text = f"{previous_fps:.1f}"

            if comparable and previous_fps > 0:
                change = (
                    result["sim_fps"] / previous_fps - 1.0
                ) * 100.0

                change_text = f"{change:+.1f}%"

        print(
            f"{result['team_size']:>8} "
            f"{result['total_agents']:>8} "
            f"{result['sim_fps']:>12.1f} "
            f"{previous_text:>12} "
            f"{change_text:>10}"
        )

def profile_simulation(
        team_size: int,
        simulation_seconds: float,
        top_count: int,
) -> list[dict]:
    game = create_game(team_size)

    profiler = cProfile.Profile()

    profiler.enable()

    run_updates(
        game,
        simulation_seconds,
    )

    profiler.disable()

    stats = pstats.Stats(profiler)

    project_root = Path(__file__).resolve().parent

    entries = []

    for key, values in stats.stats.items():
        filename, line_number, function_name = key
        call_count, primitive_calls, total_time, cumulative_time, _ = values

        try:
            path = Path(filename).resolve()
        except OSError:
            continue

        if path != project_root / path.name:
            continue

        if path.name == Path(__file__).name:
            continue

        entries.append(
            {
                "function": (
                    f"{path.name}:{line_number}:{function_name}"
                ),
                "calls": primitive_calls,
                "total_seconds": total_time,
                "cumulative_seconds": cumulative_time,
            }
        )

    entries.sort(
        key = lambda item: item["cumulative_seconds"],
        reverse=True,
    )

    return entries[:top_count]

def print_profile_results(
        profile_results: list[dict],
        profile_team_size: int,
) -> None:
    print()
    print(
        f"Top bottlenecks "
        f"(team size = {profile_team_size})"
    )
    print()

    print(
        f"{'Function':<45} "
        f"{'Calls':>10} "
        f"{'Cum. sec':>12}"
    )
    print("-" * 70)

    for item in profile_results:
        print(
            f"{item['function']:<45} "
            f"{item['calls']:>10} "
            f"{item['cumulative_seconds']:>12.4f}"
        )
    
def save_result(result: dict) -> None:
    RESULT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    RESULT_PATH.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark AlifeBattle simulation performance."
    )

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

    parser.add_argument(
        "--profile-size",
        type=int,
        default=None,
        help="Team size used for profiling. Defaults to largest size.",
    )

    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Number of profiling entries to display.",
    )

    args = parser.parse_args()

    profile_team_size = (
        args.profile_size
        if args.profile_size is not None
        else max(args.sizes)
    )

    original_team_size = config.TEAM_SIZE
    original_seed = config.RANDOM_SEED

    previous = load_previous_result()

    comparable = (
        previous is not None
        and settings_are_comparable(
            previous,
            args.seconds,
            args.repeats,
        )
    )

    try:
        print()
        print("AlifeBattle performance benchmark")
        print(
            f"Simulation duration: {args.seconds:.1f} s "
        )
        print(
            f"Repeats: {args.repeats} "
        )

        if previous is None:
            print("Previous result: none")
        elif comparable:
            print("Previous result: comparable")
        else:
            print(
                "Previous result: found, "
                "but benchmark settings differ"
            )

        current_results = [
            benchmark_team_size(
                team_size,
                args.seconds,
                args.repeats,
            )
            for team_size in args.sizes
        ]

        print_benchmark_results(
            current_results,
            previous,
            comparable,
        )

        profile_results = profile_simulation(
            profile_team_size,
            args.seconds,
            args.top,
        )

        print_profile_results(
            profile_results,
            profile_team_size,
        )

        result = {
            "timestamp": datetime.now().astimezone().isoformat(
                timespec="seconds"
            ),
            "python": platform.python_version(),
            "seed": BENCHMARK_SEED,
            "simulation_dt": SIMULATION_DT,
            "simulation_seconds": args.seconds,
            "repeats": args.repeats,
            "profile_team_size": profile_team_size,
            "benchmarks": current_results,
            "profile_top": profile_results,
        }

        if profile_results:
            result["primary_bottleneck"] = (
                profile_results[0]["function"]
            )

        save_result(result)

        print()
        print(f"Saved: {RESULT_PATH}")

    finally:
        config.TEAM_SIZE = original_team_size
        config.RANDOM_SEED = original_seed

if __name__ == "__main__":
    main()