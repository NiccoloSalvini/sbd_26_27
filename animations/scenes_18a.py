"""Lecture 18 clips rewritten on 2 Nov 2026: Boundary, PerceptronByHand,
Perceptron, GradientDescent. Same class names as scenes.py, so rendering this
file replaces those clips. One caption slot per clip, a right-hand panel with a
fixed left edge, and every number on screen computed here.

    cd animations
    PATH="$HOME/Library/TinyTeX/bin/universal-darwin:$PATH" .venv/bin/manim -qm --disable_caching scenes_18a.py Boundary
"""
from scenes import *
from scipy.optimize import minimize

SLOT = np.array([0, -3.3, 0])
CORAL = "#e2725b"


def cap(s, color=CREAM, size=26):
    return label(s, size, color).move_to(SLOT)


def left_at(mob, x, y):
    """Put a mobject with its left edge at x and its centre at height y."""
    return mob.move_to([0, y, 0]).align_to([x, 0, 0], LEFT)


def clip_line(a, b, c, xr, yr):
    """End points of the line a*x + b*y = c inside the box xr × yr (data units)."""
    pts = []
    for x in xr:
        if abs(b) > 1e-12:
            yv = (c - a * x) / b
            if yr[0] - 1e-9 <= yv <= yr[1] + 1e-9:
                pts.append((x, yv))
    for yv in yr:
        if abs(a) > 1e-12:
            x = (c - b * yv) / a
            if xr[0] - 1e-9 <= x <= xr[1] + 1e-9:
                pts.append((x, yv))
    return max(((p, q) for p in pts for q in pts),
               key=lambda pq: np.hypot(pq[0][0] - pq[1][0], pq[0][1] - pq[1][1]))


# ================================================================ 1. motivation
HR0, T0, SA, SB = 80.0, 37.0, 27.0, 1.2      # the safe zone: centre and semi-axes
HR_R, T_R = (40, 150), (34.5, 40.5)          # the plot box


def ward_patients(seed=5):
    """80 invented ward patients. Stable ones inside an ellipse of normal vitals,
    deteriorated ones in a ring around it, on every side; three the vitals do not
    warn about (two deteriorated inside, one stable outside)."""
    rng = np.random.default_rng(seed)
    pts, lab = [], []
    while lab.count(0) < 53:
        hr, t = rng.normal(HR0, 11), rng.normal(T0, 0.45)
        if np.hypot((hr - HR0) / SA, (t - T0) / SB) < 0.92:
            pts.append((hr, t)); lab.append(0)
    while lab.count(1) < 24:
        ang, r = rng.uniform(0, 2 * np.pi), rng.uniform(1.12, 1.85)
        hr, t = HR0 + SA * r * np.cos(ang), T0 + SB * r * np.sin(ang)
        if 44 <= hr <= 146 and 34.8 <= t <= 40.2:
            pts.append((hr, t)); lab.append(1)
    pts += [(84, 37.3), (71, 36.7), (118, 37.6)]
    lab += [1, 1, 0]
    return np.array(pts), np.array(lab)


def best_line(Z, y, n_ang=3600):
    """Every direction in 0.05° steps, every cut between two points: the fewest
    mistakes a straight line can make, and that line (normal, threshold)."""
    n = len(y)
    best = (n + 1, None, None)
    for k in range(n_ang):
        th = np.pi * k / n_ang
        nrm = np.array([np.cos(th), np.sin(th)])
        proj = Z @ nrm
        order = np.argsort(proj)
        ys, ps = y[order], proj[order]
        ones_left = np.concatenate([[0], np.cumsum(ys)])
        zeros_right = np.concatenate([np.cumsum((1 - ys)[::-1])[::-1], [0]])
        m1 = ones_left + zeros_right          # 0 below the cut, 1 above
        m2 = n - m1                           # the reverse
        for m, sign in ((m1, 1), (m2, -1)):
            i = int(m.argmin())
            if m[i] < best[0]:
                thr = ps[0] - 1 if i == 0 else ps[-1] + 1 if i == n else (ps[i - 1] + ps[i]) / 2
                best = (int(m[i]), nrm, thr)
    return best[0], best[1], best[2], n_ang * (n + 1)


