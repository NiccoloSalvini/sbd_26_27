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
    return Text(s, font=FONT, font_size=size, color=color)


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


class PerceptronByHand(Stage):
    """The AND table, every row and every number. Epoch 1 at speaking pace, the
    rest a little quicker; W moves only on the rows marked wrong. About 160 s."""
    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        ax = and_axes(4.4).to_edge(LEFT, buff=0.55).shift(DOWN * 0.35)
        dots = and_dots(ax)
        self.add(ax, dots, and_legend(dots))
        # the three rules stay up, small and muted, while the numbers change under them
        rules = VGroup(
            MathTex(r"z = W_1 X_1 + W_2 X_2", color=MUTED, font_size=28),
            MathTex(r"\hat y = 1 \text{ if } z \ge \theta,\ \text{else } 0", color=MUTED, font_size=28),
            MathTex(r"W \leftarrow W + \eta\,(y - \hat y)\,X", color=MUTED, font_size=28),
            MathTex(rf"\theta = {num(THETA)},\quad \eta = {num(ETA)}", color=MUTED, font_size=28),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.14).to_corner(UR, buff=0.45)
        self.play(FadeIn(rules), run_time=1.0)
        self.wait(2.0)
        w = W0
        wlab = w_tex(w).next_to(ax, DOWN, buff=0.25)
        bnd = and_boundary(ax, w)
        self.play(Create(bnd), Write(wlab), run_time=1.2)
        self.wait(2.5)

        epoch_lab = label("epoch 1", 30, GOLD).next_to(ax, UP, buff=0.25).align_to(ax, LEFT)
        self.play(FadeIn(epoch_lab), run_time=0.6)
        panel_corner = np.array([ax.get_right()[0] + 0.7, rules.get_bottom()[1] - 0.55, 0])

        for r in perceptron_run():
            pace = 1.0 if r["epoch"] == 1 else 0.7
            x1, x2 = r["x"]
            y, z, yhat, err = r["y"], r["z"], r["yhat"], r["err"]
            wb, wa = r["before"], r["after"]
            wrong = err != 0
            ring = Circle(radius=0.22, color=GOLD if wrong else CREAM, stroke_width=3).move_to(dots[r["i"]])

            hdr = VGroup(label(f"obs {r['i'] + 1}", 28, CREAM),
                         MathTex(rf"X = ({x1},\,{x2}),\quad y = {y}", color=CREAM, font_size=34)).arrange(RIGHT, buff=0.35)
            zl = MathTex(rf"z = {num(wb[0])} \cdot {x1} \;+\; {par(wb[1])} \cdot {x2} \;=\; {num(z)}", color=CREAM, font_size=34)
            rel = r"\ge" if z >= THETA else "<"
            cl = MathTex(rf"{num(z)} {rel} {num(THETA)} \;\Rightarrow\; \hat y = {yhat}", color=CREAM, font_size=34)
            if wrong:
                el = VGroup(MathTex(rf"y - \hat y = {y} - {yhat} = {err:+d}", color=GOLD, font_size=34),
                            label("wrong", 26, GOLD)).arrange(RIGHT, buff=0.4)
                ul = MathTex(rf"W \leftarrow ({num(wb[0])},\ {num(wb[1])}) + {num(ETA)} \cdot ({err:+d}) \cdot ({x1},\,{x2})"
                             rf" = ({num(wa[0])},\ {num(wa[1])})", color=GOLD, font_size=34)
                lines = VGroup(hdr, zl, cl, el, ul)
            else:
                el = VGroup(MathTex(rf"y - \hat y = {y} - {yhat} = 0", color=MUTED, font_size=34),
                            label("right, nothing changes", 26, MUTED)).arrange(RIGHT, buff=0.4)
                lines = VGroup(hdr, zl, cl, el)
            lines.arrange(DOWN, aligned_edge=LEFT, buff=0.32).move_to(panel_corner, aligned_edge=UL)

            self.play(Create(ring), FadeIn(hdr), run_time=0.6 * pace)
            self.wait(1.2 * pace)
            self.play(Write(zl), run_time=1.0 * pace)
            self.wait(1.6 * pace)
            self.play(Write(cl), run_time=0.8 * pace)
            self.wait(1.4 * pace)
            self.play(Write(el), run_time=0.8 * pace)
            self.wait(1.2 * pace)
            if wrong:
                self.play(Write(ul), run_time=1.2 * pace)
                self.wait(1.4 * pace)
                new_w = w_tex(wa).next_to(ax, DOWN, buff=0.25)
                self.play(Transform(bnd, and_boundary(ax, wa)), Transform(wlab, new_w), run_time=1.4)
                self.wait(1.8 * pace)
            self.play(FadeOut(lines), FadeOut(ring), run_time=0.4)

            if r["last"]:
                m = r["mistakes"]
                tally = label(f"epoch {r['epoch']}: {m} mistake{'s' if m != 1 else ''}", 30, GOLD if m else SKY)
                tally.move_to(panel_corner, aligned_edge=UL)
                self.play(FadeIn(tally), run_time=0.5)
                self.wait(2.0)
                if m == 0:
                    done = VGroup(label("a whole epoch with no mistake:", 28, CREAM),
                                  label("nothing will ever change again. Converged.", 28, CREAM)
                                  ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).next_to(tally, DOWN, aligned_edge=LEFT, buff=0.5)
                    self.play(FadeIn(done), run_time=0.8)
                    self.wait(4.0)
                else:
                    nxt = label(f"epoch {r['epoch'] + 1}", 30, GOLD).move_to(epoch_lab, aligned_edge=LEFT)
                    self.play(FadeOut(tally), Transform(epoch_lab, nxt), run_time=0.6)
                    self.wait(0.8)


class Perceptron(Stage):
    """The same run as geometry only: every row gets a ring on the point and a
    status line under the plot, the boundary turns on each mistake, an epoch
    with no mistake ends it. ~55 s."""
    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        ax = and_axes(5.6).to_edge(LEFT, buff=0.8).shift(DOWN * 0.2)
        dots = and_dots(ax)
        self.add(ax, dots, and_legend(dots))
        rule = MathTex(r"\hat y = 1 \text{ if } W_1 X_1 + W_2 X_2 \ge \theta", color=CREAM, font_size=34)
        upd = MathTex(r"W \leftarrow W + \eta\,(y - \hat y)\,X", color=GOLD, font_size=34)
        right = VGroup(rule, upd).arrange(DOWN, aligned_edge=LEFT, buff=0.35).to_edge(RIGHT, buff=0.7).shift(UP * 2.0)
        self.play(Write(rule), run_time=1.0)
        self.play(Write(upd), run_time=0.8)
        self.wait(1.5)
        w = W0
        wlab = w_tex(w, 36).next_to(right, DOWN, aligned_edge=LEFT, buff=0.7)
        epoch_lab = label("epoch 1", 30, GOLD).next_to(wlab, DOWN, aligned_edge=LEFT, buff=0.5)
        count = label("mistakes so far: 0", 26, MUTED).next_to(epoch_lab, DOWN, aligned_edge=LEFT, buff=0.3)
        bnd = and_boundary(ax, w)
        self.play(Create(bnd), FadeIn(wlab), FadeIn(epoch_lab), FadeIn(count), run_time=1.0)
        self.wait(2.0)
        total = 0
        for r in perceptron_run():
            wrong = r["err"] != 0
            d = dots[r["i"]]
            ring = Circle(radius=0.24, color=GOLD if wrong else CREAM, stroke_width=3).move_to(d)
            tag = label(f"obs {r['i'] + 1}: {'wrong' if wrong else 'right'}", 26, GOLD if wrong else MUTED).next_to(ax, DOWN, buff=0.3)
            self.play(Create(ring), FadeIn(tag), run_time=0.5)
            self.wait(0.9)
            if wrong:
                total += 1
                self.play(Transform(bnd, and_boundary(ax, r["after"])),
                          Transform(wlab, w_tex(r["after"], 36).move_to(wlab, aligned_edge=LEFT)),
                          Transform(count, label(f"mistakes so far: {total}", 26, MUTED).move_to(count, aligned_edge=LEFT)),
                          run_time=1.3)
                self.wait(1.4)
            self.play(FadeOut(ring), FadeOut(tag), run_time=0.3)
            if r["last"]:
                m = r["mistakes"]
                if m == 0:
                    ok = label("an epoch with no mistake — it stops", 28, GOLD).to_edge(DOWN, buff=0.4)
                    self.play(FadeIn(ok), run_time=0.6)
                    self.wait(3.5)
                else:
                    self.play(Transform(epoch_lab, label(f"epoch {r['epoch'] + 1}", 30, GOLD).move_to(epoch_lab, aligned_edge=LEFT)), run_time=0.5)
                    self.wait(0.8)


