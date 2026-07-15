import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

# --- Algorithm Recipe defaults (see README "Finalized Algorithm Recipe") ---
GENRE_WEIGHT = 2.0        # points for a genre match
MOOD_WEIGHT = 1.0         # points for a mood match
ENERGY_WEIGHT = 1.0       # multiplier on the 0..1 energy-similarity score
ACOUSTIC_BONUS = 0.5      # extra points when an acoustic-lover gets an acoustic song
ACOUSTIC_THRESHOLD = 0.5  # acousticness at or above this counts as "acoustic"


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py

    The last five fields are optional "advanced" attributes (Challenge 1);
    they default so older 10-field Song(...) construction still works.
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: Optional[int] = None      # 0..100
    release_decade: Optional[int] = None  # e.g. 1990, 2000, 2010, 2020
    mood_tags: str = ""                   # pipe-separated, e.g. "uplifting|euphoric"
    language: str = ""
    explicit: bool = False

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


# --------------------------------------------------------------------------
# Challenge 2: Scoring modes via a simple Strategy pattern.
# Each ScoringStrategy is a set of weights; the scorer reads the weights, so
# swapping strategies swaps ranking behavior without touching the scorer.
# --------------------------------------------------------------------------
@dataclass
class ScoringStrategy:
    name: str
    genre_weight: float = GENRE_WEIGHT
    mood_weight: float = MOOD_WEIGHT
    energy_weight: float = ENERGY_WEIGHT
    acoustic_bonus: float = ACOUSTIC_BONUS
    # Advanced-feature weights (Challenge 1); no-ops unless the song has the
    # attribute AND the profile expresses the matching preference.
    popularity_weight: float = 0.5   # scaled by popularity/100 when min_popularity met
    decade_weight: float = 0.5       # flat bonus for a release-decade match
    tag_weight: float = 0.3          # per matching mood tag


BALANCED = ScoringStrategy("balanced")
GENRE_FIRST = ScoringStrategy("genre-first", genre_weight=3.0, mood_weight=0.5, energy_weight=0.5)
MOOD_FIRST = ScoringStrategy("mood-first", genre_weight=0.5, mood_weight=3.0, energy_weight=0.5)
ENERGY_FOCUSED = ScoringStrategy("energy-focused", genre_weight=0.5, mood_weight=0.5, energy_weight=3.0)

STRATEGIES: Dict[str, ScoringStrategy] = {
    s.name: s for s in (BALANCED, GENRE_FIRST, MOOD_FIRST, ENERGY_FOCUSED)
}


@dataclass
class DiversityConfig:
    """Challenge 3: cap repeats of the same artist/genre in the ranked list."""
    max_per_artist: int = 1
    max_per_genre: int = 2
    penalty: float = 1.0  # points subtracted per repeat beyond the cap


def _parse_tags(raw) -> List[str]:
    """Split a pipe-separated mood_tags string into a clean list."""
    if not raw:
        return []
    return [t.strip().lower() for t in str(raw).split("|") if t.strip()]


def _song_values(song) -> Dict:
    """Normalize a Song object or a song dict into a plain dict of values."""
    return asdict(song) if isinstance(song, Song) else song


def _pref_values(prefs) -> Dict:
    """Normalize a UserProfile or a prefs dict into a plain dict of values."""
    if isinstance(prefs, UserProfile):
        return {
            "genre": prefs.favorite_genre,
            "mood": prefs.favorite_mood,
            "energy": prefs.target_energy,
            "likes_acoustic": prefs.likes_acoustic,
        }
    return prefs


