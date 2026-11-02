"""manim scenes for the Module 2 decks — lecture 18, neural networks.

Render one:      uv run manim -qm scenes.py Perceptron
Render all:      make clips   (from the repo root; remuxes and copies to lectures/media/)

The look is the one maths reels use: a dark stage, one object, one
transformation at a time, formulas set in real LaTeX. The stage is the
course navy rather than black, so a clip on a white slide reads as ours.
Each clip is one idea, paced to be spoken over: the sentence next to it on
the slide does the rest.
"""
from manim import *
import glob, os
import manimpango

# Libre Franklin sits in ~/Library/Fonts; Pango's render process needs the
# files registered explicitly even when fontconfig lists them.
for _f in glob.glob(os.path.expanduser("~/Library/Fonts/LibreFranklin-*.otf")):
    manimpango.register_font(_f)

NAVY   = "#002f57"   # stage
CREAM  = "#f3ead7"   # primary ink on navy
GOLD   = "#e0b354"   # the thing to look at
SKY    = "#8fc4e8"   # the second class / the second curve
MUTED  = "#8a9bb0"   # axes, secondary labels
FONT   = "Libre Franklin"

config.background_color = NAVY


def label(s, size=28, color=CREAM):
    # Set at four times the size and scaled down: below about 26 pt Pango hints
    # Libre Franklin's spaces to nothing ("whichisw", "start:three").
    return Text(s, font=FONT, font_size=size * 4, color=color).scale(0.25)


class Stage(Scene):
    """Every clip is spoken over, so it must breathe. The older scenes were timed
    for a reel; WAIT_SCALE/PLAY_SCALE stretch them from here without retiming
    each line. Scenes written with speech in mind set both to 1.0."""
    WAIT_SCALE = 2.0
    PLAY_SCALE = 1.4

    def setup(self):
        self.camera.background_color = NAVY

    def wait(self, duration=1.0, **kw):
        return super().wait(duration * self.WAIT_SCALE, **kw)

    def play(self, *anims, **kw):
        if "run_time" in kw:
            kw["run_time"] = kw["run_time"] * self.PLAY_SCALE
        return super().play(*anims, **kw)

    def caption(self, mob, run_time=0.8):
        """One caption per clip, in one slot: the last one leaves as this one
        arrives, so two never sit on top of each other. Refuses one that would
        leave the frame."""
        half_w, half_h = config.frame_width / 2 - 0.2, config.frame_height / 2 - 0.1
        if mob.get_left()[0] < -half_w or mob.get_right()[0] > half_w or mob.get_bottom()[1] < -half_h:
            raise ValueError(f"caption leaves the frame: {getattr(mob, 'text', mob)}")
        old = getattr(self, "_caption", None)
        if old is not None:                      # out, then in: never both on screen
            self.play(FadeOut(old), run_time=run_time * 0.4)
        self.play(FadeIn(mob), run_time=run_time * 0.6)
        self._caption = mob
        return mob


# ---------------------------------------------------------------- 2. perceptron
AND_DATA = [((0, 0), 0), ((0, 1), 0), ((1, 0), 0), ((1, 1), 1)]
W0, THETA, ETA = (30, -10), 25, 10


def num(v):
    """hundredths -> tex: 30 -> 0.3, -10 -> -0.1, 25 -> 0.25, 0 -> 0.0"""
    t = f"{v / 100:.2f}".rstrip("0")
    return t + "0" if t.endswith(".") else t


def par(v):
    """a negative factor in a product gets brackets: (-0.1)·0"""
    return f"({num(v)})" if v < 0 else num(v)


def perceptron_run(w=W0, theta=THETA, eta=ETA, max_epochs=10):
    """One dict per row visited, in order, until an epoch has no mistake."""
    w = list(w)
    for epoch in range(1, max_epochs + 1):
        mistakes = 0
        for i, ((x1, x2), y) in enumerate(AND_DATA):
            z = w[0] * x1 + w[1] * x2
            yhat = 1 if z >= theta else 0
            err = y - yhat
            before = tuple(w)
            if err:
                mistakes += 1
                w[0] += eta * err * x1
                w[1] += eta * err * x2
            yield dict(epoch=epoch, i=i, x=(x1, x2), y=y, z=z, yhat=yhat, err=err,
                       before=before, after=tuple(w), last=(i == 3), mistakes=mistakes)
        if mistakes == 0:
            return


def and_axes(size=4.6):
    return Axes(x_range=[-0.5, 1.6, 1], y_range=[-0.5, 1.6, 1], x_length=size, y_length=size,
                axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.5})


def and_dots(ax):
    return VGroup(*[Dot(ax.c2p(*p), radius=0.11, color=GOLD if y else SKY) for p, y in AND_DATA])


def and_legend(dots):
    """'y = 1' straight above (1,1): every boundary of the run passes to its side, never through."""
    return VGroup(label("y = 1", 22, GOLD).next_to(dots[3], UP, buff=0.12),
                  label("y = 0", 22, SKY).next_to(dots[0], DL, buff=0.08))


def and_boundary(ax, w, theta=THETA, lo=-0.5, hi=1.6):
    """The line W1 x + W2 y = theta clipped to the plot box, as a Line (so Transform stays a Line)."""
    w1, w2 = w
    pts = []
    for x in (lo, hi):
        if w2:
            y = (theta - w1 * x) / w2
            if lo <= y <= hi:
                pts.append((x, y))
    for y in (lo, hi):
        if w1:
            x = (theta - w2 * y) / w1
            if lo <= x <= hi:
                pts.append((x, y))
    uniq = []
    for q in pts:
        if all(abs(q[0] - u[0]) + abs(q[1] - u[1]) > 1e-9 for u in uniq):
            uniq.append(q)
    if len(uniq) < 2:
        return Line(ax.c2p(lo, lo), ax.c2p(lo, lo), color=CREAM, stroke_width=3)
    a, b = max(((p, q) for p in uniq for q in uniq),
               key=lambda pq: np.hypot(pq[0][0] - pq[1][0], pq[0][1] - pq[1][1]))
    return Line(ax.c2p(*a), ax.c2p(*b), color=CREAM, stroke_width=3)


def w_tex(w, size=34, color=CREAM):
    return MathTex(rf"W = ({num(w[0])},\ {num(w[1])})", color=color, font_size=size)


# ---------------------------------------------------------------- 1. motivation
# ---------------------------------------------------------------- 3. gradient descent
# ---------------------------------------------------------------- 4. one neuron = GLM
# ---------------------------------------------------------------- 5. hidden layer
# ---------------------------------------------------------------- 6. overfitting
# ================================================================ lecture 19 — the lab
# ---------------------------------------------------------------- 1. three splits
# ---------------------------------------------------------------- 2. validation curve
# ---------------------------------------------------------------- 3. why the tree wins
# ---------------------------------------------------------------- 4. the scale of deep
# ---------------------------------------------------------------- 5. autoencoder = PCA
# ================================================================ lecture 11 — k-means
# The six customers of the by-hand slide, in the deck's own order and numbers.
KM_PTS = {"A": (1, 1), "B": (2, 1), "C": (1, 2), "D": (8, 8), "E": (9, 8), "F": (8, 9)}


def km_axes(x=(0, 10, 2), y=(0, 10, 2), xl=6.0, yl=5.0):
    return Axes(x_range=list(x), y_range=list(y), x_length=xl, y_length=yl,
                axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.4})


