"""Lecture 18, clips 4-6 rebuilt: Sigmoid, HiddenLayer, Overfitting.

What the old scenes got wrong (frames of 2 Nov 2026): captions placed next to
each plot, so two sat on screen at once and one ran off the left edge; a step
drawn as three pieces that turned into a comb when it morphed into the
sigmoid; a 0/1 step labelled sign(); hidden-layer "bends" that were hand-typed
tanh curves on a picture whose network had two inputs, so one neuron drew a
bend where it can only draw a line; overfitting curves and boundaries typed in
by hand, test points that never did anything, labels cut at the right edge.

Here every curve, boundary, count and percentage is computed in the scene:
the networks are fitted (scipy L-BFGS for the hidden-layer fits, plain Adam
for the overfitting run) on invented patients, and the captions go through
the one slot of Stage.caption().
"""
from scenes import *
from scipy.optimize import minimize

SLOT = np.array([0, -3.25, 0])
COL = 1.3                                   # left edge of the right-hand panel


def sigma(x):
    return 1 / (1 + np.exp(-x))


def patients(rng, n):
    """Invented patients: BMI and systolic blood pressure, drawn around typical
    values and kept inside the plot (rejection, so nothing piles up on an edge).
    At risk = outside a safe oval: too thin or too heavy, too low or too high."""
    out = []
    while len(out) < n:
        b, s = rng.normal(26, 5.5), rng.normal(128, 24)
        if 15.5 < b < 39.5 and 82 < s < 178:
            out.append((b, s))
    X = np.array(out)
    risk = ((X[:, 0] - 25.5) / 7.0) ** 2 + ((X[:, 1] - 126) / 30) ** 2 > 1
    return X, risk.astype(float)


MU, SD = np.array([26.0, 128.0]), np.array([5.5, 24.0])     # inputs on the scale the network sees


def risk_axes(xl, yl):
    ax = Axes(x_range=[15, 40, 5], y_range=[80, 180, 20], x_length=xl, y_length=yl,
              axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.4},
              x_axis_config={"numbers_to_include": [20, 30, 40], "font_size": 20},
              y_axis_config={"numbers_to_include": [100, 140, 180], "font_size": 20})
    for n in ax.x_axis.numbers + ax.y_axis.numbers:
        n.set_color(MUTED)
    return ax


def boundary_curve(ax, logit, color=CREAM, width=4.5, depth=6):
    """The 0.5 contour of a fitted network, drawn on the axes."""
    (x0, y0, _), (x1, y1, _) = ax.c2p(15, 80), ax.c2p(40, 180)

    def f(x, y):
        b, s = ax.p2c(np.array([x, y, 0]))
        return logit(np.array([[b, s]]))[0]
    return ImplicitFunction(f, x_range=[x0, x1], y_range=[y0, y1], min_depth=depth, max_quads=4000,
                            color=color, stroke_width=width)


