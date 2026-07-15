import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# --- Algorithm Recipe weights (see README "Finalized Algorithm Recipe") ---
GENRE_WEIGHT = 2.0        # points for a genre match
MOOD_WEIGHT = 1.0         # points for a mood match
ACOUSTIC_BONUS = 0.5      # extra points when an acoustic-lover gets an acoustic song
ACOUSTIC_THRESHOLD = 0.5  # acousticness at or above this counts as "acoustic"


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
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


def _score_features(
    fav_genre: Optional[str],
    fav_mood: Optional[str],
    target_energy: Optional[float],
    likes_acoustic: bool,
    genre: Optional[str],
    mood: Optional[str],
    energy: float,
    acousticness: float,
) -> Tuple[float, List[str]]:
    """Shared scoring core so the dict and object APIs use one Algorithm Recipe."""
    score = 0.0
    reasons: List[str] = []

    if fav_genre is not None and genre == fav_genre:
        score += GENRE_WEIGHT
        reasons.append(f"genre match: {genre} (+{GENRE_WEIGHT:.1f})")

    if fav_mood is not None and mood == fav_mood:
        score += MOOD_WEIGHT
        reasons.append(f"mood match: {mood} (+{MOOD_WEIGHT:.1f})")

    if target_energy is not None:
        similarity = 1.0 - abs(energy - target_energy)
        score += similarity
        reasons.append(
            f"energy fit: {energy:.2f} vs target {target_energy:.2f} (+{similarity:.2f})"
        )

    if likes_acoustic and acousticness >= ACOUSTIC_THRESHOLD:
        score += ACOUSTIC_BONUS
        reasons.append(f"acoustic match: acousticness {acousticness:.2f} (+{ACOUSTIC_BONUS:.1f})")

    if not reasons:
        reasons.append("no strong matches for this profile")

    return score, reasons


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Score one Song against a UserProfile using the shared recipe."""
        return _score_features(
            user.favorite_genre,
            user.favorite_mood,
            user.target_energy,
            user.likes_acoustic,
            song.genre,
            song.mood,
            song.energy,
            song.acousticness,
        )

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
    """Load songs from a CSV into a list of dicts, converting numeric fields to numbers."""
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            for field in ("energy", "tempo_bpm", "valence", "danceability", "acousticness"):
                row[field] = float(row[field])
            songs.append(row)
    print(f"Loaded songs: {len(songs)}")
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song dict against a user_prefs dict; returns (score, reasons)."""
    fav_genre = user_prefs.get("favorite_genre", user_prefs.get("genre"))
    fav_mood = user_prefs.get("favorite_mood", user_prefs.get("mood"))
    target_energy = user_prefs.get("target_energy", user_prefs.get("energy"))
    likes_acoustic = user_prefs.get("likes_acoustic", False)
    return _score_features(
        fav_genre,
        fav_mood,
        target_energy,
        likes_acoustic,
        song.get("genre"),
        song.get("mood"),
        float(song.get("energy", 0.0)),
        float(song.get("acousticness", 0.0)),
    )


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5
) -> List[Tuple[Dict, float, str]]:
    """Score every song, rank highest first, and return the top k as (song, score, explanation)."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, "; ".join(reasons)))
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
