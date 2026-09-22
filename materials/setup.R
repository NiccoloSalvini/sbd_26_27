# Statistics & Big Data 26/27 — one-shot setup
#
# Paste this single line into the RStudio *Console* (the pane at the bottom
# left) and press Enter:
#
#   source("https://sbd-26-27.netlify.app/materials/setup.R")
#
# It checks your R version, installs only the packages you are missing, makes
# a project folder for the course, and tells you in plain words what it did.
# Running it twice is harmless. Nothing here needs a terminal.

local({

  ok   <- function(...) cat("  ✓ ", sprintf(...), "\n", sep = "")
  warn <- function(...) cat("  !  ", sprintf(...), "\n", sep = "")
  head <- function(...) cat("\n", sprintf(...), "\n", sep = "")

  # -- 1. R itself ------------------------------------------------------------
  head("1/4  Checking R")
  v <- getRversion()
  if (v < "4.6.0") {
    warn("You are on R %s. The course targets 4.6 or newer.", v)
    warn("Everything below will still run, but reinstall R before the exam:")
    warn("https://sbd-26-27.netlify.app/setup.html#install-r")
  } else {
    ok("R %s", v)
  }
  if (!nzchar(Sys.getenv("RSTUDIO"))) {
    warn("This does not look like RStudio. It works anyway, but the course uses RStudio.")
  } else {
    ok("Running inside RStudio")
  }

  # -- 2. Packages ------------------------------------------------------------
  head("2/4  Course packages")
  pkgs <- c(
    # data manipulation and graphics
    "tidyverse", "here", "skimr",
    # Module 1 — regression, regularisation, forecasting
    "glmnet", "survival", "fable", "feasts", "tsibble", "forecast",
    # Module 2 — unsupervised learning and machine learning
    "factoextra", "FactoMineR", "cluster", "rpart", "rpart.plot",
    "ranger", "xgboost", "nnet", "iml",
    # datasets from the textbook
    "ISLR2"
  )
  have    <- rownames(installed.packages())
  missing <- setdiff(pkgs, have)

  if (length(missing) == 0) {
    ok("All %d packages already installed — nothing to download", length(pkgs))
  } else {
    cat(sprintf("  Installing %d of %d packages (%s). This can take a few minutes.\n",
                length(missing), length(pkgs), paste(missing, collapse = ", ")))
    cat("  Red text scrolling past is normal. Wait for the summary below.\n\n")
    options(install.packages.compile.from.source = "never")
    # Use the repository this machine is already set up for. On Linux that is
    # often a binary mirror, and taking it turns a twenty-minute compile — which
    # then fails on a missing system library — into a one-minute download.
    # Windows and macOS get binaries from the cloud mirror either way.
    repo <- getOption("repos")[["CRAN"]]
    if (is.null(repo) || !nzchar(repo) || identical(unname(repo), "@CRAN@"))
      repo <- "https://cloud.r-project.org"
    # On Linux a plain CRAN mirror ships sources only: every package is compiled,
    # which takes an hour and stops on the first missing system library. Say so
    # before it happens rather than after.
    if (identical(Sys.info()[["sysname"]], "Linux") &&
        !grepl("p3m.dev|packagemanager.posit.co", repo)) {
      warn("Linux with a source-only mirror (%s).", repo)
      warn("Packages will be compiled: slow, and it stops on a missing -dev library.")
      warn("Faster: use Posit Package Manager for your distribution, see")
      warn("https://p3m.dev/client/#/repos/cran/setup")
    }
    for (p in missing) {
      tryCatch(
        suppressWarnings(install.packages(p, quiet = TRUE, repos = repo)),
        error = function(e) NULL
      )
    }
    still <- setdiff(pkgs, rownames(installed.packages()))
    if (length(still) == 0) {
      ok("All %d packages installed", length(pkgs))
    } else {
      warn("Could not install: %s", paste(still, collapse = ", "))
      warn("Run the script again once. If it still fails, bring this exact line")
      warn("to office hours — do not spend an evening on it.")
    }
  }

  # -- 3. Project folder --------------------------------------------------------
  head("3/4  Project folder")
  root <- file.path(path.expand("~"), "sbd_26_27")
  made <- FALSE
  for (d in c(root, file.path(root, c("data", "scripts", "output")))) {
    if (!dir.exists(d)) { dir.create(d, recursive = TRUE); made <- TRUE }
  }
  rproj <- file.path(root, "sbd_26_27.Rproj")
  if (!file.exists(rproj)) {
    writeLines(c("Version: 1.0", "", "RestoreWorkspace: No", "SaveWorkspace: No",
                 "AlwaysSaveHistory: Default", "", "EnableCodeIndexing: Yes",
                 "UseSpacesForTab: Yes", "NumSpacesForTab: 2", "Encoding: UTF-8",
                 "", "RnwWeave: Sweave", "LaTeX: pdfLaTeX"), rproj)
    made <- TRUE
  }
  if (made) ok("Created %s with data/, scripts/, output/", root)
  else      ok("Project folder already there: %s", root)

  # -- 4. Does it actually work? --------------------------------------------------
  head("4/4  Final check")
  test <- tryCatch({
    suppressPackageStartupMessages({ library(tidyverse); library(glmnet); library(here) })
    fit <- glmnet(as.matrix(mtcars[, -1]), mtcars$mpg)
    TRUE
  }, error = function(e) e)
  if (isTRUE(test)) {
    ok("tidyverse, glmnet and here all load and run")
    head("Done. Next time you sit down to work: File > Open Project > %s", rproj)
    cat("  That opens RStudio inside the course folder, so file paths just work.\n\n")
  } else {
    warn("Packages installed but a test model failed: %s", conditionMessage(test))
    warn("Restart R (Session > Restart R) and run the line again.")
  }
})
