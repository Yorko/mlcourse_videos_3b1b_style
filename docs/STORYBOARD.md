# Decision Trees — Manim Storyboard

Built from `docs/narration_decision_trees.md` (draft 2). Uses Manim Community 0.21 and `manim-voiceover`.
One table row = one narration sentence = one `with self.voiceover(text=...) as tracker:` block.
Row IDs (`3.7`) are scene.sentence, and are meant to be used as code comments.

⚠️ marks visuals that are hard to implement. Each one is explained in the **Implementation flags** list at the end.

---

## Global conventions

### Color mapping

`docs/STYLE.md` is a narration guide and defines no palette. The palette lives in `style.py`. Use these semantic names; the aliases are proposed additions to `style.py`:

| Alias (add to `style.py`) | Maps to | Hex-ish | Meaning in this video |
|---|---|---|---|
| `CLASS_0` | `PRIMARY` = `BLUE_C` | #58C4DD | blue ball, "repaid", class 0 |
| `CLASS_1` | `SECONDARY` = `YELLOW_C` | #FFFF00 | yellow ball, "defaulted", class 1 |
| `GAIN` | `POSITIVE` = `GREEN_C` | #83C167 | information gain, the winning cut |
| `IMPURITY` | `NEGATIVE` = `RED_C` | #FC6255 | entropy/error, a bad cut, "deny" |
| `HIGHLIGHT` | `ACCENT` = `TEAL_C` | #5CD0B3 | cut lines, sliders, the active path |
| `TEXT` / `TEXT_MUTED` | `WHITE` / `GREY_B` | | labels / dimmed labels |
| `GRID` | `GREY_D` | | axes, tree edges at rest |

⚠️ **Conflict to resolve in `style.py`:** its comments say `POSITIVE … class 1` and `NEGATIVE … class 0`, and `SECONDARY` is "highlights". This video uses yellow for a class, so **never use yellow to highlight**. Use `HIGHLIGHT` (teal) or a white `Indicate`/`Circumscribe` instead.

- **Dimming:** `set_opacity(0.25)` on the mobject (not a color change), so un-dimming restores it exactly.
- **Background:** `BACKGROUND` #1C1C1C (already set globally by `style.py`).

### Layout

- **Frame:** 14.22 × 8 units. Safe area x ∈ [−6.6, 6.6], y ∈ [−3.5, 3.5].
- **Title zone:** `TITLE_POSITION` (y = 3.2).
- **Caption zone:** y = −3.3, `CAPTION_SIZE`.
- **Split screen:** LEFT panel centered at x = −3.5, RIGHT panel at x = +3.5, each ~6.5 wide.
- **Formula zone:** top center (y ≈ 2.4) unless noted. Formulas use `MathTex` (LaTeX is installed); labels use `Text(font=FONT)`.
- **Sizes:** body `BODY_SIZE`, small labels `CAPTION_SIZE`.

### Timing

- Each row's `run_time` comes from `tracker.duration`. Animation timings below are approximate fractions of the sentence.
- `self.wait(...)` holds (2–3 s) go after the sentence, as in STYLE.md's "silence after reveals".
- ⚠️ **Bookmarks aren't available.** `voice.py` sets `transcription_model=None`, so `<bookmark>` / `wait_until_bookmark` won't work. Any mid-sentence sync below is written as "split this row into two voiceover blocks" instead.

### Reusable components (build first, in `components/`)

| Component | Used in | Notes |
|---|---|---|
| `BallRow(positions, colors)` | 3, 4, 5, 8, 9 | 20 `Dot`s (r = 0.15) on a `NumberLine(0..19)`. `.split_at(t)` returns two groups and animates a gap opening between them |
| `EntropyCurve` | 3, 4, 6 | `Axes(0..1, 0..1)` + `plot(H)`, a `ValueTracker` p with an `always_redraw` dot, and `.mark(p, label)` |
| `TreeDiagram` ⚠️ | 1, 5, 6, 7, 10 | node = `RoundedRectangle` + `Text`, edge = `Line`. `.grow(node_id)`, `.light_path([...])`, `.leaf(color)`. Layout is computed from a nested dict |
| `GainBars(thresholds, gains)` | 4, 6 | `BarChart` or custom `Rectangle`s on a shared x-axis aligned with `BallRow` |
| `PartitionedPlane(tree_json)` ⚠️ | 7, 8 | `Axes`, 200 dots, and per-leaf `Rectangle` fills, all driven by exported sklearn thresholds |
| `CelebrityGrid(n=64)` ⚠️ | 2, 4 | 8 × 8 grid of person icons |
| `Jar(n_blue, n_yellow)` | 3, 6 | U-shaped `VMobject` with balls packed inside, and `.set_p(p)` to recolor |

### Data files (Phase 3, never hard-code)

| File | Contents |
|---|---|
| `data/balls.json` | positions and colors, plus IG for every threshold ⚠️ (open question: is x ≤ 12 the argmax?) |
| `data/age.json` | the 11 clients, switch points, IG per switch point |
| `data/tree2d.json` | sklearn tree (seed 17, entropy, depth 3), leaf rectangles, plus unlimited-depth leaves |
| `data/accuracy.json` | train and CV accuracy vs. depth |
| `data/regression.json` | the 150 points, plus step-function fits at depths 1, 2, 3, 5 |
| `data/loan_tree.json` | the cold-open tree, plus its "regrown" variant ⚠️ (structure not yet defined) |

### Image assets

| File | Contents |
|---|---|
| `media/images/s01a_intro/yury.jpg` | 600 × 600 portrait on a white background (source) |
| `media/images/s01a_intro/ods_stickers.jpg` | 1320 × 300 banner: mascot with an "ML" laptop in the center, hexagon stickers on each side (source) |
| `media/images/s01a_intro/yury_circle.png` | **to generate:** circular crop of `yury.jpg` with a transparent background |
| `media/images/s01a_intro/ods_left.png`, `ods_mascot.png`, `ods_right.png` | **to generate:** the banner cut into three pieces, so the mascot and the two sticker clusters can animate separately |

---

## Scene 1 — Cold open (`s01_cold_open.py`, `VoiceoverScene`)

**Persistent:**
- `card`: a `RoundedRectangle` 2.6 × 3.2 with 4 `Text` rows (Age, Home-ownership, Income, Education), placed LEFT at (−4.5, 0).
- `loan_tree`: a `TreeDiagram`, RIGHT, root at (2.5, 2.4), depth 3. Edges in `GRID`. The deny leaf is `IMPURITY` and the approve leaves are `HIGHLIGHT`.

⚠️ The tree's exact structure isn't in the article. Define it in `data/loan_tree.json`. The narration needs two levels: "Owns a home?" → No → "Income above 5,000?" → No → Deny.