def _sig(z):
    return 1 / (1 + np.exp(-z))


def net_forward(p, Z):
    W1, b1, W2, b2 = p[:6].reshape(2, 3), p[6:9], p[9:12], p[12]
    h = _sig(Z @ W1 + b1)
    return h, _sig(h @ W2 + b2)


def net_fit(Z, y, starts=20, seed=0):
    """A 2-3-1 network, sigmoid everywhere, cross-entropy with a small weight
    decay, BFGS from 20 random starts: the best one."""
    def loss(p):
        o = np.clip(net_forward(p, Z)[1], 1e-9, 1 - 1e-9)
        return -np.mean(y * np.log(o) + (1 - y) * np.log(1 - o)) + 1e-3 * np.sum(p ** 2)
    rng = np.random.default_rng(seed)
    runs = [minimize(loss, rng.normal(0, 1, 13), method="BFGS", options={"maxiter": 3000})
            for _ in range(starts)]
    return min(runs, key=lambda r: r.fun).x


class Boundary(Stage):
    """Why a curve at all, on patients. Danger lies on every side of normal vitals:
    too slow, too fast, too cold, too hot. Single cuts are tried and their
    mistakes logged; the best straight line there is still misses 15. A network
    with three hidden neurons draws three lines and blends them into a closed
    curve: 3 wrong, the patients whose vitals gave no warning."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        P, y = ward_patients()
        mu, sd = P.mean(0), P.std(0)
        Z = (P - mu) / sd

        ax = Axes(x_range=[HR_R[0], HR_R[1], 10], y_range=[T_R[0], T_R[1], 0.5], x_length=6.2, y_length=4.5,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.4}
                  ).to_edge(LEFT, buff=1.35).shift(UP * 0.55)
        ax.x_axis.add_numbers([40, 60, 80, 100, 120, 140], font_size=22, num_decimal_places=0)
        ax.y_axis.add_numbers([35, 36, 37, 38, 39, 40], font_size=22, num_decimal_places=0)
        ax.x_axis.numbers.set_color(MUTED); ax.y_axis.numbers.set_color(MUTED)
        xl = label("heart rate (beats a minute)", 22, MUTED).next_to(ax, DOWN, buff=0.5)
        yl = label("temperature (°C)", 22, MUTED).rotate(PI / 2).next_to(ax, LEFT, buff=0.55)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.2)

        dots = VGroup(*[Dot(ax.c2p(*p), radius=0.06, color=MUTED) for p in P])
        self.play(FadeIn(dots, lag_ratio=0.02), run_time=1.4)
        self.caption(cap(f"{len(P)} ward patients at admission: heart rate and temperature"))
        self.wait(2.6)

        # the panel: a legend, then one row per rule tried, newest in gold
        COLX, VALX = 1.35, 6.7
        leg = VGroup(
            VGroup(Dot(radius=0.07, color=GOLD), label("deteriorated within 24 hours", 22, CREAM)).arrange(RIGHT, buff=0.2),
            VGroup(Dot(radius=0.07, color=SKY), label("stable", 22, CREAM)).arrange(RIGHT, buff=0.2),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        leg.move_to([0, 2.95, 0]).align_to([COLX, 0, 0], LEFT)
        self.play(*[d.animate.set_color(GOLD if yy else SKY) for d, yy in zip(dots, y)], FadeIn(leg), run_time=1.2)
        self.caption(cap(f"gold: {y.sum()} who deteriorated. Danger lies on every side of normal"))
        self.wait(3.0)

        head = VGroup(left_at(label("rule", 22, MUTED), COLX, 1.95),
                      label("wrong", 22, MUTED).move_to([0, 1.95, 0]).align_to([VALX, 0, 0], RIGHT))
        rows = VGroup()

        def log(text, n):
            yy = 1.4 - 0.58 * len(rows)
            name = left_at(label(text, 24, CREAM), COLX, yy)
            val = label(str(n), 30, GOLD).move_to([0, yy, 0]).align_to([VALX, 0, 0], RIGHT)
            anims = [FadeIn(VGroup(name, val), shift=RIGHT * 0.15)]
            if len(rows):
                anims.append(rows[-1][1].animate.set_color(CREAM))
            rows.add(VGroup(name, val))
            return anims

        def data_line(a, b, c, **kw):
            p, q = clip_line(a, b, c, HR_R, T_R)
            return Line(ax.c2p(*p), ax.c2p(*q), **kw)

        cuts = [  # (rule text, caption, line a*hr + b*t = c, prediction)
            ("temperature above 38.3 °C", "one straight line is one cut: alert above 38.3 °C",
             (0, 1, 38.3), P[:, 1] > 38.3),
            ("heart rate above 105", "another cut: alert above 105 beats a minute",
             (1, 0, 105), P[:, 0] > 105),
            ("temperature below 35.8 °C", "or below 35.8 °C: each cut catches one side, misses the rest",
             (0, 1, 35.8), P[:, 1] < 35.8),
        ]
        line = None
        for i, (text, sentence, abc, pred) in enumerate(cuts):
            n_wrong = int((pred != y).sum())
            new = data_line(*abc, color=CREAM, stroke_width=4)
            first = [FadeIn(head)] if i == 0 else []
            self.play(*(first + ([Create(new)] if line is None else [Transform(line, new)])), *log(text, n_wrong), run_time=1.3)
            if line is None:
                line = new
            self.caption(cap(sentence))
            self.wait(2.6)

        # the best straight line there is
        bl, nrm, thr, n_lines = best_line(Z, y)
        a, b = nrm / sd
        best = data_line(a, b, thr + a * mu[0] + b * mu[1], color=CREAM, stroke_width=4)
        self.play(Transform(line, best), *log("best straight line", bl), run_time=1.6)
        self.caption(cap(f"the best of {n_lines:,} straight lines still gets {bl} wrong".replace(",", " ")))
        self.wait(3.4)

        # a network with three hidden neurons: three lines, blended
        p = net_fit(Z, y)
        W1, b1 = p[:6].reshape(2, 3), p[6:9]
        self.play(FadeOut(line), run_time=0.6)
        self.caption(cap("a network with three hidden neurons: each one draws a straight line"))
        hidden = VGroup()
        for k in range(3):
            ak, bk = W1[:, k] / sd
            pa, pb = clip_line(ak, bk, -b1[k] + ak * mu[0] + bk * mu[1], HR_R, T_R)
            hl = DashedLine(ax.c2p(*pa), ax.c2p(*pb), dash_length=0.14, color=SKY, stroke_width=3)
            hidden.add(hl)
            self.play(Create(hl), run_time=1.0)
            self.wait(0.9)

        # the output neuron's 0.5 line, traced ray by ray from the middle of the safe zone
        f = lambda z: net_forward(p, z[None, :])[1][0]
        c = (np.array([HR0, T0]) - mu) / sd
        lo, hi = (np.array([HR_R[0], T_R[0]]) - mu) / sd, (np.array([HR_R[1], T_R[1]]) - mu) / sd
        ring = []
        for th in np.linspace(0, 2 * np.pi, 240, endpoint=False):
            d = np.array([np.cos(th), np.sin(th)])
            tmax = min(((hi[j] if d[j] > 0 else lo[j]) - c[j]) / d[j] for j in range(2) if abs(d[j]) > 1e-12)
            t0, t1 = 0.0, tmax
            if f(c + t1 * d) > 0.5:
                for _ in range(40):
                    tm = (t0 + t1) / 2
                    t0, t1 = (tm, t1) if f(c + tm * d) < 0.5 else (t0, tm)
            q = mu + (c + t1 * d) * sd
            ring.append(ax.c2p(*q))
        curve = VMobject(color=GOLD, stroke_width=5).set_points_smoothly(ring + [ring[0]])
        out = net_forward(p, Z)[1]
        wrong_idx = np.where((out > 0.5) != y)[0]
        self.caption(cap("the output neuron blends them: safe only inside all three"))
        self.play(Create(curve), hidden.animate.set_stroke(opacity=0.35), *log("network, 3 hidden neurons", len(wrong_idx)),
                  run_time=2.4)
        self.wait(2.8)

        rings = VGroup(*[Circle(radius=0.17, color=CREAM, stroke_width=2.5).move_to(dots[i]) for i in wrong_idx])
        self.play(Create(rings), run_time=0.8)
        self.caption(cap(f"{len(wrong_idx)} wrong: patients whose vitals gave no warning"))
        self.wait(3.2)
        self.caption(cap("one line cannot fence in a safe zone. Three bent lines can", GOLD))
        self.wait(4.0)


# ================================================================ 2. the perceptron, by hand
class PerceptronByHand(Stage):
    """The AND table, filled in the way the slide fills it. Epoch 1 at speaking
    pace with every product written out; epochs 2 to 4 fill the table directly
    and write the arithmetic only on the rows that move W. The log on the left
    counts the mistakes per epoch until one has none."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        # ---- the table, left
        XS = [-6.2, -5.25, -4.4, -3.55, -2.45, -1.45, -0.35]
        HEAD_Y, ROW0, STEP = 2.5, 1.85, 0.66
        heads = VGroup(label("obs", 26, MUTED).move_to([XS[0], HEAD_Y, 0]),
                       *[MathTex(t, color=MUTED, font_size=36).move_to([x, HEAD_Y, 0])
                         for t, x in zip(["X_1", "X_2", "y", "z", r"\hat y"], XS[1:6])],
                       label("error", 26, MUTED).move_to([XS[6], HEAD_Y, 0]))
        rule_ = Line([XS[0] - 0.45, HEAD_Y - 0.34, 0], [XS[6] + 0.55, HEAD_Y - 0.34, 0], color=MUTED, stroke_width=1.2)
        fixed = VGroup()
        for i, ((x1, x2), yy) in enumerate(AND_DATA):
            ry = ROW0 - STEP * i
            fixed.add(label(str(i + 1), 28, CREAM).move_to([XS[0], ry, 0]),
                      *[MathTex(str(v), color=CREAM, font_size=36).move_to([x, ry, 0]) for v, x in zip((x1, x2, yy), XS[1:4])])
        self.play(FadeIn(heads), Create(rule_), FadeIn(fixed, lag_ratio=0.05), run_time=1.2)
        self.caption(cap("the AND gate: y = 1 only when both inputs are 1"))
        self.wait(2.4)

        # ---- weights and rules, right
        COLX = 0.6
        w = W0
        wlab = left_at(MathTex(rf"W = ({num(w[0])},\ {num(w[1])})", color=CREAM, font_size=44), COLX, 3.3)
        rules = VGroup(
            MathTex(r"z = W_1 X_1 + W_2 X_2,\quad \hat y = 1 \text{ if } z \ge \theta", color=MUTED, font_size=30),
            MathTex(r"W \leftarrow W + \eta\,(y - \hat y)\,X", color=MUTED, font_size=30),
            MathTex(rf"\theta = {num(THETA)},\quad \eta = {num(ETA)}", color=MUTED, font_size=30),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        rules.move_to([0, 2.25, 0]).align_to([COLX, 0, 0], LEFT)
        epoch_lab = left_at(label("epoch 1", 32, GOLD), XS[0] - 0.45, 3.3)
        self.play(Write(wlab), FadeIn(rules), FadeIn(epoch_lab), run_time=1.2)
        self.caption(cap(f"start at W = ({num(w[0])}, {num(w[1])}): threshold {num(THETA)}, learning rate {num(ETA)}".replace("-", "−")))
        self.wait(2.8)

        bar = Rectangle(width=XS[6] - XS[0] + 1.0, height=0.5, stroke_width=0, fill_color=CREAM, fill_opacity=0.09)
        bar.move_to([(XS[0] + XS[6]) / 2, ROW0, 0])
        self.play(FadeIn(bar), run_time=0.4)
        cells, log_rows = VGroup(), VGroup()
        LINE_Y = [1.15, 0.53, -0.09, -0.71, -1.33]

        def panel(texts, colors):
            return VGroup(*[left_at(MathTex(t, color=c, font_size=32), COLX + (0.45 if t.startswith("=") else 0), LINE_Y[j])
                            for j, (t, c) in enumerate(zip(texts, colors))])

        captions = {  # (epoch, obs index) -> the sentence that goes with that row
            (1, 0): "a right answer: the error is 0, so W does not move",
            (1, 2): "a wrong answer: W moves by η × error × X",
            (1, 3): "wrong the other way: W moves up, along X = (1, 1)",
            (2, 2): "epoch 2: the fix for obs 4 has broken obs 3",
            (3, 2): "epoch 3: one more correction",
            (4, 0): "epoch 4: four right answers in a row",
        }

        for r in perceptron_run():
            e, i = r["epoch"], r["i"]
            x1, x2 = r["x"]
            yy, z, yhat, err = r["y"], r["z"], r["yhat"], r["err"]
            wb, wa = r["before"], r["after"]
            wrong = err != 0
            full = e == 1
            ry = ROW0 - STEP * i
            if i == 0 and e > 1:                       # a new epoch: clear the computed columns
                nxt = left_at(label(f"epoch {e}", 32, GOLD), XS[0] - 0.45, 3.3)
                self.play(FadeOut(cells), Transform(epoch_lab, nxt), bar.animate.move_to([bar.get_x(), ry, 0]), run_time=0.7)
                cells = VGroup()
            elif not (i == 0 and e == 1):
                self.play(bar.animate.move_to([bar.get_x(), ry, 0]), run_time=0.3)
            if (e, i) in captions:
                self.caption(cap(captions[(e, i)], GOLD if wrong else CREAM))

            row_cells = VGroup(MathTex(num(z), color=CREAM, font_size=36).move_to([XS[4], ry, 0]),
                               MathTex(str(yhat), color=CREAM, font_size=36).move_to([XS[5], ry, 0]),
                               MathTex(f"{err:+d}" if err else "0", color=GOLD if wrong else CREAM, font_size=36).move_to([XS[6], ry, 0]))
            rel = r"\ge" if z >= THETA else "<"
            zt = rf"z = {num(wb[0])} \cdot {x1} + {par(wb[1])} \cdot {x2} = {num(z)}"
            ct = rf"{num(z)} {rel} {num(THETA)} \;\Rightarrow\; \hat y = {yhat}"
            et = rf"y - \hat y = {yy} - {yhat} = {err:+d}" if wrong else rf"y - \hat y = {yy} - {yhat} = 0"
            ut1 = rf"W \leftarrow ({num(wb[0])},\ {num(wb[1])}) + {num(ETA)} \cdot ({err:+d}) \cdot ({x1},\ {x2})"
            ut2 = rf"= ({num(wa[0])},\ {num(wa[1])})"

            if full:                                   # epoch 1: every line, at speaking pace
                texts = [zt, ct, et] + ([ut1, ut2] if wrong else [])
                cols = [CREAM, CREAM, GOLD if wrong else MUTED] + [GOLD, GOLD]
                lines = panel(texts, cols)
                for j, ln in enumerate(lines):
                    self.play(Write(ln), run_time=0.8)
                    if j == 1:
                        self.play(FadeIn(row_cells[0]), FadeIn(row_cells[1]), run_time=0.4)
                    if j == 2:
                        self.play(FadeIn(row_cells[2]), run_time=0.3)
                    self.wait(0.75 if j < 3 else 0.6)
            elif wrong:                                # later epochs: arithmetic only where W moves
                lines = panel([zt, et, ut1, ut2], [CREAM, GOLD, GOLD, GOLD])
                self.play(FadeIn(lines[:2]), FadeIn(row_cells), run_time=0.6)
                self.wait(0.7)
                self.play(Write(lines[2:]), run_time=0.9)
                self.wait(0.6)
            else:
                lines = VGroup()
                self.play(FadeIn(row_cells), run_time=0.5)
                self.wait(0.45)
            cells.add(row_cells)
            if wrong:
                w = wa
                self.play(Transform(wlab, left_at(MathTex(rf"W = ({num(w[0])},\ {num(w[1])})", color=GOLD, font_size=44), COLX, 3.3)),
                          run_time=0.8)
                self.wait(0.8 if full else 0.5)
                self.play(wlab.animate.set_color(CREAM), FadeOut(lines), run_time=0.4)
            elif len(lines):
                self.play(FadeOut(lines), run_time=0.4)

            if r["last"]:                              # one line per epoch in the log
                m = r["mistakes"]
                txt = f"epoch {e}: {m} mistake{'s' if m != 1 else ''}" if m else f"epoch {e}: no mistake"
                entry = left_at(label(txt, 26, GOLD if m else SKY), XS[0] - 0.45, -0.95 - 0.45 * len(log_rows))
                log_rows.add(entry)
                self.play(FadeIn(entry, shift=RIGHT * 0.15), run_time=0.5)
                if e == 1:
                    self.caption(cap("epoch 1: two mistakes. Now the same four rows again"))
                    self.wait(1.6)
                elif m:
                    self.wait(0.6)

        self.caption(cap(f"a whole epoch with no mistake: W = ({num(w[0])}, {num(w[1])}) has learned AND", GOLD))
        self.wait(2.6)
        self.caption(cap("with every error 0, the rule can never move W again: it has converged"))
        self.wait(3.0)


# ================================================================ 2b. the same run, as geometry
def half_plane(w, theta=THETA, lo=-0.5, hi=1.6):
    """The plot box cut to the side where W1 x + W2 y >= theta (a polygon, in data units)."""
    poly = [(lo, lo), (hi, lo), (hi, hi), (lo, hi)]
    inside = lambda p: w[0] * p[0] + w[1] * p[1] >= theta
    out = []
    for k in range(len(poly)):
        p, q = poly[k], poly[(k + 1) % len(poly)]
        if inside(p):
            out.append(p)
        if inside(p) != inside(q):
            fp, fq = w[0] * p[0] + w[1] * p[1] - theta, w[0] * q[0] + w[1] * q[1] - theta
            t = fp / (fp - fq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out


class Perceptron(Stage):
    """The same run as geometry. The shaded side of the line is where the
    perceptron says 1, so a wrong row is a point on the wrong side; every update
    moves the line, and a counter says how many points are still on the wrong
    side. The line separates the gate in epoch 3, but the perceptron only knows
    after epoch 4, a whole epoch with no mistake."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        ax = and_axes(5.0).to_edge(LEFT, buff=1.1).shift(UP * 0.45)
        dots = and_dots(ax)
        x1l = MathTex("X_1", color=MUTED, font_size=30).next_to(ax.c2p(1.6, -0.5), DOWN, buff=0.15)
        x2l = MathTex("X_2", color=MUTED, font_size=30).next_to(ax.c2p(-0.5, 1.6), LEFT, buff=0.15)
        leg = VGroup(VGroup(Dot(radius=0.08, color=GOLD), MathTex("y = 1", color=CREAM, font_size=30)).arrange(RIGHT, buff=0.15),
                     VGroup(Dot(radius=0.08, color=SKY), MathTex("y = 0", color=CREAM, font_size=30)).arrange(RIGHT, buff=0.15)
                     ).arrange(RIGHT, buff=0.6)
        left_at(leg, 0.5, 3.3)
        self.play(Create(ax), FadeIn(x1l), FadeIn(x2l), FadeIn(dots), FadeIn(leg), run_time=1.2)
        self.caption(cap("the four rows of the AND gate, as points: only (1, 1) is a 1"))
        self.wait(2.4)

        def shade(w):
            return Polygon(*[ax.c2p(*q) for q in half_plane(w)], stroke_width=0, fill_color=GOLD, fill_opacity=0.16)

        def n_wrong(w):
            return sum(1 for (p, yy) in AND_DATA if (w[0] * p[0] + w[1] * p[1] >= THETA) != bool(yy))

        COLX = 0.5
        w = W0
        sh, bnd = shade(w), and_boundary(ax, w)
        key = left_at(label("shaded: the perceptron says 1", 24, GOLD), COLX, 2.7)
        rule = left_at(MathTex(rf"W_1 X_1 + W_2 X_2 \ge {num(THETA)}", color=MUTED, font_size=30), COLX, 2.2)
        wlab = left_at(w_tex(w, 40), COLX, 1.5)
        self.play(FadeIn(sh), Create(bnd), FadeIn(key), FadeIn(rule), Write(wlab), run_time=1.4)
        self.caption(cap(f"the line where z = {num(THETA)}: points on the shaded side get ŷ = 1"))
        self.wait(2.8)

        side = VGroup(label("on the wrong side now:", 26, CREAM), label(str(n_wrong(w)), 30, GOLD)).arrange(RIGHT, buff=0.25)
        left_at(side, COLX, 0.8)
        bad = VGroup(*[Circle(radius=0.24, color=GOLD, stroke_width=3).move_to(dots[i])
                       for i, (p, yy) in enumerate(AND_DATA) if (w[0] * p[0] + w[1] * p[1] >= THETA) != bool(yy)])
        self.play(FadeIn(side), Create(bad), run_time=0.9)
        self.caption(cap("two points on the wrong side: (1, 0) is shaded, (1, 1) is not"))
        self.wait(2.8)
        self.play(FadeOut(bad), run_time=0.4)

        epoch_lab = left_at(label("epoch 1", 28, GOLD), COLX, 0.1)
        self.play(FadeIn(epoch_lab), run_time=0.4)
        log_rows = VGroup()
        captions = {
            (1, 2): ("obs 3 is wrong: the line moves until (1, 0) leaves the shade", GOLD),
            (1, 3): ("obs 4 is wrong: the line takes (1, 1) in, and (1, 0) with it", GOLD),
            (2, 2): ("epoch 2: the same tug of war between (1, 0) and (1, 1)", CREAM),
            (3, 2): ("epoch 3: one more correction", CREAM),
            (4, 0): ("epoch 4: four right answers, nothing moves", CREAM),
        }
        for r in perceptron_run():
            e, i = r["epoch"], r["i"]
            wrong = r["err"] != 0
            if i == 0 and e > 1:
                self.play(Transform(epoch_lab, left_at(label(f"epoch {e}", 28, GOLD), COLX, 0.1)), run_time=0.4)
            if (e, i) in captions:
                self.caption(cap(*captions[(e, i)]))
            ring = Circle(radius=0.24, color=GOLD if wrong else CREAM, stroke_width=3).move_to(dots[i])
            tag = label(f"obs {i + 1}: {'wrong' if wrong else 'right'}", 24, GOLD if wrong else MUTED)
            tag.next_to(epoch_lab, RIGHT, buff=0.5)
            self.play(Create(ring), FadeIn(tag), run_time=0.4)
            self.wait(0.9 if wrong else 0.45)
            if wrong:
                w = r["after"]
                k = n_wrong(w)
                newside = label(str(k), 30, GOLD).move_to(side[1], aligned_edge=LEFT)
                self.play(Transform(sh, shade(w)), Transform(bnd, and_boundary(ax, w)),
                          Transform(wlab, left_at(w_tex(w, 40), COLX, 1.5)), Transform(side[1], newside), run_time=1.3)
                self.wait(1.4)
                if k == 0:
                    self.play(FadeOut(ring), FadeOut(tag), run_time=0.3)
                    self.caption(cap("no point on the wrong side, but the perceptron cannot know it yet"))
                    self.wait(2.6)
                    continue
            self.play(FadeOut(ring), FadeOut(tag), run_time=0.3)
            if r["last"]:
                m = r["mistakes"]
                txt = f"epoch {e}: {m} mistake{'s' if m != 1 else ''}" if m else f"epoch {e}: no mistake"
                entry = left_at(label(txt, 24, GOLD if m else SKY), COLX, -0.55 - 0.42 * len(log_rows))
                log_rows.add(entry)
                self.play(FadeIn(entry, shift=RIGHT * 0.15), run_time=0.4)
                self.wait(0.4)

        self.caption(cap(f"a whole epoch with no mistake: it stops at W = ({num(w[0])}, {num(w[1])})", GOLD))
        self.wait(4.0)


# ================================================================ 3. gradient descent
class GradientDescent(Stage):
    """One bowl, L(W) = (W - 2)^2, three learning rates from the same start W = 4.
    The first three steps of each are written out with their own numbers; a log
    on the right keeps where each run ended. 0.3 lands, 0.03 is still short after
    26 steps, 1.05 jumps past the bottom and climbs the walls."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    @staticmethod
    def L(w):
        return (w - 2.0) ** 2

    @staticmethod
    def dL(w):
        return 2.0 * (w - 2.0)

    def construct(self):
        ax = Axes(x_range=[-2, 6, 1], y_range=[0, 16, 4], x_length=6.4, y_length=4.4,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.4}
                  ).to_edge(LEFT, buff=1.0).shift(UP * 0.4)
        ax.x_axis.add_numbers([-2, 0, 2, 4, 6], font_size=22, num_decimal_places=0)
        ax.y_axis.add_numbers([4, 8, 12, 16], font_size=22, num_decimal_places=0)
        ax.x_axis.numbers.set_color(MUTED); ax.y_axis.numbers.set_color(MUTED)
        wl = MathTex("W", color=MUTED, font_size=30).next_to(ax.x_axis.get_right(), RIGHT, buff=0.15)
        curve = ax.plot(self.L, x_range=[-2, 6], color=CREAM, stroke_width=3.5)
        title = MathTex(r"L(W) = (W - 2)^2", color=CREAM, font_size=32).next_to(ax, UP, buff=0.15)
        self.play(Create(ax), FadeIn(wl), run_time=1.0)
        self.play(Create(curve), FadeIn(title), run_time=1.2)
        self.caption(cap("one weight W, one loss: L(W) = (W − 2)², lowest at W = 2"))
        self.wait(2.4)

        COLX = 1.4
        rule = left_at(MathTex(r"W_{t+1} = W_t - \eta\,\frac{\partial L}{\partial W}", color=CREAM, font_size=38), COLX, 3.0)
        slope = left_at(MathTex(r"\frac{\partial L}{\partial W} = 2\,(W - 2)", color=MUTED, font_size=32), COLX, 2.0)
        self.play(Write(rule), run_time=1.0)
        self.play(FadeIn(slope), run_time=0.6)
        self.caption(cap("each step: the old W minus η times the slope where you stand"))
        self.wait(2.4)

        LOG_Y = [-1.25, -1.75, -2.25]
        done = VGroup()

        def run(eta, steps, colour, opening, closing):
            w = 4.0
            head = left_at(MathTex(rf"\eta = {eta:g}", color=colour, font_size=36), COLX, 1.2)
            dot = Dot(ax.c2p(w, self.L(w)), color=colour, radius=0.1)
            self.play(FadeIn(head), FadeIn(dot, scale=1.6), run_time=0.7)
            self.caption(cap(opening))
            self.wait(2.0)
            trail, lines = VGroup(), VGroup()
            for k in range(steps):
                g = self.dL(w)
                wn = w - eta * g
                if k < 3:
                    gtxt = f"{g:.2f}" if g >= 0 else f"({g:.2f})"
                    ex = left_at(MathTex(rf"{w:.2f} - {eta:g} \times {gtxt} = {wn:.2f}", color=colour, font_size=30),
                                 COLX, 0.62 - 0.5 * k)
                    self.play(FadeIn(ex, shift=RIGHT * 0.15), run_time=0.6)
                    lines.add(ex)
                seg = Line(ax.c2p(w, self.L(w)), ax.c2p(wn, self.L(wn)), color=colour, stroke_width=2.5, stroke_opacity=0.8)
                trail.add(seg)
                self.play(Create(seg), dot.animate.move_to(ax.c2p(wn, self.L(wn))),
                          run_time=0.6 if k < 3 else (0.32 if steps < 12 else 0.14))
                if k < 3:
                    self.wait(0.8)
                w = wn
            self.caption(cap(closing))
            entry = left_at(MathTex(rf"\eta = {eta:g}\text{{:}}\ \ W = {w:.2f} \text{{ after {steps} steps}}",
                                    color=colour, font_size=28), COLX, LOG_Y[len(done)])
            done.add(entry)
            self.play(FadeIn(entry, shift=RIGHT * 0.15), run_time=0.6)
            self.wait(2.4)
            self.play(FadeOut(VGroup(head, dot, trail, lines)), run_time=0.6)
            return w

        g0 = self.dL(4.0)
        run(0.3, 8, GOLD,
            f"at W = 4 the slope is 2 × (4 − 2) = {g0:g}: positive, so step left",
            "big steps where it is steep, small ones near the bottom: the slope shrinks")
        run(0.03, 26, SKY,
            "η = 0.03: the same direction, steps ten times shorter",
            "after 26 steps it is still short of the bottom")
        run(1.05, 7, CORAL,
            "η = 1.05: every step jumps past the bottom and lands higher",
            "each step overshoots by more than the last: it diverges")

        self.caption(cap("too small creeps, too large diverges: η is your choice, not the data's", GOLD))
        self.wait(3.6)
