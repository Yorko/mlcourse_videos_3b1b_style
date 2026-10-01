"""A grid of tiny decision-tree icons for the random-forest teaser (scene 10).

One template (a depth-2 ``TreeDiagram`` without labels, 4 leaves) is built
once and ``.copy()``-ed for every tree, then its leaf dots are recoloured by
class. Shape jitter (scale, tilt) is cosmetic and seeded.
"""

import numpy as np
from manim import PI, VGroup

from components.tree_diagram import DEFAULT_LEAF_COLORS, TreeDiagram

LEAF_IDS = ["l0", "l1", "l2", "l3"]  # left to right
TEMPLATE_SPEC = {
    "id": "r", "q": "",
    "no": {"id": "a", "q": "", "no": {"id": "l0", "leaf": ""}, "yes": {"id": "l1", "leaf": ""}},
    "yes": {"id": "b", "q": "", "no": {"id": "l2", "leaf": ""}, "yes": {"id": "l3", "leaf": ""}},
}


class Forest(VGroup):
    def __init__(self, trees: list[dict], cols: int = 15, cell_w: float = 0.8, cell_h: float = 0.6,
                 seed: int = 0, icon_width: float = 0.5, **kwargs):
        """``trees``: list of {"leaves": [4 x "Deny"/"Approve"], "landing": int, "vote": str}."""
        super().__init__(**kwargs)
        rng = np.random.default_rng(seed)
        template = TreeDiagram(TEMPLATE_SPEC, labels=False, h_spacing=0.3, level_gap=0.32,
                               dot_radius=0.05, edge_width=2)
        template.set_width(icon_width)
        self.icons: list[TreeDiagram] = []
        rows = int(np.ceil(len(trees) / cols))
        for k, t in enumerate(trees):
            icon = template.copy()
            for lid, cls in zip(LEAF_IDS, t["leaves"]):
                icon.node(lid).set_color(DEFAULT_LEAF_COLORS[cls])
            icon.scale(rng.uniform(0.85, 1.1)).rotate(rng.uniform(-1, 1) * PI / 30)
            r, c = divmod(k, cols)
            icon.move_to([(c - (cols - 1) / 2) * cell_w, ((rows - 1) / 2 - r) * cell_h, 0])
            icon.shift(rng.uniform(-0.04, 0.04, 3) * [1, 1, 0])
            self.icons.append(icon)
        self.trees = trees
        self.add(*self.icons)

    def landing_point(self, k: int) -> np.ndarray:
        """Centre of the leaf where the applicant lands in tree ``k``."""
        return self.icons[k].node(LEAF_IDS[self.trees[k]["landing"]]).get_center()