# ---------------------------------------------------------------- 1. motivation
class Boundary(Stage):
    """Why a curve at all. A line is tried, its mistakes are counted, it is
    rotated and counted again; no angle gets below twelve. Then the curve, then
    the fact that the curve is three lines blended — which is Section 5."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        rng = np.random.default_rng(3)
        ax = Axes(x_range=[-3, 3, 1], y_range=[-2.2, 2.2, 1], x_length=8.4, y_length=4.6,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.5}).shift(UP * 0.25)
        self.play(Create(ax), run_time=1.0)

        truth = lambda x: 0.9 * np.sin(1.3 * x)
        data = []
        for _ in range(60):
            x, y = rng.uniform(-2.8, 2.8), rng.uniform(-2, 2)
            data.append((x, y, y > truth(x)))
        dots = VGroup(*[Dot(ax.c2p(x, y), radius=0.062, color=(GOLD if above else SKY)) for x, y, above in data])
        self.play(FadeIn(dots, lag_ratio=0.03), run_time=1.6)
        self.wait(1.4)

        # a counter that means something: how many points the rule gets wrong
        def miscount(fn):
            return sum(1 for x, y, above in data if (y > fn(x)) != above)

        tally = VGroup(label("wrong", 24, MUTED), Integer(0, color=GOLD, font_size=46)).arrange(RIGHT, buff=0.3)
        tally.to_corner(UR, buff=0.5)

        slopes = [0.0, 0.55, -0.5, 0.22]
        first = lambda x: 0.0 * x
        line = ax.plot(first, color=CREAM, stroke_width=4)
        cap = label("one straight line", 26, CREAM).next_to(ax, DOWN, buff=0.3)
        tally[1].set_value(miscount(first))
        self.play(Create(line), FadeIn(cap), FadeIn(tally), run_time=1.2)
        self.wait(3.0)

        # rotate it and let the count speak for itself
        for s in slopes[1:]:
            fn = lambda x, s=s: s * x
            new = ax.plot(fn, color=CREAM, stroke_width=4)
            self.play(Transform(line, new),
                      ChangeDecimalToValue(tally[1], miscount(fn)), run_time=1.8)
            self.wait(2.2)

        verdict = label("no straight line gets below twelve", 26, CREAM).next_to(ax, DOWN, buff=0.3)
        self.play(FadeTransform(cap, verdict), run_time=1.0)
        self.wait(3.4)

        curve = ax.plot(truth, color=GOLD, stroke_width=5)
        cap2 = label("one curve", 26, GOLD).next_to(ax, DOWN, buff=0.3)
        self.play(Transform(line, curve), FadeTransform(verdict, cap2),
                  ChangeDecimalToValue(tally[1], miscount(truth)), run_time=2.6)
        self.wait(3.6)

        # where the curve comes from — three bends, blended. Section 5, foreshadowed.
        pieces = VGroup(
            ax.plot(lambda x: 1.15 * np.tanh(2.2 * (x + 1.7)) - 0.35, color=SKY, stroke_width=2.5, stroke_opacity=0.9),
            ax.plot(lambda x: -1.3 * np.tanh(2.0 * x), color=SKY, stroke_width=2.5, stroke_opacity=0.9),
            ax.plot(lambda x: 1.15 * np.tanh(2.2 * (x - 1.7)) + 0.35, color=SKY, stroke_width=2.5, stroke_opacity=0.9),
        )
        cap3 = label("three simple bends, added together", 26, SKY).next_to(ax, DOWN, buff=0.3)
        self.play(FadeTransform(cap2, cap3), run_time=0.8)
        for pc in pieces:
            self.play(Create(pc), run_time=1.1)
            self.wait(1.2)
        self.wait(2.6)
        self.play(FadeOut(pieces), run_time=1.0)
        self.wait(2.0)


# ---------------------------------------------------------------- 3. gradient descent
class GradientDescent(Stage):
    """One bowl, three learning rates, and the arithmetic of every step on
    screen. The point is not that a dot rolls downhill; it is that each step is
    the old weight minus eta times a slope you can read."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    F = staticmethod(lambda w: (w - 2.0) ** 2)
    G = staticmethod(lambda w: 2.0 * (w - 2.0))     # dL/dW

    def construct(self):
        ax = Axes(x_range=[-1.2, 5.4, 1], y_range=[0, 9, 3], x_length=7.4, y_length=4.4,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.5}).to_edge(LEFT, buff=0.7).shift(DOWN * 0.2)
        curve = ax.plot(self.F, color=SKY, stroke_width=4)
        self.play(Create(ax), Create(curve), run_time=1.4)
        self.play(FadeIn(MathTex(r"L(W) = (W-2)^2", color=SKY, font_size=32).next_to(ax, UP, buff=0.2)), run_time=0.8)

        rule = MathTex(r"W_{t+1} = W_t - \eta\,\frac{\partial L}{\partial W}", color=CREAM, font_size=38)
        rule.to_corner(UR, buff=0.7).shift(LEFT * 0.2)
        self.play(Write(rule), run_time=1.4)
        self.wait(1.8)

        def run(eta, steps, colour, title, show_arithmetic):
            head = MathTex(title, color=colour, font_size=34).next_to(rule, DOWN, buff=0.5).align_to(rule, LEFT)
            self.play(FadeIn(head), run_time=0.7)
            w = 4.8
            dot = Dot(ax.c2p(w, self.F(w)), color=colour, radius=0.1)
            self.play(FadeIn(dot, scale=1.6), run_time=0.6)
            self.wait(0.8)
            trail, lines = VGroup(), []
            for k in range(steps):
                g = self.G(w)
                wn = w - eta * g
                if show_arithmetic and k < 3:
                    # the step, written out with the numbers of this step
                    expr = MathTex(rf"{w:.2f} - {eta}\times({g:.2f}) = {wn:.2f}", color=colour, font_size=30)
                    expr.next_to(head, DOWN, buff=0.35 + 0.45 * k).align_to(head, LEFT)
                    self.play(FadeIn(expr, shift=RIGHT * 0.2), run_time=0.8)
                    lines.append(expr)
                    self.wait(1.0)
                wn_c = max(-1.15, min(5.35, wn))
                seg = Line(ax.c2p(w, self.F(w)), ax.c2p(wn_c, self.F(wn_c)),
                           color=colour, stroke_width=2.5, stroke_opacity=0.8)
                trail.add(seg)
                self.play(Create(seg), dot.animate.move_to(ax.c2p(wn_c, self.F(wn_c))),
                          run_time=0.45 if k < 3 else 0.28)
                w = wn
            self.wait(1.4)
            self.play(FadeOut(VGroup(head, dot, trail, *lines)), run_time=0.8)

        run(0.3, 8, GOLD, r"\eta = 0.3\ \ \text{(right)}", True)
        self.wait(0.6)
        run(0.03, 26, SKY, r"\eta = 0.03\ \ \text{(too small: 26 steps, still short)}", True)
        self.wait(0.6)
        run(1.05, 7, "#e2725b", r"\eta = 1.05\ \ \text{(too large: it climbs the far wall)}", True)

        closing = label("the minus sign is the whole idea", 28, CREAM).next_to(ax, DOWN, buff=0.35)
        self.play(FadeIn(closing), run_time=1.0)
        self.wait(2.2)


# ---------------------------------------------------------------- 4. one neuron = GLM
class Sigmoid(Stage):
    """Why the step had to go: its derivative is zero everywhere, so there is
    nothing for gradient descent to descend. The sigmoid fixes exactly that, and
    hands back a probability while it is at it."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        ax = Axes(x_range=[-6, 6, 2], y_range=[-0.15, 1.15, 0.5], x_length=8.6, y_length=3.4,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.5}).shift(UP * 1.15)
        dax = Axes(x_range=[-6, 6, 2], y_range=[0, 0.3, 0.1], x_length=8.6, y_length=1.5,
                   axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.2}).shift(DOWN * 1.9)
        self.play(Create(ax), run_time=0.9)
        self.play(FadeIn(MathTex(r"\lambda = W_0 + \textstyle\sum_j W_j X_j", color=MUTED, font_size=26)
                         .next_to(dax, DOWN, buff=0.25)), run_time=0.7)

        step = VGroup(ax.plot(lambda x: 0, x_range=[-6, -0.02], color=SKY, stroke_width=4),
                      ax.plot(lambda x: 1, x_range=[0.02, 6], color=SKY, stroke_width=4),
                      DashedLine(ax.c2p(0, 0), ax.c2p(0, 1), color=SKY, stroke_width=2))
        ts = MathTex(r"g(\lambda) = \operatorname{sign}(\lambda)", color=SKY, font_size=34).to_edge(UP, buff=0.35)
        self.play(Create(step), Write(ts), run_time=1.4)
        self.wait(3.0)

        # the derivative panel is the argument
        self.play(Create(dax), FadeIn(label("slope", 22, MUTED).next_to(dax, LEFT, buff=0.2)), run_time=0.9)
        flat = dax.plot(lambda x: 0.0, color=SKY, stroke_width=4)
        self.play(Create(flat), run_time=1.0)
        why = label("slope zero everywhere: nothing to descend", 26, SKY).next_to(ax, DOWN, buff=0.35)
        self.play(FadeIn(why), run_time=0.9)
        self.wait(4.2)

        sig = ax.plot(lambda x: 1 / (1 + np.exp(-x)), color=GOLD, stroke_width=4)
        tg = MathTex(r"g(\lambda) = \sigma(\lambda) = \frac{1}{1 + e^{-\lambda}}", color=GOLD, font_size=34).to_edge(UP, buff=0.35)
        dsig = dax.plot(lambda x: np.exp(-x) / (1 + np.exp(-x)) ** 2, color=GOLD, stroke_width=4)
        why2 = label("a slope you can follow", 26, GOLD).next_to(ax, DOWN, buff=0.35)
        self.play(Transform(step, sig), FadeTransform(ts, tg), Transform(flat, dsig),
                  FadeTransform(why, why2), run_time=2.4)
        self.wait(2.0)
        self.play(FadeIn(MathTex(r"\sigma'(\lambda) = \sigma(\lambda)\,[1-\sigma(\lambda)]",
                                 color=GOLD, font_size=28).next_to(dax, RIGHT, buff=-2.4).shift(UP * 0.55)), run_time=1.0)
        self.wait(3.2)

        # read two values off the curve: it is a probability, not a verdict
        self.play(FadeOut(why2), run_time=0.5)
        for x0, colour in ((1.4, CREAM), (-0.6, CREAM), (3.2, CREAM)):
            p0 = 1 / (1 + np.exp(-x0))
            v = DashedLine(ax.c2p(x0, 0), ax.c2p(x0, p0), color=colour, stroke_width=2)
            h = DashedLine(ax.c2p(x0, p0), ax.c2p(-6, p0), color=colour, stroke_width=2)
            pl = MathTex(rf"\lambda = {x0} \Rightarrow \hat\pi = {p0:.2f}", color=colour, font_size=28)
            pl.next_to(ax.c2p(-6, p0), RIGHT, buff=0.25).shift(UP * 0.28)
            self.play(Create(v), Create(h), FadeIn(pl), run_time=1.1)
            self.wait(2.8)
            self.play(FadeOut(VGroup(v, h, pl)), run_time=0.6)

        bridge = MathTex(r"\text{one sigmoid neuron} + \text{cross-entropy} \;=\; \text{logistic regression}",
                         color=CREAM, font_size=30).next_to(ax, DOWN, buff=0.35)
        self.play(Write(bridge), run_time=1.6)
        self.wait(3.6)


# ---------------------------------------------------------------- 5. hidden layer
class HiddenLayer(Stage):
    """What a hidden neuron actually contributes. Each one is a single bend;
    the output layer adds them with weights. Shown one neuron at a time, with
    the pieces visible before the sum."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        rng = np.random.default_rng(7)
        ax = Axes(x_range=[-3, 3, 1], y_range=[-2.4, 2.4, 1], x_length=7.0, y_length=4.4,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.5}).to_edge(LEFT, buff=0.45).shift(DOWN * 0.15)
        truth = lambda x: 0.9 * np.sin(1.3 * x)
        pts = VGroup()
        for _ in range(60):
            x, y = rng.uniform(-2.8, 2.8), rng.uniform(-2, 2)
            pts.add(Dot(ax.c2p(x, y), radius=0.055, color=GOLD if y > truth(x) else SKY))
        self.play(Create(ax), FadeIn(pts, lag_ratio=0.02), run_time=1.6)

        def net(L):
            g = VGroup()
            xs = VGroup(*[Dot(radius=0.12, color=MUTED) for _ in range(2)]).arrange(DOWN, buff=0.65)
            hs = VGroup(*[Dot(radius=0.12, color=GOLD) for _ in range(L)]).arrange(DOWN, buff=0.32)
            out = Dot(radius=0.14, color=CREAM)
            cols = VGroup(xs, hs, out).arrange(RIGHT, buff=1.0)
            for a in xs:
                for b in hs:
                    g.add(Line(a.get_center(), b.get_center(), stroke_width=1.1, color=MUTED, stroke_opacity=0.55))
            for b in hs:
                g.add(Line(b.get_center(), out.get_center(), stroke_width=1.1, color=MUTED, stroke_opacity=0.55))
            g.add(cols)
            return g.scale(0.9).to_edge(RIGHT, buff=0.5).shift(UP * 0.35)

        # each hidden neuron is one tanh bend; the output layer weights them
        bends = [
            (1.05, 2.0, 0.0),
            (-1.30, 1.9, 1.75),
            (1.25, 1.9, -1.75),
            (0.55, 1.6, 0.9),
            (-0.5, 1.7, -0.9),
        ]

        def blend(k):
            def f(x):
                return sum(a * np.tanh(b * (x - c)) for a, b, c in bends[:k]) / max(1, (k + 1) / 2.0)
            return f

        cur_net = net(1)
        cur_lab = MathTex(r"L = 1", color=CREAM, font_size=38).next_to(cur_net, UP, buff=0.35)
        cur_w = MathTex(r"\text{weights} = 3\cdot 1 + 2 = 5", color=MUTED, font_size=26).next_to(cur_net, DOWN, buff=0.45)
        self.play(FadeIn(cur_net), FadeIn(cur_lab), FadeIn(cur_w), run_time=1.2)

        piece = ax.plot(lambda x: bends[0][0] * np.tanh(bends[0][1] * (x - bends[0][2])), color=SKY,
                        stroke_width=2.5, stroke_opacity=0.85)
        boundary = ax.plot(blend(1), color=CREAM, stroke_width=4.5)
        cap = label("one neuron: one bend", 26, CREAM).next_to(ax, DOWN, buff=0.3)
        self.play(Create(piece), run_time=1.2)
        self.play(Create(boundary), FadeIn(cap), run_time=1.2)
        self.wait(4.0)

        shown = VGroup(piece)
        for L in (2, 3, 5):
            new_pieces = VGroup(*[
                ax.plot(lambda x, a=a, b=b, c=c: a * np.tanh(b * (x - c)), color=SKY,
                        stroke_width=2.2, stroke_opacity=0.75)
                for a, b, c in bends[len(shown):L]
            ])
            n, w = net(L), (3 * L + L + 1)
            nl = MathTex(rf"L = {L}", color=CREAM, font_size=38).next_to(n, UP, buff=0.35)
            wl = MathTex(rf"\text{{weights}} = 3\cdot {L} + {L+1} = {w}", color=MUTED, font_size=26).next_to(n, DOWN, buff=0.45)
            cap2 = label(f"{L} neurons: {L} bends, then the sum", 26, CREAM).next_to(ax, DOWN, buff=0.3)

            self.play(FadeTransform(cur_net, n), Transform(cur_lab, nl), Transform(cur_w, wl),
                      FadeTransform(cap, cap2), run_time=1.2)
            cur_net, cap = n, cap2
            for pc in new_pieces:
                self.play(Create(pc), run_time=0.9)
                self.wait(0.5)
            shown.add(*new_pieces)
            self.wait(1.4)
            self.play(Transform(boundary, ax.plot(blend(L), color=CREAM, stroke_width=4.5)), run_time=1.8)
            self.wait(3.0)

        self.play(FadeOut(shown), run_time=1.2)
        closing = label("every neuron is a line; the output layer blends them", 26, GOLD).next_to(ax, DOWN, buff=0.3)
        self.play(FadeTransform(cap, closing), run_time=1.0)
        self.wait(3.4)