| # | Narration | Mobjects on screen | Animation | Position / color | Stays / fades |
|---|---|---|---|---|---|
| 1.1 | "This is a loan application, and this little flowchart just denied it." | card, loan_tree | `FadeIn(card, shift=UP*0.3)` in the first ~1 s. Then `Create(loan_tree)` (LaggedStart over nodes, lag 0.15) | card at (−4.5, 0), `TEXT` on a `GRID`-stroked box. Tree on the right | both stay |
| 1.2 | "Own a home? No." | + `card_copy` (scaled 0.35) | `card_copy` = `card.copy().scale(0.35)`. Move it into the root (`Transform` toward the root), then `MoveAlongPath` down the "No" edge. The edge recolors `HIGHLIGHT` (`ShowPassingFlash` then `set_color`). A "No" label `FadeIn`s by the edge | the lit edge is `HIGHLIGHT`, stroke 6 | the lit edge stays lit |
| 1.3 | "Income above 5,000? No." | same | Same move to the level-2 node and down its "No" edge | `HIGHLIGHT` | stays |
| 1.4 | "Denied." | + "DENY" leaf | `card_copy` lands on the leaf. Leaf `Flash(color=IMPURITY)` plus `Indicate` | leaf fill `IMPURITY`, opacity 0.8 | stays |
| 1.5 | "And the path itself is the explanation." | same | Everything off the path: `animate.set_opacity(0.25)`. The path's nodes `Circumscribe(color=HIGHLIGHT)` | | off-path nodes stay dimmed |
| 1.6 | "What's remarkable is that nobody wrote these questions by hand." | same | `card` `FadeOut(shift=LEFT)`. The tree slides to center (`animate.move_to(ORIGIN)`) | tree centered | the card fades |
| 1.7 | "An algorithm studied thousands of past applicants…" | + `crowd`: ~150 tiny dots below the tree | `LaggedStart(FadeIn)` the crowd at y = −2.8, colored `CLASS_0`/`CLASS_1` at random. Then `LaggedStart` a few dots flying up into the tree (`MoveToTarget`, lag 0.02) | dots r = 0.04 | the crowd fades at the end of the row |
| 1.8 | "That's a decision tree." | tree | Un-dim the tree (`set_opacity(1)`). `Write(Text("decision tree"))` under it | label at y = −3.0, `TEXT` | label stays until 1.10 |
| 1.9 | "So out of all the questions it could ask, how does it decide which one comes first?" | tree, root "?" | Root text `ReplacementTransform`s into `Text("?", size=60)`. `Indicate` on loop ×2 (`there_and_back`) | "?" in `HIGHLIGHT` | stays |
| 1.10 | "The answer is a beautiful idea from information theory." | same | No new motion (let it breathe). The subtle "?" pulse continues | | |
| 1.11 | "And by the end you'll also see why a tree that's perfect…" | same + a small ghost tree | ⚠️(minor) A teaser: the tree briefly shatters into an overgrown version (`TransformMatchingShapes` to a precomputed deep tree), then snaps back | | the ghost fades |
| — | *(hold 2 s)* | title | `FadeOut(tree)`. `Write(title)`: "Decision trees: what should you ask first?" | `TITLE_POSITION`, `TITLE_SIZE` | all fade at the end of the scene |

---

## Scene 1a — Course intro (`s01a_intro.py`, `VoiceoverScene`)

This plays right after the cold open's title card, so the hook comes first and the intro follows it.

The narration is new and isn't in draft 2 of `docs/narration_decision_trees.md`. It's the user's wording, split into two sentences.

**Asset prep (one-off script, `scripts/prep_s01a_assets.py`, Pillow; Manim already depends on it):**
- `yury_circle.png`: crop `yury.jpg` to a circle (alpha mask from `ImageDraw.ellipse`) centered slightly above the image center, so the face sits in the middle. Manim CE can't mask an `ImageMobject` to a circle, so this has to be baked into the PNG.
- Banner pieces: crop `ods_stickers.jpg` at x = 0–525, 525–795 and 795–1320 px. Check the cut lines visually, so that no hexagon or the mascot's laptop gets sliced.
- The banner has a white background. Key it out (white → alpha) or put it on a light rounded "sticker sheet" panel. Keying is cleaner on the dark background but can eat white sticker interiors ⚠️ (see flag 17).

**Persistent:** `banner` = `Group(left, mascot, right)`. These are `ImageMobject`s, so use `Group`, not `VGroup`.

| # | Narration | Mobjects on screen | Animation | Position / color | Stays / fades |
|---|---|---|---|---|---|
| 1a.1 | "This is lecture 3 of the machine learning course mlcourse.ai." | mascot, left/right sticker clusters, title, lecture line | `FadeIn(mascot, scale=0.8)` (0.8 s). Then `FadeIn(left, shift=RIGHT*0.6)` and `FadeIn(right, shift=LEFT*0.6)` together (0.8 s), so the stickers fan out from the mascot. `Write(Text("mlcourse.ai"))`, then `FadeIn(lecture_line, shift=UP*0.2)` with "Lecture 3 · Decision trees" | banner full width (12.5 units, height ≈ 2.85), centered at (0, 1.0). Title at (0, −1.3), `TITLE_SIZE`, bold, `TEXT`. Lecture line at (0, −2.1), `BODY_SIZE`, `TEXT_MUTED`, with "3" in `HIGHLIGHT` (`t2c`) | all stay into 1a.2 |
| 1a.2 | "I'm Yury, and let's dive into decision trees." | + portrait, name, small tree | **First half ("I'm Yury"):** the banner and title `animate.scale(0.5).move_to(UP*2.9)` together. `FadeIn(portrait, scale=0.9)`, with a `Circle` ring `Create`d around it. The name "Yury Kashnitsky" `Write`s to the right of the portrait. **Second half ("decision trees"):** "Decision trees" in the lecture line `Indicate(color=HIGHLIGHT)`, then a small dot-only `TreeDiagram(labels=False)` grows with `create_animation()` on the right. Split into 2 voiceover blocks, or time with fractions of `tracker.duration` | portrait radius 1.3 at (−3.4, −0.4), ring `HIGHLIGHT` stroke 4. Name at (−1.6, −0.4), left-aligned, `BODY_SIZE`, `TEXT`. Lecture line moves under the name (−1.6, −1.0), `CAPTION_SIZE`. Tree icon at (3.6, −0.5), height 2.2, leaves in `CLASS_0`/`CLASS_1` | hold 0.5 s, then `FadeOut` everything (0.5 s), so scene 2 opens on an empty frame |

**Notes:**
- Run time is about 7–9 s at your voice's pace. It comes after the hook, so it doesn't delay it, but keep it short anyway so Twenty Questions starts promptly.
- Scene 1 ends by fading out its title card ("Decision trees / what should you ask first?"), and this scene starts on an empty frame.
- `ImageMobject` can't use `Create`/`Write`. Use `FadeIn`, `.animate.scale/move_to`, or `FadeTransform`.
- Leave the name label as "Yury Kashnitsky", or use just "Yury" to match the narration exactly.

---

## Scene 2 — Twenty Questions (`s02_twenty_questions.py`)

**Persistent:**
- `grid`: a `CelebrityGrid(64)` (8 × 8, icon height 0.45, spacing 0.6), LEFT-center at (−2, −0.3), colored `TEXT_MUTED`.
- `counter`: `Text("questions: 0")`, top-right at (5, 3).
- `bar`: a `Rectangle` + `DecimalNumber` "left", RIGHT at (4.5, 0).

