# CrewAI 1.15.18 + GPT-5.6 (Terra/Luna) Upgrade

Audit trail for the crewai/model upgrade done on branch
`feature/gpt-5.6-terra-upgrade`. Each entry: what changed, why, and how to
revert just that piece. Intended to be replayable on other crewAI projects.

## Research findings (grounded, not assumed)

- **GPT-5.6** is a real OpenAI model family released 2026-07-09, three tiers:
  Luna (fast/cheap), Terra (balanced, 1.05M-token context, $2/$12 per M
  input/output tokens), Sol (flagship). `gpt-5.1` (previously used here) was
  removed from ChatGPT in March 2026 and is legacy.
- **GPT-5.6 rejects `temperature` unless `reasoning.effort="none"`** — passing
  both causes an OpenAI 400 error. Verified against crewai 1.15.18's native
  OpenAI completion path (`crewai/llms/providers/openai/completion.py`), which
  always forwards `temperature` if set and does not auto-strip it for
  reasoning models.
- **CrewAI 1.12–1.13 rearchitected the LLM class**: litellm is no longer a
  core dependency. OpenAI, Anthropic, Gemini, Azure, and Bedrock now route
  through native SDKs (`crewai/llms/providers/*`); litellm is pulled in only
  as an optional `litellm` extra, needed here for the (currently unused)
  Mistral/Ollama provider entries.
- crewai 1.15.18 already contains a specific workaround for a documented
  GPT-5.6 quirk (auto-retry with `reasoning_effort="none"` when the API
  rejects function tools + reasoning_effort together) — evidence this crewai
  version was built with GPT-5.6 compatibility in mind.
- crewai's `reasoning_effort` field is `Literal["none","low","medium","high"]`
  — it does not yet expose OpenAI's `xhigh`/`max` tiers.
- The `anthropic` Python SDK was not installed at all pre-upgrade. Native
  Anthropic routing after the crewai upgrade needs the `anthropic` extra;
  skipped here since the `claude-*` providers aren't assigned to any agent.

## Amendments

### 1. `pyproject.toml`
- Changed: `crewai[tools]>=1.3.0` → `crewai[tools]>=1.15.18`.
- Why: 1.3.0 predates native-SDK routing and any GPT-5.6-specific handling.
- Revert: change the version constraint back and run `uv sync`.

### 2. `uv.lock` / `.venv`
- Changed: `uv sync` after the pyproject bump. `litellm` is no longer
  installed (it was previously a transitive dependency of crewai; it's now
  an opt-in extra we did not add).
- Consequence: the `mistral` and `ollama` provider entries in
  `llm_config.yaml` will raise `ImportError` if ever assigned to an agent
  (no native SDK adapter, and litellm isn't installed). They are currently
  unused, so this is inert. If you need them again: add `litellm` to the
  `crewai[...]` extras in `pyproject.toml` and `uv sync`.
- Revert: `git checkout main -- pyproject.toml uv.lock && uv sync`.

### 3. `src/transit_reader/config/llm_config.yaml`
- Changed: removed `gpt` (gpt-5.1), `gpt4` (gpt-4.1), `gpt4_mini`
  (gpt-4.1-mini) providers; added `gpt5_6_terra` (`gpt-5.6-terra`,
  `reasoning_effort: medium`) and `gpt5_6_luna` (`gpt-5.6-luna`,
  `reasoning_effort: low`). Reassigned every agent that was on `gpt`/`gpt4`/
  `gpt4_mini`: `temperature: deterministic` agents (the `*_reader` chart
  agents) plus `chart_data_synthesizer` → `gpt5_6_luna`; every other agent
  (creative/review/synthesis-labeled but not literally the `synthesis`
  preset used by `chart_data_synthesizer`) → `gpt5_6_terra`.
- Why: user request to modernize off gpt-5.1/gpt-4.1 and split "main model"
  vs "technical/deterministic model" duties between Terra and Luna.
- Non-OpenAI providers (`gemini`, `gemini_flash`, `ollama`, `mistral`,
  `claude-*`) left untouched — not in scope, not currently reassigned.
- **Backup**: the pre-upgrade file is saved verbatim at
  `src/transit_reader/config/llm_config.pre-gpt5.6.yaml.bak`.
- Revert: `cp src/transit_reader/config/llm_config.pre-gpt5.6.yaml.bak src/transit_reader/config/llm_config.yaml`.

### 4. `src/transit_reader/utils/llm_manager.py`
- Changed `_create_llm_instance`: if a provider defines `reasoning_effort`,
  that's passed to `LLM(...)` and `temperature` is omitted entirely (instead
  of always passing `temperature`). Providers without `reasoning_effort`
  behave exactly as before.
- Why: required to avoid the GPT-5.6 400 error described above.
- Removed the dead legacy-compatibility block: `_create_legacy_llms()`,
  `_create_fallback_llms()`, and the module-level `gpt41_deterministic` /
  `gpt41_creative` / `gpt41` instances (previously ~57 lines, executed
  eagerly at import time). Confirmed via repo-wide grep that nothing outside
  this file imported those names. Removal was necessary, not incidental
  cleanup: once `gpt-4.1` was removed from `providers`, this block would have
  silently fallen through to `_create_fallback_llms()`, which hardcodes
  `model="gpt-4.1"` directly — reintroducing the exact sunset model on every
  import, bypassing the whole config-driven design.
- Revert: `git checkout main -- src/transit_reader/utils/llm_manager.py`.

## Deferred / explicitly out of scope

- **Prompt tuning for creative/deterministic steering.** Temperature used to
  differentiate agent behavior (0.1 deterministic → 0.9 creative); GPT-5.6
  agents now run at a fixed `reasoning_effort` per provider instead, with no
  equivalent per-agent dial. If output quality/style needs the old spread of
  behavior, that now has to come from `config/tasks.yaml` prompt wording —
  deliberately left untouched here so the model swap could be verified in
  isolation before mixing in prompt changes.
- **`litellm`/`anthropic` extras** — not added since those providers are
  unused; add them if that changes (see amendment 2).

## Verification performed

1. `python -m transit_reader.utils.llm_manager` — config loads; both new
   providers instantiate; no agent left on a sunset provider.
2. `uv run pytest` — 22 passed. (2 test files fail to collect due to a
   missing `googleapiclient`/`google-api-python-client` dependency that has
   never been in `uv.lock` in this repo's git history — pre-existing,
   unrelated to this upgrade, not touched here.)
3. Live smoke test: real `.call()` against both `gpt5_6_luna` and
   `gpt5_6_terra` via `get_llm_for_agent` — both returned successfully with
   `reasoning_effort` set and no `temperature` passed, confirming no 400.
4. Not yet done: full `uv run kickoff` end-to-end report generation. Do this
   before merging to `main`.

## Go/no-go note

If the end-to-end run in step 4 above surfaces new errors that aren't
resolved by a small follow-up (vs. needing a deeper prompt-tuning project),
revert via amendment steps above (or `git checkout main` / delete this
branch) rather than debugging indefinitely — the isolated live smoke test
already confirms the core plumbing works, so a real failure at that stage is
likely price/behavior/quality related, not a wiring bug.

## Replaying on other crewAI projects

If this proves stable: the reusable pattern is (a) bump crewai past 1.12+,
(b) check whether each currently-used provider has a native SDK route or
needs the `litellm`/`anthropic`/etc. extras, (c) for any OpenAI reasoning-tier
model, gate `temperature` behind a `reasoning_effort`-is-absent check in
whatever central LLM-factory function that project uses, (d) grep for and
remove any hardcoded legacy-model fallback code before sunsetting the old
model from config, or it will silently keep getting used.
