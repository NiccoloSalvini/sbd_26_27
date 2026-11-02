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
the gradebook side. Time limit, attempts and results release are not on the
public API; Ultra's private API takes attempts and results release, which
`bb_test_settings` writes (2 Nov 2026), and the time limit is read only.

Writes are off by default; grade writes have a second switch of their own.

## Intermediate exams on Blackboard

Both intermediates are Blackboard tests sat on the lab machines. The settings,
fixed on the first one (October 2026), are the same every time:

| Setting | Value |
|---|---|
| Questions | **15, 2 points each, 30 in total**; pass mark 18. (The *full exam*, both modules: 20 questions, 1.5 points each, 30 in total, 90 minutes) |
| Mix | 6 multiple choice · 3 true/false · 5 open medium · 1 open challenging, drawn per student from question pools: MC easy 4 · MC medium 2 · TF easy 2 · TF medium 1 · open medium 5 · open challenging 1. Six easy, eight medium, **one challenging**: Niccolò wants about 5% hard questions in the paper (26 Oct 2026); the banks keep more for variety |
| Language | English, like the syllabus |
| Time limit | **60 minutes, automatic submission** |
| Attempts | 1 |
| Due date | **none**: the time limit and the visibility window do the job; a due date only adds a "late" flag and blocks the settings page |
| Location restriction | `Aula + WIFI (tutte le sedi)` |
| Results | submission, question feedback and question scores visible **after all marks have been posted**; **correct answers never shown**, because the banks are drawn from again |
| Mark category | Test; marks posted automatically |
| Visibility | hidden until the exam starts; the date is announced on Blackboard and on the site |

Open questions are answered in the text box: the R code, the numbers, and one
sentence that reads them. They are marked by hand, 0 to 2 in steps of 0.5:
right code, numbers and sentence = 2; right code and numbers, vague sentence
= 1.5; right function, wrong reading = 1; a relevant attempt = 0.5. The
mock of 23 Oct 2026 was sat as 20 questions at 1.5 (a mistake, corrected the
same day): the pool's `points` is 2, and `bb_build_exam` takes `points`
explicitly: 2 for an intermediate, 1.5 for the full exam.

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
question. Until 2 Nov 2026 the MCP posted every MC with `positionAfter:
"start"`, so a manifest of MCs went in reversed; fixed by the MCP's PR 1
(branch `impostazioni-test`, `bb_test_settings` with it; `private/set-10-fill.json` is the reversed workaround used
for Set 10). Read the order back either way. Shuffle the answer options in the pool file too: Ultra keeps them
as written, and a pool written correct-first gives the answer away. The
practice-set tests (Set 10 onwards) are 1 point a question, MC and TF only:
the Ultra route takes no numeric type, so a number to check is an MC whose
distractors are the neighbouring results (the next k, a bad start). Their
settings go through `bb_test_settings(course, content_id, attempts=0,
show_after_submission=[…], auto_post_grades=True)`: unlimited attempts,
score and correct answers at submission, grades posted. Set 10 was set so on
2 Nov 2026, and released with its folder `hw` by `bb_release_by_date` from
Tue 3 Nov 12:00 Rome (11:00 UTC). The Upload Questions file is the fallback (then
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
removed from the midterm banks), `midterm-1.json` (26 Oct 2026: not one paper
but the 113 questions the intermediate's pools can draw, in pool order, so a
later exam can exclude them; its key, `midterm-1-paper.pdf`, prints them all).
An open question's
`example` is the model answer and goes to Blackboard as the question's answer
text; notes for the marker ("half marks if…") go in `marking`, which only the
key prints. Open questions use mtcars, cars, PlantGrowth, warpbreaks, lung and
`churn.csv`; `customers.csv` was dropped from the pool on 23 Oct 2026 (its
columns are independent by construction and the lab never opened it).

**An exam on the lab machines uses only data that ship with R** — `datasets`
or a recommended package such as `survival` — never a CSV, and no package the
machines may lack (`car`). In the mock of 23 Oct 2026 the three `churn.csv`
questions were left blank by 34–38 of 41 students, including those who reached
the last question: nobody could load the file on those machines. The churn
questions already sat (mock, practice) stay in the pool, the others were
deleted; `private/not-on-lab-machines.json` lists what is left (and D4, on
`car::vif`) in manifest form, so it goes in every `exclude_manifests`.
The same holds for `pool-module-2.json`, although the Module 2 labs run on
`customers.csv`, `brands.csv` and `churn.csv`: its open questions need built-in
data (USArrests, iris, …).

