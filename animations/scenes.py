"""manim scenes for the Module 2 decks — lecture 18, neural networks.

Render one:      uv run manim -qm scenes.py Perceptron
Render all:      make clips   (from the repo root; remuxes and copies to lectures/media/)

The look is the one maths reels use: a dark stage, one object, one
transformation at a time, formulas set in real LaTeX. The stage is the
course navy rather than black, so a clip on a white slide reads as ours.
Each clip is one idea in six to twelve seconds; the sentence next to it on
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
    def setup(self):
        self.camera.background_color = NAVY


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
class Perceptron(Stage):
    """The AND gate, learnt: one weight update per mistake, the boundary turns."""

    def construct(self):
        ax = Axes(x_range=[-0.5, 1.6, 1], y_range=[-0.5, 1.6, 1], x_length=4.6, y_length=4.6,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.5}).to_edge(LEFT, buff=0.7)
        self.add(ax)
        data = [((0, 0), 0), ((0, 1), 0), ((1, 0), 0), ((1, 1), 1)]
        dots = VGroup(*[Dot(ax.c2p(*p), radius=0.11, color=GOLD if y else SKY) for p, y in data])
        self.add(dots)
        self.add(label("y = 1", 22, GOLD).next_to(dots[3], UR, buff=0.08),
                 label("y = 0", 22, SKY).next_to(dots[0], DL, buff=0.08))
        # the rule, on the right
        rule = MathTex(r"\hat y = \operatorname{sign}\!\big(W_1 X_1 + W_2 X_2 - \theta\big)",
                       color=CREAM, font_size=36).to_edge(RIGHT, buff=0.6).shift(UP * 2.2)
        upd = MathTex(r"W \leftarrow W + \eta\,(y - \hat y)\,X", color=GOLD, font_size=36).next_to(rule, DOWN, buff=0.35)
        self.play(Write(rule), run_time=1.0)
        self.play(Write(upd), run_time=0.8)
        w = np.array([0.3, -0.1]); theta, eta = 0.2, 0.1

        def boundary(w):
            # W1 x + W2 y = theta  ->  y = (theta - W1 x) / W2 ; handle W2 ~ 0
            if abs(w[1]) < 1e-6:
                x0 = theta / w[0]
                return Line(ax.c2p(x0, -0.5), ax.c2p(x0, 1.6), color=CREAM, stroke_width=3)
            return ax.plot(lambda x: (theta - w[0] * x) / w[1], x_range=[-0.5, 1.6], color=CREAM, stroke_width=3)

        wlab = always_redraw(lambda: MathTex(rf"W = ({w[0]:.1f},\ {w[1]:.1f})", color=CREAM, font_size=34)
                             .next_to(upd, DOWN, buff=0.6))
        bnd = boundary(w)
        self.play(Create(bnd), FadeIn(wlab), run_time=0.8)
        # two epochs, only the rows that change something get a beat
        for epoch in (1, 2):
            for (x1, x2), y in data:
                z = w[0] * x1 + w[1] * x2 - theta
                yhat = 1 if z >= 0 else 0
                if yhat == y:
                    continue
                d = dots[data.index(((x1, x2), y))]
                self.play(Indicate(d, color=CREAM, scale_factor=1.6), run_time=0.5)
                w = w + eta * (y - yhat) * np.array([x1, x2])
                new = boundary(w)
                self.play(Transform(bnd, new), run_time=0.9)
        ok = label("every row correct — it stops", 26, GOLD).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(ok), run_time=0.6)
        self.wait(1.2)


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


SCENES = ["Boundary", "Perceptron", "GradientDescent", "Sigmoid", "HiddenLayer", "Overfitting"]
