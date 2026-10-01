# Plan: a 3Blue1Brown-style video on decision trees

**Source:** mlcourse.ai Topic 3, "Classification, Decision Trees and k Nearest Neighbors" (decision-tree part only)
**Target:** a 12–18 minute video, 4K/60fps, made with Manim Community Edition and narrated by an ElevenLabs clone of your voice
**Principle:** AI drafts everything (script, storyboard, code, voice, subtitles, metadata). You act as director and editor: you decide what is true, what is clear, and what looks good.

> Note: I couldn't load the article from this session (the domain is blocked here), so the scene outline below is based on what I know of the Topic 3 content. That includes the 20-balls entropy example, information gain, Gini, the 2D toy dataset, overfitting and regression trees. Paste the article into your AI assistant in Phase 2 so the script follows your exact text and numbers.

---

## Phase 0. Tooling setup (½ day)

1. **Python environment:** Python 3.11+ with `uv` or `conda`. Create a project such as `dt-video/`.
2. **Manim Community:** `pip install manim`. Also install its dependencies:
   - macOS: `brew install ffmpeg cairo pango pkg-config`
   - LaTeX for formulas: `brew install --cask mactex-no-gui` (or BasicTeX plus the packages `standalone preview doublestroke relsize fundus-calligra wasysym physics dvisvgm jknapltx rsfs wasy cm-super everysel setspace`)
   - Check the install with `manim -pql example.py SquareToCircle`
3. **Voice-to-animation sync:** `pip install "manim-voiceover[elevenlabs]"`. This plugin lets you write narration *inside* each scene (`with self.voiceover(text="...") as tracker:`). Animation timing then follows the audio, which removes most manual syncing.
4. **ML side:** `pip install scikit-learn numpy pandas matplotlib`
5. **AI coding assistant:** Claude Code (terminal) or Cursor/VS Code with Claude, opened in the project folder. Claude Code works best here because it can run `manim` itself, extract frames, *look at them*, and fix layout problems in a loop.
6. **Editing:** DaVinci Resolve (free) for final assembly, music and color.
7. **Accounts:** ElevenLabs (Creator plan or higher is needed for a Professional Voice Clone).

**AI shortcut:** ask Claude Code: *"Set up a Manim Community project with manim-voiceover and ElevenLabs, a `style.py` module, a `scenes/` folder, and a Makefile with `preview` (-ql) and `final` (-qk --fps 60) targets. Verify it renders a test scene."*

---

## Phase 1. Learn the 3b1b style and turn it into a style guide (1 day)

Watch these with the question "what does each visual *do* for understanding?" in mind:
- *Neural networks* ch. 1–2 (the closest ML analogue)
- *Solving Wordle using information theory*, which covers entropy and "good questions". It is the closest match to your topic
- *But what is the Central Limit Theorem?* (data viz + narration pacing)

Then have AI turn your notes and the transcripts into a **one-page `STYLE.md`**. That file is passed to every later AI prompt. It should cover:

- **Pedagogy:** concrete example before abstraction. Pose a question before giving its answer. Have one "aha" per section. Show the formula only *after* the intuition, and build it piece by piece.
- **Visual language:** dark background (`#1C1C1C`-ish), a small palette with *fixed semantic meaning* (e.g. BLUE = class 0, YELLOW = class 1 to match your balls example, GREEN = information gain, RED = impurity/error). Little on-screen text, plenty of whitespace, formulas in LaTeX (CMU Serif look).
- **Motion:** `TransformMatchingTex` for formula steps, smooth camera moves (`MovingCameraScene`), `Indicate`/`Circumscribe` for emphasis, objects that *become* other objects rather than cutting.
- **Narration:** conversational, second person, short sentences, rhetorical questions, little jargon until it is earned.
- **Note:** the Pi Creatures belong to 3b1b and aren't in Manim CE. Leave them out, or design your own small mascot (e.g. a little tree character). AI image tools plus a hand-cleaned SVG work well for that.

**Prompt:** *"Here are transcripts of 3 3Blue1Brown videos [paste]. Extract a style guide covering narrative structure, pacing (words per minute, pause usage), how formulas are introduced, how visuals are sequenced, and recurring rhetorical devices. Output a concise STYLE.md I can feed to other prompts."*

---

## Phase 2. Script (2–3 days, several AI rounds)

### 2a. Narrative outline
Give the AI your article, `STYLE.md`, and the outline below. Ask for a *beat sheet*: for each scene, the question it raises, the insight it delivers, and the key visual.

**Suggested arc (≈15 min, ~2,100 words at 140 wpm):**

