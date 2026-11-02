"""Lecture 14, principal components: the three clips rewritten to the clip rules
(one caption slot, a fixed right panel, every number computed here, 40 to 90 s).

    .venv/bin/manim -qm --disable_caching scenes_14.py Rotation PCAByHand ScreeChoice

Same class names as in scenes.py, so the Makefile and the deck keep working once
these replace the old ones there.
"""
from scenes import *

MAUVE_ = "#c98bb9"   # the second component, as in the other PCA clips


# ---------------------------------------------------------------- Rotation
class Rotation(Stage):
    """Sixty hospital wards, patients' average score for courtesy and for clarity,
    centred. A line turns through the cloud; every ward is dropped onto it, and
    the variance of where they land is traced against the angle on the right.
    It peaks at the first component and bottoms out 90 degrees later. Then one
    ward's score, the second component, and the share: 89% on one direction."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        rng = np.random.default_rng(4)
        a = np.deg2rad(32)
        t, nz = rng.normal(0, 0.95, 60), rng.normal(0, 0.33, 60)
        P = np.column_stack([t * np.cos(a) - nz * np.sin(a), t * np.sin(a) + nz * np.cos(a)])
        P = P - P.mean(0)                                   # centred, as the deck says
        C = P.T @ P / len(P)                                # X'X / n, the deck's covariance
        lam, V = np.linalg.eigh(C)
        l1, l2 = lam[1], lam[0]
        v1 = V[:, 1] * np.sign(V[0, 1])
        v2 = np.array([-v1[1], v1[0]])
        a_max = np.degrees(np.arctan2(v1[1], v1[0]))

        # equal scale on both axes, so right angles look like right angles
        ax = Axes(x_range=[-2.5, 2.5, 1], y_range=[-2, 2, 1], x_length=6.0, y_length=4.8,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.4})
        ax.to_edge(LEFT, buff=0.9).shift(UP * 0.45)
        xl = label("courtesy", 22, MUTED).next_to(ax, DOWN, buff=0.2)
        yl = label("clarity", 22, MUTED).rotate(PI / 2).next_to(ax, LEFT, buff=0.2)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.0)
        dots = VGroup(*[Dot(ax.c2p(*p), radius=0.055, color=SKY) for p in P])
        self.play(FadeIn(dots, lag_ratio=0.02), run_time=1.4)
        slot = np.array([0, -3.2, 0])
        self.caption(label("60 hospital wards: patients' average score for courtesy and for clarity", 26).move_to(slot))
        self.wait(3.0)
        self.caption(label("both centred at zero. Wards good at one tend to be good at the other", 26).move_to(slot))
        self.wait(3.0)

        theta = ValueTracker(a_max - 90)

        def d():
            r = np.deg2rad(theta.get_value())
            return np.array([np.cos(r), np.sin(r)])

        def var_at(deg):
            r = np.deg2rad(deg)
            u = np.array([np.cos(r), np.sin(r)])
            return float(u @ C @ u)

        line = always_redraw(lambda: Line(ax.c2p(*(-2.1 * d())), ax.c2p(*(2.1 * d())),
                                          color=CREAM, stroke_width=3))
        self.caption(label("a line through the centre: every ward dropped onto it at right angles", 26).move_to(slot))
        self.play(Create(line), run_time=1.0)
        u0 = d()
        drops = VGroup(*[Line(ax.c2p(*p), ax.c2p(*((p @ u0) * u0)), color=CREAM,
                              stroke_width=1.2, stroke_opacity=0.55) for p in P])
        feet = always_redraw(lambda: VGroup(*[Dot(ax.c2p(*((p @ d()) * d())), radius=0.035, color=GOLD)
                                              for p in P]))
        self.play(Create(drops, lag_ratio=0.02), FadeIn(feet), run_time=1.6)
        self.wait(3.0)

        # the panel: variance of the projection, traced against the angle
        COL = 1.5
        head = label("variance of where they land, by angle", 22, MUTED).move_to([0, 3.2, 0]).align_to([COL - 0.4, 0, 0], LEFT)
        ax2 = Axes(x_range=[-60, 130, 30], y_range=[0, 1, 0.5], x_length=4.8, y_length=2.0,
                   axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.2})
        ax2.move_to([0, 1.6, 0]).align_to([COL, 0, 0], LEFT)
        xt = VGroup(*[label(f"{g}°", 16, MUTED).next_to(ax2.c2p(g, 0), DOWN, buff=0.12) for g in (-60, 0, 60, 120)])
        yt = VGroup(*[label(f"{g:.1f}", 16, MUTED).next_to(ax2.c2p(-60, g), LEFT, buff=0.12) for g in (0.5, 1.0)])
        start = theta.get_value()
        trace = always_redraw(lambda: ax2.plot(var_at, x_range=[start, max(start + 1, theta.get_value()), 1],
                                               color=GOLD, stroke_width=3))
        tip = always_redraw(lambda: Dot(ax2.c2p(theta.get_value(), var_at(theta.get_value())),
                                        radius=0.06, color=GOLD))
        vlab = MathTex(r"\operatorname{Var}(X\phi) =", color=CREAM, font_size=34)
        vnum = DecimalNumber(var_at(start), num_decimal_places=2, color=GOLD, font_size=34)
        rowA = VGroup(vlab, vnum).arrange(RIGHT, buff=0.2).move_to([0, -0.15, 0]).align_to([COL - 0.4, 0, 0], LEFT)
        vnum.add_updater(lambda m: m.set_value(var_at(theta.get_value())).next_to(vlab, RIGHT, buff=0.2))
        self.play(FadeOut(drops), FadeIn(head), Create(ax2), FadeIn(xt), FadeIn(yt),
                  FadeIn(trace), FadeIn(tip), FadeIn(rowA), run_time=1.2)
        self.caption(label("how spread out they land: the variance of the projection", 26).move_to(slot))
        self.wait(3.0)

        self.caption(label("turn the line, and watch the number", 26).move_to(slot))
        self.play(theta.animate.set_value(a_max + 90), run_time=9.0, rate_func=linear)
        # the whole curve stays on screen while the line goes back to its peak
        full = ax2.plot(var_at, x_range=[start, a_max + 90, 1], color=GOLD, stroke_width=3)
        self.remove(trace)
        self.add(full)
        self.wait(1.0)
        self.caption(label(f"largest at {a_max:.0f}°, smallest at right angles to it", 26).move_to(slot))
        self.play(theta.animate.set_value(a_max), run_time=3.0)
        vnum.clear_updaters()
        peak = DashedLine(ax2.c2p(a_max, 0), ax2.c2p(a_max, l1), color=GOLD, stroke_width=2)
        pc1 = Line(ax.c2p(*(-2.1 * v1)), ax.c2p(*(2.1 * v1)), color=GOLD, stroke_width=4.5)
        def clear_spot(mob, anchor, sides):
            # the side of the line's end farthest from every ward, so no label sits on a dot
            best = max(sides, key=lambda sd: min(np.linalg.norm(mob.copy().next_to(anchor, sd, buff=0.12).get_center()
                                                                 - dt.get_center()) for dt in dots))
            return mob.next_to(anchor, best, buff=0.12)

        lab1 = clear_spot(MathTex(r"\phi_1", color=GOLD, font_size=36), ax.c2p(*(2.1 * v1)), [UP, UL, UR, RIGHT, DR])
        rowA2 = MathTex(rf"\lambda_1 = \operatorname{{Var}}(X\phi_1) = {l1:.2f}", color=GOLD, font_size=34)
        rowA2.move_to(rowA).align_to(rowA, LEFT)
        rowB = MathTex(rf"\phi_1 = ({v1[0]:.2f},\ {v1[1]:.2f})", color=GOLD, font_size=34)
        rowB.move_to([0, -0.85, 0]).align_to(rowA, LEFT)
        self.remove(line)
        self.add(pc1)
        self.play(Create(peak), FadeIn(lab1), Transform(rowA, rowA2), FadeIn(rowB, shift=RIGHT * 0.15), run_time=1.0)
        self.caption(label("the maximum is the first component: a direction, found by a number", 26, GOLD).move_to(slot))
        self.wait(3.4)

        # one ward's score: where it lands on the line
        s = P @ v1
        i = int(np.argmax(s))
        foot_i = s[i] * v1
        ring = Circle(radius=0.15, color=CREAM, stroke_width=3).move_to(ax.c2p(*P[i]))
        seg = Line(ax.c2p(*P[i]), ax.c2p(*foot_i), color=CREAM, stroke_width=2.5)
        sc = label(f"score {s[i]:.2f}", 22, CREAM).next_to(ring, RIGHT, buff=0.15)
        self.play(Create(ring), Create(seg), FadeIn(sc), run_time=1.0)
        self.caption(label("a ward's score on PC1 is where it lands: this one, the best on both", 26).move_to(slot))
        self.wait(3.4)

        # the second component, at right angles, with what is left
        pc2 = Line(ax.c2p(*(-1.6 * v2)), ax.c2p(*(1.6 * v2)), color=MAUVE_, stroke_width=4)
        lab2 = clear_spot(MathTex(r"\phi_2", color=MAUVE_, font_size=34), ax.c2p(*(1.6 * v2)), [UP, UL, UR, LEFT, DL])
        rowC = MathTex(rf"\lambda_2 = {l2:.2f}", color=MAUVE_, font_size=34)
        rowC.move_to([0, -1.55, 0]).align_to(rowA, LEFT)
        self.play(FadeOut(VGroup(ring, seg, sc)), FadeOut(feet), Create(pc2), FadeIn(lab2),
                  FadeIn(rowC, shift=RIGHT * 0.15), run_time=1.4)
        self.caption(label("at right angles, the spread that is left: the second component", 26).move_to(slot))
        self.wait(3.2)

        share = l1 / (l1 + l2)
        rowD = MathTex(rf"\frac{{\lambda_1}}{{\lambda_1 + \lambda_2}} = {100 * share:.0f}\%", color=GOLD, font_size=34)
        rowD.move_to([0, -2.3, 0]).align_to(rowA, LEFT)
        self.play(FadeIn(rowD, shift=RIGHT * 0.15), run_time=0.8)
        self.caption(label(f"{100 * share:.0f}% of the spread on one direction: call it service experience", 26).move_to(slot))
        self.wait(3.6)
        self.caption(label("a rotation, not a deletion: two axes in, two axes out, nothing dropped yet", 26, GOLD).move_to(slot))
        self.wait(4.2)


# ---------------------------------------------------------------- PCAByHand
class PCAByHand(Stage):
    """Four patients, height and arm span in tens of cm from the mean: two columns
    that always agree. The table on the right keeps the old columns next to the
    new ones, so the variance row shows the whole method: 1.25 + 1.25 in,
    2.5 + 0 out. Every score is a weighted sum written out, and on the second
    component all four patients land on the same spot."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        X = np.array([[-1.5, -1.5], [-0.5, -0.5], [0.5, 0.5], [1.5, 1.5]])
        names = ["A", "B", "C", "D"]
        C = X.T @ X / len(X)                                 # X'X / n
        lam, V = np.linalg.eigh(C)
        v1 = V[:, 1] * np.sign(V[0, 1])
        v2 = np.array([v1[1], -v1[0]])
        s1, s2 = X @ v1, X @ v2
        var_cols = X.var(0)
        l1, l2 = s1.var(), s2.var()

        def fmt(x, nd=2):
            x = 0.0 if abs(x) < 1e-9 else x
            return f"{x:.{nd}f}".rstrip("0").rstrip(".") if nd == 1 else f"{x:.{nd}f}"

        ax = Axes(x_range=[-2.5, 2.5, 1], y_range=[-2.5, 2.5, 1], x_length=4.8, y_length=4.8,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.4})
        ax.to_edge(LEFT, buff=1.1).shift(UP * 0.35)
        xl = label("height", 22, MUTED).next_to(ax, DOWN, buff=0.15)
        yl = label("arm span", 22, MUTED).rotate(PI / 2).next_to(ax, LEFT, buff=0.15)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.0)
        slot = np.array([0, -3.2, 0])

        # the table: old columns, then new ones
        L = 0.3
        CX = {"h": 2.0, "a": 3.3, "p1": 4.75, "p2": 6.05}
        YH, YR, YV = 2.05, [1.45, 0.9, 0.35, -0.2], -0.95
        hdr = VGroup(label("height", 22, MUTED).move_to([CX["h"], YH, 0]),
                     label("arm span", 22, MUTED).move_to([CX["a"], YH, 0]))
        hdr_pc = VGroup(label("PC1", 22, GOLD).move_to([CX["p1"], YH, 0]),
                        label("PC2", 22, MAUVE_).move_to([CX["p2"], YH, 0]))
        sep = Line([4.05, YH + 0.25, 0], [4.05, YV - 0.25, 0], color=MUTED, stroke_width=1.2)
        rule = Line([L, YV + 0.35, 0], [6.75, YV + 0.35, 0], color=MUTED, stroke_width=1.2)

        def num(x, col, y, color=CREAM):
            return MathTex(fmt(x, 1) if col in ("h", "a") else fmt(x), color=color, font_size=30).move_to([CX[col], y, 0])

        self.caption(label("four patients: height and arm span, in tens of cm from the mean", 26).move_to(slot))
        self.play(FadeIn(hdr), run_time=0.6)
        dots, tags = VGroup(), VGroup()
        for k, (p, nm) in enumerate(zip(X, names)):
            dt = Dot(ax.c2p(*p), radius=0.085, color=SKY)
            tg = label(nm, 20, MUTED).next_to(dt, DR, buff=0.08)
            row = VGroup(label(nm, 22, MUTED).move_to([L + 0.2, YR[k], 0]), num(p[0], "h", YR[k]), num(p[1], "a", YR[k]))
            self.play(FadeIn(dt, scale=1.4), FadeIn(tg), FadeIn(row, shift=RIGHT * 0.1), run_time=0.6)
            dots.add(dt); tags.add(tg)
        self.wait(1.6)
        self.caption(label("arm span equals height for every one of them: the columns always agree", 26).move_to(slot))
        self.wait(3.0)

        vrow = VGroup(label("variance", 22, MUTED).move_to([0, YV, 0]).align_to([L, 0, 0], LEFT),
                      MathTex(f"{var_cols[0]:.2f}", color=CREAM, font_size=30).move_to([CX["h"], YV, 0]),
                      MathTex(f"{var_cols[1]:.2f}", color=CREAM, font_size=30).move_to([CX["a"], YV, 0]))
        self.play(Create(rule), FadeIn(vrow), run_time=0.8)
        self.caption(label(f"each column has variance {var_cols[0]:.2f}: {var_cols.sum():g} in total", 26).move_to(slot))
        self.wait(3.0)

        # the first component
        diag = Line(ax.c2p(*(-3.0 * v1)), ax.c2p(*(3.0 * v1)), color=GOLD, stroke_width=4)
        phi1 = MathTex(rf"\phi_1 = ({v1[0]:.3f},\ {v1[1]:.3f})", color=GOLD, font_size=32)
        phi1.move_to([0, 3.3, 0]).align_to([L, 0, 0], LEFT)
        self.play(Create(diag), FadeIn(phi1), Create(sep), FadeIn(hdr_pc), run_time=1.2)
        self.caption(label("the cloud is a line at 45°: that line is the first component", 26).move_to(slot))
        self.wait(3.0)

        f1 = MathTex(rf"\text{{PC1}} = {v1[0]:.3f} \times \text{{height}} + {v1[1]:.3f} \times \text{{arm span}}",
                     color=CREAM, font_size=28).move_to([0, -1.75, 0]).align_to([L, 0, 0], LEFT)
        self.play(FadeIn(f1), run_time=0.8)
        self.caption(label("a score is a weighted sum: the loadings are the weights", 26).move_to(slot))
        self.wait(2.4)
        work, cells = None, VGroup()
        for k, (p, s) in enumerate(zip(X, s1)):
            w = MathTex(rf"{v1[0]:.3f} \times ({fmt(p[0], 1)}) + {v1[1]:.3f} \times ({fmt(p[1], 1)}) = {fmt(s)}",
                        color=GOLD, font_size=28).move_to([0, -2.35, 0]).align_to([L, 0, 0], LEFT)
            c = num(s, "p1", YR[k], GOLD)
            anims = [dots[k].animate.set_color(GOLD), FadeIn(c, shift=RIGHT * 0.1)]
            anims.append(FadeIn(w) if work is None else Transform(work, w))
            self.play(*anims, run_time=0.8)
            if work is None:
                work = w
            self.wait(1.5 if k == 0 else 1.0)
            cells.add(c)
        self.play(cells.animate.set_color(CREAM), run_time=0.4)
        v1cell = MathTex(f"{l1:.2f}", color=GOLD, font_size=30).move_to([CX["p1"], YV, 0])
        self.play(FadeIn(v1cell, scale=1.3), run_time=0.7)
        self.caption(label(f"the four scores have variance {l1:g}: all of the total", 26).move_to(slot))
        self.wait(3.0)

        # the second component, and its zero
        perp = Line(ax.c2p(*(-3.0 * v2)), ax.c2p(*(3.0 * v2)), color=MAUVE_, stroke_width=4)
        phi2 = MathTex(rf"\phi_2 = ({v2[0]:.3f},\ {v2[1]:.3f})", color=MAUVE_, font_size=32)
        phi2.move_to([0, 2.75, 0]).align_to([L, 0, 0], LEFT)
        f2 = MathTex(rf"\text{{PC2}} = {v2[0]:.3f} \times \text{{height}} {v2[1]:.3f} \times \text{{arm span}}",
                     color=CREAM, font_size=28).move_to(f1).align_to([L, 0, 0], LEFT)
        self.play(Create(perp), FadeIn(phi2), Transform(f1, f2), FadeOut(work), run_time=1.3)
        self.caption(label("at right angles to it: the second component", 26).move_to(slot))
        self.wait(2.6)

        land = VGroup(*[Dot(ax.c2p(*p), radius=0.07, color=MAUVE_) for p in X])
        self.add(land)
        z = VGroup(*[num(s, "p2", YR[k], MAUVE_) for k, s in enumerate(s2)])
        self.play(*[m.animate.move_to(ax.c2p(*((p @ v2) * v2))) for m, p in zip(land, X)],
                  FadeIn(z, lag_ratio=0.25), run_time=2.0)
        self.caption(label("drop each patient onto it: all four land on the same spot, 0", 26).move_to(slot))
        self.wait(3.0)
        v2cell = MathTex(fmt(l2), color=MAUVE_, font_size=30).move_to([CX["p2"], YV, 0])
        self.play(FadeIn(v2cell, scale=1.3), run_time=0.7)
        self.caption(label(f"{l1:g} + 0: the same total, now all of it on one component", 26).move_to(slot))
        self.wait(3.2)
        self.caption(label("two columns, one piece of information: PCA says so with a number", 26, GOLD).move_to(slot))
        self.wait(3.4)
        self.caption(label("which is why arm span can stand in for height when a patient cannot stand", 26).move_to(slot))
        self.wait(4.0)


