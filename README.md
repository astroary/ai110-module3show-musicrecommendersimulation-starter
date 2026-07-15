# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

This version is a content-based music recommender. It represents each song as a set of measurable attributes (genre, mood, energy, and more) and represents a listener as a small taste profile. For any user, it scores every song in the catalog by how closely that song matches the user's stated preferences, then ranks the songs and returns the top few. Unlike a real platform, it uses no listening history or crowd behavior — recommendations come purely from matching song attributes to the profile, which makes the reasoning easy to inspect and explain.

---

## How The System Works

### How real platforms do it

Streaming services like Spotify and YouTube predict what you'll love next using two
main strategies, usually blended together:

- **Collaborative filtering** — recommends songs based on *other users' behavior*.
  If people with listening patterns similar to yours loved a track, the system guesses
  you will too. It relies on signals like likes, skips, replays, and playlist
  co-occurrence. It needs a lot of users and history to work well.
- **Content-based filtering** — recommends songs based on *the songs' own attributes*
  (tempo, energy, mood, genre, "acousticness," etc.) and how well they match a profile
  of what you already enjoy. It works even for a brand-new song with no play history.

Real systems combine both at massive scale and add context (time of day, device,
what's trending). **My version focuses on content-based filtering**, because it is
transparent — I can point to exactly which attributes made a song score well — and it
works on a tiny catalog with no user history.

### What my system prioritizes

My recommender rewards songs that *match the user's taste profile*. A matching genre or
mood earns points, and numeric attributes (like energy) earn more points the *closer*
they are to the user's target rather than simply being high or low. Genre and mood are
weighted more heavily than the fine-grained numeric fit, because the overall "vibe"
matters more to a listener than an exact energy value.

### Data model

**`Song` features used** (from `data/songs.csv`):

| Feature | Type | Used for |
| --- | --- | --- |
| `genre` | categorical (pop, lofi, rock, jazz, …) | exact-match bonus |
| `mood` | categorical (happy, chill, intense, …) | exact-match bonus |
| `energy` | numeric 0.0–1.0 | closeness to `target_energy` |
| `acousticness` | numeric 0.0–1.0 | bonus when user likes acoustic |
| `tempo_bpm`, `valence`, `danceability` | numeric | available for experiments / stretch scoring |
| `id`, `title`, `artist` | identity | display and explanations |

**`UserProfile` stores:**

| Field | Type | Meaning |
| --- | --- | --- |
| `favorite_genre` | string | preferred genre |
| `favorite_mood` | string | preferred mood |
| `target_energy` | float 0.0–1.0 | the energy level the user wants |
| `likes_acoustic` | bool | whether acoustic songs should be boosted |

### Scoring rule vs. ranking rule

The system needs two distinct rules:

- **Scoring rule** (one song) — turns a single song + profile into a number. Add a
  weighted bonus for each matching categorical feature, and for each numeric feature add
  points proportional to *how close* the song is to the target, e.g.
  `energy_score = 1 - |song.energy - user.target_energy|`. The closer the match, the
  higher the score. Each contribution is also recorded as a human-readable reason.
- **Ranking rule** (a list of songs) — applies the scoring rule to every song in the
  catalog, sorts them from highest to lowest score, and returns the top *k*. Scoring
  alone tells you how good one song is; ranking is what turns those individual scores
  into an ordered recommendation list.

### Example user profile

The recommender compares every song against a single taste profile, stored as a
dictionary of target values:

```python
user_prefs = {
    "favorite_genre": "lofi",      # preferred genre
    "favorite_mood": "chill",      # preferred mood
    "target_energy": 0.40,         # desired energy on a 0.0–1.0 scale
    "likes_acoustic": True,        # boost acoustic songs
}
```

This profile is specific enough to tell "chill lofi" apart from "intense rock": the
genre and mood fields separate the two vibes, while `target_energy = 0.40` pulls the
score toward low-energy tracks and away from high-energy ones.

### Finalized Algorithm Recipe

For each song, add up:

| Rule | Points |
| --- | --- |
| Genre matches `favorite_genre` | **+2.0** |
| Mood matches `favorite_mood` | **+1.0** |
| Energy similarity to `target_energy` | **+ (1 − \|song.energy − target_energy\|)** → 0.0 to 1.0 |
| `likes_acoustic` is true **and** song is acoustic (`acousticness ≥ 0.5`) | **+0.5** |

Genre is weighted twice as heavily as mood because a listener's genre is the strongest
signal of the vibe they want; mood refines it. Energy contributes a *proportional*
similarity score rather than a flat bonus, so a song at 0.42 energy beats one at 0.90
when the target is 0.40. Every rule that fires also records a human-readable reason
(e.g. `"genre match: lofi (+2.0)"`) so recommendations can be explained.

### Data flow

```
Input                Process (the loop)                     Output
─────                ──────────────────                     ──────
user_prefs  ─▶  for each song in catalog:            ─▶  sort by score (desc)
(taste          score_song(user_prefs, song)             take top K
 profile)         → (score, reasons)                     ─▶ ranked recommendations
```

### Expected biases

- **Genre over-prioritization** — with +2.0 for genre vs +1.0 for mood, the system may
  bury a song that perfectly matches the user's mood and energy just because its genre
  differs, surfacing weaker same-genre songs instead.
- **Exact-match brittleness** — genre and mood use exact string matching, so closely
  related tastes (e.g. `pop` vs `indie pop`, `chill` vs `relaxed`) score zero overlap
  even though a human would call them similar.
- **Small, hand-authored catalog** — 18 songs with values I chose myself can encode my
  own assumptions about what a genre "should" sound like, which would skew results.

> This design (the "Algorithm Recipe") is implemented in `src/recommender.py` —
> see `score_song` for the scoring rule and `recommend_songs` for the ranking rule.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Output from `python -m src.main` with the default profile
(`genre=pop, mood=happy, energy=0.8`):

```
Loaded songs: 18

Top recommendations:

Sunrise City - Score: 3.98
Because: genre match: pop (+2.0); mood match: happy (+1.0); energy fit: 0.82 vs target 0.80 (+0.98)

Gym Hero - Score: 2.87
Because: genre match: pop (+2.0); energy fit: 0.93 vs target 0.80 (+0.87)

Rooftop Lights - Score: 1.96
Because: mood match: happy (+1.0); energy fit: 0.76 vs target 0.80 (+0.96)

Concrete Bloom - Score: 1.00
Because: energy fit: 0.80 vs target 0.80 (+1.00)

Night Drive Loop - Score: 0.95
Because: energy fit: 0.75 vs target 0.80 (+0.95)
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