| # | Narration | Mobjects on screen | Animation | Position / color | Stays / fades |
|---|---|---|---|---|---|
| 2.1 | "Start with a game you've probably played: Twenty Questions." | grid | `LaggedStart(*[FadeIn(i, scale=0.8)…], lag 0.02)`. Title "Twenty Questions" `Write` | grid `TEXT_MUTED`, title `TITLE_POSITION` | the title fades at 2.3 |
| 2.2 | "I'm thinking of a celebrity, and you can only ask yes-or-no questions." | grid | One random icon gets a hidden `HIGHLIGHT` glow (opacity 0.15) as the secret pick | | the glow stays (subtle) |
| 2.3 | "What should you ask first?" | grid | `Text("?")` appears above the grid | `HIGHLIGHT` | fades at 2.4 |
| 2.4 | "You could go for the jackpot: 'Is it Angelina Jolie?'" | + question text | `Write(Text("Is it Angelina Jolie?"))` at the top. One icon `Indicate` + `set_color(HIGHLIGHT)` | question at y = 3.0 | stays until 2.8 |
| 2.5 | "If the answer is yes, wonderful." | same | That one icon `Flash` | | |
| 2.6 | "But almost always the answer is no." | + "No" | `FadeIn(Text("No"), shift=DOWN)` beside the question, in `IMPURITY` | | stays |
| 2.7 | "And when it's no, you've ruled out exactly one person." | + bar "63 left" | That icon `FadeOut(scale=0.5)`. The bar grows to 63/64 height. The counter goes to 1 | bar `TEXT_MUTED` | the bar stays |
| 2.8 | "You've learned almost nothing." | same | The bar `Wiggle`s (small) | | the question and "No" fade at the end |
| 2.9 | "Now compare that with 'Is the celebrity a woman?'" | grid (restored to 64), new question | Restore the faded icon (`FadeIn`). Reset the counter to 0. `Write` the new question | | |
| 2.10 | "Whatever the answer, half the possibilities disappear." | | The grid splits: the left 4 columns `animate.shift(LEFT*0.3)`, the right 4 `shift(RIGHT*0.3)`. Then the right half `set_opacity(0.15)`. The bar `animate` to 32. Counter 1 | | the faded half stays ghosted, then is removed at 2.11 |
| 2.11 | "Keep asking questions like that, and 64 candidates come down to one in just six questions." | grid, counter, bar | A `Succession` of 5 halvings (32 → 16 → 8 → 4 → 2 → 1), each ~0.6 s: the losing half fades and the survivors re-center (`animate.arrange_in_grid`). The counter ticks 2…6. The bar shrinks | the last icon `HIGHLIGHT` | the final icon stays |
| 2.12 | "Twenty of them could pin down one person out of about a million, two to the twentieth." | + `MathTex("2^{20} \\approx 1{,}000{,}000")` | `Write` the formula. The counter morphs to "20" | formula RIGHT at (4, −1.5) | fades at 2.14 |
| 2.13 | "What made the second question good wasn't cleverness." | grid reset (64) | `FadeTransform` the single icon back to the full grid | | |
| 2.14 | "You couldn't predict the answer, so either answer cut away a lot." | + two mini bars (63 vs 32) | `GrowFromEdge` two bars side by side, labeled "Jolie?" and "woman?" | bars RIGHT. "woman?" bar `GAIN`, "Jolie?" bar `TEXT_MUTED` | bars fade at 2.16 |
| 2.15 | "That's what information means here: reduced uncertainty." | + key phrase | `Write(Text("information = reduced uncertainty"))` | y = −3.0, `TEXT` with "information" in `GAIN` (`t2c`) | **stays** into 2.16; hold 2 s |
| 2.16 | "But for a computer to choose questions, 'uncertainty' has to become a number." | | Grid → `TEXT_MUTED` at 0.3 opacity. The word "uncertainty" `Indicate` | | |
| 2.17 | "So how do you measure it?" | | `ReplacementTransform` the key phrase into `Text("uncertainty = ?")`. Then `FadeOut` all | | the grid scales to 0.25 and parks in the top-left corner (`grid_icon`) for reuse in 3.10 |

---

## Scene 3 — Entropy (`s03_entropy.py`)

**Persistent:** `balls` = a `BallRow` from `data/balls.json`, centered at y = 1.8, width 11. `grid_icon` is top-left (carried over from scene 2).