class Lloyd(Stage):
    """Assign, update, repeat, from a start chosen badly on purpose. Every half-step
    writes its W in a column on the right, so the claim on the slide can be read
    off the screen: W only ever falls, which is why the algorithm must stop."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        rng = np.random.default_rng(4)
        ax = km_axes(x=(-1, 11, 3), y=(-1, 11, 3), xl=6.4, yl=5.2).to_edge(LEFT, buff=0.9).shift(UP * 0.5)
        xl = label("visits per month", 22, MUTED).next_to(ax, DOWN, buff=0.2)
        yl = label("spend per visit", 22, MUTED).rotate(PI / 2).next_to(ax, LEFT, buff=0.15)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.0)

        centres = np.array([[2.5, 2.5], [8.0, 3.0], [5.5, 8.5]])
        pts = np.vstack([c + rng.normal(0, 1.05, size=(22, 2)) for c in centres])
        dots = VGroup(*[Dot(ax.c2p(*p), radius=0.06, color=MUTED) for p in pts])
        self.play(FadeIn(dots, lag_ratio=0.02), run_time=1.4)
        slot = np.array([0, xl.get_bottom()[1] - 0.45, 0])
        self.caption(label("66 customers, k = 3", 26).move_to(slot))
        self.wait(2.0)

        cols = [GOLD, SKY, "#c98bb9"]
        # a deliberately poor start: all three on the left, so the first update is large
        cent = np.array([[1.0, 5.0], [3.0, 5.5], [2.0, 7.0]])
        marks = VGroup(*[Star(n=5, outer_radius=0.17, color=c, fill_opacity=1).move_to(ax.c2p(*m))
                         for m, c in zip(cent, cols)])
        self.play(FadeIn(marks, scale=1.5), run_time=1.0)
        self.caption(label("start: three centroids, all on the left, on purpose", 26).move_to(slot))
        self.wait(2.6)

        # the log: one row per half-step, newest in gold
        LEFT_X, W_X, TOP = 1.0, 4.6, 2.9
        head = label("W after each half-step", 24, MUTED).move_to([0, TOP, 0]).align_to([LEFT_X, 0, 0], LEFT)
        self.play(FadeIn(head), run_time=0.6)
        rows = VGroup()

        def log(kind, it, W):
            y = TOP - 0.56 * (len(rows) + 1)
            name = label(f"round {it} · {kind}", 26, CREAM).move_to([0, y, 0]).align_to([LEFT_X, 0, 0], LEFT)
            val = MathTex(rf"W = {W:.0f}", color=GOLD, font_size=38).move_to([0, y, 0]).align_to([W_X, 0, 0], LEFT)
            anims = [FadeIn(VGroup(name, val), shift=RIGHT * 0.15)]
            if len(rows):
                anims.append(rows[-1][1].animate.set_color(CREAM))
            self.play(*anims, run_time=0.6)
            rows.add(VGroup(name, val))

        def assign(c):
            d = ((pts[:, None, :] - c[None, :, :]) ** 2).sum(-1)
            return d.argmin(1), d.min(1).sum()

        for it in range(1, 6):
            lab_, W = assign(cent)
            if it == 1:
                W_first = W
                self.caption(label("assign: every point joins its nearest star", 26).move_to(slot))
            self.play(*[d.animate.set_color(cols[l]) for d, l in zip(dots, lab_)], run_time=1.3)
            log("assign", it, W)
            self.wait(2.0 if it == 1 else 1.2)

            new = np.array([pts[lab_ == j].mean(0) for j in range(3)])
            W2 = ((pts - new[lab_]) ** 2).sum()
            if it == 1:
                self.caption(label("update: every star moves to the mean of its points", 26).move_to(slot))
            elif it == 2:
                self.caption(label("and again: assign, update", 26).move_to(slot))
            self.play(*[m.animate.move_to(ax.c2p(*n)) for m, n in zip(marks, new)], run_time=1.5)
            log("update", it, W2)
            self.wait(2.0 if it == 1 else 1.2)
            moved = float(np.abs(new - cent).max())
            cent = new
            if moved < 0.06:
                break

        self.caption(label(f"round {it}: nothing moved. That is convergence", 26, GOLD).move_to(slot))
        self.wait(2.6)
        self.play(rows[0][1].animate.set_color(GOLD), run_time=0.6)
        self.caption(label(f"{W_first:.0f} down to {W2:.0f}, never up once: so it has to stop", 26).move_to(slot))
        self.wait(4.0)


# the names sit away from where the centroids land, (1.33, 1.33) and (8.33, 8.33)
KM_NAME_SIDE = {"A": DL, "B": DR, "C": UL, "D": DL, "E": DR, "F": UL}


class KmeansByHand(Stage):
    """The six customers of the slide, with the distances written out: assign,
    update, then every squared distance to the new centroids and their sum.
    In fractions, so the sums on screen add up exactly: W = 8/3."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        ax = km_axes(x=(0, 10, 2), y=(0, 10, 2), xl=5.6, yl=4.8).to_edge(LEFT, buff=0.8).shift(DOWN * 0.3)
        self.play(Create(ax), run_time=0.9)
        self.play(FadeIn(label("visits per month", 22, MUTED).next_to(ax, DOWN, buff=0.25)),
                  FadeIn(label("spend per visit", 22, MUTED).rotate(PI / 2).next_to(ax, LEFT, buff=0.2)), run_time=0.7)

        dots, names = {}, VGroup()
        for n, (x, y) in KM_PTS.items():
            d = Dot(ax.c2p(x, y), radius=0.085, color=MUTED)
            t = label(n, 22, CREAM).next_to(d, KM_NAME_SIDE[n], buff=0.06)
            dots[n] = d; names.add(t)
            self.add(d)
        self.play(FadeIn(VGroup(*dots.values()), lag_ratio=0.1), FadeIn(names, lag_ratio=0.1), run_time=1.4)
        self.wait(2.8)

        # start: A and D are the centroids
        cA = Star(n=5, outer_radius=0.16, color=GOLD, fill_opacity=1).move_to(ax.c2p(1, 1))
        cD = Star(n=5, outer_radius=0.16, color=SKY, fill_opacity=1).move_to(ax.c2p(8, 8))
        self.play(FadeIn(cA, scale=1.6), FadeIn(cD, scale=1.6), run_time=1.0)
        top = label("centroids start at A and D", 24, CREAM).next_to(ax, UP, buff=0.3)
        self.play(FadeIn(top), run_time=0.8)
        self.wait(2.8)

        # the right-hand column: every line starts at COL, clear of the axes
        COL = np.array([0.5, 0, 0])
        head = MathTex(r"\text{point} \quad d^2(\cdot,A) \quad d^2(\cdot,D)", color=MUTED, font_size=28)
        head.align_to(COL, LEFT).set_y(2.7)
        self.play(FadeIn(head), run_time=0.7)

        table, prev = VGroup(head), head
        for n in ("B", "C", "E", "F"):
            x, y = KM_PTS[n]
            dA = (x - 1) ** 2 + (y - 1) ** 2
            dD = (x - 8) ** 2 + (y - 8) ** 2
            winner = GOLD if dA < dD else SKY
            line = MathTex(rf"{n} \quad\; {dA} \quad\; {dD}", color=CREAM, font_size=30)
            line.next_to(prev, DOWN, buff=0.32).align_to(COL, LEFT)
            self.play(FadeIn(line, shift=RIGHT * 0.15), run_time=0.7)
            self.play(dots[n].animate.set_color(winner), line.animate.set_color(winner), run_time=0.7)
            self.wait(2.1)
            table.add(line)
            prev = line
        self.play(dots["A"].animate.set_color(GOLD), dots["D"].animate.set_color(SKY), run_time=0.6)
        self.wait(2.2)

        # update the centroids to the group means, with the arithmetic
        m1 = MathTex(r"\bar x_1 = \tfrac{1+2+1}{3},\ \tfrac{1+1+2}{3} = (1.33,\ 1.33)", color=GOLD, font_size=28)
        m2 = MathTex(r"\bar x_2 = \tfrac{8+9+8}{3},\ \tfrac{8+8+9}{3} = (8.33,\ 8.33)", color=SKY, font_size=28)
        VGroup(m1, m2).arrange(DOWN, buff=0.3, aligned_edge=LEFT).next_to(prev, DOWN, buff=0.5).align_to(COL, LEFT)
        self.play(FadeIn(m1), cA.animate.move_to(ax.c2p(1.333, 1.333)), run_time=1.3)
        self.wait(2.0)
        self.play(FadeIn(m2), cD.animate.move_to(ax.c2p(8.333, 8.333)), run_time=1.3)
        self.wait(2.8)

        again = label("assign again: nothing changes", 24, CREAM).move_to(top)
        self.play(FadeOut(top), FadeIn(again), run_time=0.9)
        self.wait(2.8)

        # W at the final centroids: each squared distance, then the sum
        self.play(FadeOut(table), VGroup(m1, m2).animate.align_to(head, UP), run_time=1.0)
        self.wait(1.0)
        prev = m2
        for n, dx, dy, d2 in (("A", 1, 1, 2), ("B", 2, 1, 5), ("C", 1, 2, 5)):
            line = MathTex(rf"d^2({n},\bar x_1) = (\tfrac{{{dx}}}{{3}})^2 + (\tfrac{{{dy}}}{{3}})^2 = \tfrac{{{d2}}}{{9}}",
                           color=GOLD, font_size=28)
            line.next_to(prev, DOWN, buff=0.3).align_to(COL, LEFT)
            self.play(FadeIn(line, shift=RIGHT * 0.15), Indicate(dots[n], color=GOLD, scale_factor=1.8), run_time=0.9)
            self.wait(2.2)
            prev = line
        w1 = MathTex(r"W_1 = \tfrac{2}{9} + \tfrac{5}{9} + \tfrac{5}{9} = \tfrac{12}{9} = 1.33", color=GOLD, font_size=30)
        w1.next_to(prev, DOWN, buff=0.4).align_to(COL, LEFT)
        self.play(FadeIn(w1), run_time=0.8)
        self.wait(2.6)
        w2 = MathTex(r"W_2 = \tfrac{12}{9} \quad \text{the mirror image}", color=SKY, font_size=30)
        w2.next_to(w1, DOWN, buff=0.3).align_to(COL, LEFT)
        self.play(FadeIn(w2), *[Indicate(dots[n], color=SKY, scale_factor=1.8) for n in ("D", "E", "F")], run_time=1.0)
        self.wait(2.6)
        w = MathTex(r"W = \tfrac{4}{3} + \tfrac{4}{3} = \tfrac{8}{3} = 2.67", color=GOLD, font_size=36)
        w.next_to(w2, DOWN, buff=0.5).align_to(COL, LEFT)
        self.play(Write(w), run_time=1.4)
        self.wait(4.5)


def lloyd(P, cent, iters=100):
    """Plain Lloyd from the given centroids: labels, centroids, W."""
    for _ in range(iters):
        lab = ((P[:, None] - cent[None]) ** 2).sum(-1).argmin(1)
        new = np.array([P[lab == j].mean(0) for j in range(len(cent))])
        if np.allclose(new, cent):
            break
        cent = new
    return lab, cent, ((P - cent[lab]) ** 2).sum()


def kmeans_best(P, k, seed=0, nstart=25):
    """What kmeans(nstart = 25) returns: the lowest W over random starts."""
    r = np.random.default_rng(seed)
    runs = [lloyd(P, P[r.choice(len(P), k, replace=False)]) for _ in range(nstart)]
    return min(runs, key=lambda run: run[2])


