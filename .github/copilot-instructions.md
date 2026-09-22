# GitHub Copilot Instructions for AlifeBattle

## Project Purpose

AlifeBattle is both:

- a real-time artificial-life battle simulation, and
- a software engineering learning project.

The developer must be able to understand and explain the implementation.

Prefer simple, readable, and testable code over sophisticated architecture.

## Read Project Documents First

Before making a change, read:

1. `docs/VISION.md`
2. the relevant document in `docs/specs/`
3. the relevant document in `docs/designs/`
4. the affected source files and tests

Project information has the following priority:

```text
VISION
  ↓
SPEC
  ↓
DESIGN
  ↓
IMPLEMENTATION
```

Do not silently change documented behavior.

If documents and implementation conflict, report the conflict before changing the documents.

## Keep Scope Small

Implement only what the current version requires.

Do not introduce systems for hypothetical future requirements.

Avoid unnecessary:

- frameworks,
- abstraction layers,
- generalized AI systems,
- event systems,
- ECS architectures,
- performance optimizations.

Prefer the simplest implementation that satisfies the current SPEC and DESIGN.

## Module Responsibilities

main.py

- application loop,
- input,
- timing,
- calling update and rendering.

game.py

- battle state,
- simulation update phases,
- interaction between agents,
- battle result.

agent.py

- individual agent state,
- individual movement and combat behavior.

renderer.py

- visualization only.
- must not modify simulation state.

config.py

- simulation and visualization parameters.

Keep dependencies simple and avoid circular imports.

## Simulation Rules

Time-dependent behavior must use delta time.

When interaction order could affect results:

- use snapshots where appropriate,
- calculate decisions before applying shared state changes,
- collect attacks before applying damage.

Do not add special-case behavior unless it represents an actual game rule.

## Changes

Keep changes local.

Do not combine unrelated features or refactoring in one task.

Do not rewrite working code merely because another architecture is possible.

Refactor when it improves an existing concrete problem such as:

- unclear responsibilities,
- difficult-to-follow update logic,
- duplicated logic,
- difficult testing.

## Testing

Add or update tests when simulation behavior changes.

Prefer deterministic automated tests.

Rendering behavior may be verified manually unless the underlying calculation can be tested independently.

Run:
```
python -m pytest
```
after relevant changes.

## Documentation

Do not modify VISION, SPEC, or DESIGN merely to make them match accidental implementation behavior.

Version-specific rules belong in SPEC and DESIGN, not in this instruction file.

## Completion

A change is complete when:

- it matches the current SPEC and DESIGN,
- relevant tests pass,
- the application still runs,
- and the implementation can be explained clearly.

When uncertain, choose the smaller and easier-to-understand solution.