# Statistics & Big Data 26/27 — one-shot setup
#
# Paste this single line into the RStudio *Console* (the pane at the bottom
# left) and press Enter:
#
#   source("https://sbd-26-27.netlify.app/materials/setup.R")
#
# It checks your R version and your machine, fixes what it can, installs only
# the packages you are missing, makes a project folder for the course, and tells
# you in plain words what it did. Running it twice is harmless. Nothing here
# needs a terminal.

local({

  ok   <- function(...) cat("  ✓ ", sprintf(...), "\n", sep = "")
  warn <- function(...) cat("  !  ", sprintf(...), "\n", sep = "")
  head <- function(...) cat("\n", sprintf(...), "\n", sep = "")
  SITE <- "https://sbd-26-27.netlify.app/setup.html"

  stop_here <- function(...) {
    for (line in c(...)) warn("%s", line)
    warn("")
    warn("Do not spend the evening on this. Use Posit Cloud instead — it is")
    warn("RStudio in a browser tab, it installs nothing, and the same line")
    warn("works there: https://posit.cloud")
    warn("Then bring this machine to the lab session and we fix it together.")
    invisible(FALSE)
  }

  # -- 1. R itself ------------------------------------------------------------
  head("1/5  Checking R")
  v <- getRversion()
  if (v < "4.6.0") {
    warn("You are on R %s. The course targets 4.6 or newer.", v)
    warn("Everything below will still run, but reinstall R before the exam:")
    warn("%s#install-r", SITE)
  } else {
    ok("R %s", v)
  }
  if (!nzchar(Sys.getenv("RSTUDIO"))) {
    warn("This does not look like RStudio. It works anyway, but the course uses RStudio.")
  } else {
    ok("Running inside RStudio")
  }

  # Packages built under an older R sit in the library and fail to load with a
  # message that blames the package. This is the "it worked last year" case.
  stale <- tryCatch({
    built <- installed.packages(fields = "Built")[, "Built"]
    short <- function(x) paste(strsplit(x, ".", fixed = TRUE)[[1]][1:2], collapse = ".")
    names(built)[vapply(built, function(b) !is.na(b) && short(b) != short(as.character(v)),
                        logical(1))]
  }, error = function(e) character(0))
  if (length(stale) > 3) {
    warn("%d packages were built for a different version of R.", length(stale))
    warn("If one of them refuses to load later, reinstall it: install.packages(\"name\")")
  }

  # -- 2. This machine --------------------------------------------------------
  # Everything here is a failure people actually hit. Detect it now, in seconds,
  # rather than twenty minutes into an install that was never going to work.
  head("2/5  Checking this machine")

  # (a) a library R may write to. On a locked-down laptop the system library
  #     belongs to an administrator; R offers a personal one interactively, but
  #     source() is not interactive, so it would simply fail.
  lib <- .libPaths()[1]
  if (file.access(lib, 2) != 0) {
    personal <- Sys.getenv("R_LIBS_USER")
    if (!nzchar(personal) || identical(personal, "NULL"))
      personal <- file.path(path.expand("~"), "R", R.version$platform,
                            paste(R.version$major, strsplit(R.version$minor, ".", TRUE)[[1]][1], sep = "."))
    personal <- path.expand(personal)
    dir.create(personal, recursive = TRUE, showWarnings = FALSE)
    if (dir.exists(personal) && file.access(personal, 2) == 0) {
      .libPaths(c(personal, .libPaths()))
      ok("System library is read-only — using your personal one instead")
      ok("%s", personal)
    } else {
      return(stop_here("No library this account may write to, and none could be created.",
                       "That is a locked-down machine, not something you did."))
    }
  } else {
    ok("Library is writable: %s", lib)
  }

  # (b) the repository, and whether this network will let us reach it
  repo <- getOption("repos")[["CRAN"]]
  if (is.null(repo) || !nzchar(repo) || identical(unname(repo), "@CRAN@"))
    repo <- "https://cloud.r-project.org"
  if (identical(Sys.info()[["sysname"]], "Linux") &&
      !grepl("p3m.dev|packagemanager.posit.co", repo)) {
    warn("Linux with a source-only mirror (%s).", repo)
    warn("Packages will be compiled: slow, and it stops on a missing -dev library.")
    warn("Faster: use Posit Package Manager, see https://p3m.dev/client/#/repos/cran/setup")
  }
  reachable <- tryCatch({
    h <- suppressWarnings(curlGetHeaders(paste0(repo, "/src/contrib/PACKAGES"), timeout = 20))
    any(grepl("^HTTP/.* (200|30[0-9])", h))
  }, error = function(e) FALSE)
  if (!reachable) {
    return(stop_here(
      sprintf("Cannot reach %s from this network.", repo),
      "Usually a university or company proxy, or a firewall that blocks R.",
      "It is not your R installation: a browser on the same machine may work fine."))
  }
  ok("Package repository reachable")

  # (c) a home folder that is synced to the cloud. OneDrive and iCloud lock
  #     files mid-write and evict them later; both look like corruption.
  home <- path.expand("~")
  synced <- grepl("OneDrive|Dropbox|iCloud|Google Drive", home, ignore.case = TRUE)
  if (synced) {
    warn("Your home folder is inside a synced drive:")
    warn("%s", home)
    warn("Sync locks files while R is writing them. The course folder will go")
    warn("somewhere local instead, and you should keep your scripts there too.")
  }

  # (d) a path R cannot spell. An accented user name is common here and breaks
  #     installs on Windows with an error that names neither.
  if (grepl("[^ -~]", home)) {
    warn("Your home folder path contains non-ASCII characters:")
    warn("%s", home)
    warn("On Windows this can break package installs. If one fails with a path")
    warn("error, say so at the lab session — the fix is a one-line setting.")
  }

  # (e) never compile. Without Rtools (Windows) or Xcode (macOS) a source build
  #     fails at the end of a long download for no reason a student can act on.
  options(install.packages.compile.from.source = "never")
  if (identical(Sys.info()[["sysname"]], "Darwin")) options(pkgType = "binary")

  # -- 3. Packages ------------------------------------------------------------
  head("3/5  Course packages")
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
    consecutive <- 0
    for (p in missing) {
      # Two attempts. An antivirus scanning a freshly written DLL, or a mirror
      # dropping one connection, fails once and works on the retry.
      for (attempt in 1:2) {
        tryCatch(suppressWarnings(install.packages(p, quiet = TRUE, repos = repo)),
                 error = function(e) NULL)
        if (p %in% rownames(installed.packages())) break
        if (attempt == 1 && consecutive < 3) Sys.sleep(2)
      }
      consecutive <- if (p %in% rownames(installed.packages())) 0 else consecutive + 1
      # Three in a row means something systematic — a proxy that allows the
      # index but not the files, a full disk, an antivirus eating every
      # download. Twenty more minutes of it will not help.
      if (consecutive >= 3) {
        warn("Three packages in a row failed to install. Something on this")
        warn("machine or network is blocking downloads, and trying the rest")
        warn("will take twenty minutes to tell you the same thing.")
        break
      }
    }
    still <- setdiff(pkgs, rownames(installed.packages()))
    if (length(still) == 0) {
      ok("All %d packages installed", length(pkgs))
    } else {
      warn("Could not install: %s", paste(still, collapse = ", "))
      warn("Everything else is in place, so the rest of the course still works.")
      warn("Bring this list to the lab session, or run the line again first —")
      warn("a second run often picks up what a dropped connection missed.")
    }
  }

  # -- 4. Project folder --------------------------------------------------------
  head("4/5  Project folder")
  # Keep the course folder off a synced drive when we can: Documents is synced by
  # OneDrive on most Windows installs, the user profile root usually is not.
  base <- home
  if (synced) {
    candidate <- if (identical(Sys.info()[["sysname"]], "Windows"))
      Sys.getenv("USERPROFILE") else "~"
    candidate <- path.expand(candidate)
    if (nzchar(candidate) && dir.exists(candidate) &&
        !grepl("OneDrive|Dropbox|iCloud|Google Drive", candidate, ignore.case = TRUE))
      base <- candidate
  }
  root <- file.path(base, "sbd_26_27")
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

  # -- 5. Does it actually work? --------------------------------------------------
  head("5/5  Final check")
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
    warn("If it fails twice, bring it to the lab session: %s", SITE)
  }
})