# ---------------------------------------------------------------- 6. overfitting
class Overfitting(Stage):
    """The two curves, and — the part that was missing — the boundary that
    produces them. Training error falls because the boundary contorts to reach
    individual points; the test set is what notices."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        rng = np.random.default_rng(11)
        ax = Axes(x_range=[-3, 3, 1], y_range=[-2.3, 2.3, 1], x_length=5.6, y_length=3.6,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.4}).to_edge(LEFT, buff=0.55).shift(DOWN * 0.2)
        ex = Axes(x_range=[0, 10, 2], y_range=[0, 4, 1], x_length=5.6, y_length=3.6,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.4}).to_edge(RIGHT, buff=0.55).shift(DOWN * 0.2)
        self.play(Create(ax), Create(ex), run_time=1.2)
        self.play(FadeIn(label("the boundary", 24, MUTED).next_to(ax, UP, buff=0.2)),
                  FadeIn(label("error", 24, MUTED).next_to(ex, UP, buff=0.2)),
                  FadeIn(label("training iterations", 20, MUTED).next_to(ex, DOWN, buff=0.25)), run_time=0.8)

        truth = lambda x: 0.85 * np.sin(1.25 * x)
        train, test = VGroup(), VGroup()
        for _ in range(42):
            x, y = rng.uniform(-2.8, 2.8), rng.uniform(-2.1, 2.1)
            train.add(Dot(ax.c2p(x, y), radius=0.05, color=GOLD if y > truth(x) else SKY))
        for _ in range(22):
            x, y = rng.uniform(-2.8, 2.8), rng.uniform(-2.1, 2.1)
            d = Dot(ax.c2p(x, y), radius=0.055, color=GOLD if y > truth(x) else SKY,
                    fill_opacity=0.0, stroke_width=1.8)
            d.set_stroke(color=GOLD if y > truth(x) else SKY)
            test.add(d)
        self.play(FadeIn(train, lag_ratio=0.03), run_time=1.2)
        self.play(FadeIn(test, lag_ratio=0.05), run_time=1.0)
        self.play(FadeIn(VGroup(label("filled: training", 20, MUTED), label("hollow: test", 20, MUTED))
                         .arrange(DOWN, buff=0.12, aligned_edge=LEFT).next_to(ax, DOWN, buff=0.3)), run_time=0.8)
        self.wait(3.2)

        f_train = lambda t: 3.3 * np.exp(-0.45 * t) + 0.18
        f_test = lambda t: 3.3 * np.exp(-0.45 * t) + 0.18 + 0.075 * max(0.0, t - 3.4) ** 2

        # the boundary at three moments, and the two curves growing with it
        stages = [
            (2.2, lambda x: 0.30 * x, "underfit: too straight"),
            (3.4, truth, "the minimum: it follows the signal"),
            (9.4, lambda x: truth(x) + 0.42 * np.sin(6.5 * x) + 0.22 * np.sin(11.0 * x), "overfit: it chases single points"),
        ]
        boundary = ax.plot(stages[0][1], color=CREAM, stroke_width=4)
        cap = label(stages[0][2], 22, CREAM).next_to(ax, DOWN, buff=1.05)
        self.play(Create(boundary), FadeIn(cap), run_time=1.4)

        drawn_to = 0.0
        tr_curve = VGroup()
        te_curve = VGroup()
        for upto, fn, text in stages:
            seg_tr = ex.plot(f_train, x_range=[drawn_to, upto], color=SKY, stroke_width=4)
            seg_te = ex.plot(f_test, x_range=[drawn_to, upto], color=GOLD, stroke_width=4)
            new_b = ax.plot(fn, color=CREAM, stroke_width=4)
            new_c = label(text, 22, CREAM).next_to(ax, DOWN, buff=1.05)
            self.play(Create(seg_tr), Create(seg_te), Transform(boundary, new_b),
                      FadeTransform(cap, new_c), run_time=2.4, rate_func=linear)
            tr_curve.add(seg_tr); te_curve.add(seg_te); cap = new_c
            drawn_to = upto
            self.wait(3.6)

        self.play(FadeIn(label("train", 22, SKY).next_to(ex.c2p(10, f_train(10)), RIGHT, buff=0.1)),
                  FadeIn(label("test", 22, GOLD).next_to(ex.c2p(10, f_test(10)), RIGHT, buff=0.1)), run_time=0.8)
        opt = DashedLine(ex.c2p(3.4, 0), ex.c2p(3.4, 3.9), color=CREAM, stroke_width=2)
        self.play(Create(opt), FadeIn(label("stop here", 22, CREAM).next_to(opt, UP, buff=0.08)), run_time=1.0)
        self.wait(3.8)

        closing = label("past the turn, it is learning the noise", 26, GOLD).next_to(ex, DOWN, buff=0.75)
        self.play(FadeIn(closing), run_time=1.0)
        self.wait(3.2)


# ================================================================ lecture 19 — the lab
# ---------------------------------------------------------------- 1. three splits
class DataSplit(Stage):
    """Why three sets and not two, shown as the rows themselves. The last beat is
    the mistake: choosing a hyperparameter on the test set, and the honest number
    quietly becoming a dishonest one."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        title = label("7 000 customers", 30, CREAM).to_edge(UP, buff=0.6)
        bar = Rectangle(width=11.0, height=0.9, color=MUTED, stroke_width=2, fill_opacity=0.12)
        bar.shift(UP * 1.4)
        self.play(FadeIn(title), Create(bar), run_time=1.3)
        self.wait(2.9)

        widths = [(0.70, "training", GOLD, "fits the weights"),
                  (0.15, "validation", SKY, "chooses size and decay"),
                  (0.15, "test", CREAM, "touched once, at the end")]
        left = bar.get_left()[0]
        blocks, notes = VGroup(), VGroup()
        for frac, name, colour, job in widths:
            w = 11.0 * frac
            r = Rectangle(width=w, height=0.9, color=colour, stroke_width=2,
                          fill_color=colour, fill_opacity=0.28)
            r.move_to([left + w / 2, bar.get_center()[1], 0])
            n = VGroup(label(name, 24, colour), label(f"{int(frac*7000)} rows", 20, MUTED)).arrange(DOWN, buff=0.1)
            n.next_to(r, DOWN, buff=0.35)
            blocks.add(r); notes.add(n)
            left += w
        for r, n in zip(blocks, notes):
            self.play(FadeIn(r), FadeIn(n), run_time=0.9)
            self.wait(1.9)
        self.wait(2.0)

        jobs = VGroup(*[label(j, 24, c) for _, _, c, j in widths]).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        jobs.next_to(notes, DOWN, buff=0.9)
        for j in jobs:
            self.play(FadeIn(j, shift=RIGHT * 0.25), run_time=0.8)
            self.wait(2.3)
        self.wait(2.3)

        # the mistake
        warn = label("choose the hyperparameter on the test set …", 26, "#e2725b").next_to(jobs, DOWN, buff=0.7)
        self.play(FadeIn(warn), blocks[2].animate.set_fill("#e2725b", 0.45).set_stroke("#e2725b"), run_time=1.2)
        self.wait(3.8)
        warn2 = label("… and the number you report is fiction", 26, "#e2725b").next_to(jobs, DOWN, buff=0.7)
        self.play(FadeTransform(warn, warn2), run_time=1.0)
        self.wait(4.6)