class ScaleBreaks(Stage):
    """Sixty patients by age and yearly cost of care. Raw, one euro weighs as much
    as one year: k-means sees a vertical line and cuts it into cost bands, young
    and old mixed. In standard deviations age counts again, and the two groups
    the eye saw come back. Every count and share on screen is computed here."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        rng = np.random.default_rng(9)
        P = np.vstack([np.column_stack([rng.normal(36, 5, 30), rng.normal(5200, 650, 30)]),
                       np.column_stack([rng.normal(72, 5, 30), rng.normal(4600, 650, 30)])])
        young = np.arange(60) < 30
        axis = {"color": MUTED, "include_tip": False, "stroke_width": 1.4}

        ax = Axes(x_range=[20, 90, 10], y_range=[2500, 7500, 1000], x_length=6.0, y_length=4.6,
                  axis_config=axis).to_edge(LEFT, buff=1.0).shift(UP * 0.55)
        xl = label("age (years)", 22, MUTED).next_to(ax, DOWN, buff=0.25)
        yl = label("cost of care (€ a year)", 22, MUTED).rotate(PI / 2).next_to(ax, LEFT, buff=0.2)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.0)
        dots = VGroup(*[Dot(ax.c2p(*p), radius=0.06, color=MUTED) for p in P])
        self.play(FadeIn(dots, lag_ratio=0.02), run_time=1.3)
        slot = np.array([0, -3.2, 0])
        self.caption(label("60 patients: age, and what they cost the health service in a year", 26).move_to(slot))
        self.wait(2.8)
        self.caption(label("your eye sees two groups: young and old", 26).move_to(slot))
        self.wait(2.6)

        # what k-means sees: one euro on the same footing as one year
        cx = ax.c2p(55, 5000)[0]
        f = (70 / 5000) * (4.6 / 6.0)
        self.caption(label("k-means sees this: one euro counts as much as one year", 26).move_to(slot))
        self.play(*[d.animate.set_x(cx + (d.get_x() - cx) * f) for d in dots], run_time=2.0)
        self.wait(1.4)

        COL = [1.0, 0, 0]
        who = label("two patients, aged 36 and 73, €600 apart", 22, MUTED)
        d2 = MathTex(r"d^2 = (\Delta\,\text{age})^2 + (\Delta\,\text{cost})^2", color=CREAM, font_size=30)
        ex = MathTex(r"= 37^2 + 600^2 = 1\,369 + 360\,000", color=CREAM, font_size=30)
        share = label(f"age: {100 * 37**2 / (37**2 + 600**2):.1f}% of the distance", 26, GOLD)
        panel = VGroup(who, d2, ex, share).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        panel.move_to([0, 1.5, 0]).align_to(COL, LEFT)
        for m in panel:
            self.play(FadeIn(m, shift=RIGHT * 0.15), run_time=0.7)
            self.wait(1.4)

        lab_, _, _ = kmeans_best(P, 2)
        cols = [GOLD, SKY]
        self.play(*[d.animate.set_color(cols[l]) for d, l in zip(dots, lab_)], run_time=1.2)
        self.caption(label("so it cuts by cost: two bands", 26).move_to(slot))
        self.play(*[d.animate.move_to(ax.c2p(*p)) for d, p in zip(dots, P)], run_time=2.0)
        mix = VGroup(*[label(f"cluster {j + 1}: {(young & (lab_ == j)).sum()} young, "
                             f"{(~young & (lab_ == j)).sum()} old", 26, cols[j]) for j in range(2)])
        mix.arrange(DOWN, buff=0.3, aligned_edge=LEFT).next_to(panel, DOWN, buff=0.55).align_to(COL, LEFT)
        self.play(FadeIn(mix, lag_ratio=0.4), run_time=1.0)
        self.caption(label("young and old mixed in both: cost bands, not segments", 26, GOLD).move_to(slot))
        self.wait(3.6)

        # scale(): every column in standard deviations from its mean
        s = P.std(0, ddof=1)
        s_age, s_cost = round(s[0], 1), round(s[1])          # as printed, so the sum on screen adds up
        a2, c2 = (37 / s_age) ** 2, (600 / s_cost) ** 2
        z1 = MathTex(r"z = \frac{x - \bar x}{s}", color=CREAM, font_size=32)
        z2 = MathTex(rf"s_{{\text{{age}}}} = {s_age:g}\ \text{{years}}, \quad s_{{\text{{cost}}}} = {s_cost}\ \text{{euro}}",
                     color=CREAM, font_size=28)
        z3 = MathTex(rf"d^2 = \left(\tfrac{{37}}{{{s_age:g}}}\right)^2 + \left(\tfrac{{600}}{{{s_cost}}}\right)^2"
                     rf"= {a2:.2f} + {c2:.2f}", color=CREAM, font_size=30)
        share2 = label(f"age: {100 * a2 / (a2 + c2):.0f}% of the distance", 26, GOLD)
        panel2 = VGroup(z1, z2, z3, share2).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        panel2.move_to([0, 1.3, 0]).align_to(COL, LEFT)
        self.play(FadeOut(VGroup(panel, mix)), dots.animate.set_color(MUTED), run_time=0.8)
        self.caption(label("scale(): each column in standard deviations from its mean", 26).move_to(slot))
        for m in panel2:
            self.play(FadeIn(m, shift=RIGHT * 0.15), run_time=0.7)
            self.wait(1.4)

        Z = (P - P.mean(0)) / s
        az = Axes(x_range=[-2.5, 2.5, 1], y_range=[-3, 3, 1], x_length=6.0, y_length=4.6,
                  axis_config=axis).move_to(ax)
        xl2 = label("age (sd)", 22, MUTED).move_to(xl)
        yl2 = label("cost (sd)", 22, MUTED).rotate(PI / 2).move_to(yl)
        self.play(Transform(ax, az), Transform(xl, xl2), Transform(yl, yl2),
                  *[d.animate.move_to(az.c2p(*z)) for d, z in zip(dots, Z)], run_time=2.2)
        self.caption(label("the picture hardly changes. The distance does", 26).move_to(slot))
        self.wait(2.2)

        labz, _, _ = kmeans_best(Z, 2)
        self.play(*[d.animate.set_color(cols[l]) for d, l in zip(dots, labz)], run_time=1.2)
        mix2 = VGroup(*[label(f"cluster {j + 1}: {(young & (labz == j)).sum()} young, "
                              f"{(~young & (labz == j)).sum()} old", 26, cols[j]) for j in range(2)])
        mix2.arrange(DOWN, buff=0.3, aligned_edge=LEFT).next_to(panel2, DOWN, buff=0.55).align_to(COL, LEFT)
        self.play(FadeIn(mix2, lag_ratio=0.4), run_time=1.0)
        self.caption(label("same patients, same algorithm: now it finds the groups you saw", 26, GOLD).move_to(slot))
        self.wait(4.0)


class ShapeBreaks(Stage):
    """Two crescents. k-means converges, draws the straight line two centroids
    always draw, and its W is less than half the crescents' own: more starts
    cannot help, because the objective itself prefers the cut."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        rng = np.random.default_rng(2)
        t1 = rng.uniform(0, np.pi, 70)
        c1 = np.column_stack([np.cos(t1) * 2.4, np.sin(t1) * 1.5]) + rng.normal(0, 0.12, (70, 2))
        t2 = rng.uniform(0, np.pi, 70)
        c2 = np.column_stack([np.cos(t2) * 2.4 + 1.6, -np.sin(t2) * 1.5 + 0.6]) + rng.normal(0, 0.12, (70, 2))
        S = np.vstack([c1, c2])
        truth = np.repeat([0, 1], 70)
        cols = [GOLD, SKY]

        ax = km_axes(x=(-3, 5, 1), y=(-2, 2.5, 1), xl=7.0, yl=4.2).to_edge(LEFT, buff=0.6).shift(UP * 0.6)
        self.play(Create(ax), run_time=0.9)
        dots = VGroup(*[Dot(ax.c2p(*p), radius=0.05, color=MUTED) for p in S])
        self.play(FadeIn(dots, lag_ratio=0.01), run_time=1.6)
        slot = np.array([0, -3.0, 0])
        self.caption(label("two crescents: any eye separates them", 26).move_to(slot))
        self.wait(2.4)
        self.play(*[d.animate.set_color(cols[t]) for d, t in zip(dots, truth)], run_time=1.0)
        self.caption(label("these are the two groups", 26).move_to(slot))
        self.wait(2.4)
        self.play(dots.animate.set_color(MUTED), run_time=0.7)

        # k-means from a start on the left, round by round until nothing moves
        cent = np.array([[-2.0, 1.6], [-0.8, 1.8]])
        marks = VGroup(*[Star(n=5, outer_radius=0.16, color=c, fill_opacity=1).move_to(ax.c2p(*m))
                         for m, c in zip(cent, cols)])
        self.play(FadeIn(marks, scale=1.4), run_time=0.8)
        self.caption(label("k-means, k = 2: assign, update, until nothing moves", 26).move_to(slot))
        for it in range(12):
            lab_ = ((S[:, None] - cent[None]) ** 2).sum(-1).argmin(1)
            self.play(*[d.animate.set_color(cols[l]) for d, l in zip(dots, lab_)], run_time=0.9)
            new = np.array([S[lab_ == j].mean(0) for j in range(2)])
            self.play(*[m.animate.move_to(ax.c2p(*n)) for m, n in zip(marks, new)], run_time=0.9)
            done = np.abs(new - cent).max() < 0.05
            cent = new
            if done:
                break
        lab_ = ((S[:, None] - cent[None]) ** 2).sum(-1).argmin(1)
        self.wait(1.4)

        # the boundary: every point equidistant from the two centroids, a straight line
        mid, dv = cent.mean(0), cent[1] - cent[0]
        perp = np.array([-dv[1], dv[0]]) / np.linalg.norm(dv)
        ts = sorted(t for t in ((-2 - mid[1]) / perp[1], (2.5 - mid[1]) / perp[1]))
        cut = DashedLine(ax.c2p(*(mid + ts[0] * perp)), ax.c2p(*(mid + ts[1] * perp)),
                         color=CREAM, stroke_width=3)
        self.play(Create(cut), run_time=1.2)
        self.caption(label("between two centroids the boundary is always a straight line", 26).move_to(slot))
        self.wait(3.0)

        W_cut = ((S - cent[lab_]) ** 2).sum()
        W_true = sum(((S[truth == j] - S[truth == j].mean(0)) ** 2).sum() for j in range(2))
        COL = [2.2, 0, 0]
        r1 = VGroup(label("the straight cut", 24, MUTED), MathTex(rf"W = {W_cut:.0f}", color=GOLD, font_size=40))
        r2 = VGroup(label("the two crescents", 24, MUTED), MathTex(rf"W = {W_true:.0f}", color=SKY, font_size=40))
        for r in (r1, r2):
            r.arrange(DOWN, buff=0.15, aligned_edge=LEFT)
        VGroup(r1, r2).arrange(DOWN, buff=0.6, aligned_edge=LEFT).move_to([0, 0.9, 0]).align_to(COL, LEFT)
        self.play(FadeIn(r1, shift=RIGHT * 0.15), run_time=0.8)
        self.wait(1.6)
        self.play(FadeIn(r2, shift=RIGHT * 0.15), run_time=0.8)
        self.caption(label("the cut has the smaller W: k-means did exactly its job", 26).move_to(slot))
        self.wait(3.4)
        self.caption(label("so more starts cannot fix it: W itself prefers round groups", 26, GOLD).move_to(slot))
        self.wait(4.0)


