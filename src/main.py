"""
Command line runner for the Music Recommender Simulation.

Demonstrates the optional extensions:
- Challenge 1: advanced song features (popularity, release_decade, mood_tags)
- Challenge 2: multiple scoring modes (Strategy pattern) via --mode
- Challenge 3: diversity/fairness re-ranking via --diversity
- Challenge 4: a formatted ASCII results table

Examples:
    python -m src.main
    python -m src.main --mode genre-first
    python -m src.main --mode energy-focused --diversity
"""

import argparse
import textwrap

try:
    # Works with: python -m src.main  (run from the project root)
    from src.recommender import (
        load_songs, recommend_songs, STRATEGIES, BALANCED, DiversityConfig,
    )
except ImportError:
    # Works with: python src/main.py
    from recommender import (
        load_songs, recommend_songs, STRATEGIES, BALANCED, DiversityConfig,
    )


# Profiles now use the advanced preferences too (Challenge 1).
PROFILES = [
    ("High-Energy Pop", {
        "genre": "pop", "mood": "happy", "energy": 0.9,
        "min_popularity": 70, "preferred_decade": 2020, "preferred_tags": ["euphoric"],
    }),
    ("Chill Lofi", {
        "genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True,
        "preferred_tags": ["calm", "focused"],
    }),
    ("Deep Intense Rock", {
        "genre": "rock", "mood": "intense", "energy": 0.9,
        "preferred_tags": ["aggressive"],
    }),
]


def format_table(recommendations) -> str:
    """Render recommendations as an ASCII table with a wrapped 'Why' column."""
    headers = ["#", "Title", "Artist", "Score", "Why (reasons)"]
    why_width = 46
    rows = []
    for i, (song, score, explanation) in enumerate(recommendations, start=1):
        rows.append([
            str(i),
            str(song.get("title", "")),
            str(song.get("artist", "")),
            f"{score:.2f}",
            textwrap.wrap(explanation, why_width) or [""],
        ])

    # Column widths (the Why column is fixed-width and wrapped).
    widths = [
        max(len(headers[0]), *(len(r[0]) for r in rows)),
        max(len(headers[1]), *(len(r[1]) for r in rows)),
        max(len(headers[2]), *(len(r[2]) for r in rows)),
        max(len(headers[3]), *(len(r[3]) for r in rows)),
        why_width,
    ]

    def sep() -> str:
        return "+" + "+".join("-" * (w + 2) for w in widths) + "+"

    def render(cells) -> str:
        return "| " + " | ".join(cells[i].ljust(widths[i]) for i in range(len(widths))) + " |"

    lines = [sep(), render(headers), sep()]
    for r in rows:
        why_lines = r[4]
        for line_idx, why in enumerate(why_lines):
            if line_idx == 0:
                lines.append(render([r[0], r[1], r[2], r[3], why]))
            else:
                lines.append(render(["", "", "", "", why]))
        lines.append(sep())
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Music recommender simulation")
    parser.add_argument(
        "--mode", choices=sorted(STRATEGIES), default="balanced",
        help="scoring strategy (Challenge 2)",
    )
    parser.add_argument(
        "--diversity", action="store_true",
        help="cap repeats of the same artist/genre in the results (Challenge 3)",
    )
    args = parser.parse_args()

    strategy = STRATEGIES.get(args.mode, BALANCED)
    diversity = DiversityConfig() if args.diversity else None

    songs = load_songs("data/songs.csv")
    print(f"\nScoring mode: {strategy.name}  |  diversity: {'on' if diversity else 'off'}")

    for name, prefs in PROFILES:
        print(f"\n=== Profile: {name} ===")
        print(f"Preferences: {prefs}")
        recs = recommend_songs(prefs, songs, k=5, strategy=strategy, diversity=diversity)
        print(format_table(recs))


if __name__ == "__main__":
    main()
