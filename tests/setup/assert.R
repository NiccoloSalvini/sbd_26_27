# Runs the course setup script the way a student runs it, then checks what it
# actually did. Exits non-zero on the first broken promise, so the container's
# exit status is the test result.
#
#   Rscript assert.R /path/to/setup.R        real install, the slow honest test
#   MOCK=1 Rscript assert.R /path/to/setup.R logic only: no downloads
args <- commandArgs(trailingOnly = TRUE)
src  <- if (length(args)) args[[1]] else "https://sbd-26-27.netlify.app/materials/setup.R"
mock <- nzchar(Sys.getenv("MOCK"))

fail <- function(...) { cat("FAIL: ", sprintf(...), "\n", sep = ""); quit(status = 1) }
pass <- function(...) cat("  ok   ", sprintf(...), "\n", sep = "")

if (mock) {
  # stand in for the real installer: the search path finds this before utils::
  install.packages <- function(pkgs, ...) {
    cat("      [mock] would install:", paste(pkgs, collapse = ", "), "\n")
    invisible(NULL)
  }
}

cat("\n== running setup from:", src, "\n")
out <- character()
con <- textConnection("out", "w", local = TRUE)
sink(con, split = TRUE)
err <- tryCatch({ source(src); NULL }, error = function(e) e)
sink(); close(con)

if (!is.null(err)) fail("the script raised an error: %s", conditionMessage(err))
pass("script ran to the end without an error")

txt <- paste(out, collapse = "\n")

# 1 — it must say something about the R version, and the right something
v <- getRversion()
if (v < "4.6.0") {
  if (!grepl("targets 4.6 or newer", txt)) fail("R %s but no version warning shown", v)
  pass("old R (%s) correctly warned about", v)
} else {
  if (!grepl(sprintf("R %s", v), txt, fixed = TRUE)) fail("did not report R %s", v)
  pass("reports the running R version (%s)", v)
}

# 2 — the project folder is the part a student will look for
root <- file.path(path.expand("~"), "sbd_26_27")
for (d in c(root, file.path(root, c("data", "scripts", "output"))))
  if (!dir.exists(d)) fail("missing folder: %s", d)
pass("project folder and data/ scripts/ output/ exist")
if (!file.exists(file.path(root, "sbd_26_27.Rproj"))) fail("no .Rproj written")
pass(".Rproj written")

# 3 — running it twice must be harmless, as the page promises
err2 <- tryCatch({ capture.output(source(src)); NULL }, error = function(e) e)
if (!is.null(err2)) fail("second run failed: %s", conditionMessage(err2))
pass("second run is harmless")

# 4 — in a real run, the packages must actually be usable
if (!mock) {
  need <- c("tidyverse", "glmnet", "here", "ranger", "xgboost", "rpart", "cluster",
            "FactoMineR", "factoextra", "iml", "ISLR2", "forecast", "fable")
  miss <- need[!vapply(need, requireNamespace, logical(1), quietly = TRUE)]
  if (length(miss)) fail("packages missing after setup: %s", paste(miss, collapse = ", "))
  pass("every package the course uses loads")
  fit <- tryCatch(glmnet::glmnet(as.matrix(mtcars[, -1]), mtcars$mpg),
                  error = function(e) fail("glmnet failed: %s", conditionMessage(e)))
  pass("a model fits on this machine")
  if (!grepl("Done\\.", txt)) fail("the script did not report success")
  pass("script reported Done")
}

cat("\nPASS\n")
