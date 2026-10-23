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

`.mcp.json` points at `~/dev/mcp-blackboard-ucsc` — an MCP server for Blackboard
Learn Ultra: course content, assessments, questions, gradebook, grading,
attendance, rubrics, adaptive release, groups, and the SVE grade file. Keep the
checkout out of iCloud; a venv under `~/Desktop` gets evicted file by file and
every import hangs.

**Auth is settled.** The Rome administration registered the application under
Admin → REST API Integrations on 18 September 2026, bound to Niccolò's user, so
client credentials work: `bb_whoami` answers with his account, the token lasts an
hour and the server renews it itself. The `BB_TOKEN` stopgap — a token lifted
from DevTools, alive for minutes — is gone. Key and secret live in that repo's
`.env`, never here.

Getting the same thing at another institution is documented in
`docs/access.md` there, including the message to send the administrator.

Course IDs: 26/27 is `_170037_1`, 25/26 is `_158385_1`.

What the public API can and cannot do on this build (4001.2.0 in October 2026;
`/v1/system/version` says, and the matching swagger is
`https://devportal-docstore.s3.amazonaws.com/learn-swagger-<version>.json`): content,
folders, test *shells*, gradebook columns, attempts and grades all work.
**Question content does not** — verified on 22 October 2026 and written in the
swagger (every `questionHandler.type` but `Presentation` is *Read Only*): `POST …/questions`
answers *"Creating non-presentation questions is not supported"* for every
scored type and creates only `Presentation` text blocks; reads come back as
opaque `QuestionBlock` handles. So tests are authored in the Ultra UI or
imported with Upload Questions, and the API does the rest: title, release date
(`bb_release_by_date`), points after the upload (`bb_set_question_points`), and
the gradebook side. Time limit, attempts and results-release settings are not
exposed on any route.

Writes are off by default; grade writes have a second switch of their own.

## Intermediate exams on Blackboard

Both intermediates are Blackboard tests sat on the lab machines. The settings,
fixed on the first one (October 2026), are the same every time:

| Setting | Value |
|---|---|
| Questions | **15, 2 points each, 30 in total**; pass mark 18. (The *full exam*: 20 questions, 2 points each, 40 in total, 60 minutes) |
| Mix | 6 multiple choice · 3 true/false · 4 open medium · 2 open challenging |
| Language | English, like the syllabus |
| Time limit | **60 minutes, automatic submission** |
| Attempts | 1 |
| Due date | **none**: the time limit and the visibility window do the job; a due date only adds a "late" flag and blocks the settings page |
| Location restriction | `Aula + WIFI (tutte le sedi)` |
| Mark category | Test; marks posted automatically |
| Visibility | hidden until the exam starts; the date is announced on Blackboard and on the site |

Open questions are answered in the text box: the R code, the numbers, and one
sentence that reads them. They are marked by hand, 0 to 2 in steps of 0.5:
right code, numbers and sentence = 2; right code and numbers, vague sentence
= 1.5; right function, wrong reading = 1; a relevant attempt = 0.5. The
mock of 23 Oct 2026 was sat as 20 questions at 1.5 (a mistake, corrected the
same day): the pool's `points` is 2 for every exam; `bb_build_exam` takes `points`
explicitly all the same.

**Authoring.** Questions live in **pools**, one per module, as JSON in
`private/` (git-ignored: the repo is public): `private/pool-module-1.json` is
the model, `private/pool-module-2.json` is to be written from lectures 10–21.
The format and the tools are in the MCP (`bb_mcp.exams`): `bb_pool_check`
validates and counts a pool; `bb_build_exam` draws a paper — the first
intermediate from pool 1, the second from pool 2, the full exam half from
each — with a seed, excluding every id in earlier manifests, and writes the
*Upload Questions* file, the key (`<name>-key.qmd`, rendered with typst from
a copy outside this project, or `_site/` would serve it) and the manifest
`<name>.json`. **Into Blackboard: `bb_test_fill(course, test_id,
"private/<name>.json", replace=True)`** after `bb_ultra_connect` — it writes the
manifest's questions straight into the test, in order, at its points, through
the Ultra interface's own API (a test is an assessment on the same route as a
bank). `bb_assessment_questions` reads the test back to check it against the
pool; the mock of 23 Oct 2026 went in this way and was verified question by
question. The Upload Questions file is the fallback (then
`bb_set_question_points` for the points). Every
number in a key comes from `private/mock-exam-1-key.R`, run; a question whose
answer moves with the seed says so in its key. The mock before each
intermediate uses the same settings, different questions, and **counts for
nothing**: the course has no overall-grade column (marks go to the SVE file),
so a mock score enters no calculation; the "Formative assessment" switch in
the test settings is the label for it, and it is UI-only (every API write of
`isFormative` is ignored or refused, tried 23 Oct 2026).
Manifests so far: `mock-exam-1.json` (23 Oct 2026), `practice-1.json` (the
practice paper on the site, `homework/m1-practice.qmd`, drawn 23 Oct 2026 and
removed from the midterm banks), `midterm-1.json` (draft). An open question's
`example` is the model answer and goes to Blackboard as the question's answer
text; notes for the marker ("half marks if…") go in `marking`, which only the
key prints. Open questions use mtcars, cars, PlantGrowth, warpbreaks, lung and
`churn.csv`; `customers.csv` was dropped from the pool on 23 Oct 2026 (its
columns are independent by construction and the lab never opened it). The
`private/*.qmd` keys are excluded from the render (`"!private/"` in
`_quarto.yml`), or `make deploy` would publish them.

**Question banks, the next step.** Ultra tests can draw *question pools*
(k questions at random) from the course's *question banks*; the plan is one
bank per topic, filled from the pool files, and exams built as lists of
pools, so every student gets a different paper. The public API cannot write
questions, but the MCP's `bb_banks_from_pool` does it through the Ultra
interface's own API, using the lecturer's signed-in browser session (a
Chrome started with `--remote-debugging-port=9223`, then `bb_ultra_connect`;
details in the MCP README). The step that is still manual, or to be recorded
next, is adding the question pools to a test: a pool reads back as a
`questionBlock`, and `bb_assessment_clear` deletes one, but the request that
creates one was never captured. Until then, a paper is a fixed list of
questions, `bb_test_fill`.

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

The lab deck `lectures/lab-module-1-in-r.qmd` ends with an appendix, one slide
per mock question with the answer, generated from the pool and the Blackboard
order; regenerate it rather than editing those slides by hand.

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
