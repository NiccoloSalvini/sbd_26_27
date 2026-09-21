# CLAUDE.md — Statistics & Big Data course site

Course website for *Statistics and Big Data (Business Statistics and Artificial
Intelligence)*, HEMA specialistic degree, Università Cattolica del Sacro Cuore,
Rome. Proff. Giuseppe Arbia (Module 1) and Niccolò Salvini (Module 2).

Live: <https://sbd-26-27.netlify.app> · Repo: `NiccoloSalvini/sbd_26_27`

## Commands

```bash
make preview   # quarto preview, live reload while editing
make build     # quarto render -> _site/
make deploy    # build, then netlify deploy --prod
make qr        # printable QR of booking-url, on demand — not part of build
make clean     # rm -rf _site .quarto
```

`make deploy` is the whole publishing workflow. There is no CI: the site is
rendered locally and the finished `_site/` is pushed to Netlify.

## Architecture, and why it is this way

**Quarto website, not bookdown.** The 22/23 → 25/26 editions were bookdown
(`sbd_25_26` and earlier). Bookdown compiles a *book* — a chapter tree read in
sequence. Nobody reads a course site in sequence; they arrive on Tuesday to get
Tuesday's slides. Quarto `type: website` gives independent pages with a navbar,
so the structure matches the use.

**The home page is the schedule table**, Stanford-style (CS229, CS231n). One row
per lecture, everything else hangs off it. No introductory prose above it.

**The schedule is a plain markdown table, not generated from YAML by an R chunk.**
A chunk would add a build dependency (the `yaml` package, a working R) to save
nothing — editing a table row costs the same either way. Fewer moving parts in
November at 16:50.

**Netlify has no build command.** Its image has no Quarto, and installing it on
every deploy is a part that breaks when Quarto changes version. Rendering locally
puts that fragility on a machine where you see it immediately. `netlify.toml`
only sets `publish = "_site"` and a couple of headers.

## The weekly loop

Adding a lecture's material is one line. Drop the file in `slides/`, then in
`index.qmd` change the `—` in that lecture's **Materials** cell:

```markdown
| 3 | Fri 25 Sep | 09:00–13:00 · 204 | Multiple regression | [slides](slides/03-regression.pdf) |
```

Several links in one cell:

```markdown
| ... | [slides](slides/03.pdf) · [code](materials/03.R) · [ISLR 3](https://www.statlearning.com/) |
```

Then `make deploy`. Files in `slides/`, `materials/` and `homework/` are copied to
the site verbatim — they are listed under `resources:` in `_quarto.yml`.

**Practice sets are rendered pages, not attachments.** `homework/NN-topic.qmd`
is rendered by Quarto (it is in `project: render:`) and linked from the table in
`homework.qmd`; the folder is deliberately *not* in `resources:`, or the `.qmd`
sources would be copied next to the HTML. Numbering follows the **set** (10–18
for Module 2), not the lecture, because Module 1's sets are 1–9.

A set is 30 to 45 minutes, one dataset, four to six questions, and most
questions end in a sentence the student has to write rather than a number they
have to get — the exam asks for a justified choice, and that is the part that
cannot be improvised. Datasets come from `materials/`, which is in `resources:`.

## Files

| Path | What |
|---|---|
| `index.qmd` | home = schedule, both modules, instructors |
| `syllabus.qmd` | full syllabus, assessment rules |
| `setup.qmd` | R / RStudio / Python install guide, shown in class |
| `homework.qmd` | optional practice sets — **not graded**, the syllabus says no assignments are required |
| `resources.qmd` | textbooks, deep-dive reading |
| `office-hours.qmd` | booking link, marks policy |
| `_variables.yml` | links used on several pages |
| `styles.scss` | theme: Cattolica navy `#002f57`, Libre Franklin, schedule table styling |
| `.mcp.json` | Blackboard MCP server (see below) |

## Shared links

Anything appearing on more than one page lives in `_variables.yml` and is used as
`{{< var booking-url >}}`:

| Variable | Note |
|---|---|
| `booking-url` | Google appointment page (Prof. Salvini only) |
| `blackboard-url` | Blackboard course page |
| `repo-url` | this repository |

`materials/setup.R` is served verbatim and is what the Setup page tells students
to `source()`. The package list in it and the one shown on the page must match;
the page says "this is what it runs".

## Conventions

- **Site language is English.** The syllabus and the degree are in English.
- **Screenshots: photograph what is stable, write commands for what changes.**
  Vendor pages (CRAN, posit.co) get redesigned without warning and a stale
  screenshot misleads silently, so installing goes through the CRAN installer and
  prose, with `rig` as the terminal-user option. The
  RStudio *Preferences* and *New Project* screenshots stay: that UI has been
  stable for a decade and the image is where the teaching is.
