# 3Blue1Brown Narration Style Guide

Taken from four transcripts: *But what is a neural network?*, *Gradient descent*,
*But what is the Central Limit Theorem?*, and *Solving Wordle using information theory*.
Use it as a spec when writing narration and planning scenes.

---

## 1. Pacing

| Metric | Value (range across videos) |
|---|---|
| Overall rate, pauses included | **180–200 wpm** (NN 183, GD 179, CLT 200, Wordle ~208) |
| Rate while speaking | **200–220 wpm** (~3.4–3.7 words/s) |
| Sentence length | median **~25 words**. Long, comma-chained spoken sentences, with short punch lines mixed in |
| Pauses ≥ 1 s | ~**1.5–2 per minute** |
| Pauses ≥ 3 s | ~**1 every 3–5 minutes** |
| Rhetorical questions | ~**0.4–0.8 per minute** |
| Episode length | 18–31 min, ~3,400–6,300 words |

**Where pauses go.** Silence is for visuals. The narrator stops talking while an animation plays.
- **~2 s:** after a new object appears or a definition lands ("…compute their weighted sum according to these weights." ⏸).
- **3–5 s:** at section breaks, and after a key number or result is revealed ("…is about 5.8." ⏸, "…classifying about 96%…" ⏸). Also before "Now…", "So…", or "Let's zoom out…".
- **5–16 s:** while a simulation runs, after a "ponder this" question, or before the outro.
- Never pause in the middle of an idea. The pause comes after the sentence that sets up the visual.

**Within a section, the rhythm is**: a long explanatory sentence, then a short confirmation ("That's it, that is the general idea." / "And that is just one neuron." / "There you go, that gives us the answer.").

---

## 2. Narrative structure

Every video follows the same arc. Positions are given as a fraction of runtime.

1. **Cold open on one concrete object (first ~5 s).** Use a demonstrative and a noun: *"This is a 3."*, *"This is a Galton board."*, *"The game Wordle has gone pretty viral…"*. No title card and no "today we'll learn."
2. **Make it feel strange or hard (to ~5%).** *"Take a moment to appreciate how crazy it is that brains can do this so effortlessly."* Turn a trivial-seeming task into a daunting one.
3. **Promise and scope (5–10%).** Say what this video covers and what it doesn't: *"assuming no background"*, *"this video is just going to be devoted to the structure… the following one is going to tackle learning."* Tease the deeper follow-up.
4. **Toy model with stated simplifications (10–15%).** Give the simplest version and admit its flaws openly: *"we make the highly unrealistic assumption…"*, *"as if they're all ghosts."*
5. **The core claim in plain words (~15%).** Before any formula: *"as you let the size of that sum get bigger… it will look more and more like a bell curve. That's it."*
6. **Pose a concrete target question (~15–20%)** to answer by the end (*"Could you find a range… 95% sure…?"*). Optionally hold something back: *"I'm not going to tell you what [the three assumptions] are until the very end."*
7. **Build intuition with examples and simulations (20–50%).** Raise the complexity one step at a time.
8. **Formalize (50–80%).** Introduce notation and formulas (see §3), then restate each in words.
9. **Recap with "zoom out" (~75%).** *"Let's zoom out and sum up where we are so far."* Stack the layers: *"…a layer of complexity on top of that… one more layer of complexity still."*
10. **Payoff:** answer the target question with concrete numbers (350, 17.1, so 316 to 384).
11. **Twist or honest caveat (80–95%).** Compare what we hoped for with what actually happens (*"So is this what our network is actually doing? Well, for this one at least, not at all."*). Mention violated assumptions, especially ones the cold-open example breaks.
12. **Close:** a question for the viewer to ponder, a tease of the next video, thanks. Sometimes add an expert interview clip.

---

## 3. How formulas are introduced

- **Concept first, name second, symbol last.** *"This number inside the neuron is called its activation."* *"The computation… has a fancy name, it's called a convolution, but it's essentially just the weighted version of the counting game."* *"This process… is called gradient descent."*
- **Build the formula one piece at a time, justifying each piece.** For the normal pdf: eˣ (growth), then e⁻ˣ (decay), then e^(−|x|) (rejected: "awkward sharp point"), then e^(−x²) (smooth bell). Next a constant to stretch it, then "suggestively" naming it σ², then dividing by √π so the area is 1, which gives 1/(σ√2π). Show rejected alternatives too.
- **Derive from examples, never state from nowhere.** Information: 1 bit halves the possibilities, 2 bits quarter them, 3 bits cut to an eighth. Then: *"take a moment and pause and ask yourself, what is the formula?"* Then (½)^bits = p, then 2^bits = 1/p, then log₂(1/p), then −log₂ p.
- **Write it the long way first, then compress.** Write the explicit weighted sum with sigmoid. Then *"the actual function here is a little cumbersome to write down, don't you think?"* leads to σ(Wa + b), with each row of W mapped back to one neuron.
- **Read every formula back in plain English right away.** *"It's essentially saying how many standard deviations away from the mean is this sum?"* *"…a very intuitive idea of asking how many times you've cut down your possibilities in half."*
- **Justify odd choices.** *"Why are logarithms entering the picture?"* Because information adds where probability multiplies. Squaring beats absolute value "to make the math much nicer," but the units are off, which is why we take the square root to get σ.
- **Offer two readings of one object.** The gradient is the uphill direction, *and* it encodes the relative importance of each weight ("bang for your buck").
- **Present the rigorous statement last, as optional.** *"For the more theoretically minded… the rigorous no-jokes-this-time statement…"*
- **Point to other material instead of detouring.** *"If you're unfamiliar with multivariable calculus… check out…"*, *"all that matters for you and me right now is that in principle there exists a way to compute this vector."*
- **Use concrete numbers throughout:** 784, 16, 13,000, 2.24, 5.8 bits, 96%.

