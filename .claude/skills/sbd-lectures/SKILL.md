---
name: sbd-lectures
description: "Rules and checks for Niccolò's Module 2 of Statistics & Big Data (HEMA, Università Cattolica, repo sbd_26_27): writing, fixing or reviewing a lecture deck in lectures/ (revealjs), adding in-class drills, making or repairing manim clips in animations/scenes*.py, healthcare examples, checking slides before a lecture, and publishing with make deploy. Use it whenever the request touches a Module 2 lecture, slide, drill, clip, animation, practice set or the course site, even when the user only says 'la lezione di domani', 'le slide', 'la clip', 'il drill', 'pubblica' or pastes text copied from a deck."
---

# Statistics & Big Data — Module 2 lectures

Niccolò Salvini teaches Module 2 (lectures 10–21, 2 Nov → 11 Dec) of *Statistics
and Big Data*, HEMA specialist degree, Università Cattolica del Sacro Cuore, Rome.
Site: <https://sbd-26-27.netlify.app>, repo `NiccoloSalvini/sbd_26_27`. The repo's
`CLAUDE.md` holds the course facts (calendar, exams, Blackboard); this skill holds
how a lecture is built, checked and published. Materials are in English; talk to
Niccolò in Italian.

**Who is in the room.** The students graduate in **healthcare management**. They
are not data scientists and they are not shop owners. A method lands when they
see it on patients, wards, a health district, a hospital budget, so every lecture
carries healthcare examples next to the business ones (retail, CRM), and the drill
that applies the method is about patients whenever it can be. *Why a manager
cares* names a health-system manager next to the commercial one.

## The shape of a deck

`lectures/NN-topic.qmd`, revealjs with `lectures/cattolica.scss`; start from
`10-opening.qmd`. One deck per row of the schedule in `index.qmd`. Niccolò likes
this shape because it is reproducible, so keep it; a deck that skips a step should
have a reason:

Objectives → *Why a manager cares* → sections, each with intuition, method, a
worked example by hand, In R → **a drill where a section's explanation ends** →
an *Attention* callout for the trap → one `.statement` slide → *Before the lab* →
*Practice: Set n* → Reading (ISLR chapter, Provost & Fawcett chapter, package
reference).

- A lecture file sets title, subtitle (`Lecture n · room`), author, ISO `date`, and
  content, and nothing visual: colours and fonts are the theme's job.
- Section slides: `## [Section n]{.section-kicker} Title {.section-slide background-color="#002f57"}`.
  One-line slide: `## Text {.statement}`.
- Code blocks are display-only (`{.r}`), never executed at render: the site builds
  without R. Every number a slide prints is computed in R first, in a scratch
  script, and the slide says it the way R prints it.
- The *Today* table adds up to the slot (2 h on Mondays, 3 h on Tue/Fri, a 15'
  break in a 3 h slot) and counts the drill minutes.
- Math is KaTeX. Callouts: `callout-note`, `callout-important` titled
  *Attention*, `callout-tip`.

## Drills

The class works between two parts of the explanation, it does not only listen.
What Niccolò settled on lecture 11 (2 Nov 2026):

- **A drill comes when the explanation it tests is finished**, at the end of a
  section, never wedged into the middle of one. A section without a natural
  exercise has none: do not force one in to fill the pattern.
- **No pen-and-paper arithmetic.** Running Lloyd by hand on nine points and
  squaring distances were written for lecture 11 and cut: the worked example and
  its clip already do that, and in class it is dead time. A drill is an output
  table to read, a profile to interpret, a choice to make and defend.
- It ends in a **decision and the sentence that defends it**, the thing the exam
  asks for, not only in a number. One number to compute from a table is fine
  when it carries the argument (lecture 11: 6% of patients make 47% of the spending).
- Format: `## [Drill n]{.drill-kicker} Title` (gold tag from the theme), subtitle
  `In pairs · 10 minutes · <what the table is>`, the table, two or three numbered
  questions. The next slide is `## [Drill n · answer]{.drill-kicker} Title` with the
  answer and, if there is arithmetic, the arithmetic in one muted line.
- About patients whenever the method allows it; the invented tables say what they
  are ("a health district, k = 4 on scaled columns, means per patient, per year").
- If *Before the lab* refers to a drill, its number must follow renumbering.
- A table whose first column is a short label (A, B, C) needs
  `: {tbl-colwidths="[6,47,47]"}`, or pandoc gives the labels a third of the width
  and every other cell wraps.

## Check the claims, not only the numbers

Reviewing lectures 12–21 (2 Nov 2026) found statements that the data contradict,
in decks that had looked finished: a tree said never to split on a variable it
splits on, a "hundred times the median" that was 16, loadings that were not unit
length, a clip whose single-linkage chain was drawn along points sorted by x, a
practice question whose premise was false on the map, `xgboost` code that stops
with an error on the current version. Before calling a deck ready, run every
claim it makes about a dataset, not only the drill numbers.