- Content is created hidden / unavailable by default wherever the option exists.
- Fonts: **Libre Franklin** (body and headings), **JetBrains Mono** (code).
  Source Sans Pro and IBM Plex Sans were both tried and rejected — don't
  reintroduce them.

## Calendar

The real timetable does **not** match the syllabus's "weeks 1–6 / 7–12" split.
Check the actual room booking every year.

| | Dates | Lectures | Hours |
|---|---|---|---|
| Module 1 · Arbia | 14 Sep → 23 Oct 2026 | 9 | 30 |
| Module 2 · Salvini | 2 Nov → 11 Dec 2026 | 12 | 30 |

Hours summing to 30 each is the check that the split is right: sessions vary
between 2, 3 and 4 hours, so two equal totals that nobody imposed is strong
evidence the assignment is correct.

## Blackboard MCP

`.mcp.json` points at `~/Desktop/py_projects/mcp-blackboard-ucsc` — an MCP server
for Blackboard Learn Ultra: course content, assessments, questions, gradebook,
grading.

It needs a bearer token. Two ways, both documented in that repo's README:

- **`BB_TOKEN`** — a token lifted from a logged-in Ultra session (DevTools →
  Network → `tokeninfo`). Works now, lasts about an hour. The stopgap.
- **client credentials** — an application registered at developer.anthology.com
  *and* a Blackboard administrator adding its ID under Admin → REST API
  Integrations. Niccolò is not an admin (`systemRoleIds: ["User"]`), so this
  needs the Rome Blackboard support office. The proper arrangement.

Course IDs: 26/27 is `_170037_1`, 25/26 is `_158385_1`.

What the public API can and cannot do on this build (4000.21.0): content,
folders, test *shells*, gradebook columns, attempts and grades all work.
**Question content does not** — questions come back as opaque `QuestionBlock`
handles, so tests are authored in the Ultra UI (or imported), and the API reads
the gradebook side. Time limit, attempts and results-release settings are not
exposed on any route.

Writes are off by default; grade writes have a second switch of their own.

## Slides: one Beamer theme for every lecture

`latex/beamer/` holds `beamerthemeCattolica.sty`, `template.tex` and the logo.
A lecture starts as a copy of the template: change `\lecture{n}{title}`,
`\author`, `\date`, write frames. Everything visual is the theme's job — a
lecture file that sets a colour or a font is wrong. Push the whole folder to
an Overleaf project with `overleaf_push_dir`; it is self-contained.

It compiles with pdflatex (Overleaf's default), xelatex and lualatex. Fonts
come from CTAN (`librefranklin`, `sourcecodepro`), not the system, so the
deck looks the same on every machine; a TeX lacking them falls back to
Helvetica with one log warning rather than failing in a lecture.

Three names it must never define, learnt the hard way: `\note` (beamer's
speaker notes), `\accent` (a TeX primitive), and loading tcolorbox with
`[most]` (pulls listingsutf8, absent on minimal installs). The callout
environments are `remark`, `important`, `definition*`; the colour helpers
`\navy`, `\muted`, `\gold`; code goes in `rcode`.

Final PDFs go to `slides/` (served by the site); build artefacts are ignored.

**The web sister: `lectures/`.** Any `.qmd` there renders as a revealjs deck
with `lectures/cattolica.scss` — same navy, same callouts, same bullets, Libre
Franklin and JetBrains Mono as web fonts. `lectures/_metadata.yml` carries every
visual option; a lecture file sets title, subtitle (`Lecture n · room`), author,
`date` (ISO, formatted by `date-format`) and content. Section slides are
`## [Section n]{.section-kicker} Title {.section-slide background-color="#002f57"}`;
a one-line slide is `## Text {.statement}`. Math is KaTeX — MathJax dropped
`\mathcal` glyphs. Rendered to `_site/lectures/`, so `make deploy` publishes it.

**Module 2 is twelve decks, `lectures/10-*.qmd` to `21-*.qmd`, one per row of
the schedule**, all in this format; Module 1 (Prof. Arbia) is PDFs in `slides/`.
Start a new deck from `10-opening.qmd`. Every deck follows one shape, and a
deck that skips a step should have a reason: Objectives → *Why a manager cares*
→ sections (intuition, method, a worked example by hand, In R) → an *Attention*
callout for the trap → one `.statement` slide → *Before the lab* → Reading
(ISLR chapter, Provost & Fawcett chapter, package reference). Section slides
carry `[Section n]{.section-kicker}`. Code blocks are display-only (`{.r}`),
never executed at render, so the site builds without R.

The three lab datasets — `materials/customers.csv` (L13), `brands.csv` (L15),
`churn.csv` (L17) — are **generated**, not hand-edited: `Rscript
materials/gen-data.R` rebuilds them byte for byte from fixed seeds and then
runs each lab's own pipeline as an assertion (silhouette, seed stability,
chi-square and inertia, churn rate and AUC). Change a lab's expectations there
first, then regenerate. The schedule links each dataset next to its deck.