class ElbowLie(Stage):
    """W against k, twice: the textbook curve with its corner, then the curve most
    data give. The drop at each step is written next to the plot, so the elbow is
    a number you can see collapse, or fail to."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        ax = Axes(x_range=[0, 10.5, 1], y_range=[0, 100, 25], x_length=7.0, y_length=4.4,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.4})
        ax.to_edge(LEFT, buff=1.0).shift(UP * 0.55)
        ticks = VGroup(*[label(str(k), 20, MUTED).next_to(ax.c2p(k, 0), DOWN, buff=0.15) for k in range(1, 11)])
        kl = label("k", 24, MUTED).next_to(ticks, DOWN, buff=0.15)
        wl = MathTex("W", color=MUTED, font_size=32).next_to(ax, LEFT, buff=0.25)
        self.play(Create(ax), FadeIn(ticks), FadeIn(kl), FadeIn(wl), run_time=1.0)

        ks = np.arange(1, 11)
        W = np.array([92, 44, 22, 18.5, 16, 14, 12.2, 10.6, 9.2, 8.0])
        pts = [ax.c2p(k, w) for k, w in zip(ks, W)]
        curve = VMobject(color=GOLD, stroke_width=4).set_points_as_corners(pts)
        dots = VGroup(*[Dot(p, radius=0.07, color=GOLD) for p in pts])
        slot = np.array([0, -3.2, 0])
        self.caption(label("W against k: the curve the textbook shows", 26).move_to(slot))
        self.play(Create(curve), run_time=2.2)
        self.play(FadeIn(dots, lag_ratio=0.1), run_time=0.9)
        self.wait(1.6)
        self.caption(label("k = 1: W is all the variance. k = n: W is zero", 26).move_to(slot))
        self.wait(3.0)
        self.caption(label("it falls at every k: it always votes for more", 26).move_to(slot))
        self.wait(2.6)

        # the drops, written out: the elbow is where they collapse
        COL = [1.6, 0, 0]
        head = label("how much W falls", 24, MUTED).move_to([0, 2.6, 0]).align_to(COL, LEFT)
        self.play(FadeIn(head), run_time=0.6)

        def drop_rows(w, color):
            rows = VGroup()
            for i in range(6):
                rows.add(MathTex(rf"{i + 1} \to {i + 2}", r"\quad", rf"{w[i] - w[i + 1]:g}",
                                 color=color, font_size=32))
            rows.arrange(DOWN, buff=0.22, aligned_edge=LEFT).next_to(head, DOWN, buff=0.35).align_to(COL, LEFT)
            return rows

        rows = drop_rows(W, CREAM)
        for r in rows:
            self.play(FadeIn(r, shift=RIGHT * 0.15), run_time=0.45)
        self.wait(1.2)
        el = Circle(radius=0.3, color=CREAM, stroke_width=3).move_to(pts[2])
        self.play(Create(el), rows[1].animate.set_color(GOLD), rows[2].animate.set_color(GOLD), run_time=1.0)
        self.caption(label("22, then 3.5: the drop collapses after k = 3. That is the elbow", 26).move_to(slot))
        self.wait(3.6)

        smooth = np.array([92, 61, 47, 39, 33, 29, 25.5, 23, 21, 19.5])
        pts2 = [ax.c2p(k, w) for k, w in zip(ks, smooth)]
        curve2 = VMobject(color=SKY, stroke_width=4).set_points_as_corners(pts2)
        dots2 = VGroup(*[Dot(p, radius=0.07, color=SKY) for p in pts2])
        rows2 = drop_rows(smooth, SKY)
        self.caption(label("and this is the curve most real data give", 26).move_to(slot))
        self.play(FadeOut(el), Transform(curve, curve2), Transform(dots, dots2),
                  Transform(rows, rows2), run_time=2.0)
        self.wait(2.4)
        self.caption(label("31, 14, 8, 6, 4: it shrinks a little at every step. No corner", 26).move_to(slot))
        self.wait(3.6)
        self.caption(label("the elbow you find here is the one you went looking for", 26).move_to(slot))
        self.wait(3.0)
        self.caption(label("bring a second criterion: silhouette, stability, what a team can act on", 26, GOLD).move_to(slot))
        self.wait(4.0)


# ================================================================ lecture 12 — hierarchical
# The five patients of the by-hand slide: length of stay, in days.
STAY = [2, 3, 6, 10, 11]


# ================================================================ lecture 14 — PCA
# ================================================================ the lab: Module 1 in R
# Two clips for lectures/lab-module-1-in-r.qmd. Both hardcode an R dataset so
# the numbers on screen are the numbers the deck prints: mtcars for lm(), and
# AirPassengers for decompose().

MT_WT = [2.62, 2.875, 2.32, 3.215, 3.44, 3.46, 3.57, 3.19, 3.15, 3.44, 3.44, 4.07, 3.73, 3.78,
         5.25, 5.424, 5.345, 2.2, 1.615, 1.835, 2.465, 3.52, 3.435, 3.84, 3.845, 1.935, 2.14,
         1.513, 3.17, 2.77, 3.57, 2.78]
MT_MPG = [21, 21, 22.8, 21.4, 18.7, 18.1, 14.3, 24.4, 22.8, 19.2, 17.8, 16.4, 17.3, 15.2, 10.4,
          10.4, 14.7, 32.4, 30.4, 33.9, 21.5, 15.5, 15.2, 13.3, 19.2, 27.3, 26, 30.4, 15.8,
          19.7, 15, 21.4]
OLS_A, OLS_B = 37.285, -5.344            # coef(lm(mpg ~ wt, mtcars))


class LeastSquares(Stage):
    """What lm() minimises, watched. The 32 cars of mtcars, a candidate line,
    and the residuals drawn as the squares they are. The line moves five
    times; the sum of the squares is read out at every step, falls, rises on
    an overshoot, and stops at 278.3 — the number no other line beats."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        ax = Axes(x_range=[1, 6, 1], y_range=[5, 40, 5], x_length=6.6, y_length=4.5,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.4})
        ax.to_edge(LEFT, buff=0.6).shift(DOWN * 0.1)
        xl = label("weight, 1 000 lb", 20, MUTED).next_to(ax.x_axis, DOWN, buff=0.15)
        yl = label("mpg", 20, MUTED).next_to(ax.y_axis.get_top(), RIGHT, buff=0.15)
        xt = VGroup(*[label(str(v), 16, MUTED).next_to(ax.c2p(v, 5), DOWN, buff=0.1) for v in range(1, 7)])
        yt = VGroup(*[label(str(v), 16, MUTED).next_to(ax.c2p(1, v), LEFT, buff=0.1) for v in range(10, 41, 10)])
        self.play(Create(ax), FadeIn(xl), FadeIn(yl), FadeIn(xt), FadeIn(yt), run_time=1.2)

        dots = VGroup(*[Dot(ax.c2p(w, m), radius=0.065, color=SKY) for w, m in zip(MT_WT, MT_MPG)])
        dots.set_z_index(3)
        self.play(FadeIn(dots, lag_ratio=0.03), run_time=1.6)
        title = label("32 cars: what does weight cost in fuel?", 28, CREAM).to_edge(UP, buff=0.35)
        self.play(FadeIn(title), run_time=0.8)
        self.wait(2.6)

        # the candidate line and its squares, all driven by two numbers
        a = ValueTracker(float(np.mean(MT_MPG)))
        b = ValueTracker(0.0)

        def fitted(w):
            return a.get_value() + b.get_value() * w

        line = always_redraw(lambda: Line(
            ax.c2p(1.15, fitted(1.15)), ax.c2p(5.85, fitted(5.85)),
            color=CREAM, stroke_width=3.5).set_z_index(2))

        def squares():
            g = VGroup()
            for w, m in zip(MT_WT, MT_MPG):
                p, q = ax.c2p(w, m), ax.c2p(w, fitted(w))
                s = abs(p[1] - q[1])
                if s < 1e-3:
                    continue
                sq = Square(side_length=s, color=GOLD, stroke_width=1.0,
                            fill_color=GOLD, fill_opacity=0.16)
                sq.move_to([p[0] + s / 2, min(p[1], q[1]) + s / 2, 0])
                g.add(sq)
            return g.set_z_index(1)

        sqs = always_redraw(squares)

        def rss():
            return float(sum((m - fitted(w)) ** 2 for w, m in zip(MT_WT, MT_MPG)))

        # right panel: the line's equation, then the number
        eq_l = MathTex(r"\widehat{\text{mpg}} = ", color=CREAM, font_size=32)
        num_a = DecimalNumber(a.get_value(), num_decimal_places=1, color=CREAM, font_size=32)
        num_b = DecimalNumber(b.get_value(), num_decimal_places=2, include_sign=True, color=CREAM, font_size=32)
        eq_r = MathTex(r"\,\text{wt}", color=CREAM, font_size=32)
        eq = VGroup(eq_l, num_a, num_b, eq_r).arrange(RIGHT, buff=0.12)
        eq.move_to([1.2, 1.9, 0], aligned_edge=LEFT)
        num_a.add_updater(lambda m: m.set_value(a.get_value()).next_to(eq_l, RIGHT, buff=0.12))
        num_b.add_updater(lambda m: m.set_value(b.get_value()).next_to(num_a, RIGHT, buff=0.12))
        eq_r.add_updater(lambda m: m.next_to(num_b, RIGHT, buff=0.06))

        rss_l = label("sum of squared residuals", 22, MUTED).next_to(eq, DOWN, buff=0.7).align_to(eq, LEFT)
        rss_n = DecimalNumber(rss(), num_decimal_places=1, color=GOLD, font_size=52, group_with_commas=False)
        rss_n.next_to(rss_l, DOWN, buff=0.15).align_to(rss_l, LEFT)
        rss_n.add_updater(lambda m: m.set_value(rss()))

        self.play(Create(line), FadeIn(eq), run_time=1.2)
        cap = label("1 · ignore weight: a flat line at the mean", 24, CREAM).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(cap), run_time=0.7)
        self.wait(2.0)

        # one car first: the residual is a distance, and its square is a square
        w1, m1 = 2.2, 32.4                      # Fiat 128
        r1 = m1 - fitted(w1)
        seg = Line(ax.c2p(w1, fitted(w1)), ax.c2p(w1, m1), color=GOLD, stroke_width=4).set_z_index(2)
        rtxt = MathTex(rf"{m1} - {fitted(w1):.2f} = {r1:.2f}", color=GOLD, font_size=30)
        rtxt.next_to(rss_l, DOWN, buff=0.15).align_to(rss_l, LEFT)
        self.play(Create(seg), FadeIn(rtxt), run_time=1.0)
        self.wait(2.2)
        s1 = abs(ax.c2p(w1, m1)[1] - ax.c2p(w1, fitted(w1))[1])
        sq1 = Square(side_length=s1, color=GOLD, stroke_width=1.5, fill_color=GOLD, fill_opacity=0.25).set_z_index(1)
        sq1.move_to([ax.c2p(w1, m1)[0] + s1 / 2, ax.c2p(w1, fitted(w1))[1] + s1 / 2, 0])
        r2txt = MathTex(rf"{r1:.2f}^2 = {r1 ** 2:.1f}", color=GOLD, font_size=30)
        r2txt.next_to(rtxt, DOWN, buff=0.2).align_to(rss_l, LEFT)
        self.play(FadeIn(sq1), FadeIn(r2txt), run_time=1.0)
        self.wait(2.4)

        # now all 32, and their sum
        self.play(FadeOut(seg), FadeOut(sq1), FadeOut(rtxt), FadeOut(r2txt), run_time=0.5)
        self.play(FadeIn(sqs), run_time=1.2)
        self.play(FadeIn(rss_l), FadeIn(rss_n), run_time=0.8)
        self.wait(3.6)

        steps = [
            (30.0, -2.0, "2 · tilt it: every square shrinks"),
            (35.0, -4.5, "3 · steeper still: smaller again"),
            (44.0, -8.0, "4 · too steep: the sum rises"),
            (OLS_A, OLS_B, "5 · back to where it is smallest"),
        ]
        for av, bv, text in steps:
            new = label(text, 24, CREAM).to_edge(DOWN, buff=0.3)
            self.play(a.animate.set_value(av), b.animate.set_value(bv),
                      FadeTransform(cap, new), run_time=2.4)
            cap = new
            self.wait(4.4)

        # the answer: the line lm() returns, and the number nothing beats
        final = Line(ax.c2p(1.15, fitted(1.15)), ax.c2p(5.85, fitted(5.85)),
                     color=GOLD, stroke_width=4.5).set_z_index(2)
        self.play(FadeOut(line), FadeIn(final), run_time=0.8)
        ans = MathTex(r"\widehat{\text{mpg}} = 37.3 - 5.34\,\text{wt}", color=GOLD, font_size=36)
        ans.move_to(eq, aligned_edge=LEFT)
        self.play(FadeOut(eq), FadeIn(ans), run_time=1.0)
        best = label("no other line does better", 22, GOLD).next_to(rss_n, DOWN, buff=0.3).align_to(rss_l, LEFT)
        closing = label("that is all lm() does — it is called least squares", 24, CREAM).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(best), FadeTransform(cap, closing), run_time=1.0)
        self.wait(5.0)