def _score(strategy: ScoringStrategy, prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one normalized song dict against one normalized prefs dict."""
    fav_genre = prefs.get("genre", prefs.get("favorite_genre"))
    fav_mood = prefs.get("mood", prefs.get("favorite_mood"))
    target_energy = prefs.get("energy", prefs.get("target_energy"))
    likes_acoustic = prefs.get("likes_acoustic", False)
    min_popularity = prefs.get("min_popularity")
    preferred_decade = prefs.get("preferred_decade")
    preferred_tags = _parse_tags("|".join(prefs.get("preferred_tags", [])))

    score = 0.0
    reasons: List[str] = []

    if fav_genre is not None and song.get("genre") == fav_genre:
        score += strategy.genre_weight
        reasons.append(f"genre match: {fav_genre} (+{strategy.genre_weight:.1f})")

    if fav_mood is not None and song.get("mood") == fav_mood:
        score += strategy.mood_weight
        reasons.append(f"mood match: {fav_mood} (+{strategy.mood_weight:.1f})")

    if target_energy is not None:
        similarity = strategy.energy_weight * (1.0 - abs(float(song.get("energy", 0.0)) - target_energy))
        score += similarity
        reasons.append(
            f"energy fit: {float(song.get('energy', 0.0)):.2f} vs target {target_energy:.2f} (+{similarity:.2f})"
        )

    if likes_acoustic and float(song.get("acousticness", 0.0) or 0.0) >= ACOUSTIC_THRESHOLD:
        score += strategy.acoustic_bonus
        reasons.append(
            f"acoustic match: acousticness {float(song.get('acousticness', 0.0)):.2f} (+{strategy.acoustic_bonus:.1f})"
        )

    # --- Advanced features (Challenge 1) ---
    if min_popularity is not None and song.get("popularity") is not None:
        popularity = float(song["popularity"])
        if popularity >= min_popularity:
            pts = strategy.popularity_weight * (popularity / 100.0)
            score += pts
            reasons.append(f"popularity {popularity:.0f} ≥ {min_popularity} (+{pts:.2f})")

    if preferred_decade is not None and song.get("release_decade") is not None:
        if int(song["release_decade"]) == int(preferred_decade):
            score += strategy.decade_weight
            reasons.append(f"decade match: {int(preferred_decade)}s (+{strategy.decade_weight:.1f})")

    if preferred_tags:
        matched = [t for t in preferred_tags if t in _parse_tags(song.get("mood_tags"))]
        if matched:
            pts = strategy.tag_weight * len(matched)
            score += pts
            reasons.append(f"mood tags {', '.join(matched)} (+{pts:.2f})")

    if not reasons:
        reasons.append("no strong matches for this profile")

    return score, reasons


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song], strategy: ScoringStrategy = BALANCED):
        self.songs = songs
        self.strategy = strategy

    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Score one Song against a UserProfile using the shared scorer."""
        return _score(self.strategy, _pref_values(user), _song_values(song))

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k Songs for a user, ranked highest score first."""
        scored = [(self._score(user, song)[0], song) for song in self.songs]
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [song for _, song in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation of why a song was scored as it was."""
        score, reasons = self._score(user, song)
        return f"{song.title} scored {score:.2f} — " + "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV into a list of dicts, converting typed fields."""
    int_fields = ("id", "popularity", "release_decade")
    float_fields = ("energy", "tempo_bpm", "valence", "danceability", "acousticness")
    bool_fields = ("explicit",)
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for f_name in int_fields:
                if row.get(f_name) not in (None, ""):
                    row[f_name] = int(row[f_name])
            for f_name in float_fields:
                if row.get(f_name) not in (None, ""):
                    row[f_name] = float(row[f_name])
            for f_name in bool_fields:
                if row.get(f_name) not in (None, ""):
                    row[f_name] = str(row[f_name]).strip().lower() in ("true", "1", "yes")
            songs.append(row)
    print(f"Loaded songs: {len(songs)}")
    return songs


def score_song(
    user_prefs: Dict, song: Dict, strategy: ScoringStrategy = BALANCED
) -> Tuple[float, List[str]]:
    """Score one song dict against a user_prefs dict; returns (score, reasons)."""
    return _score(strategy, _pref_values(user_prefs), _song_values(song))


def _apply_diversity(
    scored: List[Tuple[Dict, float, str]], k: int, cfg: DiversityConfig
) -> List[Tuple[Dict, float, str]]:
    """Greedily pick k items, penalizing repeats of the same artist/genre."""
    pool = list(scored)
    artist_count: Dict[str, int] = {}
    genre_count: Dict[str, int] = {}
    selected: List[Tuple[Dict, float, str]] = []

    while pool and len(selected) < k:
        best_i, best_adj, best_pen = 0, float("-inf"), 0.0
        for i, (song, base, expl) in enumerate(pool):
            artist = str(_song_values(song).get("artist", ""))
            genre = str(_song_values(song).get("genre", ""))
            over_artist = max(0, artist_count.get(artist, 0) - (cfg.max_per_artist - 1))
            over_genre = max(0, genre_count.get(genre, 0) - (cfg.max_per_genre - 1))
            penalty = cfg.penalty * (over_artist + over_genre)
            adj = base - penalty
            if adj > best_adj:
                best_i, best_adj, best_pen = i, adj, penalty

        song, base, expl = pool.pop(best_i)
        artist = str(_song_values(song).get("artist", ""))
        genre = str(_song_values(song).get("genre", ""))
        artist_count[artist] = artist_count.get(artist, 0) + 1
        genre_count[genre] = genre_count.get(genre, 0) + 1
        if best_pen > 0:
            expl = f"{expl}; diversity penalty (-{best_pen:.2f})"
        selected.append((song, best_adj, expl))

    return selected


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    strategy: ScoringStrategy = BALANCED,
    diversity: Optional[DiversityConfig] = None,
) -> List[Tuple[Dict, float, str]]:
    """Score every song, rank highest first, and return the top k as (song, score, explanation)."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, strategy)
        scored.append((song, score, "; ".join(reasons)))
    scored.sort(key=lambda item: item[1], reverse=True)
    if diversity is not None:
        return _apply_diversity(scored, k, diversity)
    return scored[:k]