# ---------------------------------------------------------------- 4. one neuron = GLM
class Sigmoid(Stage):
    """Why the step had to go, shown with a point sliding along λ: on the step
    the slope it reads is 0 everywhere, so gradient descent has no direction.
    Softened into the sigmoid, every λ has a slope, σ(1 − σ), largest at 0.
    Then three patients read off the curve: a probability of readmission,
    which is what logistic regression gives."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        axis = {"color": MUTED, "include_tip": False, "stroke_width": 1.5}
        ax = Axes(x_range=[-6, 6, 2], y_range=[0, 1.1, 0.5], x_length=6.6, y_length=3.0, axis_config=axis)
        ax.move_to([-2.3, 1.25, 0])
        dax = Axes(x_range=[-6, 6, 2], y_range=[0, 0.3, 0.25], x_length=6.6, y_length=1.35, axis_config=axis)
        dax.move_to([-2.3, -1.6, 0])
        guides = VGroup()
        for a, v, t in ((ax, 0.5, "0.5"), (ax, 1, "1"), (dax, 0.25, "0.25")):
            guides.add(DashedLine(a.c2p(-6, v), a.c2p(6, v), color=MUTED, stroke_width=1, stroke_opacity=0.45,
                                  dash_length=0.05),
                       label(t, 20, MUTED).next_to(a.c2p(-6, v), LEFT, buff=0.15))
        out_l = label("output", 22, MUTED).next_to(ax.y_axis, UP, buff=0.12)
        slope_l = label("slope", 22, MUTED).next_to(dax.y_axis, UP, buff=0.12)
        lam_a = MathTex(r"\lambda", color=MUTED, font_size=28).next_to(ax.x_axis, RIGHT, buff=0.12)
        lam_b = MathTex(r"\lambda", color=MUTED, font_size=28).next_to(dax.x_axis, RIGHT, buff=0.12)
        self.play(Create(ax), FadeIn(out_l, lam_a, guides[:4]), run_time=1.0)

        # the panel: what λ is, which g is on screen, and live readouts
        lam_def = MathTex(r"\lambda = W_0 + \textstyle\sum_j W_j X_j", color=MUTED, font_size=30)
        lam_def.move_to([0, 3.15, 0]).align_to([COL + 0.5, 0, 0], LEFT)
        g_step = MathTex(r"g(\lambda) = \begin{cases} 1 & \lambda \ge 0 \\ 0 & \lambda < 0 \end{cases}",
                         color=SKY, font_size=34)
        g_step.move_to([0, 2.05, 0]).align_to(lam_def, LEFT)
        # a single steep path, so the morph into the sigmoid is one curve bending
        step = ax.plot(lambda x: sigma(60 * x), x_range=[-6, 6, 0.005], color=SKY, stroke_width=4)
        self.play(Create(step), FadeIn(lam_def), Write(g_step), run_time=1.6)
        self.caption(label("the perceptron's step: output 0 below zero, 1 above, nothing between", 26).move_to(SLOT))
        self.wait(3.0)

        self.play(Create(dax), FadeIn(slope_l, lam_b, guides[4:]), run_time=0.9)
        flat = dax.plot(lambda x: 0.0, x_range=[-6, 6, 0.005], color=SKY, stroke_width=4)
        self.play(Create(flat), run_time=1.0)

        # a point slides along λ; the panel reads value and slope where it is
        lam = ValueTracker(-4.5)
        mode = {"g": lambda x: float(x >= 0), "d": lambda x: 0.0, "col": SKY}

        def tracer():
            x = lam.get_value()
            gx, dx = mode["g"](x), mode["d"](x)
            p = ax.c2p(x, gx)
            ux = ax.c2p(1, 0)[0] - ax.c2p(0, 0)[0]
            uy = ax.c2p(0, 1)[1] - ax.c2p(0, 0)[1]
            v = np.array([ux, dx * uy, 0]); v = v / np.linalg.norm(v) * 0.85
            return VGroup(Line(p - v, p + v, color=CREAM, stroke_width=3),
                          Dot(p, radius=0.08, color=CREAM),
                          DashedLine(ax.c2p(x, 0), dax.c2p(x, 0.3), color=MUTED, stroke_width=1.5,
                                     dash_length=0.06),
                          Dot(dax.c2p(x, dx), radius=0.08, color=CREAM))

        def readout():
            rows = VGroup()
            for i, (lhs, fn, places, col) in enumerate((
                    (r"\lambda =", lambda x: x, 1, CREAM),
                    (r"g(\lambda) =", lambda x: mode["g"](x), 2, CREAM),
                    (r"\text{slope} =", lambda x: mode["d"](x), 2, mode["col"]))):
                left = MathTex(lhs, color=col, font_size=32)
                left.move_to([0, 0.8 - 0.62 * i, 0]).align_to(lam_def, LEFT)
                num = DecimalNumber(fn(lam.get_value()), num_decimal_places=places, color=col, font_size=32)
                num.next_to(left, RIGHT, buff=0.15)
                num.add_updater(lambda m, fn=fn, left=left: m.set_value(fn(lam.get_value())).next_to(left, RIGHT, buff=0.15))
                rows.add(VGroup(left, num))
            return rows

        tr, ro = always_redraw(tracer), readout()
        self.play(FadeIn(tr), FadeIn(ro), run_time=0.8)
        self.caption(label("slide λ along the step: the slope it reads is 0 everywhere", 26).move_to(SLOT))
        self.play(lam.animate.set_value(4.5), run_time=4.5, rate_func=linear)
        self.wait(1.2)
        self.caption(label("gradient descent follows the slope: at 0 it has no direction to move", 26, SKY).move_to(SLOT))
        self.wait(3.2)

        # soften the step
        g_sig = MathTex(r"g(\lambda) = \sigma(\lambda) = \frac{1}{1 + e^{-\lambda}}", color=GOLD, font_size=34)
        g_sig.move_to(g_step).align_to(lam_def, LEFT)
        sig = ax.plot(sigma, x_range=[-6, 6, 0.005], color=GOLD, stroke_width=4)
        dsig = dax.plot(lambda x: sigma(x) * (1 - sigma(x)), x_range=[-6, 6, 0.005], color=GOLD, stroke_width=4)
        self.play(FadeOut(tr), FadeOut(ro), run_time=0.5)
        self.caption(label("soften the step into the sigmoid", 26).move_to(SLOT))
        self.play(Transform(step, sig), Transform(flat, dsig), FadeTransform(g_step, g_sig), run_time=2.4)
        self.wait(1.6)

        mode.update(g=sigma, d=lambda x: sigma(x) * (1 - sigma(x)), col=GOLD)
        lam.set_value(-4.5)
        tr, ro = always_redraw(tracer), readout()
        self.play(FadeIn(tr), FadeIn(ro), run_time=0.6)
        self.caption(label("now every λ has a slope, so gradient descent knows which way is down", 26).move_to(SLOT))
        self.play(lam.animate.set_value(0), run_time=3.2, rate_func=smooth)
        self.wait(0.6)
        self.caption(label(f"steepest at λ = 0: slope {sigma(0) * (1 - sigma(0)):.2f}, the top of the bell", 26).move_to(SLOT))
        self.wait(2.4)

        x1 = 1.4
        s1 = sigma(x1)
        self.play(lam.animate.set_value(x1), run_time=1.6)
        f1 = MathTex(r"\sigma'(\lambda) = \sigma(\lambda)\,[1 - \sigma(\lambda)]", color=GOLD, font_size=30)
        f2 = MathTex(rf"= {s1:.2f} \times {1 - s1:.2f} = {s1 * (1 - s1):.2f}", color=GOLD, font_size=30)
        VGroup(f1, f2).arrange(DOWN, buff=0.22, aligned_edge=LEFT).move_to([0, -1.55, 0]).align_to(lam_def, LEFT)
        self.caption(label("and the slope comes from the output itself: σ times (1 − σ)", 26).move_to(SLOT))
        self.play(FadeIn(f1, shift=RIGHT * 0.15), run_time=0.7)
        self.play(FadeIn(f2, shift=RIGHT * 0.15), run_time=0.7)
        self.wait(2.8)
        self.play(lam.animate.set_value(4.5), FadeOut(f2), run_time=2.0)
        self.caption(label(f"far out it flattens, {sigma(4.5) * (1 - sigma(4.5)):.2f} at λ = 4.5, but never to exactly 0", 26).move_to(SLOT))
        self.wait(2.8)

        # read patients off the curve: a probability, not a verdict
        self.play(FadeOut(tr), FadeOut(ro), FadeOut(f1), run_time=0.6)
        self.caption(label("the output is a probability: three patients, readmission within 30 days", 26).move_to(SLOT))
        head = label("λ from each patient's record", 22, MUTED).move_to([0, 0.95, 0]).align_to(lam_def, LEFT)
        self.play(FadeIn(head), run_time=0.5)
        rows = VGroup()
        for i, (name, x0) in enumerate((("A", -0.6), ("B", 1.4), ("C", 3.2))):
            p0 = sigma(x0)
            v = DashedLine(ax.c2p(x0, 0), ax.c2p(x0, p0), color=CREAM, stroke_width=2)
            h = DashedLine(ax.c2p(x0, p0), ax.c2p(-6, p0), color=CREAM, stroke_width=2)
            d = Dot(ax.c2p(x0, p0), radius=0.08, color=CREAM)
            tag = label(name, 22, CREAM).next_to(d, UL if x0 > 0 else DR, buff=0.08)
            row = MathTex(rf"\text{{{name}}}:\ \lambda = {x0}\ \Rightarrow\ \hat\pi = {p0:.2f}", color=CREAM, font_size=32)
            row.move_to([0, 0.35 - 0.6 * i, 0]).align_to(lam_def, LEFT)
            self.play(Create(v), Create(h), FadeIn(d, tag), FadeIn(row, shift=RIGHT * 0.15), run_time=1.1)
            rows.add(row)
            self.wait(1.6)
            self.play(FadeOut(VGroup(v, h)), run_time=0.4)
        self.caption(label("0.35, 0.80, 0.96: how likely, for each patient, not a yes or a no", 26).move_to(SLOT))
        self.wait(3.0)
        self.caption(label("one sigmoid neuron + cross-entropy = logistic regression, as glm() fits it", 26, GOLD).move_to(SLOT))
        self.wait(4.0)


# ---------------------------------------------------------------- 5. hidden layer
class HiddenLayer(Stage):
    """Two hundred invented patients, BMI and systolic pressure, at risk outside
    a safe oval. A network is fitted with 1, 2, 3 and 4 hidden neurons. Each
    hidden neuron is a line in the plane (dashed, numbered as in the diagram);
    the output layer blends the lines into the boundary. The log on the right
    counts weights and patients classified right, both computed here."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    def construct(self):
        X, y = patients(np.random.default_rng(3), 200)
        Z = (X - MU) / SD

        ax = risk_axes(6.0, 4.6).to_edge(LEFT, buff=1.0).shift(UP * 0.5)
        xl = label("BMI", 22, MUTED).next_to(ax.x_axis, DOWN, buff=0.42)
        yl = label("systolic BP", 22, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.55)
        self.play(Create(ax), FadeIn(xl, yl), run_time=1.0)
        dots = VGroup(*[Dot(ax.c2p(*p), radius=0.05, color=GOLD if r else SKY) for p, r in zip(X, y)])
        self.play(FadeIn(dots, lag_ratio=0.01), run_time=1.4)
        self.caption(label(f"{len(y)} patients (invented): BMI and systolic blood pressure", 26).move_to(SLOT))
        self.wait(2.4)
        self.caption(label(f"gold: at risk, {int(y.sum())} of them, too low or too high on either", 26, GOLD).move_to(SLOT))
        self.wait(2.6)

        def fit(L, lam=3e-4, starts=40):
            def unpack(w):
                return w[:3 * L].reshape(3, L), w[3 * L:]

            def loss(w):
                W1, W2 = unpack(w)
                p = np.clip(sigma(W2[0] + np.tanh(W1[0] + Z @ W1[1:]) @ W2[1:]), 1e-9, 1 - 1e-9)
                return -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)) + lam * np.sum(w ** 2)
            r = np.random.default_rng(L)
            best = min((minimize(loss, r.normal(0, 1, 4 * L + 1), method="L-BFGS-B") for _ in range(starts)),
                       key=lambda res: res.fun)
            W1, W2 = unpack(best.x)

            def logit(P):
                return W2[0] + np.tanh(W1[0] + ((P - MU) / SD) @ W1[1:]) @ W2[1:]
            return W1, logit

        def neuron_line(w):
            """Where hidden neuron (b, a1, a2) is zero, clipped to the plot."""
            b, a1, a2 = w
            pts = []
            for bm in (15, 40):
                s = MU[1] - SD[1] * (b + a1 * (bm - MU[0]) / SD[0]) / a2
                if 80 <= s <= 180:
                    pts.append((bm, s))
            for s in (80, 180):
                bm = MU[0] - SD[0] * (b + a2 * (s - MU[1]) / SD[1]) / a1
                if 15 <= bm <= 40:
                    pts.append((bm, s))
            pts = sorted(set((round(p[0], 6), round(p[1], 6)) for p in pts))
            return (pts[0], pts[-1]) if len(pts) >= 2 else None

        def diagram(L):
            ins = VGroup(*[Circle(radius=0.2, color=MUTED, stroke_width=2) for _ in range(2)]).arrange(DOWN, buff=0.7)
            hid = VGroup(*[Circle(radius=0.2, color=MUTED, stroke_width=2) for _ in range(L)]).arrange(DOWN, buff=0.22)
            out = Circle(radius=0.2, color=CREAM, stroke_width=2.5)
            VGroup(ins, hid, out).arrange(RIGHT, buff=1.0)
            edges = VGroup(*[Line(a.get_center(), b.get_center(), buff=0.2, color=MUTED, stroke_width=1.2,
                                  stroke_opacity=0.6) for a in ins for b in hid],
                           *[Line(b.get_center(), out.get_center(), buff=0.2, color=MUTED, stroke_width=1.2,
                                  stroke_opacity=0.6) for b in hid])
            nums = VGroup(*[label(str(i + 1), 20, CREAM).move_to(c) for i, c in enumerate(hid)])
            names = VGroup(label("BMI", 20, MUTED).next_to(ins[0], LEFT, buff=0.15),
                           label("BP", 20, MUTED).next_to(ins[1], LEFT, buff=0.15),
                           label("risk", 20, CREAM).next_to(out, RIGHT, buff=0.15))
            g = VGroup(edges, ins, hid, out, nums, names)
            g.move_to([0, 2.25, 0]).align_to([COL, 0, 0], LEFT)
            g.hid = hid
            return g

        # the log: one row per network
        C1, C2, C3, TOP = COL, COL + 1.35, COL + 3.45, 0.55
        head = VGroup(label("hidden", 22, MUTED).move_to([0, TOP, 0]).align_to([C1, 0, 0], LEFT),
                      label("weights", 22, MUTED).move_to([0, TOP, 0]).align_to([C2, 0, 0], LEFT),
                      label("right", 22, MUTED).move_to([0, TOP, 0]).align_to([C3, 0, 0], LEFT))
        rows = VGroup()

        cur_d = None
        lines = VGroup()
        bnd = None
        texts = {
            1: "one hidden neuron: the boundary can only be a straight line",
            2: "two neurons, two lines: the boundary bends where they meet",
            3: "three lines fence the safe zone: the boundary rounds their triangle",
            4: "four lines: the boundary rounds towards the oval",
        }
        for L in (1, 2, 3, 4):
            W1, logit = fit(L)
            right = int(((logit(X) > 0) == (y > 0.5)).sum())
            w_count = 3 * L + (L + 1)
            print(f"L={L}: {right} of {len(y)} right, {w_count} weights")

            d = diagram(L)
            anims = [FadeOut(lines)] if len(lines) else []
            if bnd is not None:
                anims.append(FadeOut(bnd))
            anims.append(FadeIn(d) if cur_d is None else FadeTransform(cur_d, d))
            if L == 1:
                anims.append(FadeIn(head))
            self.play(*anims, run_time=1.0)
            cur_d = d
            self.caption(label(texts[L], 26).move_to(SLOT))

            lines = VGroup()
            for i in range(L):
                seg = neuron_line(W1[:, i])
                if seg is None:
                    continue
                a, b = ax.c2p(*seg[0]), ax.c2p(*seg[1])
                ln = DashedLine(a, b, color=MUTED, stroke_width=2.5, dash_length=0.12)
                # the number sits at the line's end, pushed into the plot
                inward = ax.c2p(27.5, 130) - a
                tag = label(str(i + 1), 20, CREAM).move_to(a + 0.28 * inward / np.linalg.norm(inward))
                self.play(Create(ln), FadeIn(tag), d.hid[i].animate.set_stroke(CREAM, width=3), run_time=0.9)
                lines.add(ln, tag)
                self.wait(0.5)

            bnd = boundary_curve(ax, logit)
            self.play(Create(bnd), run_time=1.5)
            y_row = TOP - 0.55 * L
            row = VGroup(MathTex(rf"L = {L}", color=GOLD, font_size=32).move_to([0, y_row, 0]).align_to([C1, 0, 0], LEFT),
                         MathTex(rf"3 \cdot {L} + {L + 1} = {w_count}", color=GOLD, font_size=32).move_to([0, y_row, 0]).align_to([C2, 0, 0], LEFT),
                         label(f"{right} of {len(y)}", 26, GOLD).move_to([0, y_row, 0]).align_to([C3, 0, 0], LEFT))
            prev = [rows[-1].animate.set_color(CREAM)] if len(rows) else []
            self.play(FadeIn(row, shift=RIGHT * 0.15), *prev, run_time=0.6)
            rows.add(row)
            self.wait(2.6 if L < 4 else 2.0)

        self.play(FadeOut(lines), run_time=0.8)
        self.caption(label("each hidden neuron is a line; the output layer blends them into the boundary", 26, GOLD).move_to(SLOT))
        self.wait(4.0)


