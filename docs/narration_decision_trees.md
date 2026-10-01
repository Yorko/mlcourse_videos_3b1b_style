# Decision Trees — Full Narration (draft 2)

Source: mlcourse.ai Topic 3 (decision-tree part), `docs/STYLE.md`, `docs/beat_sheet_decision_trees.md`.
Colors: BLUE = class 0 / blue ball, YELLOW = class 1 / yellow ball, GREEN = information gain, RED = impurity/error.
Numbers on screen should come from `data/*.json` (Phase 3). Values quoted here were recomputed from the article.

Draft 2 folds in three reviews (confused beginner, ML expert, YouTube editor). Changes from the beat sheet:
- The numeric-features scene moves before the 2D scene, so the "trap" teaser leads straight into overfitting.
- "Other criteria" shrinks to a short Gini aside inside that scene.
- There are now 10 scenes.

> **Open data check (scenes 4–5):** the article never says x ≤ 12 is the highest-gain cut for the 20 balls. Depending on the exact positions, another cut may win. Once `data/balls.json` exists, highlight the true tallest bar in scene 4. If it isn't x ≤ 12, rebuild scene 5's tree around the real greedy choices.

---

## 1. Cold open (~1.0 min)

[VISUAL: Dark screen. A loan application card: Age, Home-ownership, Income, Education. A small flowchart beside it.]

This is a loan application, and this little flowchart just denied it.

[VISUAL: The card drops into the root and falls down the tree, lighting each edge: "Owns a home?" No. "Income above 5,000?" No. It lands on a RED "deny" leaf.]

Own a home? No. Income above 5,000? No. Denied. And the path itself is the explanation.

[VISUAL: The path stays lit. The rest of the tree dims.]

What's remarkable is that nobody wrote these questions by hand. An algorithm studied thousands of past applicants and worked out for itself which questions to ask, in what order, and where to set each cutoff. That's a decision tree.

[VISUAL: The root node pulses with a "?" on it.]

So out of all the questions it could ask, how does it decide which one comes first? The answer is a beautiful idea from information theory. And by the end you'll also see why a tree that's perfect on the data it learned from can be confidently wrong about the very next person who walks in.

[VISUAL: Title: "Decision trees: what should you ask first?" Hold 2 s.]

---

## 2. Twenty Questions (~1.5 min)

[VISUAL: A grid of 64 small celebrity silhouettes.]

Start with a game you've probably played: Twenty Questions. I'm thinking of a celebrity, and you can only ask yes-or-no questions. What should you ask first?

[VISUAL: The question "Is it Angelina Jolie?" appears. One silhouette highlights.]

You could go for the jackpot: "Is it Angelina Jolie?" If the answer is yes, wonderful. But almost always the answer is no.

[VISUAL: The answer "No" appears. One silhouette fades. A bar reads "63 left".]

And when it's no, you've ruled out exactly one person. You've learned almost nothing.

[VISUAL: Reset. New question: "Is the celebrity a woman?" The grid splits into two halves of 32; one half fades. A bar reads "32 left".]

Now compare that with "Is the celebrity a woman?" Whatever the answer, half the possibilities disappear.

[VISUAL: Keep halving: 32 → 16 → 8 → 4 → 2 → 1, with a counter of questions asked.]

Keep asking questions like that, and 64 candidates come down to one in just six questions. Twenty of them could pin down one person out of about a million, two to the twentieth.

What made the second question good wasn't cleverness. You couldn't predict the answer, so either answer cut away a lot. That's what information means here: reduced uncertainty.

[VISUAL: The words "information = reduced uncertainty" under the grid. Hold 2 s.]

But for a computer to choose questions, "uncertainty" has to become a number. So how do you measure it?

---

## 3. Entropy (~2.5 min)

[VISUAL: Clear. 20 balls on a number line at positions 0 to 19: 9 BLUE, 11 YELLOW. Blues lean left, yellows lean right, with some mixing.]

Let's switch to a simpler world. Here are twenty balls on a line, nine blue and eleven yellow. Blues tend to sit on the left and yellows on the right, so a ball's position is a clue to its color. Eventually we'll build a tree that predicts color from position. But first, before asking anything, how uncertain are we?

[VISUAL: A hand pulls out a random ball. Probabilities appear: 9/20 blue, 11/20 yellow.]

If I pull out a ball at random, it's blue with probability 9 out of 20 and yellow with probability 11 out of 20. That's close to a coin flip. You'd have a hard time betting either way.

[VISUAL: Three small jars side by side: all yellow; 19 yellow and 1 blue; 10 and 10.]