# ---------------------------------------------------------------- 2. validation curve
class ValidationCurve(Stage):
    """Thirty fits, one figure. The unpenalised line turns up as capacity grows;
    the heavily penalised one never learns anything. The minimum sits between."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        ax = Axes(x_range=[0, 4.4, 1], y_range=[0.40, 0.62, 0.05], x_length=8.6, y_length=4.6,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.5},
                  y_axis_config={"decimal_number_config": {"num_decimal_places": 2}}).shift(DOWN * 0.25)
        self.play(Create(ax), run_time=1.2)
        xl = label("hidden neurons", 22, MUTED).next_to(ax, DOWN, buff=0.3)
        yl = label("validation log-loss", 22, MUTED).next_to(ax, LEFT, buff=0.25).rotate(PI / 2)
        ticks = VGroup(*[label(t, 20, MUTED).next_to(ax.c2p(i, 0.40), DOWN, buff=0.18)
                         for i, t in enumerate(["1", "3", "5", "10", "20"])])
        self.play(FadeIn(xl), FadeIn(yl), FadeIn(ticks), run_time=0.9)
        self.wait(2.6)

        # alpha = 0 overfits as capacity grows; alpha = 1 is flat and mediocre
        series = [
            (0.0,   [0.545, 0.492, 0.487, 0.512, 0.578], "#e2725b", r"\alpha = 0"),
            (0.01,  [0.540, 0.472, 0.468, 0.474, 0.486], GOLD,      r"\alpha = 0.01"),
            (1.0,   [0.556, 0.551, 0.550, 0.551, 0.553], SKY,       r"\alpha = 1.0"),
        ]
        for a, ys, colour, tex in series:
            pts = [ax.c2p(i, v) for i, v in enumerate(ys)]
            line = VMobject(color=colour, stroke_width=4).set_points_as_corners(pts)
            dots = VGroup(*[Dot(p, radius=0.07, color=colour) for p in pts])
            lab_ = MathTex(tex, color=colour, font_size=30).next_to(pts[-1], RIGHT, buff=0.2)
            self.play(Create(line), run_time=1.6)
            self.play(FadeIn(dots, lag_ratio=0.15), FadeIn(lab_), run_time=0.9)
            self.wait(3.8)

        best = ax.c2p(2, 0.468)
        ring = Circle(radius=0.22, color=CREAM, stroke_width=3).move_to(best)
        cap = label("5 neurons, decay 0.01", 26, CREAM).next_to(ring, UP, buff=0.35)
        self.play(Create(ring), FadeIn(cap), run_time=1.2)
        self.wait(4.3)
        closing = label("the rising orange line is Monday's overfitting slide, drawn by your laptop",
                        24, "#e2725b").next_to(ax, DOWN, buff=0.85)
        self.play(FadeIn(closing), run_time=1.0)
        self.wait(4.9)


# ---------------------------------------------------------------- 3. why the tree wins
class ModelRace(Stage):
    """The scoreboard, then the reason behind it: the signal in a customer table
    is a threshold, which a tree states in one split and a network can only
    approach with smooth functions."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        rows = [("Gradient boosting", 0.847, GOLD), ("Random forest", 0.839, GOLD),
                ("Neural network", 0.821, SKY), ("Logistic", 0.818, SKY),
                ("Pruned tree", 0.776, MUTED)]
        head = label("AUC on the test rows", 28, CREAM).to_edge(UP, buff=0.6)
        self.play(FadeIn(head), run_time=0.8)

        x0, scale = -3.4, 9.0
        group = VGroup()
        for k, (name, auc, colour) in enumerate(rows):
            y = 1.9 - k * 0.85
            nm = label(name, 24, CREAM).move_to([x0 - 1.9, y, 0], aligned_edge=RIGHT)
            bar = Rectangle(width=0.01, height=0.42, color=colour, fill_color=colour,
                            fill_opacity=0.75, stroke_width=0).move_to([x0, y, 0], aligned_edge=LEFT)
            val = DecimalNumber(0.0, num_decimal_places=3, color=colour, font_size=28)
            val.next_to(bar, RIGHT, buff=0.25)
            group.add(nm, bar, val)
            self.play(FadeIn(nm), run_time=0.4)
            self.play(bar.animate.stretch_to_fit_width((auc - 0.70) * scale).move_to([x0, y, 0], aligned_edge=LEFT),
                      ChangeDecimalToValue(val, auc),
                      UpdateFromFunc(val, lambda m, b=bar: m.next_to(b, RIGHT, buff=0.25)),
                      run_time=1.3)
            self.wait(1.4)
        self.wait(3.5)
        self.play(FadeOut(group), FadeOut(head), run_time=1.0)

        # the reason, in one picture
        ax = Axes(x_range=[0, 24, 6], y_range=[0, 1.05, 0.5], x_length=8.6, y_length=3.6,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.5}).shift(DOWN * 0.3)
        self.play(Create(ax), run_time=0.9)
        self.play(FadeIn(label("months as a customer", 22, MUTED).next_to(ax, DOWN, buff=0.25)),
                  FadeIn(label("P(churn)", 22, MUTED).next_to(ax, LEFT, buff=0.2)), run_time=0.7)

        truth = VGroup(ax.plot(lambda x: 0.82, x_range=[0, 6], color=CREAM, stroke_width=4),
                       ax.plot(lambda x: 0.19, x_range=[6, 24], color=CREAM, stroke_width=4),
                       DashedLine(ax.c2p(6, 0.19), ax.c2p(6, 0.82), color=CREAM, stroke_width=2))
        self.play(Create(truth), run_time=1.4)
        self.play(FadeIn(label("the real signal: a threshold at six months", 24, CREAM).next_to(ax, UP, buff=0.3)),
                  run_time=0.9)
        self.wait(4.1)

        t1 = label("a tree: one split, exactly right", 24, GOLD).next_to(ax, DOWN, buff=0.85)
        self.play(FadeIn(t1), Flash(ax.c2p(6, 0.5), color=GOLD, line_length=0.35, num_lines=14), run_time=1.2)
        self.wait(3.8)

        smooth = ax.plot(lambda x: 0.19 + 0.63 / (1 + np.exp(1.1 * (x - 6))), color=SKY, stroke_width=4)
        t2 = label("a network: a smooth function leaning on it", 24, SKY).next_to(ax, DOWN, buff=0.85)
        self.play(Create(smooth), FadeTransform(t1, t2), run_time=1.8)
        self.wait(4.6)
        closing = label("on rows and columns, the tree is speaking the data's own language",
                        24, GOLD).next_to(ax, DOWN, buff=1.5)
        self.play(FadeIn(closing), run_time=1.0)
        self.wait(4.6)


# ---------------------------------------------------------------- 4. the scale of deep
class DeepScale(Stage):
    """Four million weights, sixty thousand images. The arithmetic done in front
    of them, because the ratio is the entire argument for dropout."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        layers = [("input", 784), ("hidden", 1024), ("hidden", 1024), ("hidden", 2048), ("output", 10)]
        cols = VGroup()
        for name, n in layers:
            h = np.clip(0.0022 * n, 0.35, 4.3)
            r = Rectangle(width=0.62, height=h, color=SKY, fill_color=SKY, fill_opacity=0.22, stroke_width=2)
            lab_ = VGroup(label(str(n), 24, CREAM), label(name, 18, MUTED)).arrange(DOWN, buff=0.08)
            cols.add(VGroup(r, lab_))
        cols.arrange(RIGHT, buff=1.25).shift(UP * 0.45)
        for col in cols:
            col[1].next_to(col[0], DOWN, buff=0.28)

        self.play(FadeIn(cols[0]), run_time=0.8)
        for k in range(1, len(cols)):
            links = VGroup(*[Line(cols[k - 1][0].get_right(), cols[k][0].get_left(),
                                  stroke_width=1.0, color=MUTED, stroke_opacity=0.5).shift(UP * dy)
                             for dy in np.linspace(-0.25, 0.25, 5)])
            self.play(FadeIn(cols[k]), Create(links), run_time=0.9)
            self.wait(0.9)
        self.wait(2.3)

        terms = [(784, 1024), (1024, 1024), (1024, 2048), (2048, 10)]
        running = 0
        shown = VGroup()
        for a, b in terms:
            running += a * b
            t = MathTex(rf"{a}\times{b}", color=GOLD, font_size=30)
            shown.add(t)
            shown.arrange(RIGHT, buff=0.55).to_edge(DOWN, buff=1.5)
            self.play(FadeIn(t, shift=UP * 0.15), run_time=0.8)
            self.wait(1.3)
        total = MathTex(r"\approx 4\ \text{million weights}", color=GOLD, font_size=42).to_edge(DOWN, buff=0.6)
        self.play(Write(total), run_time=1.4)
        self.wait(3.8)

        # the ratio that matters
        self.play(FadeOut(cols), FadeOut(shown), total.animate.to_edge(UP, buff=0.8), run_time=1.2)
        w = Rectangle(width=10.0, height=0.7, color=GOLD, fill_color=GOLD, fill_opacity=0.3, stroke_width=0)
        i = Rectangle(width=10.0 * 60000 / 4_000_000, height=0.7, color=SKY, fill_color=SKY, fill_opacity=0.45, stroke_width=0)
        VGroup(w, i).arrange(DOWN, buff=0.9, aligned_edge=LEFT).shift(DOWN * 0.3)
        self.play(FadeIn(w), FadeIn(label("4 000 000 weights", 24, GOLD).next_to(w, UP, buff=0.18, aligned_edge=LEFT)), run_time=1.0)
        self.play(FadeIn(i), FadeIn(label("60 000 training images", 24, SKY).next_to(i, DOWN, buff=0.22, aligned_edge=LEFT)), run_time=1.0)
        self.wait(4.3)
        closing = label("sixty-six parameters per image: it will memorise unless you stop it",
                        26, CREAM).to_edge(DOWN, buff=0.7)
        self.play(FadeIn(closing), run_time=1.0)
        self.wait(4.9)


# ---------------------------------------------------------------- 5. autoencoder = PCA
class AutoencoderPCA(Stage):
    """Squeeze the data through one linear neuron and what comes back out is the
    first principal component. Lecture 14, arrived at from the other side."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        rng = np.random.default_rng(5)
        ax = Axes(x_range=[-3.2, 3.2, 1], y_range=[-2.4, 2.4, 1], x_length=6.6, y_length=4.4,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.4}).to_edge(LEFT, buff=0.6)
        self.play(Create(ax), run_time=1.0)

        ang, pts = 0.52, []
        for _ in range(55):
            t, n = rng.normal(0, 1.35), rng.normal(0, 0.42)
            x = t * np.cos(ang) - n * np.sin(ang)
            y = t * np.sin(ang) + n * np.cos(ang)
            pts.append((x, y))
        dots = VGroup(*[Dot(ax.c2p(x, y), radius=0.055, color=SKY) for x, y in pts])
        self.play(FadeIn(dots, lag_ratio=0.03), run_time=1.4)
        self.wait(3.6)

        # the network: 2 -> 1 -> 2
        def node(c, col):
            return Dot(c, radius=0.14, color=col)
        xs = VGroup(node(ORIGIN, MUTED), node(ORIGIN, MUTED)).arrange(DOWN, buff=0.9)
        hs = VGroup(node(ORIGIN, GOLD))
        os_ = VGroup(node(ORIGIN, CREAM), node(ORIGIN, CREAM)).arrange(DOWN, buff=0.9)
        net = VGroup(xs, hs, os_).arrange(RIGHT, buff=1.5).to_edge(RIGHT, buff=1.0).shift(UP * 0.5)
        wires = VGroup()
        for a in xs:
            wires.add(Line(a.get_center(), hs[0].get_center(), stroke_width=1.3, color=MUTED, stroke_opacity=0.6))
        for b in os_:
            wires.add(Line(hs[0].get_center(), b.get_center(), stroke_width=1.3, color=MUTED, stroke_opacity=0.6))
        cap = MathTex(r"2 \rightarrow 1 \rightarrow 2", color=CREAM, font_size=34).next_to(net, UP, buff=0.5)
        loss = label("loss = reproduce your own input", 22, MUTED).next_to(net, DOWN, buff=0.6)
        self.play(FadeIn(net), Create(wires), FadeIn(cap), run_time=1.4)
        self.play(FadeIn(loss), run_time=0.8)
        self.wait(5.7)

        # the bottleneck forces a direction: the one that loses least
        axis = ax.plot(lambda x: np.tan(ang) * x, x_range=[-2.6, 2.6], color=GOLD, stroke_width=4)
        self.play(Create(axis), run_time=1.6)
        self.play(FadeIn(label("the direction the single neuron keeps", 22, GOLD).next_to(ax, DOWN, buff=0.3)), run_time=0.9)
        self.wait(4.9)

        proj = VGroup()
        for x, y in pts[:26]:
            t = x * np.cos(ang) + y * np.sin(ang)
            proj.add(Line(ax.c2p(x, y), ax.c2p(t * np.cos(ang), t * np.sin(ang)),
                          color=CREAM, stroke_width=1.4, stroke_opacity=0.55))
        self.play(Create(proj, lag_ratio=0.05), run_time=2.0)
        self.wait(5.3)

        verdict = MathTex(r"\text{linear autoencoder} \;=\; \text{PCA}", color=GOLD, font_size=40)
        verdict.next_to(net, DOWN, buff=1.4)
        self.play(FadeOut(loss), Write(verdict), run_time=1.6)
        self.wait(6.9)




