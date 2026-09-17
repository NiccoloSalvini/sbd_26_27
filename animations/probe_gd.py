from manim import *

NAVY, GOLD, MUTED = "#002f57", "#b8860b", "#5f6b75"

class GradientDescent(Scene):
    """A ball rolls down L(W) = (W-2)^2 in steps of -eta * L'(W). The probe scene."""
    def construct(self):
        self.camera.background_color = WHITE
        ax = Axes(x_range=[-1, 5, 1], y_range=[0, 9, 3], x_length=9, y_length=4.5,
                  axis_config={"color": MUTED, "include_tip": False})
        curve = ax.plot(lambda w: (w - 2) ** 2, color=NAVY, stroke_width=4)
        label = Text("L(W)", color=NAVY, font="Libre Franklin", font_size=30).next_to(ax.y_axis, UP)
        self.add(ax, curve, label)
        eta, w = 0.3, 4.7
        dot = Dot(ax.c2p(w, (w - 2) ** 2), color=GOLD, radius=0.12)
        self.add(dot)
        for _ in range(7):
            grad = 2 * (w - 2)
            w_new = w - eta * grad
            arrow = Arrow(ax.c2p(w, (w - 2) ** 2), ax.c2p(w_new, (w_new - 2) ** 2), buff=0, color=GOLD, stroke_width=3, max_tip_length_to_length_ratio=0.2)
            self.play(GrowArrow(arrow), run_time=0.35)
            self.play(dot.animate.move_to(ax.c2p(w_new, (w_new - 2) ** 2)), run_time=0.4)
            w = w_new
        self.wait(0.5)
