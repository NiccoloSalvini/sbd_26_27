# Runs the course setup script the way a student runs it, then checks what it
# actually did. Exits non-zero on the first broken promise, so the container's
# exit status is the test result.
#
#   Rscript assert.R /path/to/setup.R          real install, the slow honest test
#   MOCK=1 Rscript assert.R /path/to/setup.R   logic only: no downloads
#
# SCENARIO changes what is being asserted, because a locked-down machine and an
# offline one are supposed to behave differently, not merely to fail:
#
#   SCENARIO=normal   (default) the machine is fine
#   SCENARIO=locked   the system library is read-only — a personal one must appear
#   SCENARIO=offline  the repository is unreachable — say so in seconds, not minutes
args     <- commandArgs(trailingOnly = TRUE)
src      <- if (length(args)) args[[1]] else "https://sbd-26-27.netlify.app/materials/setup.R"
mock     <- nzchar(Sys.getenv("MOCK"))
scenario <- Sys.getenv("SCENARIO", "normal")

fail <- function(...) { cat("FAIL: ", sprintf(...), "\n", sep = ""); quit(status = 1) }
pass <- function(...) cat("  ok   ", sprintf(...), "\n", sep = "")

if (mock) {
  # stand in for the real installer: the search path finds this before utils::
  install.packages <- function(pkgs, ...) {
    cat("      [mock] would install:", paste(pkgs, collapse = ", "), "\n")
    invisible(NULL)
  }
}

cat("\n== running setup from:", src, " scenario:", scenario, "\n")
out <- character()
con <- textConnection("out", "w", local = TRUE)
started <- Sys.time()
sink(con, split = TRUE)
err <- tryCatch({ source(src); NULL }, error = function(e) e)
sink(); close(con)
elapsed <- as.numeric(difftime(Sys.time(), started, units = "secs"))

if (!is.null(err)) fail("the script raised an error: %s", conditionMessage(err))
pass("script ran to the end without an error")
txt <- paste(out, collapse = "\n")

# -- offline: the whole point is that it gives up quickly and says why ---------
if (scenario == "offline") {
  if (!grepl("Cannot reach", txt)) fail("no message about the unreachable repository")
  pass("says the repository cannot be reached")
  if (!grepl("proxy", txt, ignore.case = TRUE)) fail("did not name the likely cause")
  pass("names a proxy or firewall as the likely cause")
  if (!grepl("posit.cloud", txt, fixed = TRUE)) fail("did not offer the browser fallback")
  pass("offers Posit Cloud instead")
  if (elapsed > 120) fail("took %.0f s to notice it has no network", elapsed)
  pass("gave up in %.0f s rather than after a long install", elapsed)
  cat("\nPASS\n"); quit(status = 0)
}

# -- locked: a read-only system library must not stop it ----------------------
if (scenario == "locked") {
  if (!grepl("read-only", txt)) fail("did not notice the library is read-only")
  pass("noticed the read-only system library")
  if (!grepl("personal one instead", txt)) fail("did not fall back to a personal library")
  pass("switched to a personal library")
  personal <- .libPaths()[1]
  if (file.access(personal, 2) != 0) fail("the library it chose is not writable either")
  pass("the chosen library is writable")
}

# -- the R version must be reported, and an old one warned about --------------
v <- getRversion()
if (v < "4.6.0") {
  if (!grepl("targets 4.6 or newer", txt)) fail("R %s but no version warning shown", v)
  pass("old R (%s) correctly warned about", v)
} else {
  if (!grepl(sprintf("R %s", v), txt, fixed = TRUE)) fail("did not report R %s", v)
  pass("reports the running R version (%s)", v)
}

# -- a configured binary mirror must be used, not ignored ----------------------
if (!mock) {
  conf <- getOption("repos")[["CRAN"]]
  if (!is.null(conf) && nzchar(conf) && !identical(unname(conf), "@CRAN@") &&
      !grepl("cloud.r-project.org", conf, fixed = TRUE)) {
    if (grepl("compilation|source", txt, ignore.case = TRUE) && grepl("\\bmaking\\b", txt))
      fail("compiled from source although %s is configured", conf)
    pass("used the configured repository (%s)", conf)
  }
}

# -- the project folder is the part a student will look for -------------------
hits <- regmatches(txt, regexpr("(Created|Project folder already there: ?)[^\n]*", txt))
root <- sub(".*?((/|[A-Za-z]:\\\\)[^ ]*sbd_26_27).*", "\\1", hits)
if (!length(hits) || !dir.exists(root)) fail("no project folder reported or created")
for (d in file.path(root, c("data", "scripts", "output")))
  if (!dir.exists(d)) fail("missing folder: %s", d)
pass("project folder and data/ scripts/ output/ exist at %s", root)
if (!file.exists(file.path(root, "sbd_26_27.Rproj"))) fail("no .Rproj written")
pass(".Rproj written")

# -- running it twice must be harmless, as the page promises ------------------
err2 <- tryCatch({ capture.output(source(src)); NULL }, error = function(e) e)
if (!is.null(err2)) fail("second run failed: %s", conditionMessage(err2))
pass("second run is harmless")

# -- in a real run, the packages must actually be usable ----------------------
if (!mock) {
  need <- c("tidyverse", "glmnet", "here", "ranger", "xgboost", "rpart", "cluster",
            "FactoMineR", "factoextra", "iml", "ISLR2", "forecast", "fable")
  miss <- need[!vapply(need, requireNamespace, logical(1), quietly = TRUE)]
  if (length(miss)) fail("packages missing after setup: %s", paste(miss, collapse = ", "))
  pass("every package the course uses loads")
  tryCatch(glmnet::glmnet(as.matrix(mtcars[, -1]), mtcars$mpg),
           error = function(e) fail("glmnet failed: %s", conditionMessage(e)))
  pass("a model fits on this machine")
  if (!grepl("Done\\.", txt)) fail("the script did not report success")
  pass("script reported Done")
}

cat("\nPASS\n")
