# AlifeBattle Development Roadmap

## Next Architectural Direction

The current global nearest-enemy targeting model is transitional.

The intended long-term behavior separates movement from combat targeting.

### Movement

Agents should move according to high-level command intent rather than searching the entire battlefield for the nearest enemy.

Examples of future command intent may include:

- advance,
- hold,
- retreat,
- move left or right,
- and later, formation or unit-level commands.

### Combat

Movement and attack targeting should be separate concerns.

Agents should not move toward an enemy simply because that enemy is the nearest one.

Instead:

1. an agent moves according to its current command,
2. local enemies are detected around the agent,
3. if an enemy enters attack range, the agent selects a local attack target,
4. combat is resolved using the normal combat rules.

The spatial grid should eventually support both separation and local combat detection.

Global nearest-enemy search should therefore not receive major additional optimization unless it is needed temporarily.

## Next Version

v0.3 should begin with the smallest command-driven movement model.

Initially:

- Red agents advance to the right.
- Blue agents advance to the left.
- Agents do not search globally for enemies in order to move.
- Agents attack enemies only when those enemies enter local attack range.

More complex commands should be introduced only after this basic model works.