- `materials/churn.csv` is generated by adding pushes to the log-odds
  (`gen-data.R`): **logistic regression is the right model by construction**, and
  on it a network ties logistic and boosting does not win. Never write that
  boosting wins on this lab; the honest result is the lesson.
- The Python lab (lecture 19) takes its numbers from the deck's own Python code,
  run; the R decks from R. The `animations` venv has no scikit-learn, so lab
  numbers inside a clip are constants with their source named in the docstring.

## Clips (manim)

Read `references/clips.md` before writing or fixing a scene; it has the render
commands, the helpers and the failure catalogue. The rules a clip is judged by:

- **40 to 90 seconds**, spoken over. Length comes from content on screen (each
  step written with its own number), never from padding. Read the duration with
  `ffprobe`, do not estimate it from the code.
- **One caption slot**, captions through `self.caption(...)`: the old one leaves
  before the new one arrives. Two texts on top of each other is the defect
  Niccolò notices first ("le scritte si sovrappongono").
- Everything inside the frame; a right-hand panel stays right of the plot.
- **Every object on screen has a visible job.** A centroid that never moves, a
  label nobody refers to, a colour that means nothing: viewers ask "what is that
  star doing?". Simulate the data and the algorithm in Python first and pick
  starts and seeds that show the point cleanly (no empty cluster, the intended
  number of groups recovered).
- Healthcare data where it fits (lecture 11's scale clip is patients by age and
  yearly cost of care).
- The slide's caption under the clip describes *this* clip, numbers included;
  change it when the clip changes.
- Embed with `{{< video media/Name.mp4 width="880" height="495" >}}`. Never add a
  query string (`Name.mp4?v=2`): Quarto then reads the path as a YouTube id and
  renders an empty YouTube iframe.

## Checking a deck before a lecture

Do this every time a deck changes, before saying it is ready:

1. `quarto render lectures/NN-topic.qmd`, then `preview_start {name: "site"}` (port
   8765, serves `_site`). A `file://` page renders unstyled.
2. Set the tab to 1280×720 and run `scripts/measure-slides.js` with the browser's
   javascript tool (to measure several decks in one call, load each in a
   1280×720 `iframe` and run the same loop on its `contentWindow.Reveal`). Every slide's content must end **above 680 px**: the footer
   starts at about 697, and a caption that reaches it is overprinted by
   "Statistics & Big Data · HEMA…". A clip at 880×495 leaves room for two
   caption lines; at 1000×562 only one.
3. Screenshot the slides you changed, and every drill and clip slide. Read the
   picture, not only the numbers: wrapping tables, a gold tag, a callout title.
4. For a changed clip, extract frames and look at them (`scripts/contact-sheet.sh`),
   at caption changes especially.
5. Reset the viewport to desktop when done.

**Cache.** The in-app browser keeps old mp4s from `localhost` (python's server
sends no cache headers): an old clip on screen after a re-render is usually the
cache. Prove what is served instead of trusting the picture: compare
`curl -sI <live url> | grep content-length` with `stat -f%z` of the local file,
or read `video.duration` in the page. Netlify serves `max-age=0, must-revalidate`,
so the live site is fresh for students.

**Netlify badge.** The free plan injects a "Powered by Netlify" badge at the
bottom of every live page, over the slide footer. It cannot be hidden on the
free tier; do not hide it with CSS. If it bothers Niccolò in class, the options
are his to choose: present from `make preview`, or a paid plan.

## Publishing

- `make deploy` = `quarto render` + `netlify deploy --prod`. There is no CI. Ask
  Niccolò before deploying ("Pubblico?") unless he said so in this request;
  run it in the background, it renders the whole site.
- After deploying, check the live page (`curl` the HTML for the new slide titles,
  content-length of changed media).
- Commit **by path**: `git add lectures/NN-topic.qmd lectures/media/X.mp4 …`.
  Never `git add -A`: `_site/` and iCloud folders make it hang for minutes.
  Messages say what changed and why, and end with the Claude co-author trailer.
  Don't push unless asked.
- New rules learnt in a session go into this skill (and the matching line of
  `CLAUDE.md`), so the next deck starts from them.

## Theme facts that look like mistakes and are not

`lectures/cattolica.scss`:
- Quarto's title slide is `<section id="title-slide">`; the theme styles
  `#title-slide` and sets `center-title-slide: false`.
- Quarto injects an inline `<style>` after the stylesheets that colours callouts
  with `!important` on `div.callout-x`; the theme matches those selectors exactly.
- reveal sets `display:block` inline on the current slide: flex layouts need
  `!important`.
- reveal caps every `<video>` at 95% of its box; inside the video.js player that
  left a black band right and below. The theme sets the player's video back to 100%.
- `.drill-kicker` is the gold tag of a drill title.

## Data

The lab datasets `materials/customers.csv`, `brands.csv`, `churn.csv` are
generated by `Rscript materials/gen-data.R` from fixed seeds and asserted against
each lab's expectations; change expectations there, never edit a CSV. Exam
questions use only data that ship with R (see `CLAUDE.md`, intermediate exams).