---

## 4. Visual sequencing

The narration is full of deictic words ("this", "here", "on screen"), so every sentence assumes a visual is attached to it.

- **One specific instance, then many, then the abstraction.** One "3", then *"this, this and this are also 3s"*, then the general digit task. One neuron, then a whole layer, then the whole network as a function.
- **One dimension, then two, then N.** A 1-input function with a ball rolling downhill, then a 2-input surface, then the claim *"it's the same basic idea for 13,000 inputs."* Keep showing the 2-D picture and say why.
- **Zoom in, then zoom out.** *"To zoom in on one very specific example…"* means isolating one neuron or region and dimming the rest. *"Let's zoom out"* means returning to the full diagram.
- **Simulation before theory.** Run the random process live (balls, dice), then pull back: *"it also feels a little imprecise"*. Then compute the exact distribution and reuse the same layout.
- **Panels side by side for comparison.** Four simulations at once (sum of 2, 5, 10, 15). The top distribution drives the bottom distribution.
- **Use color to carry meaning, and keep it consistent.** Green = positive weight, red = negative. Brightness = magnitude. Lit neuron = high activation. Yellow, green, and gray Wordle tiles keep their meaning in every chart.
- **Keep one persistent diagram and add annotations to it.** *"Let's go back to our distribution for weary and add another little tracker on here."*
- **Make parameters interactive.** Change the input distribution and watch the output stay put. *"Notice what happens as I change…"*
- **Rescale or re-plot on screen and say so.** *"Let me rescale the y direction…"*, *"the area of each bar, rather than the height, is the probability."*
- **Transform formulas in place.** Each new term appears in the same expression, and the matching part of the graph changes at the same time.
- **Recall earlier visuals by name.** *"Remember how last video we looked at…"*, *"earlier on I actually showed this in the form of a simulation."*

---

## 5. Recurring rhetorical devices

- **"You and I"** as co-investigators: *"you and I are just going to look at the simplest plain vanilla form."*
- **Provisional definitions, revised later.** *"Right now when I say neuron all I want you to think about is a thing that holds a number."* Later: *"Remember how earlier I said…? It's actually more accurate to think of each neuron as a function."*
- **State the hope, then test it.** *"In a perfect world, we might hope that…"*, then later reveal whether it holds.
- **Rhetorical questions that frame the next step.** *"What are the neurons, and in what sense are they linked together?"*, *"In other words, what's the downhill direction?"*
- **Pause-and-predict prompts.** *"As a quiz for you…"*, *"Let me ask you, what is the entropy of this distribution?"*, *"pause right now and think deeply for a moment…"*
- **Answer objections before they're raised.** *"For those of you inclined to complain that this is a highly unrealistic model…"*, *"you might wonder, is it supposed to look that way, or is that just an artifact?"* The answer comes later.
- **Audience branching.** *"Calculus students will know…"*, *"Those of you familiar with…"*, *"If you're unfamiliar… check out…"*
- **Admit arbitrary choices.** *"16, well that was just a nice number to fit on the screen."* *"Kind of just licking my finger and sticking it into the wind."*
- **Wonder words, used sparingly:** *"the real magic here"*, *"kind of mind-boggling"*, *"crown jewels"*, *"I know, right? What is pi doing here?"*
- **Playful coinages and personification:** *"sigmoid squishification"*, *"no, bad computer… utter trash"*, *"how bad the computer should feel"*, *"put yourself in the network's shoes."*
- **Repetition to drive a point home:** *"Make it a 2, same family of curves. Make it a 3, same family of curves."* *"And let me say one more time…"*
- **Emphatic deixis at the climax:** *"This, this right here is what the central limit theorem is all about."*
- **Small historical anecdote** to lighten a dense stretch (Shannon and von Neumann naming entropy).
- **Hedges and fillers that keep it conversational:** "kind of", "basically", "sort of", "well", "I mean", "turns out".
- **Signposting phrases:** "Now…", "So…", "Again,…", "Remember,…", "By the way,…", "Back to our expression,…", "Here, it's worth taking a moment to…".

---

## 6. Quick checklist for a new script

- [ ] Opens with "This is a ___." on one concrete object
- [ ] States scope, prerequisites (ideally none), and what's deferred to the next video
- [ ] Gives a toy model with its simplifications stated out loud
- [ ] Puts the core claim in one plain sentence before any formula
- [ ] Poses a concrete question early and answers it with numbers near the end
- [ ] Introduces each formula concept first, then name, then symbol, built piece by piece and read back in English
- [ ] Moves from one instance to many and from 1-D to N-D, simulation before theory
- [ ] Has at least one "pause and think" prompt and one recap that stacks the layers
- [ ] Has an honest caveat or hope-versus-reality twist, ideally tied back to the cold open
- [ ] Runs ~190 wpm overall, with a 2–5 s silent beat after every new visual or key result
- [ ] Ends with a question to ponder, a next-video tease, and thanks
