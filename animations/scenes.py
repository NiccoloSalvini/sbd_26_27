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


# ---------------------------------------------------------------- 1. motivation
class Boundary(Stage):
    """Two classes. A line tries and fails; a curve bends where the data bend."""

    def construct(self):
        rng = np.random.default_rng(3)
        ax = Axes(x_range=[-3, 3, 1], y_range=[-2.2, 2.2, 1], x_length=8, y_length=4.8,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.5})
        self.add(ax)
        # class A: inside a band around a sine; class B: outside
        pts, cols = [], []
        for _ in range(60):
            x, y = rng.uniform(-2.8, 2.8), rng.uniform(-2, 2)
            inside = abs(y - 0.9 * np.sin(1.3 * x)) < 0.8
            pts.append(Dot(ax.c2p(x, y), radius=0.06, color=GOLD if inside else SKY))
        dots = VGroup(*pts)
        self.play(FadeIn(dots, lag_ratio=0.02), run_time=1.2)
        line = ax.plot(lambda x: 0.0 * x, color=CREAM, stroke_width=3)
        tl = label("a line", 26, CREAM).next_to(ax, UP, buff=0.15)
        self.play(Create(line), FadeIn(tl), run_time=1.0)
        self.wait(0.6)
        # it rotates looking for a fit and never finds one
        self.play(Rotate(line, angle=0.35, about_point=ax.c2p(0, 0)), run_time=0.7)
        self.play(Rotate(line, angle=-0.7, about_point=ax.c2p(0, 0)), run_time=0.9)
        self.play(Rotate(line, angle=0.35, about_point=ax.c2p(0, 0)), run_time=0.6)
        curve = ax.plot(lambda x: 0.9 * np.sin(1.3 * x), color=GOLD, stroke_width=4)
        tc = label("a curve", 26, GOLD).next_to(ax, UP, buff=0.15)
        self.play(Transform(line, curve), FadeTransform(tl, tc), run_time=1.4)
        self.wait(1.0)


# ---------------------------------------------------------------- 2. perceptron
# The AND gate, the one worked example of the deck. Arithmetic is done in
# hundredths as integers so 0.3 - 0.1 + 0.1 prints as 0.3 and never as
# 0.30000000000000004, and so "z >= theta" is an exact comparison.
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


# ---------------------------------------------------------------- 3. gradient descent
class GradientDescent(Stage):
    """The same bowl, three learning rates: creep, converge, overshoot."""

    def construct(self):
        panels = VGroup()
        specs = [(r"\eta\ \text{too small}", 0.05, 9), (r"\eta\ \text{right}", 0.3, 7), (r"\eta\ \text{too large}", 1.05, 6)]
        for ttl, eta, steps in specs:
            ax = Axes(x_range=[-1, 5, 1], y_range=[0, 9, 3], x_length=3.7, y_length=2.8,
                      axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.5})
            curve = ax.plot(lambda w: (w - 2) ** 2, color=SKY, stroke_width=4)
            t = MathTex(ttl, color=CREAM, font_size=30).next_to(ax, UP, buff=0.15)
            panels.add(VGroup(ax, curve, t))
        panels.arrange(RIGHT, buff=0.35).shift(UP * 0.3)
        self.add(panels)
        rule = MathTex(r"W_{t+1} = W_t - \eta\,\frac{\partial L}{\partial W}", color=CREAM, font_size=36).to_edge(DOWN, buff=0.35)
        self.play(Write(rule), run_time=0.9)
        f = lambda w: (w - 2) ** 2
        for (ttl, eta, steps), panel in zip(specs, panels):
            ax = panel[0]
            w = 4.6
            dot = Dot(ax.c2p(w, f(w)), color=GOLD, radius=0.09)
            self.add(dot)
            for _ in range(steps):
                wn = max(-0.9, min(4.9, w - eta * 2 * (w - 2)))
                seg = Line(ax.c2p(w, f(w)), ax.c2p(wn, f(wn)), color=GOLD, stroke_width=2.5, stroke_opacity=0.75)
                self.play(Create(seg), dot.animate.move_to(ax.c2p(wn, f(wn))), run_time=0.26)
                w = wn
        self.wait(0.8)


# ---------------------------------------------------------------- 4. one neuron = GLM
class Sigmoid(Stage):
    """From the perceptron's step to the sigmoid: a probability, and a GLM."""

    def construct(self):
        ax = Axes(x_range=[-6, 6, 2], y_range=[-0.2, 1.2, 0.5], x_length=8, y_length=4,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.5}).shift(DOWN * 0.3)
        self.add(ax)
        self.add(MathTex(r"\lambda = W_0 + \textstyle\sum_j W_j X_j", color=MUTED, font_size=28).next_to(ax, DOWN, buff=0.2))
        step = VGroup(ax.plot(lambda x: 0, x_range=[-6, 0], color=SKY, stroke_width=4),
                      ax.plot(lambda x: 1, x_range=[0, 6], color=SKY, stroke_width=4))
        ts = MathTex(r"g(\lambda) = \operatorname{sign}(\lambda)", color=SKY, font_size=36).to_edge(UP, buff=0.4)
        self.play(Create(step), Write(ts), run_time=1.0)
        self.wait(0.5)
        sig = ax.plot(lambda x: 1 / (1 + np.exp(-x)), color=GOLD, stroke_width=4)
        tg = MathTex(r"g(\lambda) = \sigma(\lambda) = \frac{1}{1 + e^{-\lambda}}", color=GOLD, font_size=36).to_edge(UP, buff=0.4)
        self.play(Transform(step, sig), FadeTransform(ts, tg), run_time=1.6)
        # a probability: read one value off the curve
        x0 = 1.4
        p0 = 1 / (1 + np.exp(-x0))
        v = DashedLine(ax.c2p(x0, 0), ax.c2p(x0, p0), color=CREAM, stroke_width=2)
        h = DashedLine(ax.c2p(x0, p0), ax.c2p(-6, p0), color=CREAM, stroke_width=2)
        pl = MathTex(rf"\hat\pi = {p0:.2f}", color=CREAM, font_size=32).next_to(ax.c2p(-6, p0), LEFT, buff=0.15)
        self.play(Create(v), Create(h), FadeIn(pl), run_time=1.0)
        bridge = MathTex(r"\text{link } h = g^{-1}:\quad \log\frac{\pi}{1-\pi} = \lambda\ \ \Rightarrow\ \ \text{logistic regression}",
                         color=CREAM, font_size=30).to_edge(DOWN, buff=0.35)
        self.play(Write(bridge), run_time=1.2)
        self.wait(1.2)


