"""manim scenes for the Module 2 decks.

Render one:      uv run manim -qm scenes.py LearningRate
Render all:      make clips   (from the repo root; copies to lectures/media/)

Every scene: white ground, the site's palette, Libre Franklin for labels,
1280x720 from manim.cfg. Keep each clip under fifteen seconds — it plays on a
slide, next to a sentence, not instead of one.
"""
from manim import *

NAVY, GOLD, MUTED, INK, RULE = "#002f57", "#b8860b", "#5f6b75", "#1c2226", "#e6e9ec"
FONT = "Libre Franklin"


def loss_axes(x_length=5.6, y_length=3.6):
    ax = Axes(x_range=[-1, 5, 1], y_range=[0, 9, 3], x_length=x_length, y_length=y_length,
              axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.5})
    curve = ax.plot(lambda w: (w - 2) ** 2, color=NAVY, stroke_width=4)
    return ax, curve


def descend(scene, ax, eta, steps, w0=4.6, color=GOLD, run=0.32):
    """Gradient descent on (w-2)^2 from w0; returns the trail."""
    w = w0
    f = lambda w: (w - 2) ** 2
    dot = Dot(ax.c2p(w, f(w)), color=color, radius=0.1)
    scene.add(dot)
    trail = VGroup()
    for _ in range(steps):
        w_new = w - eta * 2 * (w - 2)
        w_new = max(-0.9, min(4.9, w_new))
        seg = Line(ax.c2p(w, f(w)), ax.c2p(w_new, f(w_new)), color=color, stroke_width=2.5, stroke_opacity=0.7)
        scene.play(Create(seg), dot.animate.move_to(ax.c2p(w_new, f(w_new))), run_time=run)
        trail.add(seg)
        w = w_new
    return trail


class LearningRate(Scene):
    """Lecture 18, slide 'The learning rate': the same bowl, three step sizes."""

    def construct(self):
        self.camera.background_color = WHITE
        panels = VGroup()
        specs = [("η too small", 0.04, 9), ("η right", 0.3, 7), ("η too large", 1.05, 7)]
        for title, eta, steps in specs:
            ax, curve = loss_axes(x_length=3.8, y_length=2.9)
            label = Text(title, font=FONT, font_size=24, color=NAVY).next_to(ax, UP, buff=0.15)
            panels.add(VGroup(ax, curve, label))
        panels.arrange(RIGHT, buff=0.35).move_to(ORIGIN)
        self.add(panels)
        caption = Text("W(t+1) = W(t) − η · L′(W)", font=FONT, font_size=26, color=MUTED).to_edge(DOWN, buff=0.35)
        self.add(caption)
        for (title, eta, steps), panel in zip(specs, panels):
            ax = panel[0]
            descend(self, ax, eta, steps, run=0.28)
        self.wait(0.6)


class Overfitting(Scene):
    """Lecture 18, 'More flexibility, and what it costs': train falls, test turns up."""

    def construct(self):
        self.camera.background_color = WHITE
        ax = Axes(x_range=[0, 10, 2], y_range=[0, 4, 1], x_length=8, y_length=4.2,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.5})
        xl = Text("training iterations", font=FONT, font_size=22, color=MUTED).next_to(ax.x_axis, DOWN, buff=0.2)
        yl = Text("error", font=FONT, font_size=22, color=MUTED).next_to(ax.y_axis, LEFT, buff=0.2).rotate(PI / 2)
        self.add(ax, xl, yl)
        train = ax.plot(lambda x: 3.4 * np.exp(-0.45 * x) + 0.15, color=NAVY, stroke_width=4)
        test = ax.plot(lambda x: 3.4 * np.exp(-0.45 * x) + 0.15 + 0.06 * (x - 3.2) ** 2 * (x > 3.2), color=GOLD, stroke_width=4)
        lt = Text("train", font=FONT, font_size=22, color=NAVY).next_to(ax.c2p(10, train.underlying_function(10)), RIGHT, buff=0.15)
        le = Text("test", font=FONT, font_size=22, color=GOLD).next_to(ax.c2p(10, test.underlying_function(10)), RIGHT, buff=0.15)
        self.play(Create(train), Create(test), run_time=3.2, rate_func=linear)
        self.play(FadeIn(lt), FadeIn(le), run_time=0.4)
        opt = DashedLine(ax.c2p(3.2, 0), ax.c2p(3.2, 3.6), color=MUTED, stroke_width=2)
        ol = Text("stop here", font=FONT, font_size=22, color=INK).next_to(opt, UP, buff=0.1)
        self.play(Create(opt), FadeIn(ol), run_time=0.6)
        self.wait(0.8)