| # | Scene | Core idea / "aha" | Signature visual | ~min |
|---|-------|------------------|------------------|-----|
| 1 | Cold open | A tree is a sequence of questions. *Which question should come first?* | Loan application flowing down a tree, lighting up a path | 1.0 |
| 2 | 20 Questions | A good question splits the possibilities evenly. Information means reduced uncertainty | Grid of candidates halving with each yes/no | 1.5 |
| 3 | Entropy | Uncertainty can be measured: S = −Σ pᵢ log₂ pᵢ | Your 20 balls (9 blue, 11 yellow) on a line. Entropy curve S(p) traced as p slides | 2.5 |
| 4 | Information gain | A split is good if it lowers weighted entropy | Split at x ≤ 12: groups of 13 and 7, entropies computed live, IG ≈ 0.16 shown | 2.0 |
| 5 | Growing the tree | Repeat greedily until the leaves are pure | Balls recursively partitioned while the tree grows beside them | 1.5 |
| 6 | Other criteria | Gini and misclassification error. Entropy/2 ≈ Gini | Three curves on one axis, morphing between them | 1.0 |
| 7 | Trees in 2D | Axis-parallel splits carve the feature plane into rectangles | **Signature shot:** two point clouds, the plane is cut step by step *in sync* with tree nodes appearing | 2.0 |
| 8 | Numeric features | Only thresholds where the class changes matter | Sorted "age" axis with candidate thresholds flashing | 1.0 |
| 9 | Overfitting | A deep tree memorizes noise. Fix it with max_depth and min_samples_leaf, tuned by cross-validation | Boundary going jagged as depth grows. Train vs. test accuracy curve diverging | 1.5 |
| 10 | Regression trees | Same algorithm, but splits reduce variance. The result is a step function | Noisy curve with a step-function fit refining as depth grows | 1.0 |
| 11 | Wrap-up | Pros/cons. Trees are interpretable, and they lead to forests and boosting | Tree dissolving into a forest. Link to the mlcourse.ai article | 0.5 |

### 2b. Full narration draft
**Prompt:** *"Using STYLE.md, my article [paste], and this beat sheet, write the full narration. Mark each visual cue inline as [VISUAL: …]. Aim for 2,100 words. Pose each question before answering it. Introduce every formula only after the intuition."*

### 2c. Critique loops (this is where quality comes from)
Run 2–3 separate AI "reviewer" passes, each with a different persona:
- **Confused beginner:** "Where would you get lost or bored?"
- **ML expert:** "Find any technical inaccuracy or oversimplification that crosses into wrong."
- **YouTube editor:** "Where does retention drop? Is the hook strong in the first 20 seconds?"

Then **read the script aloud yourself.** Anything you stumble on, the AI voice will stumble on too.

---

## Phase 3. Ground-truth numbers (½ day)

Don't let AI invent numbers inside animation code. Write (or have AI write) one notebook, `data/compute.ipynb`, that:
- recomputes the ball example (entropies of 9/11, 8/5 and 1/6 splits, IG for **every** threshold, which gives a nice bar chart for scene 4),
- generates the 2D toy dataset with a fixed seed, fits `DecisionTreeClassifier` at depths 1…N, and exports the split thresholds and leaf regions,
- computes train/test accuracy vs. depth with cross-validation,
- fits `DecisionTreeRegressor` to the noisy function from the article.

Export everything to `data/*.json`. The Manim scenes **read** these files. That makes the numbers on screen correct and reproducible.

---

## Phase 4. Storyboard (1–2 days)

Turn the script into a scene-by-scene storyboard, `STORYBOARD.md`. For each scene, include the narration chunks, the objects on screen, the transitions, the colors, and the camera moves.

**Prompt:** *"Convert this script into a Manim storyboard. For each narration sentence, specify the Mobjects on screen, the animation (e.g. TransformMatchingTex, Create, ReplacementTransform), the screen position and color (from STYLE.md), and what stays and what fades. Flag any visual that is hard to implement."*

Optional: sketch the 3–4 hardest frames by hand (or in Excalidraw) and give the images to the AI. A rough sketch helps it more than a paragraph of text.

---

## Phase 5. Voice clone (1 day, in parallel with Phase 4)

1. **Record training audio:** 30+ minutes (more is better, up to ~2–3 h) of you reading varied, *conversational* text in the tone you want for the video. Use a quiet room and a decent USB mic, keep the same distance from the mic, and do no heavy processing.
2. **Create a Professional Voice Clone** in ElevenLabs. An Instant clone (1–2 min of audio) is fine for prototyping, but it sounds noticeably less like you.
3. **Pronunciation dictionary:** add entries for "Gini", "log base two", "scikit-learn", "max_depth" (read as "max depth"), and similar terms.
4. **Settings:** pick a multilingual/v2-class model. Lower "style exaggeration" sounds calmer and closer to 3b1b. Generate the same paragraph a few times and pick a stability setting.
5. **Disclosure:** mention in the description that the narration is an AI clone of your voice. It's good practice, and YouTube asks you to label realistic synthetic content.

