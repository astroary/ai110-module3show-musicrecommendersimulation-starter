# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I asked the agent to complete Challenge 1 (Add Advanced Song Features): introduce five
new attributes to the dataset and make the recommender score them.

**Prompts used:**

- "Add 5+ complex attributes to `data/songs.csv` that aren't in the baseline —
  popularity (0-100), release decade, detailed mood tags, language, and explicit — and
  fill sensible values for all 18 songs."
- "Update `src/recommender.py` so scoring accounts for the new attributes: a bonus when
  a song meets a `min_popularity`, a flat bonus for a `preferred_decade` match, and a
  per-tag bonus for `preferred_tags`. Keep the existing tests passing."

**What did the agent generate or change?**

- `data/songs.csv`: added `popularity, release_decade, mood_tags, language, explicit`
  columns for every row.
- `src/recommender.py`: added the new fields to the `Song` dataclass (with defaults),
  extended `load_songs` to convert the int/bool columns, and added three new scoring
  blocks (popularity, decade, mood tags) to the shared scorer.
- `src/main.py`: enriched the demo profiles with `min_popularity`, `preferred_decade`,
  and `preferred_tags`.

**What did you verify or fix manually?**

I ran `pytest` (2 passed) and `python -m src.main` to confirm the new bonuses actually
appear in the printed reasons (e.g. "popularity 78 ≥ 70 (+0.39); decade match: 2020s
(+0.5); mood tags euphoric (+0.30)"). I made sure the new `Song` fields had **defaults**
so the existing tests, which build `Song` with only the original 10 fields, still
construct — this was the main thing that would have broken otherwise.

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

The **Strategy pattern**, to support Challenge 2 (multiple scoring modes).

**How did AI help you brainstorm or implement it?**

I asked how to let a user switch between "Genre-First," "Mood-First," and
"Energy-Focused" ranking without duplicating the scoring code or filling it with
`if mode == ...` branches. The suggestion was to treat the *weights* as the interchangeable
strategy: define one scorer that reads its weights from a `ScoringStrategy` object, then
create a named instance per mode. Swapping the object swaps the behavior, and adding a new
mode is just one more instance — no changes to the scorer.

**How does the pattern appear in your final code?**

In `src/recommender.py`: the `ScoringStrategy` dataclass holds the weights, and
`BALANCED`, `GENRE_FIRST`, `MOOD_FIRST`, and `ENERGY_FOCUSED` are the concrete strategies
(collected in the `STRATEGIES` dict). The `_score()` function is the single scorer that
reads `strategy.genre_weight`, `strategy.mood_weight`, etc. `main.py` selects one via the
`--mode` flag and passes it into `recommend_songs(..., strategy=...)`.
