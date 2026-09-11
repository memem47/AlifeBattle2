# GitHub Copilot Instructions for AlifeBattle

## 1. Project Goal

AlifeBattle is developed as both:

1. a real-time artificial-life battle simulation, and
2. a software engineering learning project.

The developer must be able to understand and explain the system.

Therefore, generating working code is not the only goal.

Code should remain simple, readable, traceable, and consistent with the documented specification and design.

---

## 2. Read the Project Documents First

Before proposing or implementing changes, check the relevant project documents.

The main documents are:

```text
docs/VISION.md
docs/specs/
docs/designs/
```

For version-specific work, read both the specification and design document for that version.

For example:

```text
docs/specs/v0.1_SPEC.md
docs/designs/v0.1_DESIGN.md
```

The priority of project information is:

```text
VISION
  ↓
SPEC
  ↓
DESIGN
  ↓
IMPLEMENTATION
```

Implementation must follow the higher-level documents.

Do not silently change the intended behavior because another implementation appears easier or more sophisticated.

---

## 3. Do Not Expand the Scope

Implement only what is required by the current specification.

Do not add features because they may be useful later.

In particular, do not introduce future systems unless the current version explicitly requires them.

Examples of features that must not be added prematurely include:

* spatial partitioning,
* formation systems,
* morale systems,
* retreat systems,
* behavior trees,
* entity-component systems,
* event buses,
* plugin architectures,
* pathfinding frameworks,
* generalized AI frameworks,
* dependency injection frameworks,
* configuration systems beyond current needs,
* or other speculative abstractions.

A possible future requirement is not a current requirement.

---

## 4. Prefer Simplicity

When several implementations satisfy the specification, prefer the simplest one that is correct and understandable.

Prefer:

```python
for enemy in enemies:
    ...
```

over introducing a complex search structure when the number of agents is small.

Prefer a tuple or simple data structure over introducing a new class when the additional abstraction provides no clear current benefit.

Prefer direct and readable code over clever code.

Do not optimize before a real performance problem has been identified.

---

## 5. Keep the Current Version Small

Each development version should introduce only a small number of new concepts.

Do not combine unrelated improvements in one change.

For example, if the task is:

```text
Add agent separation.
```

do not also:

* redesign targeting,
* introduce formations,
* change combat rules,
* add new traits,
* restructure the entire project,
* or optimize unrelated code.

Keep each change easy to understand and review.

---

## 6. Respect Module Responsibilities

For v0.1, the intended responsibilities are:

### `main.py`

Responsible for:

* application startup,
* Pygame initialization,
* input processing,
* time calculation,
* calling simulation updates,
* calling rendering,
* and application shutdown.

Do not place battle logic in `main.py`.

### `game.py`

Responsible for:

* owning the battle state,
* owning agents,
* simulation update phases,
* target selection coordination,
* movement coordination,
* attack resolution,
* battle completion,
* and restart/reset behavior.

### `agent.py`

Responsible for:

* individual agent state,
* movement behavior,
* attack-related state,
* taking damage,
* checking whether the agent is alive,
* and simple operations that naturally belong to one agent.

An agent must not manage the entire battle.

### `renderer.py`

Responsible only for visualization.

Rendering may read simulation state.

Rendering must not modify simulation state.

### `config.py`

Responsible for simulation and visualization parameters.

Avoid unexplained numeric constants in simulation logic when they are configuration values.

---

## 7. Preserve Dependency Direction

Simulation logic must not depend on rendering.

Lower-level modules should not import higher-level application modules.

Prefer dependencies in this general direction:

```text
main
 ├── game
 └── renderer

game
 └── agent

agent
 └── config
```

Avoid circular imports.

Do not restructure dependencies without a clear reason.

---

## 8. Keep Simulation Logic Deterministic Where Practical

Reproducible behavior is valuable for debugging.

Prefer fixed starting positions for early versions.

If randomness is added:

* use an explicit random seed where practical,
* make the source of randomness clear,
* and avoid unnecessary randomness.

Do not introduce randomness simply to make the simulation look more interesting.

---

## 9. Keep Time-Based Behavior Independent of Frame Rate

Movement and other time-dependent simulation behavior should use elapsed simulation time.

Use:

```text
distance = speed × delta_time
```

rather than:

```text
distance = speed_per_frame
```

Do not make simulation speed depend directly on rendering FPS.

Large `delta_time` values should be handled according to the current design document.

---

## 10. Avoid Iteration-Order Bias

When multiple agents make decisions during the same simulation update, do not unintentionally give an advantage to agents that happen to be processed earlier in a Python list.

For v0.1:

* movement decisions should use a consistent position snapshot where required,
* attack decisions should be collected first,
* damage should then be applied as a separate phase.

Do not immediately apply attack damage if doing so would change whether another already-valid attack occurs during the same update.

---

## 11. Separate Decision and State Mutation When Useful

Prefer explicit simulation phases when several agents interact.

For example:

```text
select targets
    ↓
calculate movement
    ↓
apply movement
    ↓
collect attacks
    ↓
apply damage
    ↓
check battle result
```

This makes behavior easier to understand and reduces hidden dependency on execution order.

Do not create a complicated event system to achieve this.

Simple temporary lists or dictionaries are sufficient when they solve the problem.