# ---------------------------------------------------------------- 6. overfitting
class Overfitting(Stage):
    """A network far bigger than its data: 40 hidden neurons, 161 weights, 50
    training patients of whom 6 carry a flipped label. Trained with Adam, both
    losses are recorded at every iteration; the boundary is drawn at six
    moments, with the patients each set gets wrong. Training loss falls to
    zero; test loss turns up after its minimum, and that iteration is where
    early stopping keeps the weights."""

    WAIT_SCALE = 1.0
    PLAY_SCALE = 1.0

    H, T, LR = 40, 600, 0.01

    def construct(self):
        rng = np.random.default_rng(8)
        Xtr, ytr = patients(rng, 50)
        Xte, yte = patients(rng, 100)
        flipped = rng.choice(len(ytr), 6, replace=False)
        ytr[flipped] = 1 - ytr[flipped]
        Ztr, Zte = (Xtr - MU) / SD, (Xte - MU) / SD

        # train, keeping both losses at every iteration and the weights at the moments we draw
        H, T, LR = self.H, self.T, self.LR
        r = np.random.default_rng(7)
        params = [r.normal(0, 1, (2, H)), r.normal(0, 1, H), r.normal(0, 0.1, H), np.zeros(1)]
        m = [np.zeros_like(p) for p in params]
        v = [np.zeros_like(p) for p in params]

        def fwd(Z, P):
            A = np.tanh(Z @ P[0] + P[1])
            return A, sigma(A @ P[2] + P[3][0])

        def ce(p, yy):
            p = np.clip(p, 1e-9, 1 - 1e-9)
            return -np.mean(yy * np.log(p) + (1 - yy) * np.log(1 - p))

        tr_loss, te_loss, snaps = [], [], {}
        for t in range(0, T + 1):
            _, ptr = fwd(Ztr, params)
            _, pte = fwd(Zte, params)
            tr_loss.append(ce(ptr, ytr)); te_loss.append(ce(pte, yte))
            snaps[t] = [p.copy() for p in params]
            if t == T:
                break
            A, p = fwd(Ztr, params)
            g = (p - ytr) / len(ytr)
            dA = np.outer(g, params[2]) * (1 - A ** 2)
            grads = [Ztr.T @ dA, dA.sum(0), A.T @ g, np.array([g.sum()])]
            for i in range(4):
                m[i] = 0.9 * m[i] + 0.1 * grads[i]
                v[i] = 0.999 * v[i] + 0.001 * grads[i] ** 2
                params[i] = params[i] - LR * (m[i] / (1 - 0.9 ** (t + 1))) / (np.sqrt(v[i] / (1 - 0.999 ** (t + 1))) + 1e-8)
        t_star = int(np.argmin(te_loss))

        def logit_at(t):
            P = snaps[t]
            return lambda Q: np.tanh(((Q - MU) / SD) @ P[0] + P[1]) @ P[2] + P[3][0]

        def wrong(t, Xs, ys):
            return (logit_at(t)(Xs) > 0) != (ys > 0.5)

        t_zero = next(t for t in range(T + 1) if not wrong(t, Xtr, ytr).any())
        moments = [20, 50, t_star, 200, t_zero, T]
        for t in moments:
            print(f"t={t}: train loss {tr_loss[t]:.3f}, wrong {wrong(t, Xtr, ytr).sum()}/50; "
                  f"test loss {te_loss[t]:.3f}, wrong {wrong(t, Xte, yte).sum()}/100")

        # ---- the stage
        ax = risk_axes(5.8, 4.4).to_edge(LEFT, buff=1.0).shift(UP * 0.6)
        xl = label("BMI", 22, MUTED).next_to(ax.x_axis, DOWN, buff=0.42)
        yl = label("systolic BP", 22, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.55)
        ymax = float(np.ceil(max(te_loss) * 2) / 2)       # the whole test curve fits
        ex = Axes(x_range=[0, T, 100], y_range=[0, ymax, 0.5], x_length=4.3, y_length=2.3,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.4},
                  x_axis_config={"numbers_to_include": [0, 200, 400, 600], "font_size": 20},
                  y_axis_config={"numbers_to_include": list(np.arange(0.5, ymax + 0.01, 0.5)), "font_size": 20,
                                 "decimal_number_config": {"num_decimal_places": 1}})
        for n in ex.x_axis.numbers + ex.y_axis.numbers:
            n.set_color(MUTED)
        ex.move_to([0, 1.75, 0]).align_to([COL + 0.55, 0, 0], LEFT)
        assert 50 < t_star < 200 < t_zero < T, (t_star, t_zero)
        exl = label("loss (cross-entropy)", 22, MUTED).next_to(ex.y_axis, UP, buff=0.12).align_to(ex.y_axis, LEFT)
        itl = label("iterations", 22, MUTED).next_to(ex.x_axis, DOWN, buff=0.42)
        self.play(Create(ax), FadeIn(xl, yl), run_time=1.0)

        dtr = VGroup(*[Dot(ax.c2p(*p), radius=0.06, color=GOLD if c else SKY) for p, c in zip(Xtr, ytr)])
        dte = VGroup(*[Circle(radius=0.055, color=GOLD if c else SKY, stroke_width=1.8).move_to(ax.c2p(*p))
                       for p, c in zip(Xte, yte)])
        self.play(FadeIn(dtr, lag_ratio=0.02), run_time=1.0)
        self.caption(label("the patients again: 50 to train on, filled", 26).move_to(SLOT))
        self.wait(1.6)
        self.play(FadeIn(dte, lag_ratio=0.01), run_time=1.0)
        self.caption(label("and 100 held out to test, hollow: the network never sees them", 26).move_to(SLOT))
        self.wait(2.2)

        rings = VGroup(*[Circle(radius=0.15, color=CREAM, stroke_width=2.5).move_to(dtr[i]) for i in flipped])
        self.caption(label("6 training patients carry the wrong label: noise, flipped on purpose", 26).move_to(SLOT))
        self.play(Create(rings), run_time=0.8)
        self.wait(2.6)
        self.play(FadeOut(rings), run_time=0.5)

        w = 3 * H + (H + 1)
        self.play(Create(ex), FadeIn(exl, itl), run_time=1.0)
        self.caption(label(f"a network with {H} hidden neurons: {w} weights for 50 patients", 26).move_to(SLOT))
        self.wait(2.4)

        # counts panel under the loss plot

        def counts(t, colour=CREAM):
            g = VGroup(MathTex(rf"\text{{iteration }} {t}", color=colour, font_size=32),
                       label(f"training (filled): {wrong(t, Xtr, ytr).sum()} of 50 wrong", 24, CREAM),
                       label(f"test (hollow): {wrong(t, Xte, yte).sum()} of 100 wrong", 24, GOLD))
            g.arrange(DOWN, buff=0.22, aligned_edge=LEFT).move_to([0, -1.3, 0]).align_to([COL, 0, 0], LEFT)
            return g

        def miss_rings(t):
            return VGroup(*[Circle(radius=0.12, color=CREAM, stroke_width=2).move_to(dte[i])
                            for i in np.flatnonzero(wrong(t, Xte, yte))])

        def seg(vals, a, b, col):
            pts = [ex.c2p(t, min(vals[t], ymax)) for t in range(a, b + 1)]
            return VMobject(color=col, stroke_width=4).set_points_as_corners(pts)

        texts = {
            20: "iteration 20: still too simple, wrong on both sets",
            50: "both losses fall together: it is learning the oval",
            t_star: f"iteration {t_star}: the test loss is at its lowest",
            200: "training loss keeps falling, test loss has turned up",
            t_zero: f"iteration {t_zero}: no training patient wrong, the flipped ones included",
            T: "test loss climbs, training loss stays near zero: it has learned the noise",
        }
        drawn, bnd, cnt, rg = 0, None, None, None
        for t in moments:
            new_b = boundary_curve(ax, logit_at(t), depth=7)
            new_c, new_r = counts(t), miss_rings(t)
            anims = [Create(seg(tr_loss, drawn, t, CREAM)), Create(seg(te_loss, drawn, t, GOLD))]
            anims.append(Create(new_b) if bnd is None else FadeTransform(bnd, new_b))
            anims.append(FadeIn(new_c) if cnt is None else FadeTransform(cnt, new_c))
            if rg is not None:
                anims.append(FadeOut(rg))
            self.play(*anims, run_time=2.0 if t - drawn > 150 else 1.4, rate_func=linear)
            self.play(Create(new_r), run_time=0.6)
            bnd, cnt, rg, drawn = new_b, new_c, new_r, t
            self.caption(label(texts[t], 26, GOLD if t == T else CREAM).move_to(SLOT))
            if t == t_zero:                      # the curves have parted: name them
                k = t_zero - 60
                self.play(FadeIn(label("train", 22, CREAM).next_to(ex.c2p(k, tr_loss[k]), UP, buff=0.12)),
                          FadeIn(label("test", 22, GOLD).next_to(ex.c2p(k, te_loss[k]), UP, buff=0.12)), run_time=0.6)
            self.wait(3.0)

        # where early stopping would have kept the weights
        stop = DashedLine(ex.c2p(t_star, 0), ex.c2p(t_star, ymax), color=CREAM, stroke_width=2)
        stop_l = label("stop here", 22, CREAM).next_to(stop, RIGHT, buff=0.1).align_to(stop, UP)
        best_b = boundary_curve(ax, logit_at(t_star), depth=7, color=CREAM)
        self.play(Create(stop), FadeIn(stop_l), FadeTransform(bnd, best_b), FadeOut(rg),
                  FadeTransform(cnt, counts(t_star, GOLD)), run_time=1.2)
        self.caption(label(f"early stopping: keep the weights of iteration {t_star}, not the last ones", 26, GOLD).move_to(SLOT))
        self.wait(4.0)