**Ridge, LASSO and time series are never examined**, neither in an
intermediate nor in the full exam. The calendar lists them (lectures 7 and 8),
but Prof. Arbia's nine decks end at survival, and the lab of 20 Oct 2026
stopped before its sections 4 and 5: nobody taught them. The pool has no
question on them; the eight written (H1–H8) wait in
`private/mock-exam-1-draft.qmd`, *Held back*, and stay there. The
`private/*.qmd` keys are excluded from the render (`"!private/"` in
`_quarto.yml`), or `make deploy` would publish them.

**Marking.** Blackboard marks the closed questions itself. For the open ones:
`bb_test_answers(course, column_id, pool_path="private/pool-module-1.json")`
returns every submission with each open answer next to the model answer, the
pool's marking notes and a proposal (key numbers found, functions used, a
sentence or not, points on the question's scale with the reason);
`bb_question_answers` does one question across the class, the way to keep
one question's marking consistent. The proposal is read, corrected where the
sentence says more or less than the numbers, then written with
`bb_grade_answers`; posting to the students is the column's Post in Ultra.
A review file (`private/<exam>-review.md`, one block per student) is the
working document; the mock's is `private/mock-review.md`.

**Students will use AI tools to cheat, and marking must catch it.** Every
proposal carries `ai_signals`: LaTeX or markdown in a typed answer, sentences
addressed to "your lectures", hedges about "the dataset version",
approximate numbers where R prints exact ones, and above all numbers given as
output that the data do not produce. One weak signal, usually explained by a
wrong model, is marked on the merit. Several strong signals across a
student's answers is a serious case: the feedback says so plainly, without
insult, the marks stay on the merit, and the case goes to Niccolò with the
evidence. Wrong numbers are the evidence; style alone never is. The mock of
23 Oct 2026 had one such case.

**Intermediates draw from question banks, mocks do not.** Every student gets a
different paper of the same shape: the test is a list of *question pools*
(Ultra's random blocks), one per line of the Mix row above, each drawing from
the banks' questions of that type and difficulty, across topics. The mock is a
fixed list (`bb_test_fill`); an intermediate, the first and the second, is
built with `bb_test_pools(course, test_id, pool_path, groups, points=2,
exclude_manifests=[mock, practice, not-on-lab-machines, not-taught], bank_prefix="M1 · ")`
after `bb_ultra_connect`; `bb_assessment_questions` reads the pools back. The
MCP writes questions and pools through the Ultra interface's own API, with the
lecturer's signed-in browser session (a Chrome started with
`--remote-debugging-port=9223`); the pool request was read from the
interface's bundle on 26 Oct 2026 (MCP README). The session lasts 3 hours:
when a tool fails with a 401, sign in again in that Chrome and reconnect.

Module 1's banks, `M1 · <topic>`, one per pool topic, hold **120 usable
questions at 2 points, 30% easy, 50% medium, 20% challenging** (26 Oct 2026,
from 65): 59 new ones, T201–T906 (deck in the id), written to the perimeter
above and verified in `private/pool-keys/deckN.R`, and D5. The practice
paper's 15 and the mock's 20 are not in them (the mock has its own bank);
the five churn/`car` questions were deleted. A pool should hold at least four
questions per question it draws.