AP = [112, 118, 132, 129, 121, 135, 148, 148, 136, 119, 104, 118,
      115, 126, 141, 135, 125, 149, 170, 170, 158, 133, 114, 140,
      145, 150, 178, 163, 172, 178, 199, 199, 184, 162, 146, 166,
      171, 180, 193, 181, 183, 218, 230, 242, 209, 191, 172, 194,
      196, 196, 236, 235, 229, 243, 264, 272, 237, 211, 180, 201,
      204, 188, 235, 227, 234, 264, 302, 293, 259, 229, 203, 229,
      242, 233, 267, 269, 270, 315, 364, 347, 312, 274, 237, 278,
      284, 277, 317, 313, 318, 374, 413, 405, 355, 306, 271, 306,
      315, 301, 356, 348, 355, 422, 465, 467, 404, 347, 305, 336,
      340, 318, 362, 348, 363, 435, 491, 505, 404, 359, 310, 337,
      360, 342, 406, 396, 420, 472, 548, 559, 463, 407, 362, 405,
      417, 391, 419, 461, 472, 535, 622, 606, 508, 461, 390, 432]
# decompose(AirPassengers, type = "multiplicative")$figure
AP_SEASON = [0.910, 0.884, 1.007, 0.976, 0.981, 1.113, 1.227, 1.220, 1.060, 0.922, 0.801, 0.899]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MAUVE = "#c98bb9"


def ap_trend():
    """The 12-month centred moving average decompose() uses: half weight on
    the two end months so the window is centred on a month, not between two.
    Matches R's d$trend to the cent; undefined for the first and last six."""
    x = np.array(AP, float)
    tr = np.full(len(x), np.nan)
    for t in range(6, len(x) - 6):
        tr[t] = (0.5 * x[t - 6] + x[t - 5:t + 6].sum() + 0.5 * x[t + 6]) / 12
    return tr