Compare a few jars. If every ball is yellow, there's no uncertainty at all. One blue among nineteen yellow, still very little. Ten and ten, as uncertain as it gets. So whatever our measure is, it should be zero for a pure jar and largest for an even mix.

[VISUAL: The 20-question grid in a corner, with "1 halving question = 1 bit".]

Twenty Questions gives us a unit. Call one perfectly halving yes-or-no question one bit. Now flip it around. If something had a one-in-two chance and you learn that it happened, you've learned as much as one halving question: one bit. A one-in-four outcome is like two halvings, so two bits. One-in-eight, three bits.

[VISUAL: The formula assembles piece by piece: (1/2)^bits = p → 2^bits = 1/p → bits = log₂(1/p).]

So the number of bits is log base two of one over the probability. Log base two simply counts how many halvings it takes to get there. Rare outcomes carry lots of bits, and common ones carry very few.

[VISUAL: Each ball color gets a tag: blue log₂(20/9) ≈ 1.15 bits, yellow log₂(20/11) ≈ 0.86 bits.]

Blue is the rarer color here, so drawing a blue ball tells you a bit more: about 1.15 bits, versus 0.86 for yellow.

[VISUAL: TransformMatchingTex: Σ pᵢ log₂(1/pᵢ) → S = −Σ pᵢ log₂ pᵢ.]

Now average those over the outcomes, weighting each by how often it happens. That average has a name: entropy. In textbooks you'll see it with a minus sign out front, because log of one over p is the same as minus log p.

[VISUAL: Plug in: S₀ = −(9/20)log₂(9/20) − (11/20)log₂(11/20) ≈ 0.99.]

For our twenty balls, that comes out to about 0.99 bits, almost exactly one. So it really is nearly a perfect coin flip.

[VISUAL: Axes: p (fraction of yellow) from 0 to 1, entropy from 0 to 1. A slider on p traces the curve while a jar above refills to match.]

And if we slide that proportion from all blue to all yellow, entropy traces out this arch. It's zero at both ends, where the jar is pure, and peaks at exactly one bit at fifty-fifty.

[VISUAL: The curve stays. The point at p = 11/20 is marked. Hold 2 s.]

---

## 4. Information gain (~2.0 min)

[VISUAL: Back to the 20 balls. A vertical dashed line, a cut point, slides along and stops between 12 and 13.]

Now we can score a question. On this line, a question is a cut point, a threshold: "Is the position at most twelve?" Does asking it lower our uncertainty?

[VISUAL: The balls split into two groups. Left: 13 balls (8 blue, 5 yellow). Right: 7 balls (1 blue, 6 yellow).]

On the left we get thirteen balls, eight blue and five yellow. On the right, seven balls: one blue and six yellow.

[VISUAL: Entropies compute live under each group: S₁ ≈ 0.96, S₂ ≈ 0.59. Both are marked on the arch from scene 3.]

The left group is still pretty mixed, at about 0.96 bits. The right group is much more predictable, at about 0.59. Both are lower than the 0.99 we started with.

So how do we combine them into one score? You might just average them. But should a group of seven count as much as a group of thirteen?

[VISUAL: Thought experiment: a cut that peels off one lonely ball into a "pure" group with entropy 0, next to the other 19, still thoroughly mixed.]

Imagine a cut that peels off one single ball. That tiny group is perfectly pure, so a plain average would call it a great question, even though the other nineteen balls are almost exactly as mixed as before. So we weight each group by its share of the balls.

[VISUAL: Formula builds: S₀ − (13/20)·S₁ − (7/20)·S₂ ≈ 0.16, in GREEN. Then it generalizes on screen: IG(Q) = S₀ − Σ (Nᵢ/N)·Sᵢ.]

Entropy before, minus each group's entropy weighted by its share: that's the information gain. Here it's about 0.16 bits, out of the 0.99 we started with. That's a modest step, and it's the same recipe for any number of groups.

[VISUAL: Candidate cuts flash at every gap between balls. Hold 3 s before revealing bars.]

Of course, twelve was just one candidate. Before I show you, pause and guess: which cut on this line do you think lowers the uncertainty the most?

[VISUAL: A bar chart of the gain for every possible threshold, built one bar at a time. The tallest bar is highlighted in GREEN (take it from data/balls.json).]

Now "which question should come first" has a mechanical answer. Try every threshold, compute the gain of each, and pick the tallest bar.

[VISUAL: Ghost image of the celebrity grid beside the bar chart.]

It's Twenty Questions again, only now the computer keeps the books. A cut that clips off one ball is the "Angelina Jolie" question, with a tiny bar. The winner leaves both sides more predictable.

---

## 5. Growing the tree (~1.5 min)

