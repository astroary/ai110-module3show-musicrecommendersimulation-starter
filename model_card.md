# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

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

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