# ================================================================ lecture 11 — k-means
# The six customers of the by-hand slide, in the deck's own order and numbers.
KM_PTS = {"A": (1, 1), "B": (2, 1), "C": (1, 2), "D": (8, 8), "E": (9, 8), "F": (8, 9)}


def km_axes(x=(0, 10, 2), y=(0, 10, 2), xl=6.0, yl=5.0):
    return Axes(x_range=list(x), y_range=list(y), x_length=xl, y_length=yl,
                axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.4})


class Lloyd(Stage):
    """Assign, update, repeat — with W falling at every half-step, because the
    fact that it can only fall is why the algorithm is guaranteed to stop."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        rng = np.random.default_rng(4)
        ax = km_axes(x=(-1, 11, 3), y=(-1, 11, 3), xl=7.4, yl=5.4).to_edge(LEFT, buff=0.7)
        self.play(Create(ax), run_time=1.0)

        centres = np.array([[2.5, 2.5], [8.0, 3.0], [5.5, 8.5]])
        pts = np.vstack([c + rng.normal(0, 1.05, size=(22, 2)) for c in centres])
        dots = VGroup(*[Dot(ax.c2p(*p), radius=0.06, color=MUTED) for p in pts])
        self.play(FadeIn(dots, lag_ratio=0.02), run_time=1.4)
        self.wait(1.8)

        cols = [GOLD, SKY, "#c98bb9"]
        # a deliberately poor start, so the first update is visibly large
        cent = np.array([[1.5, 9.5], [3.0, 8.0], [7.0, 1.5]])
        marks = VGroup(*[Star(n=5, outer_radius=0.17, color=c, fill_opacity=1).move_to(ax.c2p(*m))
                         for m, c in zip(cent, cols)])
        self.play(FadeIn(marks, scale=1.5), run_time=1.0)
        self.play(FadeIn(label("start: three centroids, chosen badly on purpose", 24, CREAM)
                         .next_to(ax, DOWN, buff=0.3)), run_time=0.9)
        self.wait(2.2)

        wbox = VGroup(MathTex(r"W =", color=CREAM, font_size=40),
                      DecimalNumber(0, num_decimal_places=0, color=GOLD, font_size=44)).arrange(RIGHT, buff=0.25)
        wbox.to_edge(RIGHT, buff=1.3).shift(UP * 1.8)
        step = label("", 26, MUTED).next_to(wbox, DOWN, buff=0.7)

        def assign(c):
            d = ((pts[:, None, :] - c[None, :, :]) ** 2).sum(-1)
            return d.argmin(1), d.min(1).sum()

        lab_, W = assign(cent)
        wbox[1].set_value(W)
        self.play(FadeIn(wbox), run_time=0.8)
        self.wait(1.4)

        for it in range(4):
            # assign
            lab_, W = assign(cent)
            s1 = label(f"round {it + 1} · assign", 26, CREAM).next_to(wbox, DOWN, buff=0.7)
            self.play(FadeTransform(step, s1), run_time=0.5); step = s1
            self.play(*[d.animate.set_color(cols[l]) for d, l in zip(dots, lab_)],
                      ChangeDecimalToValue(wbox[1], W), run_time=1.3)
            self.wait(1.8)
            # update
            new = np.array([pts[lab_ == j].mean(0) if (lab_ == j).any() else cent[j] for j in range(3)])
            _, W2 = assign(new)
            s2 = label(f"round {it + 1} · update", 26, CREAM).next_to(wbox, DOWN, buff=0.7)
            self.play(FadeTransform(step, s2), run_time=0.5); step = s2
            moved = float(np.abs(new - cent).max())
            self.play(*[m.animate.move_to(ax.c2p(*n)) for m, n in zip(marks, new)],
                      ChangeDecimalToValue(wbox[1], W2), run_time=1.5)
            cent = new
            self.wait(1.6)
            if moved < 0.06:
                break

        done = label("nothing moved: that is convergence", 26, GOLD).next_to(ax, DOWN, buff=0.3)
        self.play(FadeIn(done), run_time=1.0)
        self.wait(2.2)
        note = label("W fell at every half-step — which is why it must stop", 24, MUTED)
        note.next_to(wbox, DOWN, buff=2.2)
        self.play(FadeIn(note), run_time=1.0)
        self.wait(3.0)


class KmeansByHand(Stage):
    """The six customers of the slide, with the distances written out. The deck
    asserts W = 5.3; here it is computed in front of them."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        ax = km_axes(x=(0, 10, 2), y=(0, 10, 2), xl=5.6, yl=4.8).to_edge(LEFT, buff=0.8).shift(DOWN * 0.3)
        self.play(Create(ax), run_time=0.9)
        self.play(FadeIn(label("visits", 22, MUTED).next_to(ax, DOWN, buff=0.25)),
                  FadeIn(label("basket", 22, MUTED).next_to(ax, LEFT, buff=0.2).rotate(PI / 2)), run_time=0.7)

        dots, names = {}, VGroup()
        for n, (x, y) in KM_PTS.items():
            d = Dot(ax.c2p(x, y), radius=0.085, color=MUTED)
            t = label(n, 22, CREAM).next_to(d, UR, buff=0.06)
            dots[n] = d; names.add(t)
            self.add(d)
        self.play(FadeIn(VGroup(*dots.values()), lag_ratio=0.1), FadeIn(names, lag_ratio=0.1), run_time=1.4)
        self.wait(2.8)

        # start: A and D are the centroids
        cA = Star(n=5, outer_radius=0.16, color=GOLD, fill_opacity=1).move_to(ax.c2p(1, 1))
        cD = Star(n=5, outer_radius=0.16, color=SKY, fill_opacity=1).move_to(ax.c2p(8, 8))
        self.play(FadeIn(cA, scale=1.6), FadeIn(cD, scale=1.6), run_time=1.0)
        self.play(FadeIn(label("centroids start at A and D", 24, CREAM).next_to(ax, UP, buff=0.3)), run_time=0.8)
        self.wait(2.8)

        rows = VGroup().to_edge(RIGHT, buff=0.9).shift(UP * 1.9)
        head = MathTex(r"\text{point} \quad d^2(\cdot,A) \quad d^2(\cdot,D)", color=MUTED, font_size=28)
        head.to_edge(RIGHT, buff=0.7).shift(UP * 2.4)
        self.play(FadeIn(head), run_time=0.7)

        prev = head
        for n in ("B", "C", "E", "F"):
            x, y = KM_PTS[n]
            dA = (x - 1) ** 2 + (y - 1) ** 2
            dD = (x - 8) ** 2 + (y - 8) ** 2
            winner = GOLD if dA < dD else SKY
            line = MathTex(rf"{n} \quad\; {dA} \quad\; {dD}", color=CREAM, font_size=30)
            line.next_to(prev, DOWN, buff=0.38).align_to(head, LEFT)
            self.play(FadeIn(line, shift=RIGHT * 0.15), run_time=0.7)
            self.play(dots[n].animate.set_color(winner), line.animate.set_color(winner), run_time=0.7)
            self.wait(2.1)
            prev = line
        self.play(dots["A"].animate.set_color(GOLD), dots["D"].animate.set_color(SKY), run_time=0.6)
        self.wait(2.2)

        # update the centroids to the group means, with the arithmetic
        m1 = MathTex(r"\bar x_1 = \tfrac{1+2+1}{3},\ \tfrac{1+1+2}{3} = (1.33,\ 1.33)", color=GOLD, font_size=28)
        m2 = MathTex(r"\bar x_2 = \tfrac{8+9+8}{3},\ \tfrac{8+8+9}{3} = (8.33,\ 8.33)", color=SKY, font_size=28)
        VGroup(m1, m2).arrange(DOWN, buff=0.3, aligned_edge=LEFT).next_to(prev, DOWN, buff=0.6).align_to(head, LEFT)
        self.play(FadeIn(m1), cA.animate.move_to(ax.c2p(1.333, 1.333)), run_time=1.3)
        self.wait(2.0)
        self.play(FadeIn(m2), cD.animate.move_to(ax.c2p(8.333, 8.333)), run_time=1.3)
        self.wait(2.8)

        again = label("assign again: nothing changes", 24, CREAM).next_to(ax, UP, buff=0.3)
        self.play(FadeIn(again), run_time=0.9)
        self.wait(2.8)

        w = MathTex(r"W = 2.67 + 2.67 = 5.33", color=GOLD, font_size=36)
        w.next_to(m2, DOWN, buff=0.7).align_to(head, LEFT)
        self.play(Write(w), run_time=1.4)
        self.wait(4.5)