**Every question stays inside what was taught, checked, not assumed.** On 28 Oct
2026 four independent reviewers checked the 120 bank questions page by page
against Arbia's decks (`~/Downloads/Big_Data_2026-lecture1…9.pdf`; 3 and 8 are
mostly images) and the lab deck up to section 3 (lines 1–498, its exercise
solutions and the cheat sheet): 3 needed concepts never taught, 14 more put
points on something untaught or contradicted a slide. All 17 are listed in
`private/not-taught.json` (a manifest for `exclude_manifests`) and replaced by
R201–R902, same type, difficulty and topic. The R a question may ask for is
what was shown: `t.test` (`mu`, `alternative`, `paired`, `var.equal`), `aov`,
`TukeyHSD`, `lm`, `summary`, `coef`, `exp`, `predict` (`interval`, `type`),
`poly` and squares built as `x2 <- x^2`, `glm`, `factor`, `table`, `mean`,
`boxplot`, the lab's cross-validation loop, `Surv`, `survfit`, `coxph`.
Never `sd`, `var`, `cor`, `tapply`, `I()`, `relevel`, `confint`,
`summary(coxph)`, nor the log-rank's meaning, extrapolation, overdispersion,
standardised effects or causation: a number they would give goes in the text.
Arbia's slides have errors a question must not depend on: deck 6 p.20 VIF =
R²/(1−R²) (questions state 1/(1−R²)), deck 6 p.14 adjusted R² (0.414 should be
0.597, which made the mock's question 1 key wrong), deck 7 pp.7–8 code the
dummy both ways, deck 9 p.35 reads the sex effect backwards, deck 5 p.31
"known" for "unknown".

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

**The rulebook for a Module 2 deck, its drills and its clips is the project
skill `.claude/skills/sbd-lectures/`** (shape, drills, healthcare examples, clip
rules and failure catalogue, the checks before a lecture, publishing). A rule
learnt in a session goes there and in the matching line below.

**Module 2 is twelve decks, `lectures/10-*.qmd` to `21-*.qmd`, one per row of
the schedule**, all in this format; Module 1 (Prof. Arbia) is PDFs in `slides/`.
Start a new deck from `10-opening.qmd`. Every deck follows one shape, and a
deck that skips a step should have a reason: Objectives → *Why a manager cares*
→ sections (intuition, method, a worked example by hand, In R), **a drill
where a section's explanation ends** → an *Attention* callout for the trap → one
`.statement` slide → *Before the lab* → Reading (ISLR chapter, Provost & Fawcett
chapter, package reference). Section slides carry `[Section n]{.section-kicker}`.

A **drill** is the class working, not listening, and it comes once the
explanation it tests is finished, never forced into the middle of one: a section
without a natural exercise has none. `## [Drill n]{.drill-kicker} Title` (a gold
tag, styled by the theme), a subtitle *in pairs · n minutes*, an output table to
read or a profile to interpret, and a question that ends in a decision and the
sentence that defends it. **No pen-and-paper arithmetic**: running Lloyd by hand
on nine points and squaring distances were tried in lecture 11 and cut, the
worked example and its clip already do that job. The next slide is
`[Drill n · answer]`. Ten minutes each, and the *Today* table counts them. Every
number on an answer slide is computed in R first. The students graduate in
healthcare management (HEMA): where a drill can be about patients, hospitals or
a health district rather than shop customers, it is (lecture 11's Drill 2). Code blocks are display-only (`{.r}`),
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

**Clips: `animations/scenes.py` and `animations/scenes_NN.py`.** manim scenes on the course navy, formulas in
`MathTex`, words in Libre Franklin via `manimpango.register_font`. `make clips-preview`
(`-ql`) to check frames, `make clips` (`-qm`, then an ffmpeg `+faststart` remux into
`lectures/media/`) for the deck; embed with `{{< video media/Name.mp4 width="880" height="495" >}}`:
that leaves two lines of caption under it clear of the footer, 1000×562 only one.
The theme lifts reveal's 95% cap on `<video>`, which inside the player left a
black band right and below.
Every clip is spoken over, and that sets the length. **A clip runs 40 to 90
seconds.** Under 30 it is a gif: it shows the finished object and is over before
a sentence about it has been said. The first five clips of lecture 18 were 7 to
12 seconds and were rewritten for exactly this reason. Length comes from
*content*, not from padding: the count of misclassified points updating as a
line rotates, each gradient-descent step written out with its own numbers, every
squared distance in a by-hand example. If a clip needs stretching to reach 40
seconds it is missing a step that should be on screen.

New scenes set `WAIT_SCALE`/`PLAY_SCALE` to 1.0 and time their own waits; the
two scales exist only to stretch the older ones. Captions go through
`self.caption(...)`: one slot per clip, the old caption leaves before the new
one arrives, and one that would leave the frame stops the render. Lecture 11's
first clips put each caption in with `FadeIn` and never took the last one out,
so they piled up on top of each other. `label()` sets text at four times the
size and scales it down: below about 26 pt Pango hinted Libre Franklin's spaces
to nothing ("start:three", "whichisw"). `make clips-preview` then
`ffprobe` the result is how you check a duration — read the number, do not guess
from the code.

`scenes.py` holds the helpers (`Stage`, `caption`, `label`, palette), lecture 11
and the Module 1 lab; lectures 12, 14, 18 and 19 have a file each
(`scenes_12.py`, `scenes_14.py`, `scenes_18a.py`, `scenes_18b.py`, `scenes_19.py`)
that starts `from scenes import *`, so two lectures' helpers never collide. The
Makefile has one group per file (`SCENES_scenes_12 := …`, listed in `CLIP_FILES`);
a new lecture's clips get a new file and a new group. The AND-gate scenes do their
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