With `manim-voiceover`, the narration text lives in the scene code and audio is generated and cached automatically on render. You can still swap in a hand-recorded or hand-picked take for any line.

---

## Phase 6. Build the animations (1.5–3 weeks; most of the work)

### Project layout
```
dt-video/
  STYLE.md  STORYBOARD.md  CLAUDE.md
  style.py            # palette, fonts, shared helpers (ball(), tree_node(), axes presets)
  components/         # reusable: BallRow, TreeDiagram, EntropyCurve, PartitionedPlane
  scenes/s01_cold_open.py … s11_wrapup.py
  data/*.json
  media/              # renders
```

### Put project rules in `CLAUDE.md`
Claude Code reads this file automatically. Include: "Use Manim Community v0.19+ API only (not manimgl). Import colors from style.py. Read numbers from data/*.json, never hard-code. Every scene uses VoiceoverScene. After writing a scene, render at -ql, extract frames at key timestamps with ffmpeg, inspect them for overlaps/off-screen text, and fix."

### Build reusable components first
The `TreeDiagram` (it grows node by node, highlights a path, and stays linked to a `PartitionedPlane`) is used in scenes 1, 5, 7 and 9. Getting it right first pays off later. Ask AI for it as a standalone component with its own test scene.

### Per-scene loop with Claude Code
1. *"Implement scene 4 from STORYBOARD.md."*
2. Claude renders at low quality and checks frames itself.
3. **You watch the preview** (`manim -pql`). Give concrete feedback, e.g. "the formula appears too early; slow the split by 0.5s; the yellow is too saturated".
4. Iterate 3–6 times. Commit to git after each scene works (git lets you roll back when an AI edit breaks something).

### Tips
- Work on one scene per session/context. Long chats about many scenes degrade AI output.
- When AI gets stuck on something visual, describe the *geometry* precisely ("the left child node sits 1.5 units below and 2 units left of the parent") or give it a sketch.
- Ask for `self.next_section()` markers so you can re-render parts of a scene.
- Ask AI to look up 3b1b's open-source scene code (github.com/3b1b/videos) for *ideas* on how Grant structures a scene. It's written for manimgl, so have AI translate the patterns, not copy the code.

---

## Phase 7. Final render and assembly (2–3 days)

1. Render everything with `manim -qk --fps 60` (4K) or `-qh` (1080p60).
2. In DaVinci Resolve, place scenes on the timeline and add short pauses between sections. Add **background music** (calm piano/ambient, royalty-free or licensed, e.g. Epidemic Sound or Artlist) ducked under the voice. Add subtle sound effects for splits and highlights, sparingly.
3. Audio mastering: normalize the voice to about −14 LUFS integrated for YouTube.
4. Watch it end to end at 1×. Then watch it again with the sound off: does the visual story still make sense?

---

## Phase 8. Review (2–3 days)

- **Accuracy pass:** generate a transcript with Whisper and ask AI to check every claim and number against your article and the `data/*.json`.
- **Test audience:** show it to 2–3 people (one beginner, one ML practitioner). Note where they look confused or reach for the scrub bar.
- **Fix and re-render** only the affected sections (this is why sections and caching matter).

---

## Phase 9. Publish (1 day)

- **Thumbnail:** a single striking frame (e.g. the partitioned plane with the tree beside it). Render it directly from Manim at full resolution. Add at most 2–4 words.
- **Title:** AI can generate 20 options in 3b1b phrasing, e.g. "How does a decision tree decide what to ask?" Pick one.
- **Description:** link the mlcourse.ai article, chapters (timestamps from your sections), and the AI-voice disclosure.
- **Subtitles:** Whisper SRT, proofread. **Dubbing:** ElevenLabs dubbing into e.g. Russian/Spanish keeps your cloned voice.
- **Repurpose:** cut the signature 2D-partition shot into a 60-second Short.
- Optionally open-source the Manim code next to the mlcourse.ai repo.

---

## Rough timeline (part-time, evenings/weekends)

| Week | Work |
|------|------|
| 1 | Setup, style guide, script plus critique loops, ground-truth notebook, voice training recording |
| 2 | Storyboard, reusable components, scenes 1–4 |
| 3 | Scenes 5–11 |
| 4 | Assembly, review, fixes, publish |

Full-time, this compresses to about 1.5–2 weeks. Expect scenes 3, 4 and 7 to take the longest.

## Where AI helps most and least
- **Highest leverage:** Manim boilerplate and components, script first drafts, critique passes, numeric notebook, voice, subtitles, dubbing, metadata.
- **Keep for yourself:** choosing the "aha" moments, judging visual taste and pacing, final accuracy sign-off. That judgment is what separates a good video from a generic one.