class ScaleBreaks(Stage):
    """Income in euros against age in years: the distance is income, and the
    clusters are income bands. Then the same points, standardised."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        rng = np.random.default_rng(9)
        # two genuine groups: young-and-rich, old-and-poor — invisible to raw distance
        g1 = np.column_stack([rng.normal(30, 4, 30), rng.normal(52000, 7000, 30)])
        g2 = np.column_stack([rng.normal(58, 4, 30), rng.normal(46000, 7000, 30)])
        P = np.vstack([g1, g2])

        ax = Axes(x_range=[18, 72, 10], y_range=[25000, 75000, 10000], x_length=5.6, y_length=4.4,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.4},
                  y_axis_config={"decimal_number_config": {"num_decimal_places": 0, "group_with_commas": False}})
        ax.to_edge(LEFT, buff=0.75).shift(DOWN * 0.25)
        self.play(Create(ax), run_time=1.0)
        self.play(FadeIn(label("age (years)", 20, MUTED).next_to(ax, DOWN, buff=0.28)),
                  FadeIn(label("income (euro)", 20, MUTED).next_to(ax, LEFT, buff=0.15).rotate(PI / 2)), run_time=0.7)
        dots = VGroup(*[Dot(ax.c2p(a, i), radius=0.055, color=MUTED) for a, i in P])
        self.play(FadeIn(dots, lag_ratio=0.02), run_time=1.3)
        self.wait(2.5)

        d2 = MathTex(r"d^2 = (\Delta\text{age})^2 + (\Delta\text{income})^2", color=CREAM, font_size=30)
        d2.to_edge(RIGHT, buff=1.0).shift(UP * 2.0)
        ex = MathTex(r"= 28^2 + 6000^2", color=CREAM, font_size=30).next_to(d2, DOWN, buff=0.4)
        ex2 = MathTex(r"= 784 + 36{,}000{,}000", color=GOLD, font_size=30).next_to(ex, DOWN, buff=0.35)
        self.play(FadeIn(d2), run_time=0.9); self.wait(2.0)
        self.play(FadeIn(ex), run_time=0.9); self.wait(2.2)
        self.play(FadeIn(ex2), run_time=0.9)
        self.wait(3.4)
        verdict = label("age contributes nothing", 26, GOLD).next_to(ex2, DOWN, buff=0.55)
        self.play(FadeIn(verdict), run_time=0.9)
        self.wait(3.1)

        # k-means on raw units: a horizontal cut, i.e. income bands
        cut = DashedLine(ax.c2p(18, 49500), ax.c2p(72, 49500), color=CREAM, stroke_width=3)
        self.play(Create(cut), run_time=1.2)
        self.play(*[d.animate.set_color(GOLD if P[i, 1] > 49500 else SKY) for i, d in enumerate(dots)], run_time=1.2)
        self.play(FadeIn(label("clusters = income bands, nothing more", 24, CREAM).next_to(ax, UP, buff=0.3)), run_time=0.9)
        self.wait(4.2)

        # standardised: the real groups appear
        Z = (P - P.mean(0)) / P.std(0)
        az = Axes(x_range=[-3, 3, 1], y_range=[-3, 3, 1], x_length=5.6, y_length=4.4,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.4})
        az.move_to(ax)
        self.play(FadeOut(cut), FadeOut(VGroup(d2, ex, ex2, verdict)), run_time=0.8)
        self.play(Transform(ax, az),
                  *[d.animate.move_to(az.c2p(*z)).set_color(GOLD if i < 30 else SKY) for i, (d, z) in enumerate(zip(dots, Z))],
                  run_time=2.4)
        self.play(FadeIn(label("scale() first, and the real groups are there", 26, GOLD).next_to(az, UP, buff=0.3)), run_time=1.0)
        self.wait(4.5)


class ShapeBreaks(Stage):
    """Two crescents. k-means cuts them straight down the middle and reports a
    perfectly respectable W — the failure that never raises an error."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        rng = np.random.default_rng(2)
        t1 = rng.uniform(0, np.pi, 70)
        c1 = np.column_stack([np.cos(t1) * 2.4, np.sin(t1) * 1.5]) + rng.normal(0, 0.12, (70, 2))
        t2 = rng.uniform(0, np.pi, 70)
        c2 = np.column_stack([np.cos(t2) * 2.4 + 1.6, -np.sin(t2) * 1.5 + 0.6]) + rng.normal(0, 0.12, (70, 2))

        ax = km_axes(x=(-4, 5, 2), y=(-2.6, 2.6, 1), xl=8.4, yl=4.6).shift(UP * 0.2)
        self.play(Create(ax), run_time=0.9)
        d1 = VGroup(*[Dot(ax.c2p(*p), radius=0.05, color=MUTED) for p in c1])
        d2 = VGroup(*[Dot(ax.c2p(*p), radius=0.05, color=MUTED) for p in c2])
        self.play(FadeIn(d1, lag_ratio=0.02), FadeIn(d2, lag_ratio=0.02), run_time=1.6)
        self.play(FadeIn(label("two crescents — any eye sees them", 26, CREAM).next_to(ax, DOWN, buff=0.35)), run_time=0.9)
        self.wait(5.8)

        # what k-means does: a straight boundary between two centroids
        allp = np.vstack([c1, c2])
        cent = np.array([[-1.4, 0.35], [2.4, 0.35]])
        marks = VGroup(*[Star(n=5, outer_radius=0.16, color=c, fill_opacity=1).move_to(ax.c2p(*m))
                         for m, c in zip(cent, (GOLD, SKY))])
        self.play(FadeIn(marks, scale=1.4), run_time=0.9)
        lab_ = (((allp[:, None, :] - cent[None, :, :]) ** 2).sum(-1)).argmin(1)
        alld = VGroup(*d1, *d2)
        self.play(*[d.animate.set_color((GOLD, SKY)[l]) for d, l in zip(alld, lab_)], run_time=1.6)
        cut = DashedLine(ax.c2p(0.5, -2.6), ax.c2p(0.5, 2.6), color=CREAM, stroke_width=3)
        self.play(Create(cut), run_time=1.2)
        self.wait(5.4)

        verdict = label("k-means draws straight boundaries. It cut both crescents in half.",
                        25, GOLD).next_to(ax, DOWN, buff=0.35)
        self.play(FadeIn(verdict), run_time=1.0)
        self.wait(6.2)
        w = label("and W = 96.4, which looks entirely fine in the output", 24, MUTED).next_to(verdict, DOWN, buff=0.35)
        self.play(FadeIn(w), run_time=1.0)
        self.wait(7.2)


class ElbowLie(Stage):
    """W falls for every k, all the way to zero. The curve cannot choose k; at
    best it hints, and on real data the hint is often unreadable."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        ax = Axes(x_range=[0, 11, 2], y_range=[0, 100, 25], x_length=8.0, y_length=4.4,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.4}).shift(DOWN * 0.2)
        self.play(Create(ax), run_time=1.0)
        self.play(FadeIn(label("k", 24, MUTED).next_to(ax, DOWN, buff=0.28)),
                  FadeIn(MathTex("W", color=MUTED, font_size=30).next_to(ax, LEFT, buff=0.22)), run_time=0.7)

        ks = np.arange(1, 11)
        W = np.array([92, 44, 22, 18.5, 16, 14, 12.2, 10.6, 9.2, 8.0])
        pts = [ax.c2p(k, w) for k, w in zip(ks, W)]
        curve = VMobject(color=GOLD, stroke_width=4).set_points_as_corners(pts)
        dots = VGroup(*[Dot(p, radius=0.07, color=GOLD) for p in pts])
        self.play(Create(curve), run_time=2.4)
        self.play(FadeIn(dots, lag_ratio=0.1), run_time=1.0)
        self.wait(2.8)

        n1 = label("k = 1: W is the total variance", 24, CREAM).next_to(ax.c2p(1, 92), RIGHT, buff=0.4)
        self.play(FadeIn(n1), Flash(pts[0], color=CREAM, line_length=0.3, num_lines=12), run_time=1.1)
        self.wait(3.1)
        n2 = label("k = n: W = 0, every point its own cluster", 24, CREAM).next_to(ax.c2p(10, 8), UR, buff=0.25)
        self.play(FadeTransform(n1, n2), run_time=1.0)
        self.wait(3.4)

        clear = label("it falls for every k. It always votes for more.", 26, GOLD).next_to(ax, DOWN, buff=0.75)
        self.play(FadeTransform(n2, clear), run_time=1.0)
        self.wait(3.6)

        # the elbow you are told to find — and the one you actually get
        el = Circle(radius=0.28, color=CREAM, stroke_width=3).move_to(pts[2])
        self.play(Create(el), FadeIn(label("the elbow, when you are lucky", 24, CREAM)
                                     .next_to(el, UP, buff=0.3)), run_time=1.2)
        self.wait(3.4)

        smooth = np.array([92, 61, 47, 39, 33, 29, 25.5, 23, 21, 19.5])
        pts2 = [ax.c2p(k, w) for k, w in zip(ks, smooth)]
        curve2 = VMobject(color=SKY, stroke_width=4).set_points_as_corners(pts2)
        self.play(FadeOut(el), FadeOut(dots), Transform(curve, curve2), run_time=2.0)
        self.play(FadeIn(label("and this is most real data: no elbow at all", 26, SKY)
                         .next_to(ax, DOWN, buff=1.25)), run_time=1.0)
        self.wait(4.8)




# ================================================================ lecture 12 — hierarchical
# The five patients of the by-hand slide: length of stay, in days.
STAY = [2, 3, 6, 10, 11]


class Dendrogram(Stage):
    """The five patients, merged one pair at a time, with the complete-linkage
    distance computed before each merge and the tree growing from the heights
    that result. The deck asserts merges at 1, 1, 4 and 9; here they are earned."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        ax = Axes(x_range=[0, 12, 2], y_range=[0, 10, 2], x_length=9.0, y_length=4.4,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.4}).shift(DOWN * 0.5)
        self.play(Create(ax), run_time=1.0)
        self.play(FadeIn(label("length of stay (days)", 22, MUTED).next_to(ax, DOWN, buff=0.3)),
                  FadeIn(label("merge height", 22, MUTED).next_to(ax, LEFT, buff=0.2).rotate(PI / 2)), run_time=0.8)

        leaves = {}
        for v in STAY:
            d = Dot(ax.c2p(v, 0), radius=0.08, color=CREAM)
            t = label(str(v), 22, CREAM).next_to(d, DOWN, buff=0.12)
            leaves[v] = {"x": v, "top": 0.0, "dot": d, "members": [v]}
            self.add(d, t)
        self.play(FadeIn(VGroup(*[leaves[v]["dot"] for v in STAY]), lag_ratio=0.15), run_time=1.2)
        self.wait(2.2)

        clusters = [leaves[v] for v in STAY]
        rule = MathTex(r"d(A,B) = \max_{a \in A,\, b \in B} |a-b|", color=SKY, font_size=30).to_edge(UP, buff=0.5)
        self.play(FadeIn(rule), run_time=0.9)
        self.wait(2.0)

        def dist(a, b):
            return max(abs(x - y) for x in a["members"] for y in b["members"])

        readout = None
        for step in range(4):
            pairs = [(dist(a, b), i, j) for i, a in enumerate(clusters) for j, b in enumerate(clusters) if i < j]
            h, i, j = min(pairs)
            a, b = clusters[i], clusters[j]

            shown = MathTex(rf"d(\{{{','.join(map(str, a['members']))}\}},\ "
                            rf"\{{{','.join(map(str, b['members']))}\}}) = {h}",
                            color=GOLD, font_size=32).next_to(rule, DOWN, buff=0.45)
            if readout is None:
                self.play(FadeIn(shown), run_time=0.8)
            else:
                self.play(FadeTransform(readout, shown), run_time=0.8)
            readout = shown
            self.wait(1.8)

            # the merge, drawn at the height it happened
            xa, xb = a["x"], b["x"]
            left = Line(ax.c2p(xa, a["top"]), ax.c2p(xa, h), color=GOLD, stroke_width=3)
            right = Line(ax.c2p(xb, b["top"]), ax.c2p(xb, h), color=GOLD, stroke_width=3)
            top = Line(ax.c2p(xa, h), ax.c2p(xb, h), color=GOLD, stroke_width=3)
            self.play(Create(left), Create(right), run_time=0.8)
            self.play(Create(top), run_time=0.7)
            hl = label(f"{h}", 20, GOLD).next_to(ax.c2p((xa + xb) / 2, h), UP, buff=0.08)
            self.play(FadeIn(hl), run_time=0.4)
            self.wait(1.6)

            merged = {"x": (xa + xb) / 2, "top": h, "members": a["members"] + b["members"]}
            clusters = [c for k, c in enumerate(clusters) if k not in (i, j)] + [merged]

        self.wait(1.4)
        self.play(FadeOut(readout), run_time=0.6)

        # cut it twice: the same tree answers two different questions
        for hcut, text, colour in ((5, "cut at 5: two groups", SKY), (2, "cut at 2: three groups", "#c98bb9")):
            line = DashedLine(ax.c2p(0, hcut), ax.c2p(12, hcut), color=colour, stroke_width=3)
            cap = label(text, 26, colour).next_to(ax, UP, buff=0.15)
            self.play(Create(line), FadeIn(cap), run_time=1.2)
            self.wait(2.8)
            self.play(FadeOut(line), FadeOut(cap), run_time=0.6)

        closing = label("k was never an input. You choose it by where you cut.", 26, GOLD).next_to(ax, UP, buff=0.15)
        self.play(FadeIn(closing), run_time=1.0)
        self.wait(3.0)