class Decompose(Stage):
    """decompose(), one layer at a time. The series is drawn; the trend is a
    moving average laid over it; the twelve seasonal factors appear month by
    month with their values; what is left is the remainder, flat within ten
    percent. The closing line is the model: series = trend × season × remainder."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        tr = ap_trend()
        axis_cfg = {"color": MUTED, "include_tip": False, "stroke_width": 1.4}

        # 1 · the series
        ax = Axes(x_range=[0, 144, 12], y_range=[0, 650, 100], x_length=10.6, y_length=4.4,
                  axis_config=axis_cfg).shift(DOWN * 0.35)
        years = VGroup(*[label(str(1949 + i), 16, MUTED).next_to(ax.c2p(12 * i, 0), DOWN, buff=0.12)
                         for i in range(0, 12, 2)])
        yt = VGroup(*[label(str(v), 16, MUTED).next_to(ax.c2p(0, v), LEFT, buff=0.1) for v in (200, 400, 600)])
        title = label("AirPassengers: monthly passengers (thousands), 1949–1960", 26, CREAM).to_edge(UP, buff=0.35)
        self.play(Create(ax), FadeIn(years), FadeIn(yt), FadeIn(title), run_time=1.2)

        series = ax.plot_line_graph(x_values=list(range(144)), y_values=AP, line_color=SKY,
                                    add_vertex_dots=False, stroke_width=2.6)
        self.play(Create(series), run_time=4.5, rate_func=linear)
        note = label("it climbs, and it breathes once a year", 23, SKY).next_to(ax, DOWN, buff=0.45)
        self.play(FadeIn(note), run_time=0.8)
        self.wait(3.0)

        # 2 · the trend: a moving average over the series
        ts = list(range(6, 138))
        trend = ax.plot_line_graph(x_values=ts, y_values=[tr[t] for t in ts], line_color=GOLD,
                                   add_vertex_dots=False, stroke_width=4.0)
        # the window the average is taken over, sliding as the trend is drawn
        pos = ValueTracker(6)
        win = always_redraw(lambda: Rectangle(
            width=ax.c2p(12, 0)[0] - ax.c2p(0, 0)[0], height=ax.c2p(0, 650)[1] - ax.c2p(0, 0)[1],
            color=GOLD, stroke_width=0, fill_color=GOLD, fill_opacity=0.18
        ).move_to(ax.c2p(pos.get_value(), 325)))
        wdot = always_redraw(lambda: Dot(ax.c2p(pos.get_value(), tr[int(round(pos.get_value()))]),
                                         radius=0.08, color=GOLD))
        note2 = label("trend: each month replaced by the average of the twelve around it", 23, GOLD)
        note2.next_to(ax, DOWN, buff=0.45)
        self.play(FadeTransform(note, note2), FadeIn(win), FadeIn(wdot), run_time=0.8)
        self.wait(1.4)
        self.play(Create(trend), pos.animate.set_value(137), run_time=4.5, rate_func=linear)
        self.play(FadeOut(win), FadeOut(wdot), run_time=0.5)
        self.wait(3.2)

        # 3 · make room: series and trend shrink to the top-left
        top = VGroup(ax, years, yt, series, trend)
        small_t = label("series and trend", 20, CREAM)
        self.play(top.animate.scale(0.5).move_to([-3.55, 1.85, 0]),
                  FadeOut(note2), FadeOut(title), run_time=1.6)
        small_t.next_to(top, UP, buff=0.15)
        self.play(FadeIn(small_t), run_time=0.5)

        # 4 · the twelve seasonal factors, one by one
        sax = Axes(x_range=[0.5, 12.5, 1], y_range=[0.7, 1.3, 0.1], x_length=5.6, y_length=2.4,
                   axis_config=axis_cfg, x_axis_config={"include_ticks": False}).move_to([3.5, 1.85, 0])
        one = DashedLine(sax.c2p(0.5, 1), sax.c2p(12.5, 1), color=MUTED, stroke_width=1.5, dash_length=0.08)
        syt = VGroup(*[label(f"{v:.1f}", 15, MUTED).next_to(sax.c2p(0.5, v), LEFT, buff=0.08) for v in (0.8, 1.0, 1.2)])
        s_title = label("season: the month's factor over the trend", 20, GOLD).next_to(sax, UP, buff=0.15)
        self.play(Create(sax), Create(one), FadeIn(syt), FadeIn(s_title), run_time=1.2)
        self.wait(0.8)

        bars, vals = [], []
        for i, (mo, f) in enumerate(zip(MONTHS, AP_SEASON), start=1):
            bar = Line(sax.c2p(i, 1), sax.c2p(i, f), color=GOLD, stroke_width=7)
            dot = Dot(sax.c2p(i, f), radius=0.06, color=GOLD)
            val = label(f"{f:.2f}", 14, CREAM).next_to(dot, UP if f >= 1 else DOWN, buff=0.1)
            mon = label(mo, 13, MUTED).next_to(sax.c2p(i, 0.7), DOWN, buff=0.08)
            bars.append(VGroup(bar, dot)); vals.append(val)
            self.play(Create(bar), FadeIn(dot), FadeIn(val), FadeIn(mon), run_time=0.4)
            self.wait(0.3)
        self.wait(1.0)
        s_note = label("July 23% above the trend, November 20% below", 20, CREAM).next_to(sax, DOWN, buff=0.45)
        self.play(bars[6].animate.set_color(CREAM), bars[10].animate.set_color(CREAM),
                  vals[6].animate.set_color(CREAM).scale(1.3), vals[10].animate.set_color(CREAM).scale(1.3),
                  FadeIn(s_note), run_time=1.0)
        self.wait(4.2)

        # 5 · the remainder: series ÷ (trend × season)
        rax = Axes(x_range=[0, 144, 12], y_range=[0.85, 1.15, 0.05], x_length=10.6, y_length=1.7,
                   axis_config=axis_cfg).move_to([0, -1.35, 0])
        rone = DashedLine(rax.c2p(0, 1), rax.c2p(144, 1), color=MUTED, stroke_width=1.5, dash_length=0.08)
        ryt = VGroup(*[label(f"{v:.1f}", 15, MUTED).next_to(rax.c2p(0, v), LEFT, buff=0.08) for v in (0.9, 1.0, 1.1)])
        ryrs = VGroup(label("1949", 15, MUTED).next_to(rax.c2p(0, 0.85), DOWN, buff=0.1),
                      label("1960", 15, MUTED).next_to(rax.c2p(144, 0.85), DOWN, buff=0.1))
        r_title = label("remainder: series ÷ (trend × season)", 20, MAUVE).next_to(rax, UP, buff=0.12).align_to(rax, LEFT)
        self.play(FadeOut(s_note), Create(rax), Create(rone), FadeIn(ryt), FadeIn(ryrs), FadeIn(r_title),
                  run_time=1.2)
        rem = [AP[t] / (tr[t] * AP_SEASON[t % 12]) for t in ts]
        rline = rax.plot_line_graph(x_values=ts, y_values=rem, line_color=MAUVE,
                                    add_vertex_dots=False, stroke_width=2.4)
        self.play(Create(rline), run_time=3.0, rate_func=linear)
        r_note = label("what neither trend nor season explains: within ±10%, no pattern left", 20, CREAM)
        r_note.next_to(rax, DOWN, buff=0.4)
        self.play(FadeIn(r_note), run_time=0.8)
        self.wait(4.4)

        # 6 · the model
        formula = MathTex(r"\text{series} = \text{trend} \times \text{season} \times \text{remainder}",
                          color=GOLD, font_size=40).to_edge(DOWN, buff=0.35)
        self.play(FadeTransform(r_note, formula), run_time=1.2)
        self.wait(5.5)


# ---- Section 1: a t-test is an interval that does or does not contain zero
MPG_AUTO = [21.4, 18.7, 18.1, 14.3, 24.4, 22.8, 19.2, 17.8, 16.4, 17.3, 15.2, 10.4, 10.4, 14.7,
            21.5, 15.5, 15.2, 13.3, 19.2]
MPG_MANUAL = [21, 21, 22.8, 32.4, 30.4, 33.9, 27.3, 26, 30.4, 15.8, 19.7, 15, 21.4]
# t.test(mpg ~ am, data = mtcars): t = -3.77, p = 0.0014, CI of (auto - manual) = [-11.28, -3.21]
TT_CI = (3.21, 11.28)


class TwoMeans(Stage):
    """t.test(), watched. Two groups of cars, their means, the gap between
    them, then the 95% interval for that gap growing around it. The whole
    sentence of a t-test is whether zero sits inside that interval."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        rng = np.random.default_rng(3)
        ax = Axes(x_range=[0.3, 2.7, 1], y_range=[5, 40, 5], x_length=4.6, y_length=4.8,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.4},
                  x_axis_config={"include_ticks": False})
        ax.to_edge(LEFT, buff=0.8).shift(DOWN * 0.2)
        yt = VGroup(*[label(str(v), 16, MUTED).next_to(ax.c2p(0.3, v), LEFT, buff=0.1) for v in range(10, 41, 10)])
        yl = label("mpg", 20, MUTED).next_to(ax.y_axis.get_top(), RIGHT, buff=0.15)
        g1 = label("automatic (19)", 20, SKY).next_to(ax.c2p(1, 5), DOWN, buff=0.2)
        g2 = label("manual (13)", 20, GOLD).next_to(ax.c2p(2, 5), DOWN, buff=0.2)
        title = label("do manual cars use less fuel?", 28, CREAM).to_edge(UP, buff=0.35)
        self.play(Create(ax), FadeIn(yt), FadeIn(yl), FadeIn(title), run_time=1.2)

        d1 = VGroup(*[Dot(ax.c2p(1 + rng.uniform(-0.22, 0.22), m), radius=0.065, color=SKY) for m in MPG_AUTO])
        d2 = VGroup(*[Dot(ax.c2p(2 + rng.uniform(-0.22, 0.22), m), radius=0.065, color=GOLD) for m in MPG_MANUAL])
        self.play(FadeIn(d1, lag_ratio=0.05), FadeIn(g1), run_time=1.4)
        self.play(FadeIn(d2, lag_ratio=0.05), FadeIn(g2), run_time=1.2)
        cap = label("thirty-two cars, in two heaps: they overlap", 24, CREAM).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(cap), run_time=0.7)
        self.wait(3.0)

        # the two means
        m1, m2 = float(np.mean(MPG_AUTO)), float(np.mean(MPG_MANUAL))
        l1 = Line(ax.c2p(0.65, m1), ax.c2p(1.35, m1), color=SKY, stroke_width=5)
        l2 = Line(ax.c2p(1.65, m2), ax.c2p(2.35, m2), color=GOLD, stroke_width=5)
        t1 = MathTex(rf"\bar{{x}} = {m1:.1f}", color=SKY, font_size=28).next_to(l1, LEFT, buff=0.12)
        t2 = MathTex(rf"\bar{{x}} = {m2:.1f}", color=GOLD, font_size=28).next_to(l2, RIGHT, buff=0.12)
        new = label("the means: 17.1 and 24.4", 24, CREAM).to_edge(DOWN, buff=0.3)
        self.play(Create(l1), Create(l2), FadeIn(t1), FadeIn(t2), FadeTransform(cap, new), run_time=1.4)
        cap = new
        self.wait(3.0)

        # the difference, as a bracket
        xb = 2.55
        br = Line(ax.c2p(xb, m1), ax.c2p(xb, m2), color=CREAM, stroke_width=3)
        tick1 = Line(ax.c2p(xb - 0.06, m1), ax.c2p(xb + 0.06, m1), color=CREAM, stroke_width=3)
        tick2 = Line(ax.c2p(xb - 0.06, m2), ax.c2p(xb + 0.06, m2), color=CREAM, stroke_width=3)
        dl = DashedLine(ax.c2p(1.35, m1), ax.c2p(xb, m1), color=SKY, stroke_width=1.5, dash_length=0.08)
        dl2 = DashedLine(ax.c2p(2.35, m2), ax.c2p(xb, m2), color=GOLD, stroke_width=1.5, dash_length=0.08)
        diff = MathTex(rf"{m2 - m1:.1f}", color=CREAM, font_size=34).next_to(br, RIGHT, buff=0.12)
        new = label("the difference: 7.2 mpg, in this sample", 24, CREAM).to_edge(DOWN, buff=0.3)
        self.play(Create(dl), Create(dl2), Create(br), FadeIn(tick1), FadeIn(tick2), FadeIn(diff),
                  FadeTransform(cap, new), run_time=1.4)
        cap = new
        self.wait(3.4)

        # a second axis: the difference, with its interval
        dax = Axes(x_range=[0, 1, 1], y_range=[-2, 14, 2], x_length=0.01, y_length=4.4,
                   axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.4},
                   x_axis_config={"stroke_opacity": 0}).move_to([2.6, -0.2, 0])
        dt = VGroup(*[label(str(v), 16, MUTED).next_to(dax.c2p(0, v), LEFT, buff=0.1) for v in (0, 4, 8, 12)])
        dlab = label("difference, mpg", 20, MUTED).next_to(dax.y_axis.get_top(), UP, buff=0.15)
        self.play(Create(dax), FadeIn(dt), FadeIn(dlab), run_time=1.0)
        pt = Dot(dax.c2p(0, m2 - m1), radius=0.09, color=CREAM)
        self.play(FadeTransform(diff.copy(), pt), run_time=1.0)
        self.wait(1.0)

        lo, hi = TT_CI
        se = MathTex(r"7.2 \pm 2.1 \times 1.9", color=CREAM, font_size=30).move_to([4.0, 1.1, 0], aligned_edge=LEFT)
        se_l = VGroup(label("the difference, give or take", 16, MUTED),
                      label("two standard errors", 16, MUTED)).arrange(DOWN, buff=0.06, aligned_edge=LEFT)
        se_l.next_to(se, DOWN, buff=0.12).align_to(se, LEFT)
        new = label("how sure? the gap moves from sample to sample, by about 1.9", 24, CREAM).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(se), FadeIn(se_l), FadeTransform(cap, new), run_time=1.0)
        cap = new
        self.wait(3.4)
        span = ValueTracker(0.0)
        ci = always_redraw(lambda: Line(
            dax.c2p(0, (m2 - m1) - span.get_value() * ((m2 - m1) - lo)),
            dax.c2p(0, (m2 - m1) + span.get_value() * (hi - (m2 - m1))),
            color=CREAM, stroke_width=7))
        new = label("the 95% interval for the true difference: 3.2 to 11.3", 24, CREAM).to_edge(DOWN, buff=0.3)
        self.add(ci)
        self.play(span.animate.set_value(1.0), FadeTransform(cap, new), run_time=2.0)
        cap = new
        e_lo = label(f"{lo:.1f}", 18, CREAM).next_to(dax.c2p(0, lo), RIGHT, buff=0.15)
        e_hi = label(f"{hi:.1f}", 18, CREAM).next_to(dax.c2p(0, hi), RIGHT, buff=0.15)
        self.play(FadeIn(e_lo), FadeIn(e_hi), run_time=0.6)
        self.wait(3.6)

        # zero, and where it is
        zero = Dot(dax.c2p(0, 0), radius=0.11, color=GOLD)
        zl = label("0", 26, GOLD).next_to(zero, RIGHT, buff=0.15)
        zero_note = label("no difference at all", 18, GOLD).next_to(zl, RIGHT, buff=0.15)
        new = label("zero is outside the interval: that is the whole test", 24, GOLD).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(zero, scale=1.8), FadeIn(zl), FadeIn(zero_note), FadeTransform(cap, new), run_time=1.0)
        cap = new
        self.wait(3.6)

        stat = MathTex(r"t = -3.77,\ \ p = 0.001", color=CREAM, font_size=28).next_to(se_l, DOWN, buff=0.5).align_to(se, LEFT)
        self.play(FadeIn(stat), run_time=0.8)
        self.wait(1.6)
        closing = label("p says the same thing as the interval; the interval also says how much", 23, CREAM).to_edge(DOWN, buff=0.3)
        self.play(FadeTransform(cap, closing), run_time=1.0)
        self.wait(4.6)