| # | Narration | Mobjects on screen | Animation | Position / color | Stays / fades |
|---|---|---|---|---|---|
| 3.1 | "Let's switch to a simpler world." | (empty, plus grid_icon) | `FadeOut(grid_icon)` | | |
| 3.2 | "Here are twenty balls on a line, nine blue and eleven yellow." | balls, number line | `Create(number_line)`, then `LaggedStart(GrowFromCenter(dot)…)`. Counters "9" and "11" `FadeIn` | dots `CLASS_0`/`CLASS_1`, line `GRID`. Tick labels 0…19 `CAPTION_SIZE` | the counters fade at 3.4 |
| 3.3 | "Blues tend to sit on the left and yellows on the right, so a ball's position is a clue to its color." | same | Two `Brace`s under the left (bluer) and right (yellower) halves with soft labels "mostly blue" / "mostly yellow" | braces `TEXT_MUTED` | braces fade at the end |
| 3.4 | "Eventually we'll build a tree that predicts color from position." | + ghost tree icon | A small `TreeDiagram` silhouette `FadeIn` at the top-right, opacity 0.3 | (5.5, 3) | stays as a faint "goal" icon until scene 5 |
| 3.5 | "But first, before asking anything, how uncertain are we?" | | `Text("uncertainty?")` under the balls | `HIGHLIGHT` | fades at 3.6 |
| 3.6 | "If I pull out a ball at random, it's blue with probability 9 out of 20…" | + one ball lifted, + fractions | ⚠️(minor) "A hand" is cut. Instead, one random ball `animate.shift(UP*1.0)` with an arc path, then returns. `MathTex("p_{blue}=9/20")` and `MathTex("p_{yellow}=11/20")` `Write` | fractions colored by class, center y = 0.3 | fractions **stay** (they're reused in 3.12) |
| 3.7 | "That's close to a coin flip." | + coin icon | A small `Circle` coin `Rotate` about the Y axis (`Rotating`, 1 s) | coin `TEXT_MUTED` | fades |
| 3.8 | "You'd have a hard time betting either way." | | No new motion | | |
| 3.9 | "Compare a few jars." | balls shrink up | `balls` `animate.scale(0.6).to_edge(UP)`. Three `Jar`s `FadeIn` (lagged) | jars at x = −4, 0, 4, y = −1.2 | jars stay to 3.13 |
| 3.10 | "If every ball is yellow, there's no uncertainty at all." | jar 1 (20 Y) | Jar 1 `Indicate`. Label "none" | label `TEXT_MUTED` | |
| 3.11 | "One blue among nineteen yellow, still very little." | jar 2 (19 Y, 1 B) | Jar 2 `Indicate`. Label "a little" | | |
| 3.12 | "Ten and ten, as uncertain as it gets." | jar 3 (10/10) | Jar 3 `Indicate`. Label "max" | label `IMPURITY` | |
| 3.13 | "So whatever our measure is, it should be zero for a pure jar and largest for an even mix." | + labels "0" and "max" | Labels `ReplacementTransform` to "0", "small" and "max". Then the jars `FadeOut` | | the jars fade |
| 3.14 | "Twenty Questions gives us a unit." | grid_icon returns | `FadeIn(grid_icon)` top-left with `Text("1 halving question = 1 bit")` | `CAPTION_SIZE` | stays to 3.18 |
| 3.15 | "Call one perfectly halving yes-or-no question one bit." | | The grid icon does one halving (reuse the 2.10 animation, scaled) | | |
| 3.16 | "Now flip it around." | | `Text("probability → bits")` with a `CurvedArrow` | center | fades |
| 3.17 | "If something had a one-in-two chance and you learn that it happened, you've learned as much as one halving question: one bit." | + a row of three pie icons | `Sector` pies: ½ → "1 bit" `FadeIn` | pies at y = 0, x = −3, 0, 3. Filled sector `HIGHLIGHT` | pies stay to 3.19 |
| 3.18 | "A one-in-four outcome is like two halvings, so two bits." | pie ¼ | `FadeIn` pie 2 + "2 bits" | | |
| 3.19 | "One-in-eight, three bits." | pie ⅛ | `FadeIn` pie 3 + "3 bits" | | pies `FadeOut` at the end |
| 3.20 | "So the number of bits is log base two of one over the probability." | formula chain | `MathTex(r"\left(\tfrac12\right)^{\text{bits}} = p")`, then `TransformMatchingTex` → `2^{\text{bits}} = \tfrac1p`, then → `\text{bits} = \log_2 \tfrac1p`. Split into 2 voiceover blocks if it runs long | formula zone (0, 1.0), `TEXT`, with `\log_2` in `HIGHLIGHT` | the final form stays |
| 3.21 | "Log base two simply counts how many halvings it takes to get there." | + halving arrows | Under `\log_2`, three small arrows "÷2 ÷2 ÷2" `LaggedStart(GrowArrow)` | `HIGHLIGHT` | arrows fade |
| 3.22 | "Rare outcomes carry lots of bits, and common ones carry very few." | | A tiny bar pair: "rare → many bits", "common → few" | | fades |
| 3.23 | "Blue is the rarer color here, so drawing a blue ball tells you a bit more: about 1.15 bits, versus 0.86 for yellow." | balls (restored center), tags | `balls` `animate` back to y = 1.8. `MathTex(r"\log_2\tfrac{20}{9}\approx1.15")` above one blue ball and `\log_2\tfrac{20}{11}\approx0.86` above a yellow one, joined by `Line`s | tags in `CLASS_0` / `CLASS_1` | tags stay to 3.25 |
| 3.24 | "Now average those over the outcomes, weighting each by how often it happens." | + weighted sum | `MathTex(r"\tfrac{9}{20}\cdot1.15 + \tfrac{11}{20}\cdot0.86")`, with the tags' numbers `TransformFromCopy` into the slots | formula zone (0, 0) | |
| 3.25 | "That average has a name: entropy." | + general form | `TransformMatchingTex` → `\sum_i p_i \log_2 \tfrac{1}{p_i}`. `Write(Text("entropy"))` beside it | "entropy" in `IMPURITY` | stays |
| 3.26 | "In textbooks you'll see it with a minus sign out front, because log of one over p is the same as minus log p." | | `TransformMatchingTex` → `S = -\sum_i p_i \log_2 p_i`. Isolate the minus sign with `{{-}}` so it visibly travels from inside the log to the front ⚠️(minor) | | stays (moves to the top-right at 3.29) |
| 3.27 | "For our twenty balls, that comes out to about 0.99 bits, almost exactly one." | + plugged-in form | `MathTex(r"S_0 = -\tfrac{9}{20}\log_2\tfrac{9}{20} - \tfrac{11}{20}\log_2\tfrac{11}{20} \approx 0.99")` `Write`. The fractions from 3.6 `TransformFromCopy` in | below the general form | `S₀ ≈ 0.99` stays (parks top-right) |
| 3.28 | "So it really is nearly a perfect coin flip." | | `Circumscribe(S0_value)` | | |
| 3.29 | "And if we slide that proportion from all blue to all yellow, entropy traces out this arch." | + `EntropyCurve`, + a jar | Clear the formulas (keep `S₀` at the top-right). `Create(axes)`. A `ValueTracker` p goes 0 → 1 over ~4 s. The curve is drawn by `always_redraw` up to p (or `Create(curve)` synced with the tracker). The jar above it `set_p(p)` via an updater ⚠️ | axes centered at (0, −0.8), size 6 × 3.5. Curve `IMPURITY`, dot `TEXT`. Jar at (4.5, 1.5) | the curve **stays** into scene 4 |
| 3.30 | "It's zero at both ends, where the jar is pure, and peaks at exactly one bit at fifty-fifty." | | The tracker goes to 0, then 1, then 0.5, with `Flash` at each end and at the peak. A dashed `DashedLine` at y = 1 | | |
| — | *(hold 2 s)* | | The dot moves to p = 11/20 and gets marked with the label "our balls" | mark `TEXT` | the curve and mark shrink to the bottom-right corner (scale 0.45) |

---

## Scene 4 — Information gain (`s04_information_gain.py`)

**Persistent:**
- `balls` (y = 1.8).
- `mini_curve`: the entropy arch, bottom-right at (5, −2.4), scale 0.45.
- `cut`: a `DashedLine` (vertical) in `HIGHLIGHT`, driven by a `ValueTracker` t.

| # | Narration | Mobjects on screen | Animation | Position / color | Stays / fades |
|---|---|---|---|---|---|
| 4.1 | "Now we can score a question." | balls, mini_curve | `Create(cut)` at x = 0 | | |
| 4.2 | "On this line, a question is a cut point, a threshold: 'Is the position at most twelve?'" | + cut, + label | t animates 0 → 12.5 (`rate_func=smooth`). Label `MathTex("x \\le 12\\,?")` follows the cut via an updater. Word "threshold" `FadeIn` | label above the cut, `HIGHLIGHT` | the cut stays |
| 4.3 | "Does asking it lower our uncertainty?" | | No new motion. The label `Indicate`s | | |
| 4.4 | "On the left we get thirteen balls, eight blue and five yellow." | | `balls.split_at(12.5)`: the left group shifts LEFT 0.6. Brace + "13: 8 blue, 5 yellow" | brace label `CAPTION_SIZE` | stays |
| 4.5 | "On the right, seven balls: one blue and six yellow." | | The right group shifts RIGHT 0.6. Brace + "7: 1 blue, 6 yellow" | | stays |
| 4.6 | "The left group is still pretty mixed, at about 0.96 bits." | + `S₁ ≈ 0.96` | `Write(MathTex("S_1\\approx0.96"))` under the left brace. A dot `TransformFromCopy` onto `mini_curve` at p = 5/13 | value `IMPURITY` | stays |
| 4.7 | "The right group is much more predictable, at about 0.59." | + `S₂ ≈ 0.59` | Same for the right, p = 6/7 | | stays |
| 4.8 | "Both are lower than the 0.99 we started with." | + `S₀ ≈ 0.99` | `S₀` (from the top-right) `Indicate`. Two small down-arrows from 0.99 to each value | arrows `GAIN` | arrows fade |
| 4.9 | "So how do we combine them into one score?" | | `MathTex("? ")` between the two values | | |
| 4.10 | "You might just average them." | + naive average | `MathTex(r"\tfrac{0.96+0.59}{2}")` appears with a "?" | `TEXT_MUTED` | |
| 4.11 | "But should a group of seven count as much as a group of thirteen?" | | The braces `Indicate`, and "7" vs "13" scale up 1.3× `there_and_back` | | the naive average stays for 4.12 |
| 4.12 | "Imagine a cut that peels off one single ball." | balls re-merged, new cut at 0.5 | `balls` re-merge (reverse split). t → 0.5. `split_at(0.5)` peels off ball 0 | the lone ball `Circumscribe` | |
| 4.13 | "That tiny group is perfectly pure, so a plain average would call it a great question…" | + "S = 0", "S ≈ 0.98", plain avg ≈ 0.49 | Values `Write`. The plain average gets a ✓ mark that then turns into ✗ | ✗ `IMPURITY` | |
| 4.14 | "So we weight each group by its share of the balls." | + weights | Under each group: `MathTex("1/20")` and `MathTex("19/20")`. Group widths `Indicate` | | everything fades except balls and `S₀`. Restore the x ≤ 12 split (`split_at(12.5)`) |
| 4.15 | "Entropy before, minus each group's entropy weighted by its share: that's the information gain." | + IG formula | `MathTex("S_0", "-", r"\tfrac{13}{20}", "S_1", "-", r"\tfrac{7}{20}", "S_2")` assembles, with `TransformFromCopy` from the existing S₀, S₁, S₂ and the brace counts. Then `Write(Text("information gain"))` | formula zone (0, −0.6). The weights tinted to match their group braces. "information gain" in `GAIN` | stays |
| 4.16 | "Here it's about 0.16 bits, out of the 0.99 we started with." | + "≈ 0.16" | `Write(MathTex(r"\approx 0.16"))` in `GAIN`. A small horizontal bar: 0.16 filled out of a 0.99 track | bar under the formula | the bar fades |
| 4.17 | "That's a modest step, and it's the same recipe for any number of groups." | general form | `TransformMatchingTex` → `IG(Q) = S_0 - \sum_i \tfrac{N_i}{N} S_i` (not read aloud) | | the formula shrinks to top-left (scale 0.6) and stays |
| 4.18 | "Of course, twelve was just one candidate." | balls re-merged | Re-merge. The cut `FadeOut`. `LaggedStart` of 19 faint ticks at every gap | ticks `HIGHLIGHT`, opacity 0.4 | ticks stay |
| 4.19 | "Before I show you, pause and guess: which cut on this line do you think lowers the uncertainty the most?" | | The ticks pulse (`Indicate` lagged), then `self.wait(3)` | | |
| 4.20 | "Now 'which question should come first' has a mechanical answer." | + `GainBars` | Axes appear under the balls, x-aligned to the gaps | bars region y ∈ [−3, 0] | stays |
| 4.21 | "Try every threshold, compute the gain of each, and pick the tallest bar." | bars | A `LaggedStart(GrowFromEdge(bar, DOWN), lag 0.12)` while the cut sweeps across synchronously (the tracker t matches the bar index). Then the tallest bar → `GAIN` and `Circumscribe`. ⚠️ The data decides which bar is tallest | bars `TEXT_MUTED`, winner `GAIN` | stays |
| 4.22 | "It's Twenty Questions again, only now the computer keeps the books." | + ghost grid | `FadeIn(grid_icon)` top-right at opacity 0.4 | | |
| 4.23 | "A cut that clips off one ball is the 'Angelina Jolie' question, with a tiny bar." | | The edge bars (gap 0–1 or 18–19) `Indicate` in `IMPURITY`. The grid icon highlights one silhouette | | |
| 4.24 | "The winner leaves both sides more predictable." | | The winning bar `Indicate`. The balls split at the winner | | everything except the balls fades at the end of the scene |

---

## Scene 5 — Growing the tree (`s05_growing_tree.py`)

**Layout:**
- **LEFT:** `balls` scaled to 6 wide at (−3.5, 1.5).
- **RIGHT:** `ball_tree` (`TreeDiagram`), root at (3.5, 2.6), level spacing 1.1, horizontal spread halving per level.

⚠️ This assumes the article's tree (root x ≤ 12, right child x ≤ 18, 3 more cuts on the left). Rebuild from `data/balls.json` if the real argmax differs.

| # | Narration | Mobjects on screen | Animation | Position / color | Stays / fades |
|---|---|---|---|---|---|
| 5.1 | "One question doesn't make a tree, though." | balls (split at the root cut), root node | `balls` `animate` to the left panel. `GrowFromCenter(root)` with label "x ≤ 12" | root stroke `HIGHLIGHT` | stays |
| 5.2 | "What do we do with the two groups we just made?" | + two "?" child stubs | `Create` two edges ending in "?" placeholders | "?" `TEXT_MUTED` | replaced in 5.3/5.5 |
| 5.3 | "We do exactly the same thing again, inside each group." | | The right group gets a teal `SurroundingRectangle`, and the right "?" `Indicate`s | | |
| 5.4 | "The right group needs just one more question, 'is the position at most eighteen?', and both pieces come out a single color." | + node "x ≤ 18", 2 leaves | **Sync:** within one `AnimationGroup`, the cut line `Create` at 18.5 on the left and the "?" `ReplacementTransform`s into the node "x ≤ 18" on the right. Then the right group splits. Two leaves `GrowFromCenter` with fills `CLASS_1` and `CLASS_0` | leaves = small `Circle`s filled by class | stay |
| 5.5 | "The left group is messier and takes three more cuts." | + 3 nodes | `Succession` of 3 synced cut+node pairs (~1 s each), same pattern as 5.4 | | stay |
| 5.6 | "A group where every ball is the same color has entropy zero, so there's nothing left to ask, and we stop." | + "S = 0" tags | Under each pure group, a small `MathTex("S=0")` `FadeIn` (lagged) | `GAIN` | the tags fade at 5.8 |
| 5.7 | "Those end points are called leaves." | + label "leaves" | A `Brace` under the leaf row + `Text("leaves")` | `TEXT` | stays to 5.9 |
| 5.8 | "Each one predicts the color of the balls that land in it." | | One ball `TransformFromCopy` → down the tree path to its leaf (reuse 1.2's `light_path`) | | |
| 5.9 | "That's the core idea behind the classic tree algorithms." | + counter, + tag | `Text("5 questions")` `FadeIn`. Small tag "ID3 · C4.5 · CART" | counter under the tree. Tag `CAPTION_SIZE`, `TEXT_MUTED`, bottom-right | the tag fades at 5.11 |
| 5.10 | "At every node, grab the question with the biggest gain right now, split, and then repeat the whole process inside each piece." | + pseudocode loop | A 3-line `Text` loop ("best split → split → repeat in each part") with a `CurvedArrow` cycling | bottom-left (−3.5, −2.4) | fades at 5.12 |
| 5.11 | "Is grabbing the best question right now guaranteed to give the best tree overall?" | | `Text("best now = best overall?")` | center-bottom | |
| 5.12 | "No. Finding the truly best tree would mean searching through an astronomical number of possible trees…" | + tree swarm | ⚠️(minor) The question gets a ✗. ~40 tiny random tree silhouettes `LaggedStart(FadeIn)` across the background (opacity 0.15), then `FadeOut` | ✗ `IMPURITY` | the swarm fades |
| 5.13 | "It works remarkably well." | | The real tree `Indicate` | | |
| 5.14 | "So now our tree is perfect: every training ball lands in a leaf of its own color." | + "perfect" | Tree `set_stroke(width=…)` glow (copy, blur via a large-stroke low-opacity duplicate). `Write(Text("perfect", slant=ITALIC))` beside it | "perfect" `GAIN` | **stays** to 5.16 |
| 5.15 | "Hold on to that word, perfect." | | "perfect" `Circumscribe` | | |
| 5.16 | "It's going to come back to bite us." | | "perfect" `animate.set_color(IMPURITY)` for 0.3 s and back (foreshadow) | | save `ball_tree` and "perfect" state (JSON) for scene 8. Everything fades |

---

## Scene 6 — Back to the bank: numeric features + Gini aside (`s06_numeric_gini.py`)

**Persistent:** the `age_table` (`Table` 11 × 2), then `age_line` (a `NumberLine` 15..66) at y = 1.0 with 11 dots.

| # | Narration | Mobjects on screen | Animation | Position / color | Stays / fades |
|---|---|---|---|---|---|
| 6.1 | "Back to the bank." | small loan_tree icon | The loan tree icon `FadeIn` top-left (scale 0.3) | | stays as a corner icon |
| 6.2 | "A real feature, a measurement like age, can take dozens of values." | + table | `Create(age_table)` (lagged rows). The Age column header `Indicate` | table LEFT (−4, 0), `CAPTION_SIZE`. The default column cells colored by class | |
| 6.3 | "Do we really have to try every possible cut?" | + age_line | ⚠️(medium) Each table row turns into a dot: `ReplacementTransform(row, dot)` to its age position (11 animations, lagged). The table fades | dots `CLASS_0` (repaid) / `CLASS_1` (defaulted) | the line stays |
| 6.4 | "Sort the clients by age and look at where the color switches." | + ~40 faint candidate ticks | `LaggedStart` ticks between every distinct neighboring pair, opacity 0.3 | ticks `TEXT_MUTED` | fade at 6.5 |
| 6.5 | "Here it switches only five times, and those five midpoints are exactly the cuts the tree ends up using." | 5 glowing ticks | The non-switch ticks `FadeOut`. Ticks at 19, 22.5, 30, 32, 43.5 → `HIGHLIGHT` + labels | labels `CAPTION_SIZE` above | stay |
| 6.6 | "So why would you never pick, say, 17.5?" | + red cut at 17.5 | `Create(DashedLine)` at 17.5 in `IMPURITY` | | |
| 6.7 | "Both seventeen and eighteen defaulted." | | Dots 17 and 18 `Indicate` (yellow) | | |
| 6.8 | "Slide the cut up to 19 and the left side stays pure, but the right side loses a defaulter and gets cleaner, so the gain roughly doubles." | + small gain bar | The cut `animate` 17.5 → 19 and turns `HIGHLIGHT`. Dot 18 crosses to the left side (brace update). A mini bar grows from 0.085 to 0.18 height (no numbers spoken; values in small text) | bar `GAIN` | the bar fades |
| 6.9 | "That's a general fact: the best cut always sits at one of these switch points." | + 5 gain bars | `GainBars` under the line at the 5 switch points, `GrowFromEdge` | bars `TEXT_MUTED` | stay |
| 6.10 | "Here the winner is 43.5, which becomes the root of the tree." | | The 43.5 bar → `GAIN`, `Circumscribe`, label "entropy IG ≈ 0.40". The corner loan-tree icon's root flashes | | |
| 6.11 | "With more features, you do the same trick for each one." | + salary line | A second `NumberLine` (salary) `FadeIn` under it, with its switch ticks flashing | y = −1.0 | both lines fade at 6.12 |
| 6.12 | "One small confession: this particular tree was actually built with a cousin of entropy called Gini impurity." | aside panel | A `RoundedRectangle` panel `FadeIn`. `EntropyCurve` inside, entropy plot drawn | panel center 8 × 5.5. Entropy curve `IMPURITY` | |
| 6.13 | "Draw two clients at random." | + two dots | Two dots pop out of a small client cluster (`TransformFromCopy`) | | |
| 6.14 | "How likely is it that one repaid and one defaulted?" | + Gini formula | One blue and one yellow dot side by side. `MathTex("G = 2p(1-p)")` `Write` | Gini curve color `TEXT` | |
| 6.15 | "Gini tops out at one half and entropy at one, so double it to compare, and the two curves closely track each other." | + Gini curve, + doubled | `Create(gini_curve)`, then `Transform(gini_curve, doubled_gini_curve)` (y-scaled ×2 via a new plot) | doubled curve `TEXT`, dashed. Text "misclassification error, rarely used" in `TEXT_MUTED` at panel bottom | |
| 6.16 | "That's why they usually pick the same splits." | | Both curves `Indicate` together | | all fade at the end of the scene |

---

## Scene 7 — Trees in two dimensions (`s07_trees_2d.py`, the signature shot)

**Layout:**
- **LEFT:** `plane` = a `PartitionedPlane(data/tree2d.json)`. `Axes` x₁ ∈ [−3, 5], x₂ ∈ [−3, 5], size 6.5 × 6.5, centered at (−3.3, −0.2).
- **RIGHT:** `tree2d` (`TreeDiagram`), root at (3.6, 2.8), depth 3, leaf row at y = −1.0.

| # | Narration | Mobjects on screen | Animation | Position / color | Stays / fades |
|---|---|---|---|---|---|
| 7.1 | "Here's where trees get their signature look." | axes | `Create(axes)` with labels x₁, x₂ | `GRID` | stays |
| 7.2 | "Now each example has two measurements, which machine learning calls features, and belongs to one of two categories, or classes." | + 200 dots | Blue cloud, then yellow cloud: `LaggedStart(FadeIn(dot, scale=0.5)…, lag 0.005)`. Labels "feature 1", "feature 2" on the axes, and a class legend | dots r = 0.05, `CLASS_0` / `CLASS_1` | stay |
| 7.3 | "There are two hundred points in two overlapping clouds." | | The overlap region gets a soft `Circle` highlight | `HIGHLIGHT`, opacity 0.2 | fades |
| 7.4 | "What does a question look like here?" | + "?" | | | |
| 7.5 | "Each question still looks at just one feature and compares it to a number." | + question text | `Write(MathTex("x_2 \\le 1.211\\,?"))` | top of the right panel | moves into the root node at 7.8 |
| 7.6 | "In the plane, that means a straight cut, either horizontal or vertical." | + one demo horizontal line and one demo vertical line | `Create` both, then `FadeOut` | `HIGHLIGHT`, dashed | fade |
| 7.7 | "The tree tries every cut on both axes, scores each one, and keeps the winner: is x₂ at most about 1.2?" | ghost sweep + IG readout | ⚠️ **Signature.** A `ValueTracker` sweeps a vertical ghost line across x₁, then a horizontal one across x₂. A `DecimalNumber` IG readout updates from a precomputed IG(threshold) array (`data/tree2d.json`). Then the horizontal line locks at 1.211 → `GAIN` + `Flash`. Split into 2 voiceover blocks: sweep / lock | ghost lines `HIGHLIGHT` at opacity 0.4, readout top-left of the plane | the locked line stays (→ `GRID` stroke after) |
| 7.8 | "That one horizontal line already separates most of the blue from most of the yellow." | + region fills, + root node | **Sync** in one `AnimationGroup`: the two half-plane `Rectangle`s `FadeIn` (fill = majority class, opacity 0.18), and the question `ReplacementTransform`s into the root node on the right. Counts "91B / 20Y" and "9B / 80Y" `FadeIn` small | fills `CLASS_0` (below) / `CLASS_1` (above) | stay |
| 7.9 | "Then each half gets its own question, and each of those gets another." | + depth-2 and depth-3 cuts and nodes | `Succession` over the 6 internal nodes: for each one, `Create(cut_segment)` (clipped to the parent rectangle), the parent region `ReplacementTransform`s into 2 child rectangles, and the tree node `GrowFromCenter`. ~1 s each ⚠️ | cuts `GRID`, stroke 3 | stay |
| 7.10 | "Every node in the tree is a cut in the plane, and every cut lives only inside its parent's region." | | Pick one depth-2 node: the node and its cut segment `Indicate` together, and its parent rectangle gets a `SurroundingRectangle` | `HIGHLIGHT` | |
| 7.11 | "Three questions deep, we have eight leaves, which means eight rectangles." | + leaf colors | Leaves `GrowFromCenter`, colored by majority. A loop highlights leaf ↔ rectangle pairs (8 × 0.3 s), each pair `Indicate` together. ⚠️(minor) One leaf is a 3–3 tie: sklearn assigns class 0, so show it as `CLASS_0` with a "tie" tooltip, or skip it in the highlight loop | | stays |
| 7.12 | "Inside each one, the tree predicts whichever color holds the majority." | | Region fills → opacity 0.3. ⚠️ Optional: the stroke between same-color neighbors fades so they merge visually | | |
| 7.13 | "So a decision tree is really a way of carving space into boxes, always with cuts parallel to the axes." | + test point | A white `Star` test point drops onto the plane (`FadeIn(shift=DOWN)`). The tree path lights (reuse `light_path`) while the matching rectangle `Indicate`s | test point `TEXT`, path `HIGHLIGHT` | the test point fades at 7.14 |
| 7.14 | "Notice the price of that." | | The tree dims to 0.3 | | |
| 7.15 | "The natural boundary between these clouds is a diagonal line, and the best a tree can do is approximate it with a staircase." | + diagonal | `Create(DashedLine)` along x₁ + x₂ = 2. The staircase boundary (outer edge of the blue region) `Indicate` | diagonal `TEXT`, dashed | stays |
| 7.16 | "More depth means finer steps, which sounds like a fix." | | A quick preview: a depth-5 staircase `FadeTransform`s in, then back | | |
| 7.17 | "It's actually a trap." | | Hard cut: all `FadeOut` (run_time 0.3) | | everything fades |

---

## Scene 8 — Overfitting (`s08_overfitting.py`)

**Layout:**
- **LEFT:** the plane from scene 7 (rebuilt).
- **Top-right:** a `depth_slider` (`NumberLine` 1..∞ with a `Triangle` knob).

| # | Narration | Mobjects on screen | Animation | Position / color | Stays / fades |
|---|---|---|---|---|---|
| 8.1 | "If deeper trees fit the data better, why not keep splitting until every leaf is pure?" | plane at depth 3, slider | The plane `FadeIn` (same as the end of 7.12). `Create(depth_slider)` with the knob at 3 | slider `HIGHLIGHT` at (4, 2.5) | |
| 8.2 | "Watch what happens." | | The knob steps 3 → 6 → 10 → ∞. At each step the region set `FadeTransform`s to the precomputed partition ⚠️ | | |
| 8.3 | "The boundary turns jagged, carving out tiny boxes around single points that are almost certainly just noise." | max-depth plane | `Circumscribe` 2–3 tiny slivers around stray points deep in the opposite cloud. The camera zooms toward one (`MovingCameraScene` `frame.animate.scale(0.5).move_to(sliver)`) | slivers `IMPURITY` outline | zoom out at 8.4 |
| 8.4 | "It's like a bank noticing that the four clients who came in wearing green trousers all defaulted, and making that a rule." | + trousers vignette | ⚠️(minor) Needs a trousers SVG icon. 4 small icons + the rule card "green trousers → default" | icons `GAIN`-green (on purpose, as a joke). Card `IMPURITY` outline | the vignette fades |
| 8.5 | "Remember our perfect tree?" | ball_tree + "perfect" restored | `FadeIn` the saved scene-5 state on the right half (the plane shrinks to the left) | as in 5.14 | |
| 8.6 | "That's exactly the problem." | | "perfect" `Indicate` | | |
| 8.7 | "It fits every training ball, and that's precisely why it can stumble on the twenty-first." | + a new ball | ⚠️ A new ball drops onto the line (`FadeIn(shift=DOWN)`) at a position inside a narrow leaf, but its true color is the opposite. It travels the tree, lands in a wrong-color leaf → ✗. "perfect" "cracks": a zig-zag `Line` overlaid, the word splits in two halves that rotate ±8° and turn `IMPURITY` | ✗ `IMPURITY` | |
| 8.8 | "A simpler tree that gets a couple of training balls wrong could easily do better on new ones." | + a 2-level tree | A pruned tree `FadeTransform`s from the full tree. Two training balls get a small ✗ and the new ball gets a ✓ | ✓ `GAIN` | all fade |
| 8.9 | "On the training data, accuracy marches up to a hundred percent." | + accuracy axes | `Create(axes)` (depth 1..10, accuracy 0.8..1.0). Train line `Create` left to right | train line `CLASS_0`-blue, label "train". Axes centered, 9 × 4.5 | stays |
| 8.10 | "On data the tree has never seen, it peaks at about four questions deep, then slowly gets worse." (the depth word is generated from `best_depth` in `data/depth_cv.json`) | + CV line, + gap | CV line `Create`. A dot on the peak at `best_depth` (4, ≈ 0.88) with `Flash`. The gap between the lines `FadeIn` as a `Polygon` fill | CV line `TEXT`, gap `IMPURITY` at opacity 0.25 | stays |
| 8.11 | "The tree has memorized instead of learned." | | `Write(Text("memorized ≠ learned"))` | bottom caption | fades |
| 8.12 | "So how do you stop it?" | the plane returns (max depth) | `FadeTransform` the chart into the plane (left) | | the chart parks top-right (scale 0.35) |
| 8.13 | "The simplest way is to stop growing early: cap the depth, or demand a minimum number of points in every leaf." | + 2 sliders | ⚠️(medium) Replace "dials" with two `NumberLine` sliders labeled "max depth" and "min points per leaf". As each knob moves, the partition `FadeTransform`s to the precomputed one | sliders `HIGHLIGHT`, right side | |
| 8.14 | "Or grow the full tree and then prune back the branches that don't earn their keep." | + tree icon pruning | A small deep tree: 2–3 subtrees `FadeOut` with a "snip" `Flash` | | fades |
| 8.15 | "And how do you pick the right depth?" | | The depth slider `Indicate` | | |
| 8.16 | "Hide part of the data from the tree, test on that hidden part, repeat with different slices hidden, and keep the depth that does best." | + 5-slice bar | ⚠️(medium) A `Rectangle` divided into 5 slices. One slice → `TEXT_MUTED` "hidden" while the others are "train". Loop over the 5 slices (0.6 s each). Meanwhile, the parked chart's CV point at `best_depth` gets circled | slices `GRID` stroke. The hidden slice `HIGHLIGHT` | |
| 8.17 | "That's cross-validation." | | `Write(Text("cross-validation"))` | caption | all fade |

---

## Scene 9 — Regression trees (`s09_regression.py`)

**Persistent:** `Axes` x ∈ [−5, 5], y ∈ [−0.5, 2], size 11 × 4.5, centered at (0, −0.3). The 150 points from `data/regression.json`.

| # | Narration | Mobjects on screen | Animation | Position / color | Stays / fades |
|---|---|---|---|---|---|
| 9.1 | "What if the answer isn't a color at all, but a number?" | axes, points | `Create(axes)`, then `LaggedStart(FadeIn(dot))`. Optional: the true curve `f` faint | points `TEXT` r = 0.04. True curve `GRID`, dashed | stay |
| 9.2 | "A leaf can't vote on a color anymore, so it predicts the average of its points." | + mean line | `Create(Line)` at y = mean, labeled "leaf prediction = average" | line `HIGHLIGHT` | stays |
| 9.3 | "And the uncertainty we want to shrink becomes how spread out those values are around that average." | + residuals | `LaggedStart(Create)` vertical `Line`s from each point to the mean | residuals `IMPURITY`, opacity 0.5 | stay to 9.4 |
| 9.4 | "That's the variance: the average squared distance from the mean." | + formula | `Write(MathTex(r"D = \frac{1}{n}\sum_i (y_i - \bar y)^2"))`, with ȳ colored `HIGHLIGHT` and linked by an arrow to the mean line | formula zone, top-right (3.5, 2.6) | the residuals fade |
| 9.5 | "Everything else stays the same." | + mini ball tree icon | A small tree icon flashes next to the formula (same algorithm) | | fades |
| 9.6 | "Find the cut that lowers variance the most, then repeat inside each piece." | depth-1 fit | The mean line `ReplacementTransform`s into a 2-step function (depth 1) with a vertical cut `Flash` | step fn `HIGHLIGHT`, stroke 4 | |
| 9.7 | "The result is a step function, and with more depth the steps follow the curve more and more closely." | depth 2 → 3 → 5 | `ReplacementTransform` the step functions in turn (precomputed). Each is built as `VMobject.set_points_as_corners` with the same point count (pad corners to avoid an ugly morph ⚠️(minor)). A depth counter ticks | | the depth-5 fit stays |
| 9.8 | "But past the edge of the data, it just stays flat." | extended axes | ⚠️(medium) Rebuild the axes to x ∈ [−8, 8] (`Transform(axes, wider_axes)` plus repositioning the points and the fit via a coordinate map), or use a `MovingCameraScene` pan to the right. Flat extensions of the fit in `HIGHLIGHT`, dashed | | |
| 9.9 | "A tree can fill in between points it has seen, but it can't predict beyond them." | | Shaded band over [−5, 5] labeled "seen". Outside it, "flat" in `IMPURITY` | | fades |
| 9.10 | "Our balls work the same way: every ball past eighteen lands in the same leaf, so a ball at twenty-five gets exactly the same prediction as one at nineteen." | ball line returns | `FadeTransform` to the ball line extended to 0..26. A ghost ball appears at 25 and gets the same color as ball 19 (blue), with matching `Indicate` | | all fade |

---

## Scene 10 — Wrap-up (`s10_wrapup.py`)

| # | Narration | Mobjects on screen | Animation | Position / color | Stays / fades |
|---|---|---|---|---|---|
| 10.1 | "So which question comes first?" | loan_tree (as in 1.5, path lit) | `FadeIn` the saved scene-1 tree state | centered | |
| 10.2 | "The one with the biggest information gain, then the same rule again, all the way down." | | The root `Indicate` in `GAIN`, then each level in sequence (lagged) | | |
| 10.3 | "That gives you a model you can read like a flowchart." | | The lit path `Circumscribe` | | |
| 10.4 | "But here's the catch." | + 6 applicant dots | A row of applicant dots below. 3 of them swap color (`animate.set_color`) | | |
| 10.5 | "Change a handful of past applicants, and the tree can regrow completely: different questions, a different reason for the same denial." | regrown tree | ⚠️ `TransformMatchingShapes(loan_tree, loan_tree_v2)`, where v2 comes from perturbed data (`data/loan_tree.json`). The card re-runs down the new path to "deny" | new path `HIGHLIGHT` | |
| 10.6 | "The path is the explanation, but it isn't stable." | | The old path as a ghost (opacity 0.25) overlaid next to the new one | | |
| 10.7 | "The fix is wonderfully simple." | | Tree scales to 0.3 and moves to the center | | |
| 10.8 | "Grow hundreds of trees, each on a random resample of the data, and let them vote." | forest | ⚠️ ~120 tree icons (a simple 3-level `TreeDiagram` without labels, as precomputed `VGroup` copies with jitter in shape and color) `LaggedStart(FadeIn, lag 0.01)` into a grid. Then tiny "votes" (dots) fly from each tree to a tally bar. Majority → "deny" | icons `GRID` with leaves by class. Tally `CLASS_0`/`CLASS_1` | |
| 10.9 | "That's a random forest, and it's next." | + end card | `Write(Text("Random forests: next"))`. `FadeIn("mlcourse.ai · Topic 3")` | `TITLE_POSITION`. Credit `CAPTION_SIZE`, `TEXT_MUTED` | hold 3 s, then fade all |

---

## Implementation flags

Ordered by risk.

| # | Where | Visual | Why it's hard | Suggested approach |
|---|---|---|---|---|
| 1 | 7.7–7.12 | **Signature shot:** plane partition synced with tree growth | Rectangles must be clipped to the parent regions. The tree layout has to match node order, and the cut, region split and node have to appear in one `AnimationGroup` | Export the sklearn `tree_` (feature, threshold, children) to `tree2d.json` with **precomputed leaf boxes per depth**. `PartitionedPlane` reads boxes and never computes geometry. Build and test it standalone first (as the plan says) |
| 2 | 1, 5, 7, 10 | `TreeDiagram` component | Layout (spacing that halves per level), `light_path`, node replacement, saving and restoring state across scenes | A nested dict → positions via simple recursive layout. Expose `.node(id)`, `.edge(parent, child)`, `.light_path(ids)`. Pickle or JSON the spec, not the mobjects |
| 3 | 4.21, 5 | Data-dependent winning cut | x ≤ 12 may not be the argmax (open question from the critique round) | Generate `data/balls.json` first. If the argmax ≠ 12, change the 4.x narration numbers and rebuild scene 5's tree from the real greedy splits |
| 4 | 8.2, 8.13 | Partition changing with depth or `min_samples_leaf` | Leaf counts differ (8 → ~40), so `Transform` scrambles them | Use `FadeTransform` of the whole region group, or cross-fade (0.6 s). Precompute partitions for every slider stop |
| 5 | 8.7 | New ball misclassified by the "perfect" tree | Positions are integers 0–19 with pure leaves, so there's no natural misclassified spot | Define a "true" generating rule (e.g. the probability of yellow rises with x) and drop the new ball at a fractional position like 13.4 inside a 1-ball leaf, colored by that rule. **The narration should be checked against whatever you choose.** For "perfect" cracking, render it as two `Text` objects ("per" + "fect") placed flush, then rotate them apart |
| 6 | 10.5 | Tree regrows on perturbed data | Needs a real second tree with a different structure | Perturb ~3 rows of the loan dataset in the notebook and confirm that sklearn yields a different root. Export both. `TransformMatchingShapes` may look chaotic, so `FadeTransform` is safer |
| 7 | 10.8 | Forest of ~120 trees + votes | Performance (~120 × ~15 submobjects) and render time | One template tree as `VGroup`, `.copy()` with random leaf colors. Keep icons stroke-only. Vote dots: `LaggedStart` with 30 representatives, not 120 |
| 8 | 3.29 | Arch traced by a slider while a jar refills | Two updaters on one `ValueTracker`. The jar recoloring 20 balls per frame | `always_redraw` for the curve segment. The jar's `set_p` recolors `round(20·p)` balls (cheap). Test at `-ql` for jitter |
| 9 | 3.20, 3.25–3.26 | `TransformMatchingTex` chains | The minus sign moving out of the log needs matching isolated substrings | Use `{{ }}` / `substrings_to_isolate=["p_i", r"\log_2", "-"]`. Check each step at `-ql`. Fall back to `TransformMatchingShapes` |
| 10 | 2 | Celebrity silhouettes | No icon in Manim, and real faces raise licensing issues | A generic person icon from primitives (`Circle` head + `Arc` shoulders) or one CC0 SVG via `SVGMobject` |
| 11 | 1.7, 8.4 | Applicant crowd, green-trousers icons | Assets | Crowd = dots (fine). Trousers = a simple `Polygon` or CC0 SVG |
| 12 | 6.3 | Table rows turning into number-line dots | `Table` cell geometry, 11 synced transforms | `ReplacementTransform(table.get_rows()[i], dot_i)` in a `LaggedStart`. Fade headers separately |
| 13 | 8.16 | Cross-validation slices | Simple, but must stay readable at speed | 5 `Rectangle`s with a moving "hidden" highlight. Keep each step ≥ 0.6 s |
| 14 | 9.8 | Extending the x-axis | Axes rescale moves every point | Pan with `MovingCameraScene` instead of rebuilding the axes: draw the axes to x = 8 from the start, but frame only [−5, 5] until 9.8 |
| 15 | Global | Mid-sentence sync | No bookmarks (whisper disabled in `voice.py`) | Split long sentences into separate voiceover blocks (marked "split" above). Or enable transcription (`transcription_model="base"`, needs the `transcribe` extra) if you'd rather use bookmarks |
| 16 | `style.py` | Palette semantics | Yellow is both a class and the default highlight | Add `CLASS_0`, `CLASS_1`, `GAIN`, `IMPURITY`, `HIGHLIGHT` aliases and fix the comments (see Global conventions) |
| 17 | Scene 1a | Images on the dark background | `yury.jpg` and the banner have white backgrounds, and Manim CE can't mask an `ImageMobject` | Bake a circular alpha mask into `yury_circle.png`. For the banner, key white to alpha with a soft threshold (check that white sticker interiors survive) or keep it on a light rounded panel. The third-party characters on the stickers (cartoons, caricatures) could attract copyright claims on YouTube, so consider using only the mascot crop if that's a concern |
| 18 | Scene 1a | Intro placement | Resolved: the intro plays after the cold open, so the hook stays in the first 20 seconds | Keep it under ~8 s so the lecture proper starts quickly |
