"""Scene 7: Trees in two dimensions, the signature shot (docs/STORYBOARD.md, rows 7.1-7.17).

Left: the 2D toy data on a PartitionedPlane. Right: the depth-3 tree, grown node by
node in sync with its cuts. Every number (points, thresholds, counts, boxes, the
root-cut IG sweep, the staircase) comes from data/toy2d.json and data/tree2d_extra.json.
"""

import json
from pathlib import Path

from manim import (
    AnimationGroup,
    Circle,
    Create,
    DashedLine,
    DecimalNumber,
    FadeIn,
    FadeOut,
    FadeTransform,
    Flash,
    GrowFromCenter,
    Indicate,
    LaggedStart,
    MathTex,
    ReplacementTransform,
    Star,
    Succession,
    Text,
    Transform,
    ValueTracker,
    VGroup,
    Write,
    there_and_back,
)
from manim_voiceover import VoiceoverScene

from components.partitioned_plane import Z_CUT, Z_TOP, PartitionedPlane
from components.tree_diagram import TreeDiagram
from style import *
from voice import speech_service

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TOY = json.loads((DATA_DIR / "toy2d.json").read_text())
EXTRA = json.loads((DATA_DIR / "tree2d_extra.json").read_text())

TREE3 = next(t for t in TOY["trees"] if t["max_depth"] == 3)
TREE5 = next(t for t in TOY["trees"] if t["max_depth"] == 5)
NODES = TREE3["nodes"]
BOXES = {b["node"]: b["box"] for b in EXTRA["depth3_node_boxes"]}
SEGMENTS = {s["node"]: s for s in TREE3["segments"]}
SWEEPS = EXTRA["root_sweep"]  # [x1 sweep, x2 sweep]
TEST = EXTRA["test_point"]

PLANE_CENTER = LEFT * 3.35 + DOWN * 0.2
TREE_ROOT = RIGHT * 3.4 + UP * 2.6
TREE_MAX_WIDTH = 6.4
LEGEND_POS = RIGHT * 3.4 + DOWN * 2.75
FEATURE_NAMES = ["x₁", "x₂"]  # x1, x2 for node labels
DEPTH2_DEMO = 5  # the depth-2 node used in 7.10
TIE_LEAF = next(n["id"] for n in NODES if n["leaf"] and n["counts"][0] == n["counts"][1])


def label(text, size=CAPTION_SIZE, color=TEXT, **kwargs):
    return Text(text, font=FONT, font_size=size, color=color, **kwargs)


def fmt(v):
    return f"{v:.2f}".replace("-", "−")  # typographic minus


def counts_text(counts):
    return f"{counts[0]}/{counts[1]}"


def tree_spec(i=0):
    """depth-3 sklearn tree -> TreeDiagram spec. sklearn's left child is the True branch ('yes')."""
    n = NODES[i]
    if n["leaf"]:
        return {"id": str(i), "leaf": counts_text(n["counts"])}
    return {
        "id": str(i),
        "q": f"{FEATURE_NAMES[n['feature']]} ≤ {fmt(n['threshold'])}",
        "yes": tree_spec(n["left"]),
        "no": tree_spec(n["right"]),
    }


def colored_counts(counts, size=CAPTION_SIZE * 0.8):
    a = label(str(counts[0]), size, CLASS_0)
    s = label("/", size, TEXT_MUTED)
    b = label(str(counts[1]), size, CLASS_1)
    return VGroup(a, s, b).arrange(RIGHT, buff=0.08)


