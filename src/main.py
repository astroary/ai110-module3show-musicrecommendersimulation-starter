"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

The functions live in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

try:
    # Works with: python -m src.main  (run from the project root)
    from src.recommender import load_songs, recommend_songs
except ImportError:
    # Works with: python src/main.py
    from recommender import load_songs, recommend_songs


# Phase 4 stress-test profiles: three distinct tastes plus one adversarial
# "conflicting" profile (wants high energy but a genre/mood that is calm).
PROFILES = [
    ("High-Energy Pop", {"genre": "pop", "mood": "happy", "energy": 0.9}),
    ("Chill Lofi", {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True}),
    ("Deep Intense Rock", {"genre": "rock", "mood": "intense", "energy": 0.9}),
    (
        "Conflicted (folk + melancholy, but energy 0.9)",
        {"genre": "folk", "mood": "melancholy", "energy": 0.9},
    ),
]


def print_recommendations(name: str, prefs: dict, songs: list) -> None:
    """Run the recommender for one profile and print the top 5 results."""
    print(f"\n=== Profile: {name} ===")
    print(f"Preferences: {prefs}")
    print("\nTop recommendations:\n")
    for song, score, explanation in recommend_songs(prefs, songs, k=5):
        print(f"{song['title']} - Score: {score:.2f}")
        print(f"Because: {explanation}")
        print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    for name, prefs in PROFILES:
        print_recommendations(name, prefs, songs)


if __name__ == "__main__":
    main()
