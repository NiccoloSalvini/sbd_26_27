"""Lecture 12 clips, rewritten on 2 Nov 2026 to the rules of lecture 11: one
caption slot, a right-hand panel with a fixed left edge, every number on screen
computed here. Same class names as in scenes.py, which these replace.

Render one:  .venv/bin/manim -qm --disable_caching scenes_12.py Dendrogram
"""
from scenes import *
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.sparse.csgraph import minimum_spanning_tree

CORAL = "#e2725b"
MAUVE = "#c98bb9"
AXIS = {"color": MUTED, "include_tip": False, "stroke_width": 1.4}


def complete_steps(names, dist):
    """Agglomerative clustering, complete linkage, the way the by-hand slide does it.
    One entry per merge: the clusters before it, their distance table, the pair
    merged (i < j, by position) and its height. The merged cluster takes slot i."""
    clusters = [[n] for n in names]
    steps = []
    while len(clusters) > 1:
        D = {(i, j): max(dist(a, b) for a in clusters[i] for b in clusters[j])
             for i in range(len(clusters)) for j in range(i + 1, len(clusters))}
        (i, j), h = min(D.items(), key=lambda kv: (kv[1], kv[0]))
        steps.append({"clusters": [list(c) for c in clusters], "D": D, "i": i, "j": j, "h": h})
        merged = clusters[i] + clusters[j]
        clusters = [c for k, c in enumerate(clusters) if k not in (i, j)]
        clusters.insert(i, merged)
    return steps


def set_name(members):
    return "{" + ", ".join(map(str, members)) + "}"