class LinkageFour(Stage):
    """Same points, four definitions of 'closest', four different trees — and
    single linkage chaining, which is the one you must be able to recognise."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        title = label("same data · four definitions of \"closest\"", 28, CREAM).to_edge(UP, buff=0.5)
        self.play(FadeIn(title), run_time=0.8)

        defs = [
            ("complete", r"\max d(a,b)", "compact, similar sizes", GOLD),
            ("single", r"\min d(a,b)", "long chains", "#e2725b"),
            ("average", r"\text{mean } d(a,b)", "a compromise", SKY),
            ("Ward", r"\min \Delta \text{within-SS}", "k-means-like blobs", "#c98bb9"),
        ]
        rows = VGroup()
        for name, formula, effect, colour in defs:
            n = label(name, 26, colour)
            f = MathTex(formula, color=CREAM, font_size=28)
            e = label(effect, 22, MUTED)
            row = VGroup(n, f, e).arrange(RIGHT, buff=0.7)
            rows.add(row)
        rows.arrange(DOWN, buff=0.55, aligned_edge=LEFT).shift(UP * 0.4)
        for r in rows:
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.8)
            self.wait(2.2)
        self.wait(2.7)

        # chaining, drawn: single linkage walks along a bridge of noise
        self.play(FadeOut(rows), FadeOut(title), run_time=0.9)
        ax = Axes(x_range=[-1, 11, 2], y_range=[-1, 5, 2], x_length=9.0, y_length=3.6,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.3}).shift(DOWN * 0.3)
        self.play(Create(ax), run_time=0.8)
        rng = np.random.default_rng(3)
        blob1 = np.column_stack([rng.normal(1.2, 0.5, 16), rng.normal(2, 0.5, 16)])
        blob2 = np.column_stack([rng.normal(9.0, 0.5, 16), rng.normal(2, 0.5, 16)])
        bridge = np.column_stack([np.linspace(2.6, 7.6, 7), np.full(7, 2.0) + rng.normal(0, 0.12, 7)])
        gb1 = VGroup(*[Dot(ax.c2p(*p), radius=0.055, color=GOLD) for p in blob1])
        gb2 = VGroup(*[Dot(ax.c2p(*p), radius=0.055, color=SKY) for p in blob2])
        gbr = VGroup(*[Dot(ax.c2p(*p), radius=0.05, color=MUTED) for p in bridge])
        self.play(FadeIn(gb1), FadeIn(gb2), run_time=1.0)
        self.wait(2.4)
        self.play(FadeIn(gbr, lag_ratio=0.2), run_time=1.2)
        self.play(FadeIn(label("seven noisy points between them", 24, MUTED).next_to(ax, UP, buff=0.3)), run_time=0.8)
        self.wait(3.3)

        chain = VGroup()
        pts = sorted(np.vstack([blob1[np.argsort(blob1[:, 0])][-1:], bridge, blob2[np.argsort(blob2[:, 0])][:1]]).tolist())
        for p, q in zip(pts, pts[1:]):
            chain.add(Line(ax.c2p(*p), ax.c2p(*q), color="#e2725b", stroke_width=3))
        self.play(Create(chain, lag_ratio=0.35), run_time=2.4)
        self.play(*[d.animate.set_color("#e2725b") for d in [*gb1, *gb2, *gbr]], run_time=1.4)
        self.play(FadeIn(label("single linkage: one cluster, via the bridge", 26, "#e2725b")
                         .next_to(ax, DOWN, buff=0.35)), run_time=1.0)
        self.wait(4.8)


class DendrogramRead(Stage):
    """The misreading the deck calls the most common one: two leaves drawn side
    by side are not therefore similar. Proved by flipping a subtree — the tree
    is unchanged, the neighbours are not."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def build_tree(self, ax, order, heights):
        """order: leaf labels left to right. heights: (i, j, h) merges by position."""
        g = VGroup()
        x = {lab: k + 1 for k, lab in enumerate(order)}
        tops = {lab: 0.0 for lab in order}
        pos = {lab: float(x[lab]) for lab in order}
        for a, b, h in heights:
            la = Line(ax.c2p(pos[a], tops[a]), ax.c2p(pos[a], h), color=CREAM, stroke_width=3)
            lb = Line(ax.c2p(pos[b], tops[b]), ax.c2p(pos[b], h), color=CREAM, stroke_width=3)
            tp = Line(ax.c2p(pos[a], h), ax.c2p(pos[b], h), color=CREAM, stroke_width=3)
            g.add(la, lb, tp)
            mid = (pos[a] + pos[b]) / 2
            pos[a] = pos[b] = mid
            tops[a] = tops[b] = h
            for k in list(pos):
                if pos[k] in (pos[a], pos[b]) and tops[k] == h:
                    pos[k], tops[k] = mid, h
        return g, x

    def construct(self):
        ax = Axes(x_range=[0, 5, 1], y_range=[0, 10, 2], x_length=7.6, y_length=4.2,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.3}).shift(DOWN * 0.4)
        self.play(Create(ax), run_time=0.9)
        self.play(FadeIn(label("merge height", 22, MUTED).next_to(ax, LEFT, buff=0.2).rotate(PI / 2)), run_time=0.6)

        # A,B merge low; C,D merge low; the two pairs only join at the top
        def draw(order):
            g = VGroup()
            xs = {lab: k + 1 for k, lab in enumerate(order)}
            pairs = [("A", "B", 1.2), ("C", "D", 1.5)]
            mids = {}
            for a, b, h in pairs:
                xa, xb = xs[a], xs[b]
                g.add(Line(ax.c2p(xa, 0), ax.c2p(xa, h), color=CREAM, stroke_width=3),
                      Line(ax.c2p(xb, 0), ax.c2p(xb, h), color=CREAM, stroke_width=3),
                      Line(ax.c2p(xa, h), ax.c2p(xb, h), color=CREAM, stroke_width=3))
                mids[(a, b)] = ((xa + xb) / 2, h)
            (m1, h1), (m2, h2) = mids[("A", "B")], mids[("C", "D")]
            g.add(Line(ax.c2p(m1, h1), ax.c2p(m1, 8.4), color=GOLD, stroke_width=3),
                  Line(ax.c2p(m2, h2), ax.c2p(m2, 8.4), color=GOLD, stroke_width=3),
                  Line(ax.c2p(m1, 8.4), ax.c2p(m2, 8.4), color=GOLD, stroke_width=3))
            labels = VGroup(*[label(lab, 24, CREAM).next_to(ax.c2p(xs[lab], 0), DOWN, buff=0.2) for lab in order])
            return g, labels

        tree, labs = draw(["A", "B", "C", "D"])
        self.play(Create(tree), FadeIn(labs), run_time=2.2)
        self.wait(3.5)

        # the tempting, wrong reading
        ring = SurroundingRectangle(VGroup(labs[1], labs[2]), color="#e2725b", buff=0.12, stroke_width=3)
        claim = label("\"B and C sit next to each other, so they are similar\"", 26, "#e2725b")
        claim.next_to(ax, UP, buff=0.25)
        self.play(Create(ring), FadeIn(claim), run_time=1.3)
        self.wait(4.3)

        # what the height actually says
        hb = DashedLine(ax.c2p(0, 8.4), ax.c2p(5, 8.4), color=GOLD, stroke_width=2)
        note = label("they only join at height 8.4 — the top of the tree", 26, GOLD).next_to(ax, UP, buff=0.25)
        self.play(Create(hb), FadeTransform(claim, note), run_time=1.4)
        self.wait(4.3)

        # and the proof: flip a subtree, nothing changes but the neighbours
        flip = label("flip one subtree: the same tree, different neighbours", 26, SKY).next_to(ax, UP, buff=0.25)
        tree2, labs2 = draw(["B", "A", "C", "D"])
        self.play(FadeOut(ring), FadeOut(hb), FadeTransform(note, flip), run_time=1.0)
        self.play(Transform(tree, tree2), Transform(labs, labs2), run_time=2.0)
        self.wait(3.8)
        tree3, labs3 = draw(["C", "D", "A", "B"])
        self.play(Transform(tree, tree3), Transform(labs, labs3), run_time=2.0)
        self.wait(3.8)

        closing = label("horizontal position carries no information. Read the height.",
                        27, GOLD).next_to(ax, DOWN, buff=0.55)
        self.play(FadeIn(closing), run_time=1.2)
        self.wait(4.9)


L12 = ["Dendrogram", "LinkageFour", "DendrogramRead"]