Three things the theme fights, learnt by reading the rendered DOM and CSS:
Quarto's title slide is `<section id="title-slide">` with no `.title-slide`
class, so the theme styles `#title-slide` and sets `center-title-slide: false`
to stop reveal's inline centring; Quarto injects an inline `<style>` *after*
every stylesheet that colours callouts with `!important` on
`div.callout-x` and paints the header on `.callout-title` under
`.callout-style-default`, so the theme matches those selectors exactly; and
reveal sets `display:block` inline on the current slide, so flex layouts on a
slide need `!important`. Do not "simplify" any of those away.


**Git on this repo: add files by path.** `git add -A` scans `_site/` and
`setup_files/` on iCloud and hangs for minutes. `git add index.qmd` is instant.

**Clips: `animations/scenes.py`.** manim scenes on the course navy, formulas in
`MathTex`, words in Libre Franklin via `manimpango.register_font`. `make clips-preview`
(`-ql`) to check frames, `make clips` (`-qm`, then an ffmpeg `+faststart` remux into
`lectures/media/`) for the deck; embed with `{{< video media/Name.mp4 width="1000" height="562" >}}`.
Every clip is spoken over, and that sets the length. **A clip runs 40 to 90
seconds.** Under 30 it is a gif: it shows the finished object and is over before
a sentence about it has been said. The first five clips of lecture 18 were 7 to
12 seconds and were rewritten for exactly this reason. Length comes from
*content*, not from padding: the count of misclassified points updating as a
line rotates, each gradient-descent step written out with its own numbers, every
squared distance in a by-hand example. If a clip needs stretching to reach 40
seconds it is missing a step that should be on screen.

New scenes set `WAIT_SCALE`/`PLAY_SCALE` to 1.0 and time their own waits; the
two scales exist only to stretch the older ones. `make clips-preview` then
`ffprobe` the result is how you check a duration — read the number, do not guess
from the code.

The Makefile groups scenes per lecture (`SCENES_11`, `SCENES_18`, `SCENES_19`)
and `SCENES` concatenates them; add a lecture's group when its clips exist. The AND-gate scenes do their
arithmetic in integer hundredths so the LaTeX never shows `0.30000000000000004`.
Two traps: `manim.cfg` is read by configparser, which keeps an inline `# comment` as
part of the value (a `#` in `media_dir` makes latex fail "without a log file"); and
the media dir must stay outside `~/Desktop` (iCloud), see `manim.cfg`.

## Overleaf MCP

`.mcp.json` also loads `~/dev/overleaf-mcp` (`NiccoloSalvini/overleaf-mcp`), so
exam papers and handouts can be written as LaTeX projects on Overleaf from this
session: `overleaf_list_projects`, `overleaf_push_dir`, `overleaf_compile`,
`overleaf_download_pdf`.

It authenticates with a browser session cookie, read from the shell environment
as `OVERLEAF_COOKIE` — the `.mcp.json` entry says `${OVERLEAF_COOKIE}` and
nothing more, because this file is public. Set it in the shell before starting
Claude Code (the full `Cookie:` header from a logged-in overleaf.com tab; it must
contain `overleaf_session2`). `overleaf_whoami` is the first call to make: it
says whether the cookie is set and still valid.

## Starting the next academic year

Copy the repo to `sbd_27_28` and work through:

1. `_quarto.yml` — navbar title year, footer, description
2. `index.qmd` — the whole schedule: dates, rooms, topics, module date ranges,
   and the facts strip at the top
3. `syllabus.qmd` — new syllabus; check whether the assessment rules changed
   (they have been stable: two optional intermediates, cannot be rejected,
   50/50 weighting)
4. `homework.qmd` — practice set dates
5. `_variables.yml` — new Blackboard course URL, new booking link
6. `setup.qmd` and `materials/setup.R` — bump the target R version in both, and the site URL inside the script
7. New Netlify site: `netlify sites:create --name sbd-27-28 --account-slug niccolo-salvini`, then `make deploy`

**Do not carry over old exam simulations.** The 25/26 mocks were left behind on
purpose in 26/27 — the syllabus changed enough that old papers confuse more than
they help. Same judgement applies each year.