class Trees2D(VoiceoverScene):
    def construct(self):
        self.set_speech_service(speech_service())

        plane = PartitionedPlane(TOY).move_to(PLANE_CENTER)
        plane_rest = VGroup(plane.frame, plane.ticks, plane.tick_labels)

        leaf_colors = {counts_text(n["counts"]): (CLASS_0, CLASS_1)[n["prediction"]] for n in NODES if n["leaf"]}
        tree = TreeDiagram(tree_spec(), font_size=20, level_gap=1.2, h_gap=0.12, leaf_colors=leaf_colors)
        if tree.width > TREE_MAX_WIDTH:
            tree.scale_to_fit_width(TREE_MAX_WIDTH)
        tree.move_root_to(TREE_ROOT)

        def tnode(i):
            return tree.node(str(i))

        def outline(nid, color, width):
            """Recolor a node's box outline. Transform the whole node so its text stays on top."""
            node = tree.node(str(nid))
            target = node.copy()
            target[0].set_stroke(color, width)
            return Transform(node, target)

        def tedge(i):
            group = VGroup(tree.edges[str(i)])
            if str(i) in tree.edge_labels:
                group.add(tree.edge_labels[str(i)])
            return group

        # 7.1
        with self.voiceover(text="Here's where trees get their signature look.") as tracker:
            self.play(Create(plane_rest), Write(plane.x_label), Write(plane.y_label), run_time=tracker.duration)

        # 7.2
        feat1 = label("feature 1", CAPTION_SIZE * 0.8, TEXT_MUTED).next_to(plane.x_label, RIGHT, buff=0.15)
        feat2 = label("feature 2", CAPTION_SIZE * 0.8, TEXT_MUTED).next_to(plane.y_label, RIGHT, buff=0.15)
        legend = VGroup(
            *[
                VGroup(Circle(radius=0.08).set_fill(c, 1).set_stroke(width=0), label(name, CAPTION_SIZE * 0.8)).arrange(
                    RIGHT, buff=0.15
                )
                for c, name in ((CLASS_0, "class 0"), (CLASS_1, "class 1"))
            ]
        ).arrange(RIGHT, buff=0.6)
        legend.move_to(LEGEND_POS)
        with self.voiceover(
            text="Now each example has two measurements, which machine learning calls features, "
            "and belongs to one of two categories, or classes."
        ) as tracker:
            d = tracker.duration
            self.play(FadeIn(feat1), FadeIn(feat2), run_time=0.15 * d)
            self.play(
                LaggedStart(*[FadeIn(dot, scale=0.5) for dot in plane.class_dots[0]], lag_ratio=0.02),
                run_time=0.35 * d,
            )
            self.play(
                LaggedStart(*[FadeIn(dot, scale=0.5) for dot in plane.class_dots[1]], lag_ratio=0.02),
                run_time=0.35 * d,
            )
            self.play(FadeIn(legend, shift=UP * 0.2), run_time=0.15 * d)

        # 7.3
        overlap = Circle(radius=1.0).set_fill(HIGHLIGHT, 0.2).set_stroke(HIGHLIGHT, 2, opacity=0.5)
        overlap.move_to(plane.c2p(*EXTRA["overlap"]["center"]))
        overlap.stretch_to_fit_width(abs(plane.c2p(EXTRA["overlap"]["radius"], 0)[0] - plane.c2p(0, 0)[0]) * 2)
        overlap.stretch_to_fit_height(abs(plane.c2p(0, EXTRA["overlap"]["radius"])[1] - plane.c2p(0, 0)[1]) * 2)
        overlap.set_z_index(Z_TOP)
        with self.voiceover(text="There are two hundred points in two overlapping clouds.") as tracker:
            self.play(FadeIn(overlap, scale=0.6), run_time=0.4 * tracker.duration)
        self.play(FadeOut(overlap), FadeOut(feat1), FadeOut(feat2), run_time=FAST)

        # 7.4
        qmark = label("?", 96, HIGHLIGHT).move_to(TREE_ROOT + DOWN * 1.6)
        with self.voiceover(text="What does a question look like here?") as tracker:
            self.play(FadeIn(qmark, shift=DOWN * 0.2), run_time=min(NORMAL, tracker.duration))

        # 7.5
        root = NODES[0]
        question = MathTex(
            rf"x_{root['feature'] + 1} \le {root['threshold']:.2f}\,?", color=TEXT, font_size=BODY_SIZE + 8
        ).move_to(TREE_ROOT)
        with self.voiceover(
            text="Each question still looks at just one feature and compares it to a number."
        ) as tracker:
            self.play(FadeOut(qmark), Write(question), run_time=0.6 * tracker.duration)

        # 7.6
        demo_h = plane.h_line(SWEEPS[1]["thresholds"][len(SWEEPS[1]["thresholds"]) * 3 // 4])
        demo_v = plane.v_line(SWEEPS[0]["thresholds"][len(SWEEPS[0]["thresholds"]) // 4])
        demo = VGroup(
            *[
                DashedLine(m.get_start(), m.get_end(), color=HIGHLIGHT, stroke_width=4).set_z_index(Z_CUT)
                for m in (demo_h, demo_v)
            ]
        )
        with self.voiceover(
            text="In the plane, that means a straight cut, either horizontal or vertical."
        ) as tracker:
            d = tracker.duration
            self.play(Create(demo[0]), run_time=0.3 * d)
            self.play(Create(demo[1]), run_time=0.3 * d)
        self.play(FadeOut(demo), run_time=FAST)

        # 7.7 (split 1/2): the sweep
        idx = ValueTracker(0)
        axis = {"f": 0}

        def ghost_line():
            s = SWEEPS[axis["f"]]
            t = s["thresholds"][int(round(idx.get_value()))]
            line = plane.v_line(t) if axis["f"] == 0 else plane.h_line(t)
            return line.set_stroke(HIGHLIGHT, 4, opacity=0.6)

        ghost = ghost_line()
        ghost.add_updater(lambda m: m.become(ghost_line()))

        ig_label = label("information gain", CAPTION_SIZE, TEXT_MUTED)
        ig_value = DecimalNumber(0, num_decimal_places=3, color=TEXT, font_size=BODY_SIZE)
        ig_value.add_updater(lambda m: m.set_value(SWEEPS[axis["f"]]["ig"][int(round(idx.get_value()))]))
        readout = VGroup(ig_label, ig_value).arrange(RIGHT, buff=0.25)
        readout.move_to([plane.frame.get_center()[0], 3.35, 0])
        ig_value.add_updater(lambda m: m.next_to(ig_label, RIGHT, buff=0.25))

        with self.voiceover(text="The tree tries every cut on both axes, scores each one, and keeps the winner:") as tracker:
            d = tracker.duration
            n0, n1 = len(SWEEPS[0]["thresholds"]), len(SWEEPS[1]["thresholds"])
            self.play(FadeIn(ghost), FadeIn(readout), run_time=0.08 * d)
            self.play(idx.animate.set_value(n0 - 1), run_time=0.42 * d, rate_func=lambda t: t)
            axis["f"] = 1
            idx.set_value(0)
            self.play(idx.animate.set_value(n1 - 1), run_time=0.42 * d, rate_func=lambda t: t)

        # 7.7 (split 2/2): lock on the winner
        best_idx = SWEEPS[1]["thresholds"].index(min(SWEEPS[1]["thresholds"], key=lambda t: abs(t - root["threshold"])))
        root_cut = plane.segment(SEGMENTS[0]["start"], SEGMENTS[0]["end"], color=GAIN, stroke_width=5)
        with self.voiceover(text="is x₂ at most about 1.2?") as tracker:
            d = tracker.duration
            self.play(idx.animate.set_value(best_idx), run_time=0.45 * d)
            ghost.clear_updaters()
            ig_value.clear_updaters()
            self.play(
                ReplacementTransform(ghost, root_cut),
                ig_value.animate.set_color(GAIN),
                run_time=0.2 * d,
            )
            self.play(Flash(root_cut.get_center(), color=GAIN, flash_radius=0.5), run_time=0.3 * d)

        # 7.8: halves tint, the question becomes the root node, counts appear
        regions = {}
        for i in (root["left"], root["right"]):
            regions[i] = plane.region(BOXES[i], NODES[i]["prediction"])
        child_counts = {
            i: colored_counts(NODES[i]["counts"]).move_to(tnode(i)) for i in (root["left"], root["right"])
        }
        with self.voiceover(
            text="That one horizontal line already separates most of the blue from most of the yellow."
        ) as tracker:
            d = tracker.duration
            self.play(
                AnimationGroup(
                    FadeIn(regions[root["left"]]),
                    FadeIn(regions[root["right"]]),
                    FadeTransform(question, tnode(0)),
                    root_cut.animate.set_stroke(GRID, 3),
                    FadeOut(readout),
                ),
                run_time=0.4 * d,
            )
            self.play(
                *[Create(tedge(i)) for i in child_counts],
                *[FadeIn(c, shift=DOWN * 0.15) for c in child_counts.values()],
                run_time=0.3 * d,
            )

        # 7.9: depth-2 and depth-3 cuts, synced with the internal nodes
        cuts = {0: root_cut}
        internal = [n["id"] for n in sorted(NODES, key=lambda n: (n["depth"], n["id"])) if not n["leaf"] and n["id"]]
        with self.voiceover(text="Then each half gets its own question, and each of those gets another.") as tracker:
            step = tracker.duration / len(internal)
            for i in internal:
                n = NODES[i]
                seg = SEGMENTS[i]
                cuts[i] = plane.segment(seg["start"], seg["end"], color=GRID, stroke_width=3)
                kids = (n["left"], n["right"])
                new = {k: plane.region(BOXES[k], NODES[k]["prediction"]) for k in kids}
                parent_rect = regions.pop(i)
                anims = [
                    Create(cuts[i]),
                    ReplacementTransform(parent_rect, new[kids[0]]),
                    ReplacementTransform(parent_rect.copy(), new[kids[1]]),
                ]
                if i in child_counts:
                    anims.append(FadeOut(child_counts.pop(i), scale=0.6))
                    anims.append(GrowFromCenter(tnode(i)))
                else:
                    anims += [Create(tedge(i)), GrowFromCenter(tnode(i))]
                self.play(*anims, run_time=step)
                regions.update(new)

        # 7.10: one depth-2 cut lives inside its parent's region
        parent_id = next(n["id"] for n in NODES if not n["leaf"] and DEPTH2_DEMO in (n["left"], n["right"]))
        parent_outline = plane.box_rect(BOXES[parent_id], opacity=0, stroke_width=6).set_stroke(HIGHLIGHT)
        parent_outline.set_z_index(Z_TOP)
        with self.voiceover(
            text="Every node in the tree is a cut in the plane, and every cut lives only inside its parent's region."
        ) as tracker:
            d = tracker.duration
            self.play(
                outline(DEPTH2_DEMO, HIGHLIGHT, 4),
                Indicate(cuts[DEPTH2_DEMO], color=HIGHLIGHT, scale_factor=1.0),
                cuts[DEPTH2_DEMO].animate.set_stroke(HIGHLIGHT, 5),
                run_time=0.35 * d,
            )
            self.play(Create(parent_outline), outline(parent_id, HIGHLIGHT, 4), run_time=0.35 * d)
        self.play(
            FadeOut(parent_outline),
            cuts[DEPTH2_DEMO].animate.set_stroke(GRID, 3),
            *[outline(i, TEXT_MUTED, 2) for i in (DEPTH2_DEMO, parent_id)],
            run_time=FAST,
        )

        # 7.11: eight leaves, eight rectangles
        leaf_ids = [lf["node"] for lf in TREE3["leaves"]]
        tie_label = label("tie", CAPTION_SIZE * 0.7, TEXT_MUTED).next_to(tnode(TIE_LEAF), DOWN, buff=0.1)
        with self.voiceover(
            text="Three questions deep, we have eight leaves, which means eight rectangles."
        ) as tracker:
            d = tracker.duration
            grow = 0.35 * d
            self.play(
                LaggedStart(*[AnimationGroup(Create(tedge(i)), GrowFromCenter(tnode(i))) for i in leaf_ids], lag_ratio=0.15),
                FadeIn(tie_label),
                run_time=grow,
            )
            pair = min(0.4, (d - grow) / len(leaf_ids))
            for i in leaf_ids:
                self.play(
                    Indicate(tnode(i), color=tnode(i)[0].get_fill_color(), scale_factor=1.2),
                    regions[i].animate(rate_func=there_and_back).set_fill(opacity=0.6),
                    run_time=pair,
                )

        # 7.12: majority color per box; same-color neighbors merge
        region_group = VGroup(*[regions[i] for i in leaf_ids])
        with self.voiceover(text="Inside each one, the tree predicts whichever color holds the majority.") as tracker:
            self.play(
                region_group.animate.set_fill(opacity=0.3),
                *[FadeOut(c) for c in cuts.values()],
                run_time=0.5 * tracker.duration,
            )

        # 7.13: a test point falls through the tree
        star = Star(n=5, outer_radius=0.16, color=TEXT).set_fill(TEXT, 1).set_z_index(Z_TOP)
        star.move_to(plane.c2p(*TEST["x"]))
        path = [str(i) for i in TEST["path"]]
        with self.voiceover(
            text="So a decision tree is really a way of carving space into boxes, always with cuts parallel to the axes."
        ) as tracker:
            d = tracker.duration
            self.play(FadeIn(star, shift=DOWN * 0.5), run_time=0.15 * d)
            self.play(
                Succession(
                    outline(0, HIGHLIGHT, 4),
                    *[
                        AnimationGroup(*tree.light_edge(c), outline(c, HIGHLIGHT, 4))
                        for c in path[1:-1]
                    ],
                    AnimationGroup(
                        *tree.light_edge(path[-1]),
                        Indicate(tree.node(path[-1]), color=tree.node(path[-1])[0].get_fill_color(), scale_factor=1.3),
                    ),
                ),
                run_time=0.5 * d,
            )
            self.play(
                regions[TEST["leaf"]].animate(rate_func=there_and_back).set_fill(opacity=0.7),
                Indicate(star, color=TEXT, scale_factor=1.4),
                run_time=0.3 * d,
            )

        # 7.14
        with self.voiceover(text="Notice the price of that.") as tracker:
            self.play(tree.animate.set_opacity(DIM_OPACITY), FadeOut(star), FadeOut(tie_label), run_time=0.8 * tracker.duration)

        # 7.15: the diagonal vs. the staircase
        line = TOY["article_line"]
        diagonal = DashedLine(plane.c2p(*line["from"]), plane.c2p(*line["to"]), color=TEXT, stroke_width=4)
        diagonal.set_z_index(Z_TOP)
        stairs3 = plane.boundary(EXTRA["boundary"]["depth3"], color=HIGHLIGHT, stroke_width=5)
        with self.voiceover(
            text="The natural boundary between these clouds is a diagonal line, "
            "and the best a tree can do is approximate it with a staircase."
        ) as tracker:
            d = tracker.duration
            self.play(Create(diagonal), run_time=0.35 * d)
            self.play(Create(stairs3), run_time=0.35 * d)
            self.play(Indicate(stairs3, color=HIGHLIGHT, scale_factor=1.0), run_time=0.25 * d)

        # 7.16: deeper = finer steps (preview, then back)
        regions5 = plane.leaf_regions(TREE5, opacity=0.3)
        stairs5 = plane.boundary(EXTRA["boundary"]["depth5"], color=HIGHLIGHT, stroke_width=5)
        depth_tag = label(f"depth {TREE5['max_depth']}", CAPTION_SIZE, HIGHLIGHT)
        depth_tag.next_to(plane.frame, UP, buff=0.2)
        with self.voiceover(text="More depth means finer steps, which sounds like a fix.") as tracker:
            d = tracker.duration
            self.play(
                FadeTransform(region_group, regions5),
                FadeTransform(stairs3, stairs5),
                FadeIn(depth_tag),
                run_time=0.3 * d,
            )
            self.wait(0.3 * d)
            region_back = plane.leaf_regions(TREE3, opacity=0.3)
            stairs_back = plane.boundary(EXTRA["boundary"]["depth3"], color=HIGHLIGHT, stroke_width=5)
            self.play(
                FadeTransform(regions5, region_back),
                FadeTransform(stairs5, stairs_back),
                FadeOut(depth_tag),
                run_time=0.3 * d,
            )

        # 7.17: hard cut
        with self.voiceover(text="It's actually a trap.") as tracker:
            self.wait(0.6 * tracker.duration)
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.3)
