# CLAUDE.md — Statistics & Big Data course site

Course website for *Statistics and Big Data (Business Statistics and Artificial
Intelligence)*, HEMA specialistic degree, Università Cattolica del Sacro Cuore,
Rome. Proff. Giuseppe Arbia (Module 1) and Niccolò Salvini (Module 2).

Live: <https://sbd-26-27.netlify.app> · Repo: `NiccoloSalvini/sbd_26_27`

## Commands

```bash
make preview   # quarto preview, live reload while editing
make build     # regenerate the QR, then quarto render -> _site/
make deploy    # build, then netlify deploy --prod
make qr        # QR only — run after changing booking-url
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

`homework.qmd` works the same way, against the `homework/` folder.

## Files

| Path | What |
|---|---|
| `index.qmd` | home = schedule, both modules, instructors |
| `syllabus.qmd` | full syllabus, assessment rules |
| `setup.qmd` | R / RStudio / Python install guide, shown in class |
| `homework.qmd` | optional practice sets — **not graded**, the syllabus says no assignments are required |
| `resources.qmd` | textbooks, deep-dive reading |
| `office-hours.qmd` | booking link + QR code |
| `_variables.yml` | links used on several pages |
| `styles.scss` | theme: Cattolica navy `#002f57`, Libre Franklin, schedule table styling |
| `.mcp.json` | Blackboard MCP server (see below) |

## Shared links

Anything appearing on more than one page lives in `_variables.yml` and is used as
`{{< var booking-url >}}`:

| Variable | Note |
|---|---|
| `booking-url` | Google appointment page — **also the QR target**, run `make qr` after changing it |
| `blackboard-url` | Blackboard course page |
| `drive-url` | shared drive, if used |
| `repo-url` | this repository |

The QR and the booking link are the same fact in two formats. Keeping them in two
places means one eventually points at the old link while still *looking* correct —
an error nobody can see. One source, regenerated.

## Conventions

- **Site language is English.** The syllabus and the degree are in English.
- **Screenshots: photograph what is stable, write commands for what changes.**
  Vendor pages (CRAN, posit.co) get redesigned without warning and a stale
  screenshot misleads silently, so installing goes through `rig` and prose. The
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

It needs a bearer token. **The browser session cookie does not authenticate the
API** — both `/learn/api/public/v1/*` and the internal `/learn/api/v1/*` return
`401` for a logged-in browser. Getting a token takes an application registered at
developer.anthology.com *and* a Blackboard administrator adding that Application
ID under Admin → REST API Integrations. The admin step is the bottleneck.

Writes are off by default; grade writes have a second switch of their own.

## Starting the next academic year

Copy the repo to `sbd_27_28` and work through:

1. `_quarto.yml` — navbar title year, footer, description
2. `index.qmd` — the whole schedule: dates, rooms, topics, module date ranges,
   and the facts strip at the top
3. `syllabus.qmd` — new syllabus; check whether the assessment rules changed
   (they have been stable: two optional intermediates, cannot be rejected,
   50/50 weighting)
4. `homework.qmd` — practice set dates
5. `_variables.yml` — new Blackboard course URL, new booking link, then `make qr`
6. `setup.qmd` — bump the target R version, check `rig` install commands still hold
7. New Netlify site: `netlify sites:create --name sbd-27-28 --account-slug niccolo-salvini`, then `make deploy`

**Do not carry over old exam simulations.** The 25/26 mocks were left behind on
purpose in 26/27 — the syllabus changed enough that old papers confuse more than
they help. Same judgement applies each year.