# ---------------------------------------------------------------- 5. hidden layer
class HiddenLayer(Stage):
    """Add hidden neurons and the boundary bends: 1, then 2, then 5."""

    def construct(self):
        rng = np.random.default_rng(7)
        ax = Axes(x_range=[-3, 3, 1], y_range=[-2.2, 2.2, 1], x_length=7.2, y_length=4.4,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.5}).to_edge(LEFT, buff=0.5)
        self.add(ax)
        truth = lambda x: 0.9 * np.sin(1.3 * x)
        pts = VGroup()
        for _ in range(60):
            x, y = rng.uniform(-2.8, 2.8), rng.uniform(-2, 2)
            pts.add(Dot(ax.c2p(x, y), radius=0.055, color=GOLD if y > truth(x) else SKY))
        self.add(pts)
        # the network diagram on the right: nodes rebuilt per L, one label transformed
        def net(L):
            g = VGroup()
            xs = VGroup(*[Dot(radius=0.13, color=MUTED) for _ in range(2)]).arrange(DOWN, buff=0.7)
            hs = VGroup(*[Dot(radius=0.13, color=GOLD) for _ in range(L)]).arrange(DOWN, buff=0.34)
            out = Dot(radius=0.15, color=CREAM)
            cols = VGroup(xs, hs, out).arrange(RIGHT, buff=1.1)
            for a in xs:
                for b in hs:
                    g.add(Line(a.get_center(), b.get_center(), stroke_width=1.2, color=MUTED, stroke_opacity=0.6))
            for b in hs:
                g.add(Line(b.get_center(), out.get_center(), stroke_width=1.2, color=MUTED, stroke_opacity=0.6))
            g.add(cols)
            return g.to_edge(RIGHT, buff=0.6)

        fits = {
            1: lambda x: 0.25 * x,
            2: lambda x: 0.9 * np.tanh(1.2 * x) * (1 - 0.15 * x),
            5: truth,
        }
        cur_b, cur_n, cur_l = None, None, None
        for L in (1, 2, 5):
            b = ax.plot(fits[L], color=CREAM, stroke_width=4)
            n = net(L)
            l = MathTex(rf"L = {L}", color=CREAM, font_size=40).next_to(n, UP, buff=0.4)
            if cur_b is None:
                self.play(Create(b), FadeIn(n), FadeIn(l), run_time=1.1)
                cur_b, cur_n, cur_l = b, n, l
            else:
                self.play(Transform(cur_b, b), FadeTransform(cur_n, n), Transform(cur_l, l), run_time=1.4)
                cur_n = n
            self.wait(0.7)
        wl = MathTex(r"\text{weights} = (p+1)L + (L+1)", color=MUTED, font_size=30).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(wl), run_time=0.5)
        self.wait(1.0)


# ---------------------------------------------------------------- 6. overfitting
class Overfitting(Stage):
    """Train keeps falling; test turns up. Stop where it turns."""

    def construct(self):
        ax = Axes(x_range=[0, 10, 2], y_range=[0, 4, 1], x_length=8, y_length=4.2,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.5})
        self.add(ax, label("training iterations", 22, MUTED).next_to(ax.x_axis, DOWN, buff=0.2),
                 label("error", 22, MUTED).next_to(ax.y_axis, LEFT, buff=0.2).rotate(PI / 2))
        train = ax.plot(lambda x: 3.4 * np.exp(-0.45 * x) + 0.15, color=SKY, stroke_width=4)
        test = ax.plot(lambda x: 3.4 * np.exp(-0.45 * x) + 0.15 + 0.06 * (x - 3.2) ** 2 * (x > 3.2), color=GOLD, stroke_width=4)
        self.play(Create(train), Create(test), run_time=3.2, rate_func=linear)
        self.play(FadeIn(label("train", 22, SKY).next_to(ax.c2p(10, train.underlying_function(10)), RIGHT, buff=0.15)),
                  FadeIn(label("test", 22, GOLD).next_to(ax.c2p(10, test.underlying_function(10)), RIGHT, buff=0.15)), run_time=0.4)
        opt = DashedLine(ax.c2p(3.2, 0), ax.c2p(3.2, 3.6), color=CREAM, stroke_width=2)
        self.play(Create(opt), FadeIn(label("stop here", 24, CREAM).next_to(opt, UP, buff=0.1)), run_time=0.6)
        self.wait(0.8)


SCENES = ["Boundary", "PerceptronByHand", "Perceptron", "GradientDescent", "Sigmoid", "HiddenLayer", "Overfitting"]