[VISUAL: Split screen. Left: the ball line. Right: a tree with a single root node.]

One question doesn't make a tree, though. What do we do with the two groups we just made?

[VISUAL: The right group splits at x ≤ 18 into pure yellow and pure blue. A node appears on the tree at the same moment.]

We do exactly the same thing again, inside each group. The right group needs just one more question, "is the position at most eighteen?", and both pieces come out a single color.

[VISUAL: The left group splits three more times. Each split appears as a new tree node, synced to the cut on the line. The end points turn solid BLUE or YELLOW and are labeled "leaves".]

The left group is messier and takes three more cuts. A group where every ball is the same color has entropy zero, so there's nothing left to ask, and we stop. Those end points are called leaves. Each one predicts the color of the balls that land in it.

[VISUAL: The finished tree with pure leaves. A counter reads "5 questions". Small on-screen tag: "ID3 · C4.5 · CART".]

That's the core idea behind the classic tree algorithms. At every node, grab the question with the biggest gain right now, split, and then repeat the whole process inside each piece.

Is grabbing the best question right now guaranteed to give the best tree overall? No. Finding the truly best tree would mean searching through an astronomical number of possible trees, so in practice everyone settles for this greedy shortcut. It works remarkably well.

[VISUAL: The finished tree glows. The word "perfect" is written beside it.]

So now our tree is perfect: every training ball lands in a leaf of its own color. Hold on to that word, perfect. It's going to come back to bite us.

---

## 6. Back to the bank: numeric features + Gini aside (~1.5 min)

[VISUAL: A table of 11 bank clients: Age, Loan default. The rows sort themselves by age onto a number line, as BLUE (repaid) and YELLOW (defaulted) dots.]

Back to the bank. A real feature, a measurement like age, can take dozens of values. Do we really have to try every possible cut?

[VISUAL: Candidate cuts flash between every pair of neighbors. Then the ones where the color switches glow: 19, 22.5, 30, 32, 43.5.]

Sort the clients by age and look at where the color switches. Here it switches only five times, and those five midpoints are exactly the cuts the tree ends up using.

[VISUAL: A cut at 17.5 flashes in RED, between two defaulters, ages 17 and 18. Then it slides to 19.]

So why would you never pick, say, 17.5? Both seventeen and eighteen defaulted. Slide the cut up to 19 and the left side stays pure, but the right side loses a defaulter and gets cleaner, so the gain roughly doubles.

[VISUAL: Gain bars for the five switch points. The bar at 43.5 is tallest (entropy IG ≈ 0.40) and becomes the root.]

That's a general fact: the best cut always sits at one of these switch points. Here the winner is 43.5, which becomes the root of the tree. With more features, you do the same trick for each one.

[VISUAL: Aside panel. The entropy arch, then the Gini curve 2p(1 − p), doubled, closely tracking it. Small text: "misclassification error, rarely used".]

One small confession: this particular tree was actually built with a cousin of entropy called Gini impurity. Draw two clients at random. How likely is it that one repaid and one defaulted? Gini tops out at one half and entropy at one, so double it to compare, and the two curves closely track each other. That's why they usually pick the same splits.

---

## 7. Trees in two dimensions (~2.0 min)

[VISUAL: Axes x₁, x₂. Two point clouds fade in: 100 BLUE around (0, 0), 100 YELLOW around (2, 2), overlapping in the middle.]

Here's where trees get their signature look. Now each example has two measurements, which machine learning calls features, and belongs to one of two categories, or classes. There are two hundred points in two overlapping clouds. What does a question look like here?

[VISUAL: An on-screen question: "x₂ ≤ 1.211?"]

Each question still looks at just one feature and compares it to a number. In the plane, that means a straight cut, either horizontal or vertical.

[VISUAL: **Signature shot.** Faint ghost lines sweep through candidate thresholds on both axes. Then a horizontal line locks in at x₂ = 1.211, flashing GREEN. Both halves tint toward their majority color. A root node appears on a tree to the right at the same instant.]

The tree tries every cut on both axes, scores each one, and keeps the winner: is x₂ at most about 1.2? That one horizontal line already separates most of the blue from most of the yellow.

[VISUAL: Inside each half, a vertical cut appears in sync with two new tree nodes. Then the third-level cuts follow, each region subdividing as its node appears.]

Then each half gets its own question, and each of those gets another. Every node in the tree is a cut in the plane, and every cut lives only inside its parent's region.

[VISUAL: The finished three-level tree: 8 leaves on the right, 8 rectangles on the left. A leaf and its rectangle highlight together. Neighboring rectangles of the same color merge visually.]