# ================================================================ Dendrogram
class Dendrogram(Stage):
    """The five patients of the by-hand slide (length of stay 2, 3, 6, 10, 11 days),
    merged with complete linkage. The right panel is the distance table: the
    smallest entry is merged, the table shrinks, and the merged group's new
    distances are the larger of the two old ones. The tree on the left grows
    from the heights that result (1, 1, 4, 9), then is cut twice."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        slot = np.array([0, -3.3, 0])
        xpos = {v: k + 1 for k, v in enumerate(STAY)}
        ax = Axes(x_range=[0, len(STAY) + 1, 1], y_range=[0, 10, 2], x_length=5.4, y_length=4.4,
                  axis_config=AXIS, x_axis_config={"include_ticks": False}).to_edge(LEFT, buff=1.3).shift(UP * 0.5)
        ynum = VGroup(*[label(str(v), 20, MUTED).next_to(ax.c2p(0, v), LEFT, buff=0.15) for v in range(0, 11, 2)])
        ytitle = label("merge height (days)", 22, MUTED).rotate(PI / 2).next_to(ynum, LEFT, buff=0.2)
        self.play(Create(ax), FadeIn(ynum), FadeIn(ytitle), run_time=1.0)

        dots, names = {}, {}
        for v in STAY:
            dots[v] = Dot(ax.c2p(xpos[v], 0), radius=0.08, color=CREAM)
            names[v] = label(str(v), 24, CREAM).next_to(dots[v], DOWN, buff=0.15)
        xtitle = label("five patients: length of stay (days)", 22, MUTED).next_to(ax, DOWN, buff=0.62)
        self.play(FadeIn(VGroup(*dots.values()), lag_ratio=0.15), FadeIn(VGroup(*names.values()), lag_ratio=0.15),
                  FadeIn(xtitle), run_time=1.2)
        self.caption(label("five patients, by length of stay: 2, 3, 6, 10 and 11 days", 26).move_to(slot))
        self.wait(2.4)

        # the right panel: the rule, then the distance table
        COL, TOP = 1.0, 1.75
        rule_name = label("complete linkage", 24, SKY).move_to([0, 3.25, 0]).align_to([COL, 0, 0], LEFT)
        rule = MathTex(r"d(A,B) = \max_{a \in A,\; b \in B} |a-b|", color=CREAM, font_size=32)
        rule.next_to(rule_name, DOWN, buff=0.22).align_to([COL, 0, 0], LEFT)
        self.play(FadeIn(rule_name), FadeIn(rule), run_time=0.8)
        self.caption(label("two groups are as far apart as their farthest pair of patients", 26).move_to(slot))
        self.wait(2.6)

        RW, CW, RH = 1.3, 1.05, 0.62

        def table(clusters, D, fresh=None):
            g, cells = VGroup(), {}
            nm = [",".join(map(str, c)) for c in clusters]
            for c in range(len(clusters) - 1):
                g.add(label(nm[c], 22, MUTED).move_to([COL + RW + CW * (c + 0.5), TOP, 0]))
            for r in range(1, len(clusters)):
                y = TOP - RH * r
                g.add(label(nm[r], 22, MUTED).move_to([0, y, 0]).align_to([COL, 0, 0], LEFT))
                for c in range(r):
                    col = SKY if fresh is not None and fresh in (c, r) else CREAM
                    m = label(f"{D[(c, r)]:g}", 26, col).move_to([COL + RW + CW * (c + 0.5), y, 0])
                    cells[(c, r)] = m
                    g.add(m)
            return g, cells

        steps = complete_steps(STAY, lambda a, b: abs(a - b))
        tab, cells = table(steps[0]["clusters"], steps[0]["D"])
        self.play(FadeIn(tab, lag_ratio=0.05), run_time=1.2)
        self.caption(label("the table: every distance between two patients, in days", 26).move_to(slot))
        self.wait(2.8)

        # the tree, one merge per step; node = members tuple -> x, height, own lines
        node = {(v,): {"x": xpos[v], "h": 0.0, "lines": VGroup(), "kids": []} for v in STAY}
        note = None
        last_lines = None
        for s, st in enumerate(steps):
            A, B, h = st["clusters"][st["i"]], st["clusters"][st["j"]], st["h"]
            box = SurroundingRectangle(cells[(st["i"], st["j"])], color=GOLD, buff=0.1, stroke_width=3)
            first = "smallest" if s == 0 else ("next smallest" if s == 1 else "smallest")
            who = (f"patients {A[0]} and {B[0]}" if len(A) == len(B) == 1
                   else f"{set_name(A)} and {set_name(B)}")
            if s == len(steps) - 1:
                text = f"one distance left, {h:g}: the last merge, at height {h:g}"
            else:
                text = f"{first} distance: {h:g}, between {who}. Merge them"
            self.play(Create(box), run_time=0.6)
            self.caption(label(text, 26).move_to(slot))
            self.wait(1.6)

            a, b = node[tuple(A)], node[tuple(B)]
            la = Line(ax.c2p(a["x"], a["h"]), ax.c2p(a["x"], h), color=GOLD, stroke_width=3)
            lb = Line(ax.c2p(b["x"], b["h"]), ax.c2p(b["x"], h), color=GOLD, stroke_width=3)
            bar = Line(ax.c2p(a["x"], h), ax.c2p(b["x"], h), color=GOLD, stroke_width=3)
            hl = label(f"{h:g}", 22, GOLD).next_to(ax.c2p(min(a["x"], b["x"]), h), LEFT, buff=0.1)
            anims = [Create(la), Create(lb)]
            if last_lines is not None:
                anims.append(last_lines.animate.set_color(CREAM))
            self.play(*anims, run_time=0.7)
            self.play(Create(bar), FadeIn(hl), run_time=0.6)
            own = VGroup(la, lb, bar)
            last_lines = VGroup(own, hl)
            node[tuple(A + B)] = {"x": (a["x"] + b["x"]) / 2, "h": h, "lines": own, "kids": [tuple(A), tuple(B)]}
            self.wait(1.0)

            if s == len(steps) - 1:
                self.play(FadeOut(box), FadeOut(tab), run_time=0.6)
                break

            # the next table: the merged group's distances are the larger of the two
            nxt = steps[s + 1]
            k = st["i"]
            others = [c for c in range(len(nxt["clusters"])) if c != k]
            o = min(others, key=lambda c: nxt["D"][tuple(sorted((c, k)))])
            other = nxt["clusters"][o]
            da = max(abs(x - y) for x in A for y in other)
            db = max(abs(x - y) for x in B for y in other)
            new_note = MathTex(rf"d(\{{{','.join(map(str, A + B))}\}},\ \{{{','.join(map(str, other))}\}})"
                               rf" = \max({da:g},\,{db:g}) = {max(da, db):g}", color=SKY, font_size=32)
            new_note.move_to([0, -1.75, 0]).align_to([COL, 0, 0], LEFT)
            tab2, cells2 = table(nxt["clusters"], nxt["D"], fresh=k)
            anims = [FadeOut(box), FadeTransform(tab, tab2)]
            anims.append(FadeIn(new_note) if note is None else FadeTransform(note, new_note))
            if s == 0:
                self.caption(label("complete linkage: the new group's distance is the larger of the two", 26).move_to(slot))
            self.play(*anims, run_time=1.0)
            tab, cells, note = tab2, cells2, new_note
            self.wait(2.4 if s == 0 else 1.8)

        self.play(last_lines.animate.set_color(CREAM), FadeOut(note), run_time=0.6)
        self.caption(label("four merges, at heights 1, 1, 4 and 9: that record is the dendrogram", 26).move_to(slot))
        self.wait(2.6)

        def subtree(key):
            n = node[key]
            g = VGroup(n["lines"])
            for kid in n["kids"]:
                g.add(subtree(kid))
            return g

        def groups_at(hcut):
            out = []
            for key, n in node.items():
                parent = [p for p, m in node.items() if key in m["kids"]]
                if n["h"] < hcut and (not parent or node[parent[0]]["h"] > hcut):
                    out.append(key)
            return sorted(out, key=lambda key: key[0])

        everything = VGroup(*[n["lines"] for n in node.values()])
        panel = None
        cut_line = None
        for hcut, cols, words in ((5, [GOLD, SKY], ["short stays", "long stays"]),
                                  (2, [GOLD, MAUVE, SKY], None)):
            gs = groups_at(hcut)
            line = DashedLine(ax.c2p(0, hcut), ax.c2p(len(STAY) + 1, hcut), color=CREAM, stroke_width=2.5)
            head = label(f"cut at height {hcut}: {len(gs)} groups", 26, CREAM)
            rows = [head]
            for g, c in zip(gs, cols):
                txt = set_name(g) + (f"   {words[gs.index(g)]}" if words else "")
                rows.append(label(txt, 26, c))
            new_panel = VGroup(*rows).arrange(DOWN, buff=0.38, aligned_edge=LEFT)
            new_panel.align_to([COL, 0, 0], LEFT).align_to([0, 1.95, 0], UP)

            anims = [everything.animate.set_color(CREAM)]
            anims += [Create(line)] if cut_line is None else [Transform(cut_line, line)]
            self.play(*anims, run_time=1.0)
            if cut_line is None:
                cut_line = line
            colour_anims = []
            for g, c in zip(gs, cols):
                colour_anims += [subtree(g).animate.set_color(c)]
                colour_anims += [dots[v].animate.set_color(c) for v in g] + [names[v].animate.set_color(c) for v in g]
            colour_anims.append(FadeIn(new_panel) if panel is None else FadeTransform(panel, new_panel))
            self.play(*colour_anims, run_time=1.0)
            panel = new_panel
            if hcut == 5:
                text = "cut at 5: two groups, the short stays and the long stays"
            else:
                text = "cut at 2: three groups. The same tree answers a different question"
            self.caption(label(text, 26).move_to(slot))
            self.wait(3.4)

        self.caption(label("k was never an input. You choose it where you cut.", 28, GOLD).move_to(slot))
        self.wait(3.4)


# ================================================================ LinkageFour
class LinkageFour(Stage):
    """Forty-one hospitals: 16 small, 16 large and 9 mid-sized ones in between.
    Single linkage merges the nearest pair, and the mid-sized hospitals carry it
    from one kind to the other: cut at k = 2 it returns 40 hospitals and 1. The
    other three linkages part small from large. Merge numbers, heights, group
    sizes and the k at which single linkage finally separates them are computed."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        rng = np.random.default_rng(26)
        nb = 9
        small = np.column_stack([rng.normal(1.2, 0.5, 16), rng.normal(2, 0.5, 16)])
        large = np.column_stack([rng.normal(9.0, 0.5, 16), rng.normal(2, 0.5, 16)])
        mid = np.column_stack([np.linspace(2.4, 7.8, nb), np.full(nb, 2.0) + rng.normal(0, 0.12, nb)])
        P = np.vstack([small, large, mid])
        kind = np.array([0] * 16 + [1] * 16 + [2] * nb)
        n = len(P)

        slot = np.array([0, -3.25, 0])
        Q = P + np.array([1.0, 0.0])          # drawn one unit right, so every point sits inside the axes
        ax = Axes(x_range=[0, 12, 2], y_range=[0, 4.2, 1], x_length=6.6, y_length=4.0,
                  axis_config={**AXIS, "include_ticks": False}).to_edge(LEFT, buff=0.8).shift(UP * 0.45)
        xt = label("size: beds (scaled)", 22, MUTED).next_to(ax, DOWN, buff=0.25)
        yt = label("case mix (scaled)", 22, MUTED).rotate(PI / 2).next_to(ax, LEFT, buff=0.2)
        self.play(Create(ax), FadeIn(xt), FadeIn(yt), run_time=1.0)
        dots = VGroup(*[Dot(ax.c2p(*q), radius=0.06, color=MUTED) for q in Q])
        self.play(FadeIn(dots, lag_ratio=0.02), run_time=1.4)
        self.caption(label(f"{n} hospitals: 16 small, 16 large, and {nb} mid-sized ones in between", 26).move_to(slot))
        self.wait(3.0)

        # single linkage = the minimum spanning tree's edges, shortest first
        D = np.sqrt(((P[:, None] - P[None]) ** 2).sum(-1))
        T = minimum_spanning_tree(D).tocoo()
        edges = sorted(zip(T.data, T.row, T.col))
        Z = linkage(P, "single")
        assert np.allclose([e[0] for e in edges], Z[:, 2])

        parent = list(range(n))

        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        joined = None                      # first merge that puts a small and a large hospital together
        for m, (_, i, j) in enumerate(edges):
            parent[find(i)] = find(j)
            roots_small = {find(k) for k in range(16)}
            roots_large = {find(k) for k in range(16, 32)}
            if joined is None and roots_small & roots_large:
                joined = m
        first_mid = next(m for m, (_, i, j) in enumerate(edges) if kind[i] == 2 and kind[j] == 2)
        batches = [(0, first_mid), (first_mid, joined + 1), (joined + 1, n - 2), (n - 2, n - 1)]

        COL = 1.0
        lines = [Line(ax.c2p(*Q[i]), ax.c2p(*Q[j]), color=CORAL, stroke_width=2.6) for _, i, j in edges]

        self.caption(label("single linkage: two groups are as close as their nearest pair", 26).move_to(slot))
        self.wait(2.4)

        counter = None
        texts = [
            "merges {a} to {b}: the short distances, mostly inside each kind",
            "merges {a} to {b}: one mid-sized hospital to the next, and small meets large",
            "merges {a} to {b}: the last outlying hospitals of each kind",
            "merge {b}, the last and the longest: one large hospital on its own",
        ]
        for (a, b), text in zip(batches, texts):
            hs = [edges[m][0] for m in range(a, b)]
            self.caption(label(text.format(a=a + 1, b=b), 26).move_to(slot))
            c1 = label(f"merge {b} of {n - 1}", 26, CREAM)
            c2 = label(f"height {hs[-1]:.2f}", 26, CORAL)
            new_counter = VGroup(c1, c2).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
            new_counter.move_to([0, 2.3, 0]).align_to([COL, 0, 0], LEFT)
            rt = 3.2 if b - a > 10 else (2.4 if b - a > 1 else 1.2)
            anims = [Create(VGroup(*lines[a:b]), lag_ratio=0.6 if b - a > 1 else 0, run_time=rt)]
            anims.append(FadeIn(new_counter) if counter is None else FadeTransform(counter, new_counter))
            self.play(*anims)
            counter = new_counter
            self.wait(1.8)

        lab1 = fcluster(Z, 2, "maxclust")
        sizes = np.bincount(lab1)[1:]
        big = np.argmax(sizes) + 1
        stray = int(np.where(lab1 != big)[0][0])
        ring = Circle(radius=0.17, color=GOLD, stroke_width=3).move_to(dots[stray])

        head = label("cut at k = 2: group sizes", 24, MUTED).move_to([0, 2.55, 0]).align_to([COL, 0, 0], LEFT)
        ROW0, DY = 1.85, 0.62

        def row(r, name, a, b, ca, cb):
            y = ROW0 - DY * r
            nm = label(name, 26, CREAM).move_to([0, y, 0]).align_to([COL, 0, 0], LEFT)
            va = label(str(a), 26, ca).move_to([0, y, 0]).align_to([COL + 2.3, 0, 0], LEFT)
            plus = label("+", 26, MUTED).next_to(va, RIGHT, buff=0.18)
            vb = label(str(b), 26, cb).next_to(plus, RIGHT, buff=0.18)
            return VGroup(nm, va, plus, vb)

        r_single = row(0, "single", sizes.max(), sizes.min(), CORAL, GOLD)
        self.play(*[d.animate.set_color(CORAL if lab1[k] == big else GOLD) for k, d in enumerate(dots)],
                  Create(ring), FadeTransform(counter, head), run_time=1.0)
        self.play(FadeIn(r_single, shift=RIGHT * 0.15), run_time=0.6)
        self.caption(label(f"cut at k = 2: a group of {sizes.max()}, and one stray hospital", 26).move_to(slot))
        self.wait(3.0)

        ksep, singles = None, 0
        for k in range(2, n):
            lab = fcluster(Z, k, "maxclust")
            if not (set(lab[kind == 0]) & set(lab[kind == 1])):
                ksep, singles = k, int((np.bincount(lab)[1:] == 1).sum())
                break
        self.caption(label(f"single needs k = {ksep} to part small from large, and then {singles} groups "
                           f"are one hospital", 26).move_to(slot))
        self.wait(3.4)

        self.play(FadeOut(VGroup(*lines)), FadeOut(ring), dots.animate.set_color(MUTED), run_time=0.9)
        defs = [("complete", "complete: as far as the farthest pair. Small and large come apart"),
                ("average", "average: the mean of all pairs. Apart again"),
                ("ward", "Ward: the merge that adds the least spread. Apart again")]
        for r, (method, text) in enumerate(defs, start=1):
            lab = fcluster(linkage(P, method), 2, "maxclust")
            s_lab = lab[0]                                  # the group that holds the small hospitals
            a, b = int((lab == s_lab).sum()), int((lab != s_lab).sum())
            name = "Ward" if method == "ward" else method
            rr = row(r, name, a, b, GOLD, SKY)
            self.caption(label(text, 26).move_to(slot))
            self.play(*[d.animate.set_color(GOLD if lab[k] == s_lab else SKY) for k, d in enumerate(dots)], run_time=1.0)
            self.play(FadeIn(rr, shift=RIGHT * 0.15), run_time=0.6)
            self.wait(2.4)

        mids = VGroup(*[dots[k] for k in range(n) if kind[k] == 2])
        self.caption(label(f"they differ only on the {nb} mid-sized hospitals: that is the judgement call", 26).move_to(slot))
        self.play(Indicate(mids, color=CREAM, scale_factor=1.6), run_time=1.4)
        self.wait(2.0)
        self.play(r_single.animate.set_color(CORAL), run_time=0.4)
        self.caption(label("single linkage chained across them, and its output carries no warning", 26, GOLD).move_to(slot))
        self.wait(3.6)