# ================================================================ lecture 14 — PCA
class Rotation(Stage):
    """The definition, made visible: a line turns through the cloud while the
    variance of the projection is measured at every angle. It stops where that
    number is largest, and that is the first component — not a metaphor, a
    maximum."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        rng = np.random.default_rng(6)
        ang_true = np.deg2rad(32)
        t = rng.normal(0, 1.5, 70)
        n = rng.normal(0, 0.55, 70)
        P = np.column_stack([t * np.cos(ang_true) - n * np.sin(ang_true),
                             t * np.sin(ang_true) + n * np.cos(ang_true)])

        ax = Axes(x_range=[-4, 4, 2], y_range=[-3, 3, 1], x_length=6.6, y_length=4.6,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.4})
        ax.to_edge(LEFT, buff=0.7)
        self.play(Create(ax), run_time=1.0)
        dots = VGroup(*[Dot(ax.c2p(*p), radius=0.055, color=SKY) for p in P])
        self.play(FadeIn(dots, lag_ratio=0.02), run_time=1.4)
        self.wait(2.0)

        theta = ValueTracker(np.deg2rad(-60))

        def direction():
            a = theta.get_value()
            return np.array([np.cos(a), np.sin(a)])

        line = always_redraw(lambda: Line(
            ax.c2p(*(-3.6 * direction())), ax.c2p(*(3.6 * direction())),
            color=CREAM, stroke_width=3.5))
        self.play(Create(line), run_time=1.0)

        def variance():
            return float(np.var(P @ direction()))

        bar_base = ax.get_right() + RIGHT * 1.9
        scale = 1.15
        bar = always_redraw(lambda: Rectangle(
            width=0.75, height=max(0.02, variance() * scale),
            color=GOLD, fill_color=GOLD, fill_opacity=0.8, stroke_width=0
        ).move_to(bar_base + UP * (max(0.02, variance() * scale) / 2 - 1.8)))
        num = always_redraw(lambda: DecimalNumber(
            variance(), num_decimal_places=2, color=GOLD, font_size=36
        ).next_to(bar, UP, buff=0.2))
        cap = MathTex(r"\operatorname{Var}(X\phi)", color=GOLD, font_size=30).move_to(bar_base + DOWN * 2.15)
        self.play(FadeIn(bar), FadeIn(num), FadeIn(cap), run_time=1.0)
        self.wait(2.2)

        # sweep: the number is the argument
        self.play(theta.animate.set_value(np.deg2rad(120)), run_time=8.0, rate_func=linear)
        self.wait(1.2)
        self.play(theta.animate.set_value(ang_true), run_time=3.0)
        self.wait(1.6)

        pc1 = Line(ax.c2p(*(-3.6 * direction())), ax.c2p(*(3.6 * direction())), color=GOLD, stroke_width=4.5)
        lab1 = MathTex(r"\phi_1", color=GOLD, font_size=36).next_to(ax.c2p(*(3.2 * direction())), UR, buff=0.1)
        self.play(FadeIn(pc1), FadeIn(lab1), run_time=1.0)
        self.play(FadeIn(label("the direction of most spread", 25, GOLD).next_to(ax, DOWN, buff=0.35)), run_time=0.9)
        self.wait(2.8)

        # the projections themselves
        d = direction()
        proj = VGroup(*[Line(ax.c2p(*p), ax.c2p(*((p @ d) * d)), color=CREAM,
                             stroke_width=1.3, stroke_opacity=0.5) for p in P[:30]])
        self.play(Create(proj, lag_ratio=0.04), run_time=2.2)
        self.play(FadeIn(label("each point's score is where it lands", 24, CREAM)
                         .next_to(ax, UP, buff=0.3)), run_time=0.9)
        self.wait(2.6)

        # the second component, perpendicular, with what is left
        d2 = np.array([-d[1], d[0]])
        pc2 = Line(ax.c2p(*(-2.2 * d2)), ax.c2p(*(2.2 * d2)), color="#c98bb9", stroke_width=4)
        lab2 = MathTex(r"\phi_2", color="#c98bb9", font_size=34).next_to(ax.c2p(*(2.0 * d2)), UL, buff=0.1)
        v2 = float(np.var(P @ d2))
        self.play(FadeOut(proj), Create(pc2), FadeIn(lab2), run_time=1.6)
        share = MathTex(rf"\frac{{\lambda_1}}{{\lambda_1+\lambda_2}} = "
                        rf"{variance() / (variance() + v2):.0%}".replace("%", r"\%"),
                        color=GOLD, font_size=34).next_to(ax, DOWN, buff=0.35)
        self.play(FadeIn(share), run_time=1.0)
        self.wait(3.2)
        closing = label("a rotation, not a deletion — nothing is dropped yet", 25, CREAM).next_to(share, DOWN, buff=0.3)
        self.play(FadeIn(closing), run_time=1.0)
        self.wait(3.0)


class PCAByHand(Stage):
    """Height and arm span for four people, standardised. Two columns holding
    one piece of information, and the second component with variance exactly
    zero — the simplest case where the method can be seen entire."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        pts = [(-1.5, -1.5), (-0.5, -0.5), (0.5, 0.5), (1.5, 1.5)]
        ax = Axes(x_range=[-2.5, 2.5, 1], y_range=[-2.5, 2.5, 1], x_length=5.4, y_length=5.4,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.4})
        ax.to_edge(LEFT, buff=0.9)
        self.play(Create(ax), run_time=0.9)
        self.play(FadeIn(label("height (z)", 20, MUTED).next_to(ax, DOWN, buff=0.25)),
                  FadeIn(label("arm span (z)", 20, MUTED).next_to(ax, LEFT, buff=0.2).rotate(PI / 2)), run_time=0.7)

        dots = VGroup(*[Dot(ax.c2p(*p), radius=0.085, color=SKY) for p in pts])
        self.play(FadeIn(dots, lag_ratio=0.2), run_time=1.4)
        self.wait(3.0)

        diag = ax.plot(lambda x: x, x_range=[-2.2, 2.2], color=GOLD, stroke_width=4)
        self.play(Create(diag), run_time=1.2)
        phi = MathTex(r"\phi_1 = (0.71,\ 0.71)", color=GOLD, font_size=34)
        phi.to_edge(RIGHT, buff=1.2).shift(UP * 2.2)
        self.play(FadeIn(phi), run_time=0.9)
        self.wait(3.2)

        # the four scores, one at a time
        rows = VGroup()
        prev = phi
        for (x, y), s in zip(pts, (-2.1, -0.7, 0.7, 2.1)):
            d = Dot(ax.c2p(x, y), radius=0.1, color=GOLD)
            t = MathTex(rf"({x},\ {y}) \;\rightarrow\; {s}", color=CREAM, font_size=30)
            t.next_to(prev, DOWN, buff=0.45).align_to(phi, LEFT)
            self.play(FadeIn(d, scale=1.5), FadeIn(t, shift=RIGHT * 0.15), run_time=0.8)
            self.wait(1.6)
            rows.add(d, t); prev = t

        var1 = MathTex(r"\text{variance} = 2.5", color=GOLD, font_size=34)
        var1.next_to(prev, DOWN, buff=0.55).align_to(phi, LEFT)
        self.play(Write(var1), run_time=1.1)
        self.wait(3.2)

        # the perpendicular one, and its zero
        perp = ax.plot(lambda x: -x, x_range=[-2.2, 2.2], color="#c98bb9", stroke_width=4)
        phi2 = MathTex(r"\phi_2 = (0.71,\ -0.71)", color="#c98bb9", font_size=32)
        phi2.next_to(var1, DOWN, buff=0.6).align_to(phi, LEFT)
        self.play(Create(perp), FadeIn(phi2), run_time=1.4)
        self.wait(2.4)
        zero = MathTex(r"\text{every score } = 0 \quad \text{variance} = 0", color="#c98bb9", font_size=30)
        zero.next_to(phi2, DOWN, buff=0.35).align_to(phi, LEFT)
        self.play(Write(zero), run_time=1.2)
        self.wait(3.5)

        closing = label("two columns, one piece of information", 27, GOLD).next_to(ax, DOWN, buff=0.45)
        self.play(FadeIn(closing), run_time=1.1)
        self.wait(4.1)


class ScreeChoice(Stage):
    """Three rules for how many components to keep, applied to one scree plot,
    giving three different answers. Which is the point."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        lam = np.array([3.4, 1.55, 1.08, 0.72, 0.51, 0.40, 0.20, 0.14])
        share = lam / lam.sum()
        cum = np.cumsum(share)

        ax = Axes(x_range=[0, 9, 2], y_range=[0, 4, 1], x_length=7.4, y_length=4.0,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.4}).shift(DOWN * 0.4)
        self.play(Create(ax), run_time=1.0)
        self.play(FadeIn(label("component", 22, MUTED).next_to(ax, DOWN, buff=0.28)),
                  FadeIn(MathTex(r"\lambda", color=MUTED, font_size=30).next_to(ax, LEFT, buff=0.22)), run_time=0.7)

        bars = VGroup()
        for k, v in enumerate(lam, start=1):
            b = Rectangle(width=0.42, height=0.001, color=SKY, fill_color=SKY, fill_opacity=0.75, stroke_width=0)
            b.move_to(ax.c2p(k, 0), aligned_edge=DOWN)
            bars.add(b)
        self.add(bars)
        self.play(*[b.animate.stretch_to_fit_height(ax.c2p(0, v)[1] - ax.c2p(0, 0)[1]).move_to(
                        ax.c2p(k, 0), aligned_edge=DOWN)
                    for b, (k, v) in zip(bars, enumerate(lam, start=1))], run_time=2.0)
        self.wait(4.1)

        # rule 1 — eigenvalue > 1
        one = DashedLine(ax.c2p(0, 1), ax.c2p(9, 1), color=GOLD, stroke_width=3)
        r1 = label("keep λ > 1  →  three components", 25, GOLD).next_to(ax, UP, buff=0.25)
        self.play(Create(one), FadeIn(r1), run_time=1.3)
        self.wait(5.1)

        # rule 2 — 80% cumulative
        k80 = int(np.argmax(cum >= 0.80)) + 1
        r2 = label(f"keep 80% of the variance  →  {k80} components", 25, "#c98bb9").next_to(ax, UP, buff=0.25)
        marks = VGroup(*[bars[i].copy().set_fill("#c98bb9", 0.85) for i in range(k80)])
        self.play(FadeTransform(r1, r2), FadeIn(marks), run_time=1.4)
        self.wait(5.1)

        # rule 3 — the elbow
        r3 = label("stop at the elbow  →  two components", 25, CREAM).next_to(ax, UP, buff=0.25)
        el = Circle(radius=0.3, color=CREAM, stroke_width=3).move_to(ax.c2p(2, lam[1]))
        self.play(FadeOut(marks), FadeTransform(r2, r3), Create(el), run_time=1.4)
        self.wait(5.1)

        closing = VGroup(
            label("three rules, three answers, one dataset", 27, GOLD),
            label("choose, and write the sentence that defends it", 24, MUTED),
        ).arrange(DOWN, buff=0.25).next_to(ax, DOWN, buff=0.7)
        self.play(FadeOut(one), FadeOut(el), FadeTransform(r3, closing), run_time=1.4)
        self.wait(5.8)


L14 = ["Rotation", "PCAByHand", "ScreeChoice"]
L11 = ["Lloyd", "KmeansByHand", "ScaleBreaks", "ShapeBreaks", "ElbowLie"]
L18 = ["Boundary", "PerceptronByHand", "Perceptron", "GradientDescent", "Sigmoid", "HiddenLayer", "Overfitting"]
L19 = ["DataSplit", "ValidationCurve", "ModelRace", "DeepScale", "AutoencoderPCA"]
SCENES = L11 + L12 + L14 + L18 + L19