# ---- Section 3: a straight line for a yes/no, and the bend that fixes it
MT_AM = [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1]
LPM_A, LPM_B = 1.5424, -0.3532         # lm(am ~ wt)
LOGIT_A, LOGIT_B = 12.040, -4.024       # glm(am ~ wt, binomial)


class LogitCurve(Stage):
    """glm(binomial), watched. Thirty-two cars at 0 or 1, the straight line
    lm() would fit and the places it leaves the unit interval, then the same
    line bent into the logistic curve, and two probabilities read off it."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        ax = Axes(x_range=[1, 6, 1], y_range=[-0.4, 1.4, 0.5], x_length=8.2, y_length=4.6,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.4},
                  y_axis_config={"include_ticks": False})
        ax.to_edge(LEFT, buff=0.7).shift(DOWN * 0.25)
        xt = VGroup(*[label(str(v), 16, MUTED).next_to(ax.c2p(v, -0.4), DOWN, buff=0.1) for v in range(1, 7)])
        xl = label("weight, 1 000 lb", 20, MUTED).next_to(ax.x_axis, DOWN, buff=0.4)
        yl = label("manual?", 20, MUTED).next_to(ax.y_axis.get_top(), RIGHT, buff=0.15)
        zero = DashedLine(ax.c2p(1, 0), ax.c2p(6, 0), color=MUTED, stroke_width=1.5, dash_length=0.08)
        one = DashedLine(ax.c2p(1, 1), ax.c2p(6, 1), color=MUTED, stroke_width=1.5, dash_length=0.08)
        y0 = label("0 = automatic", 16, MUTED).next_to(ax.c2p(1.05, 0), DR, buff=0.08)
        y1 = label("1 = manual", 16, MUTED).next_to(ax.c2p(1.05, 1), UR, buff=0.08)
        title = label("is this car a manual? a yes/no against weight", 28, CREAM).to_edge(UP, buff=0.35)
        self.play(Create(ax), FadeIn(xt), FadeIn(xl), FadeIn(yl), Create(zero), Create(one),
                  FadeIn(y0), FadeIn(y1), FadeIn(title), run_time=1.4)
        dots = VGroup(*[Dot(ax.c2p(w, y), radius=0.07, color=GOLD if y else SKY) for w, y in zip(MT_WT, MT_AM)])
        dots.set_z_index(3)
        self.play(FadeIn(dots, lag_ratio=0.03), run_time=1.6)
        cap = label("every answer is 0 or 1: nothing in between is observed", 24, CREAM).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(cap), run_time=0.7)
        self.wait(3.0)

        # the straight line lm() would draw
        lpm = ax.plot(lambda w: LPM_A + LPM_B * w, x_range=[1.1, 5.9], color=CREAM, stroke_width=3.5)
        eq1 = MathTex(r"\text{lm}:\ \ \hat{y} = 1.54 - 0.35\,\text{wt}", color=CREAM, font_size=30)
        eq1.to_corner(UR, buff=0.5).shift(DOWN * 0.4 + LEFT * 0.1)
        new = label("a straight line through 0s and 1s", 24, CREAM).to_edge(DOWN, buff=0.3)
        self.play(Create(lpm), FadeIn(eq1), FadeTransform(cap, new), run_time=1.6)
        cap = new
        self.wait(2.4)

        # where it leaves [0, 1]
        bad = "#e2725b"
        wl, wh = 1.3, 5.4
        pl, ph = LPM_A + LPM_B * wl, LPM_A + LPM_B * wh
        c_lo = Dot(ax.c2p(wh, ph), radius=0.1, color=bad)
        c_hi = Dot(ax.c2p(wl, pl), radius=0.1, color=bad)
        n_lo = MathTex(rf"\hat{{y}}({wh}) = {ph:.2f}", color=bad, font_size=28).next_to(c_lo, DOWN, buff=0.15)
        n_hi = MathTex(rf"\hat{{y}}({wl}) = {pl:.2f}", color=bad, font_size=28).next_to(c_hi, UP, buff=0.15)
        new = label("a probability below 0 for a heavy car, above 1 for a light one: nonsense", 24, bad).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(c_lo, scale=1.6), FadeIn(n_lo), FadeTransform(cap, new), run_time=1.0)
        cap = new
        self.wait(1.6)
        self.play(FadeIn(c_hi, scale=1.6), FadeIn(n_hi), run_time=1.0)
        self.wait(3.2)

        # the bend
        def logit(w):
            return 1 / (1 + np.exp(-(LOGIT_A + LOGIT_B * w)))

        curve = ax.plot(logit, x_range=[1.1, 5.9], color=GOLD, stroke_width=4)
        eq2 = MathTex(r"\text{glm}:\ \ P(\text{manual}) = \frac{1}{1 + e^{-(12.0 - 4.02\,\text{wt})}}",
                      color=GOLD, font_size=30).move_to(eq1, aligned_edge=RIGHT)
        new = label("the same line, bent: it can only run between 0 and 1", 24, GOLD).to_edge(DOWN, buff=0.3)
        self.play(FadeOut(c_lo), FadeOut(c_hi), FadeOut(n_lo), FadeOut(n_hi), run_time=0.5)
        self.play(Transform(lpm, curve), FadeTransform(eq1, eq2), FadeTransform(cap, new), run_time=2.4)
        cap = new
        self.wait(3.2)

        # read two probabilities off it
        def guide(w, colour):
            p = logit(w)
            v = DashedLine(ax.c2p(w, -0.4), ax.c2p(w, p), color=colour, stroke_width=2, dash_length=0.08)
            h = DashedLine(ax.c2p(w, p), ax.c2p(1, p), color=colour, stroke_width=2, dash_length=0.08)
            d = Dot(ax.c2p(w, p), radius=0.09, color=colour).set_z_index(4)
            t = MathTex(rf"P(\text{{manual}} \mid \text{{wt}} = {w}) = {p:.2f}", color=colour, font_size=30)
            return VGroup(v, h, d), t

        g1, t1 = guide(2.5, CREAM)
        t1.next_to(eq2, DOWN, buff=0.5).align_to(eq2, RIGHT)
        a1 = MathTex(r"12.0 - 4.02 \times 2.5 = 1.98,\quad \tfrac{1}{1+e^{-1.98}} = 0.88",
                     color=CREAM, font_size=24).next_to(t1, DOWN, buff=0.12).align_to(eq2, RIGHT)
        new = label("a light car: read up to the curve, across to the axis", 24, CREAM).to_edge(DOWN, buff=0.3)
        self.play(Create(g1), FadeIn(t1), FadeTransform(cap, new), run_time=1.4)
        cap = new
        self.wait(1.4)
        self.play(FadeIn(a1), run_time=0.8)
        self.wait(3.0)
        g2, t2 = guide(3.5, SKY)
        t2.next_to(a1, DOWN, buff=0.35).align_to(eq2, RIGHT)
        a2 = MathTex(r"12.0 - 4.02 \times 3.5 = -2.04,\quad \tfrac{1}{1+e^{2.04}} = 0.11",
                     color=SKY, font_size=24).next_to(t2, DOWN, buff=0.12).align_to(eq2, RIGHT)
        new = label("a thousand pounds heavier: the same arithmetic, a different answer", 24, SKY).to_edge(DOWN, buff=0.3)
        self.play(Create(g2), FadeIn(t2), FadeTransform(cap, new), run_time=1.4)
        cap = new
        self.wait(1.4)
        self.play(FadeIn(a2), run_time=0.8)
        self.wait(3.0)

        closing = label("one thousand pounds, from 88% to 11%: that is what the slope means", 24, CREAM).to_edge(DOWN, buff=0.3)
        self.play(FadeTransform(cap, closing), run_time=1.0)
        self.wait(4.6)


# ---- Section 4: the LASSO path, coefficient by coefficient
LASSO_NAMES = ["cyl", "disp", "hp", "drat", "wt", "qsec", "vs", "am", "gear", "carb"]
# coef(glmnet(x, y, alpha = 1), s = lambda, exact = TRUE), lambda on a 0.05 grid; row 0 is OLS
LASSO_PATH = [
    (0.00, [-0.1001, 0.0132, -0.0214, 0.7940, -3.7035, 0.8213, 0.3247, 2.5235, 0.6654, -0.2062]),
    (0.05, [-0.0668, 0.0000, -0.0130, 0.8502, -2.6270, 0.5592, 0.1372, 2.2921, 0.5216, -0.5403]),
    (0.10, [-0.2234, 0.0000, -0.0131, 0.7717, -2.6316, 0.4568, 0.1190, 2.1100, 0.3042, -0.4649]),
    (0.15, [-0.3727, 0.0000, -0.0131, 0.6972, -2.6345, 0.3566, 0.1066, 1.9322, 0.0949, -0.3926]),
    (0.20, [-0.5005, 0.0000, -0.0133, 0.6082, -2.6191, 0.2613, 0.0813, 1.7003, 0.0000, -0.3432]),
    (0.25, [-0.6068, 0.0000, -0.0138, 0.5091, -2.5906, 0.1705, 0.0501, 1.4242, 0.0000, -0.3127]),
    (0.30, [-0.7115, 0.0000, -0.0142, 0.4115, -2.5619, 0.0797, 0.0217, 1.1498, 0.0000, -0.2826]),
    (0.35, [-0.8053, 0.0000, -0.0146, 0.3094, -2.5434, 0.0000, 0.0000, 0.8935, 0.0000, -0.2486]),
    (0.40, [-0.8230, 0.0000, -0.0144, 0.2298, -2.5896, 0.0000, 0.0000, 0.7544, 0.0000, -0.2009]),
    (0.45, [-0.8412, 0.0000, -0.0143, 0.1484, -2.6350, 0.0000, 0.0000, 0.6159, 0.0000, -0.1528]),
    (0.50, [-0.8580, 0.0000, -0.0141, 0.0723, -2.6780, 0.0000, 0.0000, 0.4797, 0.0000, -0.1059]),
    (0.55, [-0.8743, 0.0000, -0.0139, 0.0000, -2.7233, 0.0000, 0.0000, 0.3383, 0.0000, -0.0586]),
    (0.60, [-0.8787, 0.0000, -0.0137, 0.0000, -2.7558, 0.0000, 0.0000, 0.1817, 0.0000, -0.0183]),
    (0.65, [-0.8912, 0.0000, -0.0131, 0.0000, -2.7758, 0.0000, 0.0000, 0.0478, 0.0000, 0.0000]),
    (0.70, [-0.8943, 0.0000, -0.0125, 0.0000, -2.7646, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000]),
    (0.80, [-0.8864, 0.0000, -0.0117, 0.0000, -2.7074, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000]),
    (0.90, [-0.8803, 0.0000, -0.0109, 0.0000, -2.6493, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000]),
    (1.00, [-0.8732, 0.0000, -0.0101, 0.0000, -2.5921, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000]),
    (1.10, [-0.8660, 0.0000, -0.0093, 0.0000, -2.5350, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000]),
    (1.20, [-0.8589, 0.0000, -0.0085, 0.0000, -2.4777, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000]),
    (1.30, [-0.8517, 0.0000, -0.0077, 0.0000, -2.4205, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000]),
    (1.40, [-0.8446, 0.0000, -0.0070, 0.0000, -2.3632, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000]),
]


def lasso_coefs(lam):
    """Linear interpolation on the grid: a coefficient that is zero at a grid
    point reaches zero exactly there, as glmnet's path does."""
    xs = [l for l, _ in LASSO_PATH]
    i = int(np.searchsorted(xs, lam, side="right")) - 1
    i = max(0, min(i, len(xs) - 2))
    l0, c0 = LASSO_PATH[i]
    l1, c1 = LASSO_PATH[i + 1]
    t = 0.0 if l1 == l0 else (lam - l0) / (l1 - l0)
    t = max(0.0, min(1.0, t))
    return [a + t * (b - a) for a, b in zip(c0, c1)]


