# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeMatch 1.0** — a content-based music recommender that matches songs to a
listener's stated "vibe."

---

## 2. Intended Use  

VibeMatch takes a short "taste profile" (a favorite genre, a favorite mood, a target
energy level, and whether the user likes acoustic songs) and suggests the songs from a
small catalog that best fit that profile. It assumes the user can describe their taste in
those four terms, and that their taste is fairly stable for a single request. This is a
**classroom exploration project**, not a real product — it runs on 18 hand-picked songs
and is meant to teach how a recommender turns data into ranked suggestions, not to serve
real listeners.

---

## 3. How the Model Works  

Think of it like a points contest. Every song in the catalog starts with zero points and
earns points for matching what the user asked for. If the song's genre matches the user's
favorite genre, it gets 2 points. If its mood matches, it gets 1 more point. Then it
earns up to 1 point for how close its energy is to the energy the user wanted — a perfect
match gets the full point, and the further off it is, the fewer points it gets. If the
user likes acoustic music and the song is acoustic, it gets a small half-point bonus.
After every song has a score, the system lines them all up from most points to fewest and
shows the top few. It also writes a plain-English reason for each song so you can see
exactly which rules earned the points. Compared to the starter code (which just returned
the first few songs), I added all of the actual scoring, the "closeness" idea for energy,
and the explanations.

---

## 4. Data  

The catalog has **18 songs** stored in `data/songs.csv`. Each song lists a genre, a mood,
and five numbers between 0 and 1 (energy, valence, danceability, acousticness) plus a
tempo. It started as 10 songs, and I added 8 more to cover genres and moods the starter
file was missing — hip hop, classical, edm, country, r&b, metal, folk, and reggae, with
moods like energetic, peaceful, euphoric, nostalgic, romantic, angry, melancholy, and
uplifting. Even so, the dataset is tiny and I chose all the values by hand, so a lot of
real musical taste is missing: there are no lyrics or language, no era or popularity, and
usually only one or two songs per genre, which limits variety in the results.

---

## 5. Strengths  

The system works well for **clear, non-contradictory tastes**. When I asked for
high-energy pop, chill lofi, or intense rock, the top result each time was a song that
genuinely matched the genre, mood, and energy — exactly what I would have picked myself.
The "closeness" scoring for energy is a real strength: a song at 0.42 energy correctly
beats one at 0.90 when the user wants 0.40, instead of the system just preferring loud
songs. It is also **transparent** — every recommendation comes with the reasons and
points that produced it, so it is easy to trust and easy to debug. In short, when a user's
preferences all point the same direction, the rankings feel right.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

The biggest weakness I found is that the **categorical bonuses (genre +2.0, mood +1.0)
overpower the energy score**, which can only ever contribute between 0.0 and 1.0. In my
"Conflicted" test the user asked for high energy (0.9), but *Paper Boats* — a folk,
melancholy song with energy 0.33 — still ranked first, because matching the requested
genre and mood alone was worth +3.0 and buried the fact that its energy was completely
wrong. In other words, a song can top the list while directly contradicting one of the
user's stated preferences. The system also uses **exact string matching**, so a fan of
`pop` gets zero credit for a great `indie pop` track, and it **ignores most of the data
it has** (tempo, valence, danceability), so two very different-feeling songs that happen
to share a genre and mood look identical to it. Finally, because I hand-authored the
18-song catalog, any genre with few entries (e.g. only one folk or metal song) gives
those users almost no variety in their top 5.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

### Profiles tested

I ran four profiles through `src/main.py` (full output is in the README under
"Experiments You Tried"):

1. **High-Energy Pop** — `genre=pop, mood=happy, energy=0.9`
2. **Chill Lofi** — `genre=lofi, mood=chill, energy=0.35, likes_acoustic=True`
3. **Deep Intense Rock** — `genre=rock, mood=intense, energy=0.9`
4. **Conflicted (adversarial)** — `genre=folk, mood=melancholy, energy=0.9`
   (deliberately asks for a calm genre/mood but high energy)

I looked for two things: whether the top result actually matched the profile's vibe,
and whether the *reasons* printed for each song explained the ranking honestly.