# ================================================================ DendrogramRead
# Six hospitals: share of emergency admissions and share of patients over 75, in %.
HOSP = {"A": (22, 18), "B": (26, 20), "C": (33, 30), "D": (50, 36), "E": (57, 45), "F": (60, 42)}


def leaves(t):
    return [t] if isinstance(t, str) else leaves(t[0]) + leaves(t[1])


def members(t):
    return frozenset(leaves(t))


class DendrogramRead(Stage):
    """The misreading the deck calls the most common one, on six hospitals with
    real distances. C and D are drawn side by side; the scatter on the right shows
    C nearer to B than to D, and the tree joins C and D only at its top. Two flips
    move the neighbours, not the data, not a height. Then the reading that is
    right: the longest stretch with no merge is where to cut."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        slot = np.array([0, -3.3, 0])
        names = list(HOSP)
        P = {k: np.array(v, float) for k, v in HOSP.items()}
        dist = lambda a, b: float(np.linalg.norm(P[a] - P[b]))
        steps = complete_steps(names, dist)

        # nested tree from the merges: (left, right, height)
        sub = {frozenset([k]): k for k in names}
        order = []
        for st in steps:
            A, B = st["clusters"][st["i"]], st["clusters"][st["j"]]
            t = (sub[frozenset(A)], sub[frozenset(B)], st["h"])
            sub[frozenset(A + B)] = t
            order.append(t)
        root = order[-1]
        top = root[2]

        # left: the tree
        ax = Axes(x_range=[0, 7, 1], y_range=[0, 50, 10], x_length=5.4, y_length=4.4,
                  axis_config=AXIS, x_axis_config={"include_ticks": False}).to_edge(LEFT, buff=1.3).shift(UP * 0.5)
        ynum = VGroup(*[label(str(v), 20, MUTED).next_to(ax.c2p(0, v), LEFT, buff=0.15) for v in range(0, 51, 10)])
        ytitle = label("merge height", 22, MUTED).rotate(PI / 2).next_to(ynum, LEFT, buff=0.2)

        def draw(t):
            """Each piece keyed by the node it belongs to, not by where it is drawn:
            the vertical rising from a node, the bar of a merge, its height. A flip
            then swings every piece to its own new place."""
            x = {k: i + 1 for i, k in enumerate(leaves(t))}
            pos = {}

            def place(u):
                if isinstance(u, str):
                    pos[members(u)] = (x[u], 0.0)
                    return
                place(u[0]); place(u[1])
                pos[members(u)] = ((pos[members(u[0])][0] + pos[members(u[1])][0]) / 2, u[2])
            place(t)
            vert, bar, hlab = {}, {}, {}
            for u in [*names, *order]:                      # a fixed key order
                if members(u) == members(t):
                    continue
                parent = next(p for p in order if members(u) in (members(p[0]), members(p[1])))
                (xu, hu) = pos[members(u)]
                vert[members(u)] = Line(ax.c2p(xu, hu), ax.c2p(xu, parent[2]), color=CREAM, stroke_width=3)
            for u in order:
                (xa, _), (xb, _) = pos[members(u[0])], pos[members(u[1])]
                bar[members(u)] = Line(ax.c2p(xa, u[2]), ax.c2p(xb, u[2]), color=CREAM, stroke_width=3)
                hlab[members(u)] = label(f"{u[2]:.1f}", 20, GOLD).next_to(ax.c2p(min(xa, xb), u[2]), LEFT, buff=0.08)
            labs = {k: label(k, 24, CREAM).next_to(ax.c2p(x[k], 0), DOWN, buff=0.18) for k in names}
            return vert, bar, hlab, labs

        # right: the data, which never move
        sx = Axes(x_range=[15, 65, 10], y_range=[10, 50, 10], x_length=4.2, y_length=3.0,
                  axis_config=AXIS).move_to([4.15, 0.75, 0])
        snum = VGroup(*[label(str(v), 18, MUTED).next_to(sx.c2p(v, 10), DOWN, buff=0.12) for v in (20, 40, 60)],
                      *[label(str(v), 18, MUTED).next_to(sx.c2p(15, v), LEFT, buff=0.12) for v in (20, 40)])
        sxt = label("emergency admissions (%)", 20, MUTED).next_to(sx, DOWN, buff=0.45)
        syt = label("patients over 75 (%)", 20, MUTED).rotate(PI / 2).next_to(sx, LEFT, buff=0.5)
        sdot = {k: Dot(sx.c2p(*P[k]), radius=0.07, color=CREAM) for k in names}
        side = {"A": LEFT, "B": DOWN, "C": UP, "D": DOWN, "E": UP, "F": RIGHT}
        slab = {k: label(k, 22, CREAM).next_to(sdot[k], side[k], buff=0.1) for k in names}

        self.play(Create(ax), FadeIn(ynum), FadeIn(ytitle), Create(sx), FadeIn(snum), FadeIn(sxt), FadeIn(syt),
                  run_time=1.2)
        self.play(FadeIn(VGroup(*sdot.values(), *slab.values()), lag_ratio=0.1), run_time=1.0)
        self.caption(label("six hospitals: emergency admissions and patients over 75, in %", 26).move_to(slot))
        self.wait(2.8)

        vert, bar, hlab, labs = draw(root)
        self.play(FadeIn(VGroup(*labs.values())), run_time=0.6)
        self.caption(label("complete linkage: each merge drawn at the distance where it happened", 26).move_to(slot))
        for u in order:
            who = [sdot[k] for k in members(u)]
            self.play(Create(vert[members(u[0])]), Create(vert[members(u[1])]),
                      *[d.animate.set_color(GOLD) for d in who], run_time=0.6)
            self.play(Create(bar[members(u)]), FadeIn(hlab[members(u)]), run_time=0.5)
            self.play(*[d.animate.set_color(CREAM) for d in who], run_time=0.3)
            self.wait(0.5)
        self.wait(1.2)

        # the tempting reading
        ring = SurroundingRectangle(VGroup(labs["C"], labs["D"]), color=CORAL, buff=0.1, stroke_width=3)
        self.play(Create(ring), run_time=0.8)
        self.caption(label("C and D are drawn side by side. So they are similar?", 26, CORAL).move_to(slot))
        self.wait(2.8)

        cb = DashedLine(sdot["C"].get_center(), sdot["B"].get_center(), color=GOLD, stroke_width=3)
        cd = DashedLine(sdot["C"].get_center(), sdot["D"].get_center(), color=CORAL, stroke_width=3)
        self.play(Create(cb), Create(cd), run_time=1.0)
        self.caption(label(f"no: in the data C is {dist('C', 'B'):.1f} points from B, "
                           f"and {dist('C', 'D'):.1f} from D", 26).move_to(slot))
        self.wait(3.0)
        y_top = ax.c2p(0, top)[1]
        hb = DashedLine(ax.c2p(0, top), [hlab[members(root)].get_left()[0] - 0.1, y_top, 0],
                        color=GOLD, stroke_width=2.5)
        self.play(Create(hb), bar[members(root)].animate.set_color(GOLD), run_time=0.8)
        self.caption(label(f"and the tree joins C and D only at {top:.1f}, its very top", 26).move_to(slot))
        self.wait(3.0)

        # flips: the drawing changes, the data and the heights do not
        L, R, h0 = root
        flips = [((L[1], L[0], L[2]), R, h0), ((L[1], L[0], L[2]), (R[1], R[0], R[2]), h0)]
        self.play(FadeOut(ring), FadeOut(hb), FadeOut(cb), FadeOut(cd),
                  bar[members(root)].animate.set_color(CREAM), run_time=0.6)
        texts = ["flip the left half at its top merge: now B sits next to D",
                 "flip the right half too: C and D end up at opposite ends"]
        for t, text in zip(flips, texts):
            v2, b2, h2, l2 = draw(t)
            self.caption(label(text, 26, SKY).move_to(slot))
            self.play(*[Transform(vert[key], v2[key]) for key in vert],
                      *[Transform(bar[key], b2[key]) for key in bar],
                      *[Transform(hlab[key], h2[key]) for key in hlab],
                      *[Transform(labs[k], l2[k]) for k in names], run_time=2.0)
            self.wait(2.4)
        self.caption(label("no hospital moved and no height changed: it is the same tree", 26).move_to(slot))
        self.play(*[Indicate(d, color=GOLD, scale_factor=1.4) for d in sdot.values()], run_time=1.2)
        self.wait(2.0)

        # the reading that is right: the longest stretch with no merge
        hs = sorted(u[2] for u in order)
        gaps = [(b - a, a, b) for a, b in zip(hs, hs[1:])]
        _, lo, hi = max(gaps)
        span = Line(ax.c2p(0, lo), ax.c2p(0, hi), color=SKY, stroke_width=9)
        self.play(Create(span), run_time=0.9)
        self.caption(label(f"read the heights instead: nothing merges between {lo:.1f} and {hi:.1f}", 26).move_to(slot))
        self.wait(3.0)

        hcut = (lo + hi) / 2
        cut = DashedLine(ax.c2p(0, hcut), ax.c2p(7, hcut), color=SKY, stroke_width=2.5)

        def sub_lines(t):
            """Everything under a node, fully below the cut: its bar and the verticals inside it."""
            if isinstance(t, str):
                return VGroup()
            return VGroup(bar[members(t)], vert[members(t[0])], vert[members(t[1])],
                          sub_lines(t[0]), sub_lines(t[1]))

        anims = [Create(cut)]
        for half, c in ((L, GOLD), (R, SKY)):
            anims.append(sub_lines(half).animate.set_color(c))
            anims += [sdot[k].animate.set_color(c) for k in members(half)]
            anims += [labs[k].animate.set_color(c) for k in members(half)]
            anims += [slab[k].animate.set_color(c) for k in members(half)]
        self.play(*anims, run_time=1.4)
        ga = ", ".join(sorted(members(L)))
        gb = ", ".join(sorted(members(R)))
        self.caption(label(f"cut in the gap: planned care ({ga}) and emergency care ({gb})", 26).move_to(slot))
        self.wait(3.4)
        self.caption(label("horizontal position carries no information. Read the height.", 28, GOLD).move_to(slot))
        self.wait(3.6)