class ShrinkPath(Stage):
    """glmnet(alpha = 1), watched. Ten OLS coefficients as bars; the penalty
    grows and the bars shrink, and seven of them reach exactly zero, one after
    another, in the order the data decide. What is left at lambda.1se is the
    model the deck prints: cyl, hp, wt."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        title = label("ten predictors of mpg, and a penalty that grows", 28, CREAM).to_edge(UP, buff=0.35)
        self.play(FadeIn(title), run_time=0.8)

        nl = NumberLine(x_range=[-4, 3, 1], length=6.6, color=MUTED, stroke_width=1.4,
                        include_numbers=False).move_to([0.6, -0.3, 0])
        nums = VGroup(*[label(str(v), 15, MUTED).next_to(nl.n2p(v), DOWN, buff=0.1) for v in range(-4, 4)])
        axis_l = label("coefficient", 18, MUTED).next_to(nl, DOWN, buff=0.35)
        rows_y = [2.35 - 0.52 * i for i in range(10)]
        nl.shift(DOWN * (nl.get_center()[1] - (rows_y[-1] - 0.45)))
        nums.next_to(nl, DOWN, buff=0.1)
        for n, v in zip(nums, range(-4, 4)):
            n.next_to(nl.n2p(v), DOWN, buff=0.1)
        axis_l.next_to(nums, DOWN, buff=0.15)
        zero_line = Line([nl.n2p(0)[0], rows_y[0] + 0.3, 0], [nl.n2p(0)[0], rows_y[-1] - 0.3, 0],
                         color=MUTED, stroke_width=1.2)
        self.play(Create(nl), FadeIn(nums), FadeIn(axis_l), Create(zero_line), run_time=1.0)

        lam = ValueTracker(0.0)
        style = {"gold": set()}

        def coef(i):
            return lasso_coefs(lam.get_value())[i]

        names, bars, vals = VGroup(), VGroup(), VGroup()
        for i, nm in enumerate(LASSO_NAMES):
            y = rows_y[i]
            names.add(label(nm, 20, CREAM).move_to([nl.n2p(-4)[0] - 0.75, y, 0]))

            def make_bar(i=i, y=y):
                c = coef(i)
                x0, x1 = nl.n2p(0)[0], nl.n2p(c)[0]
                alive = abs(c) > 1e-9
                r = Rectangle(width=max(abs(x1 - x0), 0.004), height=0.34, stroke_width=0,
                              fill_color=(GOLD if i in style["gold"] else SKY) if alive else MUTED,
                              fill_opacity=0.9 if alive else 0.35)
                r.move_to([(x0 + x1) / 2, y, 0])
                return r

            def make_val(i=i, y=y):
                c = coef(i)
                alive = abs(c) > 1e-9
                places = 3 if LASSO_NAMES[i] == "hp" else 2
                d = DecimalNumber(c, num_decimal_places=places, font_size=20,
                                  color=CREAM if alive else MUTED)
                side = RIGHT if c >= 0 else LEFT
                return d.next_to(nl.n2p(c), side, buff=0.1).shift(UP * (y - nl.n2p(c)[1]))

            bars.add(always_redraw(make_bar))
            vals.add(always_redraw(make_val))

        self.play(FadeIn(names, lag_ratio=0.05), FadeIn(bars, lag_ratio=0.05), FadeIn(vals, lag_ratio=0.05), run_time=1.6)
        cap = label("λ = 0 is plain least squares: all ten columns in, none of them zero", 24, CREAM).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(cap), run_time=0.7)
        self.wait(3.0)

        # the slider and the counter, top right
        sl = NumberLine(x_range=[0, 1.6, 0.4], length=3.6, color=MUTED, stroke_width=1.4,
                        include_numbers=False).move_to([4.4, 2.0, 0])
        sl_n = VGroup(*[label(f"{v:.1f}", 14, MUTED).next_to(sl.n2p(v), DOWN, buff=0.08) for v in (0, 0.4, 0.8, 1.2, 1.6)])
        knob = always_redraw(lambda: Dot(sl.n2p(lam.get_value()), radius=0.1, color=GOLD))
        lam_l = MathTex(r"\lambda = ", color=GOLD, font_size=34).next_to(sl, UP, buff=0.35).align_to(sl, LEFT)
        lam_n = DecimalNumber(0.0, num_decimal_places=2, color=GOLD, font_size=34).next_to(lam_l, RIGHT, buff=0.1)
        lam_n.add_updater(lambda m: m.set_value(lam.get_value()).next_to(lam_l, RIGHT, buff=0.1))
        cnt_l = label("columns left", 20, MUTED).next_to(sl_n, DOWN, buff=0.45).align_to(sl, LEFT)
        cnt_n = Integer(10, color=CREAM, font_size=44).next_to(cnt_l, DOWN, buff=0.1).align_to(sl, LEFT)
        cnt_n.add_updater(lambda m: m.set_value(sum(abs(c) > 1e-9 for c in lasso_coefs(lam.get_value()))))
        self.play(Create(sl), FadeIn(sl_n), FadeIn(knob), FadeIn(lam_l), FadeIn(lam_n), FadeIn(cnt_l), FadeIn(cnt_n), run_time=1.0)
        self.wait(1.2)

        # grow the penalty, stopping where a coefficient dies
        stages = [
            (0.05, "disp goes first: 0.013 was never far from zero"),
            (0.20, "gear is next"),
            (0.35, "qsec and vs, together"),
            (0.55, "drat"),
            (0.65, "carb"),
            (0.70, "am: the one a t-test said mattered — but wt already carries it"),
            (1.40, "λ.1se = 1.40, where cv.glmnet stops: three columns left"),
        ]
        for target, text in stages:
            new = label(text, 24, GOLD if target == 1.40 else CREAM).to_edge(DOWN, buff=0.3)
            dur = 1.2 + 2.2 * (target - lam.get_value())
            self.play(lam.animate.set_value(target), FadeTransform(cap, new), run_time=dur, rate_func=linear)
            cap = new
            self.wait(2.2 if target < 1.40 else 1.0)

        # the survivors
        keep = [0, 2, 4]
        final = [lasso_coefs(1.40)[i] for i in keep]
        style["gold"].update(keep)
        self.play(*[names[i].animate.set_color(GOLD) for i in keep], run_time=0.8)
        tag = VGroup(*[MathTex(rf"\text{{{LASSO_NAMES[i]}}}: {v:.3f}" if LASSO_NAMES[i] == "hp" else
                              rf"\text{{{LASSO_NAMES[i]}}}: {v:.2f}", color=GOLD, font_size=28)
                       for i, v in zip(keep, final)]).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
        tag.next_to(cnt_n, DOWN, buff=0.5).align_to(sl, LEFT)
        self.play(FadeIn(tag), run_time=0.8)
        self.wait(2.6)
        err = VGroup(label("cross-validated error", 18, MUTED),
                     label("OLS 20.9  →  LASSO 9.8", 24, GOLD)).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        err.next_to(tag, DOWN, buff=0.5).align_to(sl, LEFT)
        new = label("three columns predict better than ten: the seven were noise", 24, GOLD).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(err), FadeTransform(cap, new), run_time=1.0)
        cap = new
        self.wait(3.6)
        closing = label("seven coefficients are exactly zero, not merely small: the penalty chose", 24, CREAM).to_edge(DOWN, buff=0.3)
        self.play(FadeTransform(cap, closing), run_time=1.0)
        self.wait(4.6)


LAB = ["TwoMeans", "LeastSquares", "LogitCurve", "ShrinkPath", "Decompose"]
L11 = ["Lloyd", "KmeansByHand", "ScaleBreaks", "ShapeBreaks", "ElbowLie"]
# Lectures 12, 14, 18 and 19 have a file each, scenes_NN.py, which imports this one.
SCENES = L11 + LAB

