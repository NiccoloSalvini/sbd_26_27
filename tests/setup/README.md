# Does the Setup page tell the truth?

The Setup page makes a promise: install two things, paste one line, and you are
ready. This folder is how that promise gets checked instead of assumed.

## What runs where, and what it proves

| | Linux | macOS | Windows |
|---|---|---|---|
| Docker, locally (`run.sh`) | yes, three R versions | **no** | **no** |
| GitHub Actions (`.github/workflows/setup.yml`) | yes | yes, Apple silicon | yes, incl. an old R |

Docker on a Mac runs Linux containers only. Windows containers need a Windows
host, and macOS cannot legally be containerised at all. So Docker is the fast
local loop, and CI is the part that actually covers the machines students own —
which, in this course, are mostly Windows laptops and M-series MacBooks.

## The fast loop

```bash
tests/setup/run.sh            # three R versions, no downloads, ~1 minute
tests/setup/run.sh --full     # really install all 20 packages on a clean R 4.6
tests/setup/run.sh --url      # test the published script, not the local file
```

The quick mode replaces `install.packages` with a stub, so it checks the parts
that break most often — version detection, the folder it creates, the message an
old R gets, and that running it twice is harmless — without waiting for CRAN.
`--full` is the honest one: a clean machine, every package, a model fitted at
the end.

`--url` matters more than it looks. The script students run is the one on
Netlify, not the one in this repo, and those differ every time the site has not
been deployed. If `--url` passes and the local file has changed, deploy.

## What `assert.R` refuses to accept

It is not a smoke test that shrugs at a warning. It fails if the script errors,
if the project folder or `.Rproj` is missing, if a second run is not harmless,
if an old R gets no warning, or — in a full run — if any course package is
missing afterwards or `glmnet` cannot fit `mtcars`.

## What none of this covers

A university laptop with an administrator lock, a corporate proxy intercepting
CRAN, an antivirus quarantining a compiled DLL, or a disk with no space. Those
are the real support tickets, and no container reproduces them. The Setup page
answers them with Posit Cloud, which is the right answer: the browser has no
administrator.
