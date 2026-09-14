# Statistics & Big Data — 2026/2027

Course website for *Statistics and Big Data (Business Statistics and Artificial
Intelligence)*, HEMA specialistic degree, Università Cattolica del Sacro Cuore, Rome.
Proff. Giuseppe Arbia · Niccolò Salvini.

Built with [Quarto](https://quarto.org/) as a plain website (not bookdown — the site
is not read front to back, it is a schedule students dip into).

## Weekly routine

Adding the slides for a lecture is one line. Drop the file in `slides/`, then in
`index.qmd` change the `—` in that lecture's **Materials** cell:

```markdown
| 3 | Mon 9 Nov | 17:00–19:00 · 202 | Advanced regression modelling | [slides](slides/03-regression.pdf) |
```

Several links in one cell:

```markdown
| ... | [slides](slides/03-regression.pdf) · [code](materials/03-regression.R) · [ISLR 3](https://www.statlearning.com/) |
```

Same pattern for `homework.qmd` (`homework/` folder) — files in `slides/`,
`materials/` and `homework/` are copied to the site verbatim.

## Commands

```bash
make preview   # live reload while editing
make build     # regenerate QR + quarto render -> _site/
make deploy    # build, then netlify deploy --prod
make qr        # QR only, after changing booking-url
```

## Shared settings

Links that appear on several pages live in `_variables.yml` and are used as
`{{< var booking-url >}}`. Change the value once:

| Variable | What it is |
|---|---|
| `booking-url` | Google appointment page for online office hours — **also the target of the QR code**, run `make qr` after changing it |
| `blackboard-url` | Blackboard course page |
| `drive-url` | shared drive, if used |
| `repo-url` | this repository |

## First deploy

```bash
netlify login
netlify init      # link or create the site, publish dir = _site
make deploy
```

Afterwards `make deploy` is the whole workflow.