### What surprised me

The three "normal" profiles behaved exactly as I hoped — each returned a song that
matched its genre, mood, and energy as the clear #1 (*Sunrise City*, *Library Rain*,
*Storm Runner*). The surprise was the **Conflicted** profile: I expected the high energy
request (0.9) to pull an energetic song to the top, but *Paper Boats* (energy 0.33) won
anyway because the genre + mood match was worth far more than the energy gap. That single
test is what exposed the weighting problem described in Limitations and Bias.

### Comparing the profiles

- **High-Energy Pop vs Chill Lofi** — opposite ends of the energy scale. Pop surfaces
  bright, danceable tracks (*Sunrise City*, *Gym Hero*); Lofi shifts entirely toward
  quiet, acoustic, low-energy tracks (*Library Rain*, *Midnight Coding*). The acoustic
  bonus only fires for the Lofi listener, which is why its scores climb above 4.0.
- **Chill Lofi vs Deep Intense Rock** — makes sense that they share *no* songs: one wants
  low energy + acoustic, the other wants high energy + intense, so the energy term pushes
  them in opposite directions on top of the different genres.
- **High-Energy Pop vs Deep Intense Rock** — both want energy 0.9, so their lower ranks
  overlap (both pull in *Gym Hero*, *Neon Horizon* on energy alone), but the genre/mood
  bonuses correctly send each profile's own #1 to the top.
- **Any normal profile vs Conflicted** — the normal profiles' #1 song scores ~3.9–4.5
  (genre + mood + good energy all agreeing), while Conflicted's #1 scores only 3.43
  because its energy actively disagrees. The score itself signals that the match is weaker.

### Experiment I ran

I doubled the energy weight and halved the genre weight (`genre 2.0→1.0`,
`energy 1.0→2.0`) and re-ran the Conflicted profile. The high-energy songs closed the gap
(e.g. *Storm Runner* rose from 0.99 to 1.98), but *Paper Boats* **still ranked first**
(2.86 vs 1.98), because it now collected genre + mood + a decent energy score while the
energetic songs matched neither category. This showed me the ranking flip I expected did
*not* happen — the categorical bonuses are structurally hard to overcome, which is a
stronger statement about the design than just "genre is weighted a bit too high."

---

## 8. Future Work  

If I kept developing VibeMatch, I would:

1. **Rebalance the scoring so no single factor dominates** — for example, cap the total
   genre + mood bonus or require a minimum energy fit, so a song can't top the list while
   ignoring the user's energy request (the flaw my adversarial test found).
2. **Use the features I'm currently wasting** — tempo, valence, and danceability are in
   the data but never scored; adding them would tell similar songs apart instead of
   treating same-genre, same-mood songs as identical.
3. **Replace exact string matching with "similar-to" matching** — so a `pop` fan also
   gets credit for `indie pop`, and add a diversity rule so the top 5 aren't all the same
   genre on a bigger catalog.

---

## 9. Personal Reflection  

My biggest learning moment was building the adversarial "Conflicted" profile and watching
a low-energy folk song win a request for high-energy music. Seeing that made the idea of
"weighting" concrete: the numbers I picked for genre and mood quietly decided what the
system was even allowed to recommend, and my first instinct (just bump up the energy
weight) didn't actually fix it. That's also where AI tools helped most — they were great
for scaffolding the CSV loading and scoring functions and for suggesting edge-case
profiles to try, but I had to double-check the math and the rankings myself, because the
code ran fine while still producing a result that was obviously wrong. What surprised me
is how a handful of `if` statements and one subtraction can *feel* like a real
recommendation, complete with confident-sounding reasons — which is exactly why the
reasons matter, since they're the only thing that reveals when the "smart" suggestion is
really just a weighting artifact. This changed how I think about apps like Spotify: their
recommendations aren't neutral truth, they're the output of weights and data choices that
someone made, and those choices can bury things you'd actually like. If I extended this
project, I'd focus on the fixes in Future Work — rebalancing the score and using the
tempo/valence/danceability features I currently ignore.
