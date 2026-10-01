"""Binary decision-tree diagram built from a nested dict spec.

Spec format (same as ``data/loan_tree.json``)::

    {"id": "root", "q": "Owns a home?",
     "no": {...child...}, "yes": {...child...}}
    {"id": "deny", "leaf": "Deny"}          # a leaf

"no" children go left, "yes" children go right. Each subtree gets a span wide
enough for its own box and its children side by side, and every parent sits
centered over its children.

With ``labels=False`` nodes are drawn as dots (for small/background trees).
"""

import numpy as np
from manim import (
    BOLD,
    AnimationGroup,
    Create,
    Dot,
    FadeIn,
    GrowFromCenter,
    LaggedStart,
    Line,
    RoundedRectangle,
    Text,
    VGroup,
)

from style import BACKGROUND, FONT, GRID, HIGHLIGHT, IMPURITY, LEFT, RIGHT, TEXT, TEXT_MUTED

DEFAULT_LEAF_COLORS = {"Deny": IMPURITY, "Approve": HIGHLIGHT}


class TreeDiagram(VGroup):
    def __init__(
        self,
        spec: dict,
        h_spacing: float = 0.25,
        h_gap: float = 0.3,
        level_gap: float = 1.4,
        font_size: float = 22,
        labels: bool = True,
        leaf_colors: dict | None = None,
        dot_radius: float = 0.07,
        edge_width: float = 3,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.leaf_colors = leaf_colors or DEFAULT_LEAF_COLORS
        self.nodes: dict[str, VGroup] = {}
        self.edges: dict[str, Line] = {}  # keyed by child id
        self.edge_labels: dict[str, Text] = {}  # keyed by child id
        self.parent: dict[str, str] = {}
        self.node_depth: dict[str, int] = {}
        self.leaves: list[str] = []

        branch: dict[str, str] = {}
        children: dict[str, list[str]] = {}

        def collect(node: dict, d: int) -> None:
            nid = node["id"]
            self.node_depth[nid] = d
            self.nodes[nid] = self._make_node(node, labels, font_size, dot_radius)
            children[nid] = []
            for b in ("no", "yes"):
                if b in node:
                    child = node[b]
                    self.parent[child["id"]] = nid
                    branch[child["id"]] = b
                    children[nid].append(child["id"])
                    collect(child, d + 1)
            if not children[nid]:
                self.leaves.append(nid)

        collect(spec, 0)
        self.root_id = spec["id"]

        # Width-aware layout: each subtree gets a horizontal span wide enough for
        # its own box and for its children's spans side by side, so boxes on the
        # same level never overlap. Dots use h_spacing as their slot width.
        gap = h_gap if labels else 0.0
        span: dict[str, float] = {}

        def measure(nid: str) -> float:
            own = self.nodes[nid].width if labels else h_spacing
            kids = children[nid]
            span[nid] = max(own, sum(measure(c) for c in kids) + gap * (len(kids) - 1)) if kids else own
            return span[nid]

        def place(nid: str, left: float) -> float:
            kids = children[nid]
            if not kids:
                x = left + span[nid] / 2
            else:
                total = sum(span[c] for c in kids) + gap * (len(kids) - 1)
                cursor = left + (span[nid] - total) / 2
                xs = []
                for c in kids:
                    xs.append(place(c, cursor))
                    cursor += span[c] + gap
                x = (xs[0] + xs[-1]) / 2
            self.nodes[nid].move_to([x, -self.node_depth[nid] * level_gap, 0])
            return x

        place(self.root_id, -measure(self.root_id) / 2)

        for cid, pid in self.parent.items():
            a, b = self.nodes[pid], self.nodes[cid]
            if labels:
                edge = Line(a.get_bottom(), b.get_top(), color=GRID, stroke_width=edge_width)
            else:
                edge = Line(a.get_center(), b.get_center(), color=GRID, stroke_width=edge_width)
            self.edges[cid] = edge
            if labels:
                # Offset along the edge normal, on the outer side, so the label
                # clears the line even when the edge is nearly horizontal.
                side = LEFT if branch[cid] == "no" else RIGHT
                d = edge.get_unit_vector()
                normal = np.array([-d[1], d[0], 0.0])
                if np.dot(normal, side) < 0:
                    normal = -normal
                lab = Text(branch[cid].capitalize(), font=FONT, font_size=font_size * 0.8, color=TEXT_MUTED)
                lab.move_to(edge.point_from_proportion(0.55) + normal * (0.06 + 0.7 * lab.height))
                self.edge_labels[cid] = lab

        # Edges behind nodes so node fills hide line ends.
        self.add(*self.edges.values(), *self.edge_labels.values(), *self.nodes.values())

    def _make_node(self, node: dict, labels: bool, font_size: float, dot_radius: float) -> VGroup:
        is_leaf = "leaf" in node
        if not labels:
            color = self.leaf_colors.get(node.get("leaf"), TEXT_MUTED) if is_leaf else TEXT_MUTED
            return VGroup(Dot(radius=dot_radius, color=color))
        if is_leaf:
            text = Text(node["leaf"], font=FONT, font_size=font_size, color=BACKGROUND, weight=BOLD)
            color = self.leaf_colors.get(node["leaf"], TEXT_MUTED)
            box = RoundedRectangle(
                width=text.width + 0.35,
                height=text.height + 0.3,
                corner_radius=0.15,
                stroke_color=color,
                fill_color=color,
                fill_opacity=1,
            )
        else:
            text = Text(node["q"], font=FONT, font_size=font_size, color=TEXT)
            box = RoundedRectangle(
                width=text.width + 0.4,
                height=text.height + 0.35,
                corner_radius=0.12,
                stroke_color=TEXT_MUTED,
                stroke_width=2,
                fill_color=BACKGROUND,
                fill_opacity=1,
            )
        text.move_to(box)
        return VGroup(box, text)

    # --- Queries -------------------------------------------------------------

    def node(self, nid: str) -> VGroup:
        return self.nodes[nid]

    def path_ids(self, nid: str) -> list[str]:
        """Node ids from the root down to ``nid``."""
        ids = [nid]
        while ids[-1] in self.parent:
            ids.append(self.parent[ids[-1]])
        return ids[::-1]

    def path_mobjects(self, nid: str) -> VGroup:
        """Nodes, edges and edge labels along the path to ``nid``."""
        ids = self.path_ids(nid)
        mobs = [self.nodes[i] for i in ids]
        for cid in ids[1:]:
            mobs.append(self.edges[cid])
            if cid in self.edge_labels:
                mobs.append(self.edge_labels[cid])
        return VGroup(*mobs)

    def off_path_mobjects(self, nid: str) -> VGroup:
        on = set(map(id, self.path_mobjects(nid)))
        return VGroup(*[m for m in self.submobjects if id(m) not in on])

    # --- Layout / animation helpers -----------------------------------------

    def move_root_to(self, point) -> "TreeDiagram":
        self.shift(point - self.nodes[self.root_id].get_center())
        return self

    def light_edge(self, cid: str, color=HIGHLIGHT, width: float = 6) -> list:
        """Animations that recolor the edge into ``cid`` (and its label)."""
        anims = [self.edges[cid].animate.set_stroke(color=color, width=width)]
        if cid in self.edge_labels:
            anims.append(self.edge_labels[cid].animate.set_color(color))
        return anims

    def create_animation(self, lag_ratio: float = 0.35) -> LaggedStart:
        """Grow the tree level by level: edges, labels, then nodes."""
        max_depth = max(self.node_depth.values())
        levels = []
        for d in range(max_depth + 1):
            ids = [i for i, dd in self.node_depth.items() if dd == d]
            anims = [GrowFromCenter(self.nodes[i]) for i in ids]
            anims += [Create(self.edges[i]) for i in ids if i in self.edges]
            anims += [FadeIn(self.edge_labels[i]) for i in ids if i in self.edge_labels]
            levels.append(AnimationGroup(*anims))
        return LaggedStart(*levels, lag_ratio=lag_ratio)
