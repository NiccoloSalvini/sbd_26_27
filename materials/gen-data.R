# Synthetic datasets for the Module 2 labs. Seeded, so `Rscript materials/gen-data.R`
# reproduces the files byte for byte. Each generator is followed by the lab's own
# pipeline as a check: a dataset only ships if the lab's expected answer comes out.
#
#   customers.csv  — L13, clustering: four behavioural segments, RFM-style
#   brands.csv     — L15, correspondence analysis: respondents × brand × attribute
#   churn.csv      — L17, forests and boosting: telecom churn, ~27% positive

suppressPackageStartupMessages({
  library(dplyr); library(readr); library(cluster); library(FactoMineR); library(ranger)
})
ok <- function(cond, msg) { cat(if (isTRUE(cond)) "  ok   " else "  FAIL ", msg, "\n"); if (!isTRUE(cond)) stop(msg) }

# ---------------------------------------------------------------- customers ----
set.seed(2627)
n <- 6000
seg <- sample(1:4, n, replace = TRUE, prob = c(.19, .22, .18, .41))
z <- function() rnorm(n)
cust <- tibble(
  id        = sprintf("C%05d", 1:n),
  recency   = round(pmax(0, c(220, 25, 40, 30)[seg] + z() * c(60, 12, 20, 15)[seg])),
  frequency = round(pmax(1, c(3, 14, 3, 11)[seg]     + z() * c(1.5, 4, 1.5, 3)[seg])),
  monetary  = round(exp(rnorm(n, c(7.4, 5.6, 5.2, 6.6)[seg], c(.55, .45, .5, .4)[seg]))),
  tenure    = round(pmax(1, c(48, 30, 4, 60)[seg]    + z() * c(15, 12, 2, 18)[seg])),
  returns   = rpois(n, c(0.4, 1.8, 0.3, 0.6)[seg]),
  channel_online = round(pmin(1, pmax(0, c(.35, .92, .55, .10)[seg] + rnorm(n, 0, .12))), 2)
) |> slice_sample(prop = 1)
write_csv(cust, "materials/customers.csv")
cat("customers.csv:", nrow(cust), "righe\n")

feat <- cust |> select(-id) |> mutate(monetary = log1p(monetary), frequency = log1p(frequency))
X <- scale(feat)
set.seed(26); km  <- kmeans(X, 4, nstart = 50)
set.seed(27); km2 <- kmeans(X, 4, nstart = 50)
i <- sample(n, 1500)
sil <- mean(silhouette(km$cluster[i], dist(X[i, ]))[, 3])
moved <- n - sum(apply(table(km$cluster, km2$cluster), 1, max))
ok(sil > 0.30, sprintf("silhouette k=4 = %.2f (> 0.30)", sil))
ok(moved / n < 0.02, sprintf("stabilita seed 26 vs 27: %d righe cambiano (< 2%%)", moved))
ok(min(table(km$cluster)) / n > 0.10, "nessun segmento sotto il 10%")

# ------------------------------------------------------------------- brands ----
set.seed(15)
brands <- c("A", "B", "C", "D")
attrs  <- c("Reliable", "Cheap", "Innovative", "Premium", "For young people")
prof <- rbind(A = c(320, 40, 210, 180, 90), B = c(90, 410, 60, 20, 260),
              C = c(150, 60, 380, 150, 200), D = c(260, 30, 110, 350, 40))
resp <- bind_rows(lapply(1:1200, function(r) {
  b <- sample(brands, 1)
  a <- sample(attrs, sample(1:3, 1), prob = prof[b, ])
  tibble(respondent = r, brand = b, attribute = a)
}))
write_csv(resp, "materials/brands.csv")
cat("brands.csv:", nrow(resp), "menzioni da", n_distinct(resp$respondent), "rispondenti\n")