Three questions deep, we have eight leaves, which means eight rectangles. Inside each one, the tree predicts whichever color holds the majority.

[VISUAL: A new test point drops in. It travels down the tree while the matching rectangle lights up.]

So a decision tree is really a way of carving space into boxes, always with cuts parallel to the axes.

[VISUAL: A faint diagonal line, the "natural" boundary, overlays the staircase of rectangles.]

Notice the price of that. The natural boundary between these clouds is a diagonal line, and the best a tree can do is approximate it with a staircase. More depth means finer steps, which sounds like a fix. It's actually a trap.

---

## 8. Overfitting (~1.5 min)

[VISUAL: The 2D clouds again. A depth slider: 1, 2, 3, 6, 10, unlimited. The rectangles shatter into tiny slivers around individual points.]

If deeper trees fit the data better, why not keep splitting until every leaf is pure?

[VISUAL: At max depth, slivers wrap single stray points deep inside the other cloud.]

Watch what happens. The boundary turns jagged, carving out tiny boxes around single points that are almost certainly just noise. It's like a bank noticing that the four clients who came in wearing green trousers all defaulted, and making that a rule.

[VISUAL: Back to the 20 balls and the word "perfect". A new ball drops in at a spot the tree carved into a tiny leaf, and it's predicted wrong. "perfect" cracks.]

Remember our perfect tree? That's exactly the problem. It fits every training ball, and that's precisely why it can stumble on the twenty-first. A simpler tree that gets a couple of training balls wrong could easily do better on new ones.

[VISUAL: Plot of accuracy vs. depth on the 2D data. Train climbs to 100% by depth 8. Held-out accuracy peaks at depth 4 (≈ 0.88; depth 3 is nearly tied), then slowly sags. Values from data/depth_cv.json (5-fold CV repeated 10 times). The gap is shaded RED.]

On the training data, accuracy marches up to a hundred percent. On data the tree has never seen, it peaks at about four questions deep, then slowly gets worse. The tree has memorized instead of learned.

[VISUAL: Two dials labeled "max depth" and "min points per leaf". Turning them smooths the boundary.]

So how do you stop it? The simplest way is to stop growing early: cap the depth, or demand a minimum number of points in every leaf. Or grow the full tree and then prune back the branches that don't earn their keep.

[VISUAL: Data split into five slices. Each slice takes a turn being hidden while the tree trains on the rest. The best depth is circled.]

And how do you pick the right depth? Hide part of the data from the tree, test on that hidden part, repeat with different slices hidden, and keep the depth that does best. That's cross-validation.

---

## 9. Regression trees (~1.0 min)

[VISUAL: 150 noisy points scattered around the curve f(x) = e^(−x²) + 1.5·e^(−(x−2)²), for x from −5 to 5.]

What if the answer isn't a color at all, but a number?

[VISUAL: A single leaf: a flat line at the mean of all points, with vertical residual lines drawn to it.]

A leaf can't vote on a color anymore, so it predicts the average of its points. And the uncertainty we want to shrink becomes how spread out those values are around that average.

[VISUAL: Formula: D = (1/n) Σ (yᵢ − ȳ)², with ȳ highlighted as "the leaf's prediction".]

That's the variance: the average squared distance from the mean. Everything else stays the same. Find the cut that lowers variance the most, then repeat inside each piece.

[VISUAL: Depth slider 1 → 2 → 3 → 5. The fit refines from one step to a staircase that tracks both bumps.]

The result is a step function, and with more depth the steps follow the curve more closely.

[VISUAL: The x-axis extends past 5. The prediction stays flat.]

But past the edge of the data, it just stays flat. A tree can fill in between points it has seen, but it can't predict beyond them. Our balls work the same way: every ball past eighteen lands in the same leaf, so a ball at twenty-five gets exactly the same prediction as one at nineteen.

---

## 10. Wrap-up (~0.5 min)

[VISUAL: The loan tree from the cold open returns, with the applicant's path lit.]

So which question comes first? The one with the biggest information gain, then the same rule again, all the way down. That gives you a model you can read like a flowchart.

[VISUAL: A few past applicants change. The tree regrows with different questions, and the lit path now gives a different reason.]

But here's the catch. Change a handful of past applicants, and the tree can regrow completely: different questions, a different reason for the same denial. The path is the explanation, but it isn't stable.

[VISUAL: The tree multiplies into hundreds of slightly different trees, each grown on a random resample of the data, forming a forest. Their votes combine. Title card: mlcourse.ai, Topic 3.]

The fix is wonderfully simple. Grow hundreds of trees, each on a random resample of the data, and let them vote. That's a random forest, and it's next.