# ---------------------------------------------------------------- ScreeChoice
# survival::lung, the 168 patients with no missing value on these six measures:
# age, ph.ecog, ph.karno, pat.karno, meal.cal, wt.loss. cor() from R, so the
# eigenvalues below are prcomp(scale. = TRUE)'s sdev^2 (agent-14/drill2-lung.R).
LUNG_COR = np.array([
    [1.000000, 0.312261, -0.325213, -0.239432, -0.241218, 0.045926],
    [0.312261, 1.000000, -0.823544, -0.543661, -0.109339, 0.176433],
    [-0.325213, -0.823544, 1.000000, 0.533455, 0.056606, -0.129004],
    [-0.239432, -0.543661, 0.533455, 1.000000, 0.174422, -0.181690],
    [-0.241218, -0.109339, 0.056606, 0.174422, 1.000000, -0.113456],
    [0.045926, 0.176433, -0.129004, -0.181690, -0.113456, 1.000000],
])


class ScreeChoice(Stage):
    """168 lung-cancer patients, six measures, standardised: the scree plot under
    the three rules of the slide before. Each rule writes its evidence in the
    panel: the eigenvalues that pass 1, the cumulative share, the drops. They
    answer 2, 4 and 1."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        lam = np.sort(np.linalg.eigvalsh(LUNG_COR))[::-1]
        lam_r = np.round(lam, 2)                            # as printed, so differences add up
        cum = 100 * np.cumsum(lam) / lam.sum()
        p = len(lam)
        kaiser = int((lam > 1).sum())
        k80 = int(np.argmax(cum >= 80)) + 1
        drops = -np.diff(lam_r)
        k_elbow = 1                                          # the first drop is the only large one
        assert drops[0] > 3 * drops[1:].max()

        ax = Axes(x_range=[0, 6.8, 1], y_range=[0, 3, 1], x_length=6.0, y_length=4.2,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.4})
        ax.to_edge(LEFT, buff=1.0).shift(UP * 0.5)
        ticks = VGroup(*[label(str(k), 20, MUTED).next_to(ax.c2p(k, 0), DOWN, buff=0.15) for k in range(1, p + 1)])
        xl = label("component", 20, MUTED).next_to(ticks, DOWN, buff=0.12)
        yt = VGroup(*[label(str(g), 18, MUTED).next_to(ax.c2p(0, g), LEFT, buff=0.12) for g in (1, 2, 3)])
        yl = MathTex(r"\lambda", color=MUTED, font_size=32).next_to(yt, LEFT, buff=0.2)
        self.play(Create(ax), FadeIn(ticks), FadeIn(xl), FadeIn(yt), FadeIn(yl), run_time=1.0)

        def h(v):
            return ax.c2p(0, v)[1] - ax.c2p(0, 0)[1]

        bars = VGroup(*[Rectangle(width=0.55, height=h(v), color=SKY, fill_color=SKY, fill_opacity=0.75,
                                  stroke_width=0).move_to(ax.c2p(k, 0), aligned_edge=DOWN)
                        for k, v in enumerate(lam, start=1)])
        vals = VGroup(*[label(f"{v:.2f}", 20, CREAM).next_to(b, UP, buff=0.1) for b, v in zip(bars, lam_r)])
        slot = np.array([0, -3.2, 0])
        self.caption(label("168 patients with lung cancer: six measures, standardised", 26).move_to(slot))
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.15), run_time=1.8)
        self.play(FadeIn(vals, lag_ratio=0.1), run_time=0.8)
        self.wait(2.0)

        COL = 1.0
        ANS = 6.6
        tot = MathTex(rf"\lambda_1 + \dots + \lambda_{p} = {lam.sum():.2f}", color=CREAM, font_size=32)
        tot.move_to([0, 2.8, 0]).align_to([COL, 0, 0], LEFT)
        self.play(FadeIn(tot, shift=RIGHT * 0.15), run_time=0.8)
        self.caption(label("six eigenvalues, one per measure: they add up to 6", 26).move_to(slot))
        self.wait(3.0)

        def rule_rows(y, name, evidence, answer, color):
            r = label(name, 24, CREAM).move_to([0, y, 0]).align_to([COL, 0, 0], LEFT)
            a = label(str(answer), 30, color).move_to([0, y, 0]).align_to([ANS, 0, 0], RIGHT)
            e = label(evidence, 20, MUTED).move_to([0, y - 0.45, 0]).align_to([COL, 0, 0], LEFT)
            return r, e, a

        # rule 1: eigenvalue above 1
        one = DashedLine(ax.c2p(0, 1), ax.c2p(6.8, 1), color=GOLD, stroke_width=3)
        passed = ", ".join(f"{v:.2f}" for v in lam_r[:kaiser])
        r1, e1, a1 = rule_rows(1.8, "rule 1 · eigenvalue above 1", f"{passed} pass, {lam_r[kaiser]:.2f} does not",
                               kaiser, GOLD)
        self.play(Create(one), FadeIn(r1), run_time=1.0)
        self.caption(label("rule 1: keep the eigenvalues above 1, more than one measure's worth", 26).move_to(slot))
        self.play(*[bars[i].animate.set_fill(GOLD, 0.85) for i in range(kaiser)], FadeIn(e1), run_time=0.9)
        self.wait(2.6)
        self.play(FadeIn(a1, scale=1.3), run_time=0.6)
        self.caption(label(f"{lam_r[kaiser - 1]:.2f} clears the line by {lam_r[kaiser - 1] - 1:.2f}: two components", 26).move_to(slot))
        self.wait(3.0)

        # rule 2: 80% of the variance
        cums = VGroup(*[label(f"{c:.0f}%", 20, MAUVE_).next_to(b, UP, buff=0.1) for b, c in zip(bars, cum)])
        shown = ", ".join(f"{c:.0f}" for c in cum[:k80])
        r2, e2, a2 = rule_rows(0.6, "rule 2 · 80% of the variance", f"cumulative: {shown}%", k80, MAUVE_)
        self.play(FadeOut(one), bars.animate.set_fill(SKY, 0.75), FadeTransform(vals, cums), FadeIn(r2), run_time=1.0)
        self.caption(label("rule 2: keep enough components for 80% of the variance", 26).move_to(slot))
        self.play(*[bars[i].animate.set_fill(MAUVE_, 0.85) for i in range(k80)], FadeIn(e2), run_time=0.9)
        self.wait(2.6)
        self.play(FadeIn(a2, scale=1.3), run_time=0.6)
        self.caption(label(f"{cum[k80 - 2]:.0f}% at three is short of 80, {cum[k80 - 1]:.0f}% at four: four components", 26).move_to(slot))
        self.wait(3.0)

        # rule 3: the elbow
        tops = [ax.c2p(k, v) for k, v in enumerate(lam, start=1)]
        scree = VMobject(color=CREAM, stroke_width=3).set_points_as_corners(tops)
        knots = VGroup(*[Dot(t, radius=0.06, color=CREAM) for t in tops])
        ring = Circle(radius=0.28, color=CREAM, stroke_width=3).move_to(tops[1])
        dl = ", ".join(f"{x:.2f}" for x in drops[1:])
        r3, e3, a3 = rule_rows(-0.6, "rule 3 · the elbow", f"drops: {drops[0]:.2f}, then {dl}", k_elbow, CREAM)
        # the values make way for the curve; their drops are written in the panel
        self.play(bars.animate.set_fill(SKY, 0.45), FadeOut(cums), FadeIn(r3), run_time=1.0)
        self.caption(label("rule 3: stop where the curve flattens, the elbow", 26).move_to(slot))
        self.play(Create(scree), FadeIn(knots), run_time=1.4)
        self.play(Create(ring), FadeIn(e3), run_time=0.8)
        self.wait(2.4)
        self.play(FadeIn(a3, scale=1.3), bars[0].animate.set_fill(CREAM, 0.8), run_time=0.6)
        self.caption(label(f"a drop of {drops[0]:.2f}, then never more than {drops[1:].max():.2f}: flat from the second, keep one", 26).move_to(slot))
        self.wait(3.6)

        box = SurroundingRectangle(VGroup(a1, a2, a3), color=GOLD, buff=0.15, stroke_width=2.5)
        self.play(Create(box), run_time=0.8)
        self.caption(label(f"three rules, three answers: {k_elbow}, {kaiser} or {k80} components", 26, GOLD).move_to(slot))
        self.wait(3.4)
        self.caption(label("staring at the plot will not settle it. The loadings will: keep what you can name", 26).move_to(slot))
        self.wait(3.6)
        self.caption(label("choose, and write the sentence that defends it", 26, GOLD).move_to(slot))
        self.wait(4.0)
