<!-- project-memory:start -->
## Project memory

At the start of relevant project work, read:

- `.project-memory/PROJECT_STATE.md`
- `.project-memory/DECISIONS.md`
- `.project-memory/QUESTIONS.md`

Keep these files concise and grounded in repository evidence. Update them when work materially changes the project state, establishes or supersedes a durable decision, or exposes or resolves an important question. Do not duplicate routine implementation details or Git history.
<!-- project-memory:end -->

## Coding style and audience

- Write code for an intermediate Python and data-science reader who will inspect, modify, and debug it manually.
- Prefer simple, explicit, top-to-bottom code over clever or highly abstract code.
- Use the fewest libraries necessary. Prefer pandas, the Python standard library, and existing project utilities when they are sufficient.
- Do not introduce frameworks, classes, generalized helper systems, or additional dependencies unless the task clearly requires them.
- Keep exploratory transformations visible in notebooks while the logic is still being understood.
- Extract reusable functions only when repetition, testing, or correctness provides a clear reason to do so.
- Use descriptive variable names and small, focused notebook cells.
- Add concise comments that explain major steps, important assumptions, non-obvious transformations, and grain, join, or validation decisions. Do not comment obvious syntax or every individual line.
- Organize analytical notebooks in a readable flow: load, inspect, transform, validate, and persist or summarize.
- Before introducing a substantially more complex implementation, explain why the simpler approach is insufficient.
- Keep production-ready code readable and direct; production quality does not require unnecessary abstraction.

## Project direction

Before relevant project work, read `ROADMAP.md`. Treat it as the source of truth for the product architecture, development sequence, current phase, phase deliverables, and exit criteria.

- Work within the current phase unless the user explicitly requests a broader change.
- Treat the future-state repository tree as illustrative, not as scaffolding to generate immediately.
- Create directories, dependencies, services, and infrastructure only when the current task requires them.
- If implementation needs to depart materially from the roadmap, explain the conflict and rationale before making the change.

## Architecture boundaries

- Bronze preserves source-oriented data with minimal transformation.
- Silver creates clean, normalized, reusable football facts at explicit grains.
- Gold creates features that support fantasy-football decisions.
- Do not create separate Bronze or Silver pipelines for Draft Analysis, Waiver Wire, or Player Explorer. Application use cases should primarily diverge at Gold.
- Streamlit consumes Gold datasets and should not contain substantial feature-engineering logic.
- Airflow orchestrates existing pipelines and should not contain transformation logic.

## Development workflow

- Prototype unfamiliar data and feature logic in notebooks before productionizing it.
- Document metric definitions and validate source fields, joins, denominators, grains, and edge cases.
- Validate important metrics against recognizable NFL players and source totals.
- Prevent future-week leakage in weekly, rolling, and season-to-date features.
- Prefer interpretable metrics and transparent rule-based signals before composite scores or machine learning.
- Promote stable, repeated notebook logic into reusable `src/` modules with focused tests.
- Keep pipeline entry points focused on execution order and configuration; keep business logic in `src/`.
- After promotion, have notebooks import authoritative production functions where practical instead of retaining duplicate implementations.

## Data and repository hygiene

- Declare the grain of every persisted dataset and test uniqueness at that grain where applicable.
- Use Polars where practical. If pandas is introduced, make conversions deliberate and consistent.
- Use local Parquet storage during the initial phases unless a demonstrated requirement justifies another system.
- Do not commit generated NFL datasets, large local artifacts, credentials, or secrets unless the user explicitly requests and approves that scope.
- Preserve unrelated worktree changes and avoid broad formatting or structural churn.

## Documentation maintenance

- Update `ROADMAP.md` when a phase actually begins, its scope materially changes, or its exit criteria are met.
- Keep experimental findings and detailed validation close to the relevant notebook or metric documentation rather than expanding the roadmap into a work log.
- Record durable decisions and consequential unresolved questions in project memory without duplicating the roadmap.
