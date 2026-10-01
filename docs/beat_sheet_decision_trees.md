
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