---

## 12. Testing Is Part of the Implementation

When behavior is added or changed, add or update tests when practical.

Tests should focus on simulation behavior rather than rendering.

For v0.1, important behavior includes:

* damage,
* death,
* movement,
* attack range,
* cooldown,
* target selection,
* exclusion of dead targets,
* victory detection,
* draw detection,
* and simultaneous combat.

A change is not complete merely because the application runs visually.

---

## 13. Do Not Hide Bugs With Special Cases

If unexpected behavior appears, first identify its cause.

Do not immediately add special-case conditions such as:

```python
if strange_case:
    return
```

unless the condition represents an actual rule in the specification.

Prefer fixing the underlying model or implementation error.

If a workaround is unavoidable, explain why it is needed.

---

## 14. Avoid Unnecessary Defensive Complexity

Do not add large amounts of defensive code for impossible or unsupported states.

Handle realistic edge cases defined by the current specification and design.

For v0.1, examples include:

* no living enemy exists,
* two agents occupy the same position,
* HP becomes negative,
* `delta_time` becomes unusually large,
* both teams die during the same update.

Do not build a generalized error-recovery architecture unless the project actually requires one.

---

## 15. Keep Changes Local

When modifying existing code:

1. identify the smallest set of files that needs to change,
2. make the required change,
3. update tests,
4. avoid unrelated refactoring.

Do not rewrite working modules merely because another style is possible.

If a larger refactoring is genuinely necessary, explain the reason before making broad structural changes.

---

## 16. Do Not Modify Project Documents Without Intent

Do not automatically rewrite:

```text
VISION.md
SPEC documents
DESIGN documents
```

to match an implementation.

The implementation should match the documents, not the other way around.

If the implementation reveals that the specification or design should change, point out the inconsistency clearly.

A document change should be an explicit engineering decision.

---

## 17. Explain Significant Changes

When proposing a non-trivial implementation, briefly explain:

* what will change,
* why it is necessary,
* which files are affected,
* and how the change follows the current specification and design.

The explanation should focus on engineering reasoning, not merely describe syntax.

When multiple reasonable designs exist, explain the main trade-off.

---

## 18. Teach, Do Not Only Generate

This project is also used to improve the developer's engineering skills.

When appropriate, help the developer understand:

* responsibilities,
* data flow,
* update order,
* dependency direction,
* algorithmic complexity,
* state ownership,
* trade-offs,
* and reasons behind design decisions.

Do not replace a simple understandable implementation with sophisticated code solely because it is technically elegant.

A solution the developer can explain is preferred over a more advanced solution the developer cannot understand.

---

## 19. Comments

Use comments to explain:

* why something is done,
* non-obvious simulation rules,
* important design constraints,
* and behavior that may otherwise appear incorrect.

Avoid comments that merely repeat the code.

Bad:

```python
# Increase x by one
x += 1
```

Better:

```python
# Apply all attacks after decisions are collected so combat
# results do not depend on agent iteration order.
```

---

## 20. Naming

Prefer names that describe domain meaning clearly.

Examples:

```text
attack_cooldown
nearest_enemy
living_agents
attack_range
movement_speed
battle_finished
```

Avoid unexplained abbreviations unless they are widely understood in the project.

Prefer clarity over short names.

---

## 21. Type Hints

Use Python type hints where they improve understanding.

Do not introduce complex typing solely for type-system sophistication.

Type hints should make data flow easier to understand.

For example:

```python
def update(self, dt: float) -> None:
    ...
```

is useful.

A complicated generic abstraction that exists only to satisfy typing is not required.

---

## 22. Performance

Performance matters to the long-term project, but early versions prioritize clarity.

For current small-scale versions:

* use simple algorithms,
* measure before optimizing,
* identify the actual bottleneck,
* and optimize only the necessary part.

Do not introduce a Spatial Grid into a 20-agent simulation merely because the future project may contain 2000 agents.

When optimization becomes necessary, preserve simulation behavior and add tests before changing the algorithm.

---

## 23. Refactoring Rule

Refactor when at least one concrete problem exists, such as:

* duplicated logic is causing maintenance problems,
* one function has multiple unclear responsibilities,
* code cannot be tested reasonably,
* a new required feature cannot be added cleanly,
* or the current structure contradicts the design document.

Do not refactor solely because a more abstract architecture is imaginable.

---

## 24. Completion Rule

Do not treat a feature as complete only because code has been generated.

A feature is complete when:

1. it matches the specification,
2. it follows the intended design,
3. the program runs,
4. relevant tests pass,
5. its behavior can be observed,
6. and the developer can explain how it works.

---

## 25. Current v0.1 Priority

For v0.1, the goal is only:

> Twenty agents. Two teams. Move, fight, die, win.

Do not add complexity that is not necessary to accomplish this goal.

The most important architectural question is:

> Can the complete path from target selection to movement, attack, damage, death, and victory be followed and understood?

If the answer becomes difficult, simplify the code.

---

## 26. Default Decision Rule

When uncertain between two approaches, prefer the approach that is:

1. consistent with the current specification,
2. easier to understand,
3. easier to test,
4. smaller,
5. and easier to replace later.

Do not optimize for hypothetical future requirements.

> Build only what the current version needs, understand it completely, and then improve it one step at a time.