tab <- table(resp$brand, resp$attribute)
p <- suppressWarnings(chisq.test(tab)$p.value)
ca <- CA(tab, graph = FALSE)
ok(p < 1e-6, sprintf("chi-quadro p = %.1e", p))
ok(ca$eig[1, 3] > 55, sprintf("inerzia sui primi due assi = %.0f%% (> 55)", ca$eig[2, 3]))

# -------------------------------------------------------------------- churn ----
set.seed(17)
n <- 7000
churn <- tibble(
  tenure_months   = pmax(1, round(rexp(n, 1 / 30))),
  monthly_charge  = round(runif(n, 20, 110), 1),
  contract        = sample(c("month-to-month", "one-year", "two-year"), n, TRUE, c(.55, .25, .20)),
  internet        = sample(c("fibre", "dsl", "none"), n, TRUE, c(.45, .35, .20)),
  tech_support    = sample(c("yes", "no"), n, TRUE, c(.35, .65)),
  online_security = sample(c("yes", "no"), n, TRUE, c(.35, .65)),
  streaming_tv    = sample(c("yes", "no"), n, TRUE),
  paperless       = sample(c("yes", "no"), n, TRUE, c(.6, .4)),
  payment         = sample(c("e-check", "card", "bank transfer", "mailed check"), n, TRUE),
  senior          = rbinom(n, 1, .16),
  partner         = sample(c("yes", "no"), n, TRUE),
  dependents      = sample(c("yes", "no"), n, TRUE, c(.3, .7)),
  phone_lines     = sample(0:3, n, TRUE, c(.1, .5, .3, .1)),
  support_calls   = rpois(n, 0.8),
  late_payments   = rpois(n, 0.5),
  data_gb         = round(rgamma(n, 2, 1 / 40)),
  referred        = sample(c("yes", "no"), n, TRUE, c(.2, .8)),
  region          = sample(c("north", "centre", "south", "islands"), n, TRUE)
)
lp <- with(churn, -1.9 +
  1.4 * (contract == "month-to-month") - 0.9 * (contract == "two-year") +
  0.7 * (internet == "fibre") - 0.6 * (tech_support == "yes") - 0.5 * (online_security == "yes") +
  0.5 * (payment == "e-check") + 0.45 * support_calls + 0.4 * late_payments +
  0.012 * (monthly_charge - 65) - 0.018 * pmin(tenure_months, 60) + 0.3 * senior - 0.5 * (referred == "yes"))
churn$churn <- ifelse(runif(n) < plogis(lp), "yes", "no")
churn$id <- sprintf("T%05d", 1:n)
churn <- churn |> relocate(id) |> slice_sample(prop = 1)
write_csv(churn, "materials/churn.csv")
cat("churn.csv:", nrow(churn), "righe,", ncol(churn), "colonne, churn =", round(mean(churn$churn == "yes"), 3), "\n")

d <- churn |> select(-id) |> mutate(across(where(is.character), factor))
set.seed(1); tr <- sample(n, 4900)
auc <- function(p, y) { r <- rank(p); n1 <- sum(y); (sum(r[y == 1]) - n1 * (n1 + 1) / 2) / (n1 * (length(y) - n1)) }
y <- as.numeric(d$churn[-tr] == "yes")
glm_p <- predict(glm(churn ~ ., d[tr, ], family = binomial), d[-tr, ], type = "response")
rf    <- ranger(churn ~ ., d[tr, ], num.trees = 300, probability = TRUE)
rf_p  <- predict(rf, d[-tr, ])$predictions[, "yes"]
a1 <- auc(glm_p, y); a2 <- auc(rf_p, y)
ok(mean(d$churn == "yes") > .22 && mean(d$churn == "yes") < .32, "tasso di churn tra 22% e 32%")
ok(a1 > 0.75, sprintf("AUC logistica = %.3f (> 0.75)", a1))
ok(a2 > 0.75, sprintf("AUC foresta   = %.3f (> 0.75)", a2))
cat("\ntutti i dataset generati e verificati\n")
