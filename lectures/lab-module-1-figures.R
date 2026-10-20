# Figures for lectures/lab-module-1-in-r.qmd — one picture per question.
# Rscript lectures/lab-module-1-figures.R   (from the repo root) -> lectures/media/lab-*.png
# Base graphics only, so it runs on a bare R. Site colours; no titles (the slide has one).

NAVY <- "#002f57"; GOLD <- "#b8860b"; MUTED <- "#5f6b75"; LIGHT <- "#e6e9ec"
out <- function(name, w = 7.2, h = 4.6) {
  png(file.path("lectures/media", paste0("lab-", name, ".png")), width = w, height = h, units = "in", res = 200)
  par(family = "sans", mar = c(4.2, 4.4, 1, 1), cex.lab = 1.15, cex.axis = 1.05, las = 1, bty = "l",
      col.axis = "#1c2226", col.lab = "#1c2226", fg = MUTED)
}

# 1 · one mean ---------------------------------------------------------------
out("one-mean", h = 3.2)
par(mar = c(4.2, 1, 1, 1))
set.seed(2); y <- jitter(rep(1, 32), amount = 0.18)
plot(mtcars$mpg, y, pch = 16, col = adjustcolor(NAVY, .55), cex = 1.6, ylim = c(0.5, 1.5), yaxt = "n",
     xlab = "miles per gallon, 32 cars", ylab = "")
tt <- t.test(mtcars$mpg, mu = 20)
segments(tt$conf.int[1], 0.72, tt$conf.int[2], 0.72, lwd = 6, col = NAVY, lend = 1)
points(mean(mtcars$mpg), 0.72, pch = 18, cex = 3, col = NAVY)
abline(v = 20, col = GOLD, lwd = 3, lty = 2)
text(20, 1.45, "20 ?", col = GOLD, font = 2, cex = 1.3)
text(mean(mtcars$mpg), 0.58, "mean, and its 95% interval", col = NAVY, cex = 1)
dev.off()

# 2 · two means --------------------------------------------------------------
out("two-means")
boxplot(mpg ~ am, data = mtcars, names = c("automatic", "manual"), col = c(LIGHT, adjustcolor(GOLD, .35)),
        border = NAVY, lwd = 1.5, xlab = "", ylab = "miles per gallon")
points(c(1, 2), tapply(mtcars$mpg, mtcars$am, mean), pch = 18, cex = 2.6, col = GOLD)
dev.off()

# 3 · three groups -----------------------------------------------------------
out("anova")
boxplot(weight ~ group, data = PlantGrowth, names = c("control", "treatment 1", "treatment 2"),
        col = c(LIGHT, LIGHT, adjustcolor(GOLD, .35)), border = NAVY, lwd = 1.5, xlab = "", ylab = "dried weight")
points(1:3, tapply(PlantGrowth$weight, PlantGrowth$group, mean), pch = 18, cex = 2.6, col = GOLD)
dev.off()

# 4 · simple regression ------------------------------------------------------
out("simple")
plot(mpg ~ wt, data = mtcars, pch = 16, col = adjustcolor(NAVY, .6), cex = 1.5,
     xlab = "weight, 1 000 lb", ylab = "miles per gallon")
abline(lm(mpg ~ wt, data = mtcars), col = GOLD, lwd = 4)
text(4.6, 30, "mpg = 37.3 − 5.34 wt", col = GOLD, font = 2, cex = 1.2)
dev.off()

# 5 · nonlinear --------------------------------------------------------------
out("nonlinear")
plot(dist ~ speed, data = cars, pch = 16, col = adjustcolor(NAVY, .55), cex = 1.5,
     xlab = "speed, mph", ylab = "stopping distance, ft")
s <- seq(4, 25, length.out = 300)
lines(s, predict(lm(dist ~ speed, cars), data.frame(speed = s)), col = MUTED, lwd = 3, lty = 2)
lines(s, predict(lm(dist ~ poly(speed, 9), cars), data.frame(speed = s)), col = adjustcolor(NAVY, .5), lwd = 2)
lines(s, predict(lm(dist ~ poly(speed, 2), cars), data.frame(speed = s)), col = GOLD, lwd = 4)
legend("topleft", bty = "n", lwd = c(3, 4, 2), lty = c(2, 1, 1), col = c(MUTED, GOLD, adjustcolor(NAVY, .5)),
       legend = c("degree 1", "degree 2", "degree 9"), cex = 1.1)
dev.off()

# 6 · cross-validation -------------------------------------------------------
out("cv")
set.seed(1); folds <- sample(rep(1:5, length.out = nrow(cars)))
cv_mse <- function(d) mean(sapply(1:5, function(k) {
  fit <- lm(dist ~ poly(speed, d), data = cars[folds != k, ])
  mean((cars$dist[folds == k] - predict(fit, cars[folds == k, ]))^2)
}))
degs <- 1:9; e <- sapply(degs, cv_mse)
plot(degs, e, type = "b", log = "y", pch = 16, cex = 1.6, lwd = 3, col = NAVY,
     xlab = "degree of the polynomial", ylab = "cross-validated error (log scale)")
points(2, e[2], pch = 16, cex = 2.6, col = GOLD)
text(2.3, e[2] * 0.6, "degree 2", col = GOLD, font = 2, cex = 1.2, adj = 0)
dev.off()

# 7 · logistic ---------------------------------------------------------------
out("logit")
plot(am ~ wt, data = mtcars, pch = 16, col = adjustcolor(NAVY, .55), cex = 1.5, yaxt = "n",
     xlab = "weight, 1 000 lb", ylab = "manual gearbox?")
axis(2, at = c(0, 1), labels = c("no", "yes"))
w <- seq(1.4, 5.5, length.out = 300)
abline(lm(am ~ wt, data = mtcars), col = MUTED, lwd = 2, lty = 2)
lines(w, predict(glm(am ~ wt, binomial, mtcars), data.frame(wt = w), type = "response"), col = GOLD, lwd = 4)
text(4.4, 0.72, "a line goes below 0\nand above 1", col = MUTED, cex = 1)
text(2.0, 0.35, "logistic:\na probability", col = GOLD, font = 2, cex = 1.1)
dev.off()

# 8 · Poisson ----------------------------------------------------------------
out("poisson")
m <- tapply(warpbreaks$breaks, list(warpbreaks$wool, warpbreaks$tension), mean)
barplot(m, beside = TRUE, col = c(NAVY, GOLD), border = NA, names.arg = c("low", "medium", "high"),
        xlab = "tension", ylab = "mean breaks per loom", ylim = c(0, 50))
legend("topright", bty = "n", fill = c(NAVY, GOLD), border = NA, legend = c("wool A", "wool B"), cex = 1.1)
dev.off()

# 9 · survival ---------------------------------------------------------------
library(survival)
out("survival")
fit <- survfit(Surv(time, status) ~ sex, data = lung)
plot(fit, col = c(NAVY, GOLD), lwd = 4, conf.int = FALSE, xlab = "days", ylab = "share still alive", mark.time = TRUE)
abline(h = 0.5, col = MUTED, lty = 3)
legend("topright", bty = "n", lwd = 4, col = c(NAVY, GOLD), legend = c("men: median 270 days", "women: median 426 days"), cex = 1.1)
dev.off()

# 10 · LASSO path ------------------------------------------------------------
library(glmnet)
out("lasso")
x <- model.matrix(mpg ~ ., data = mtcars)[, -1]; y <- mtcars$mpg
set.seed(1); cv <- cv.glmnet(x, y, alpha = 1)
B <- as.matrix(cv$glmnet.fit$beta); L <- log(cv$glmnet.fit$lambda)
keep <- c("wt", "cyl", "hp")
par(mar = c(4.2, 4.4, 1, 4))
matplot(L, t(B), type = "l", lty = 1, lwd = ifelse(rownames(B) %in% keep, 4, 2),
        col = ifelse(rownames(B) %in% keep, NAVY, adjustcolor(MUTED, .6)),
        xlab = "log(lambda): penalty grows to the right", ylab = "coefficient")
abline(h = 0, col = LIGHT)
abline(v = log(cv$lambda.1se), col = GOLD, lwd = 3, lty = 2)
axis(4, at = B[keep, 1], labels = keep, las = 1, tick = FALSE, line = -0.6, col.axis = NAVY, font = 2)
text(log(cv$lambda.1se), max(B) * 0.9, "chosen lambda:\n3 columns left", col = GOLD, font = 2, adj = c(1.05, 1), cex = 1.05)
dev.off()

# 11 · the series -------------------------------------------------------------
out("series")
plot(AirPassengers, col = NAVY, lwd = 3, xlab = "", ylab = "passengers, thousands")
dev.off()

# 12 · decomposition ---------------------------------------------------------
png("lectures/media/lab-decompose.png", width = 6.2, height = 6.8, units = "in", res = 200)
d <- decompose(AirPassengers, type = "multiplicative")
par(family = "sans", las = 1, col.axis = "#1c2226", fg = MUTED, cex.axis = 0.95)
plot(d, col = NAVY, lwd = 2)
dev.off()

# 13 · Holt–Winters ----------------------------------------------------------
out("holtwinters")
hw <- HoltWinters(AirPassengers, seasonal = "multiplicative")
p <- predict(hw, 12)
plot(AirPassengers, col = NAVY, lwd = 3, xlim = c(1949, 1962), ylim = c(100, 700), xlab = "", ylab = "passengers, thousands")
lines(hw$fitted[, "xhat"], col = adjustcolor(GOLD, .7), lwd = 2)
lines(p, col = GOLD, lwd = 4)
legend("topleft", bty = "n", lwd = c(3, 2, 4), col = c(NAVY, adjustcolor(GOLD, .7), GOLD),
       legend = c("observed", "smoothed", "forecast 1961"), cex = 1.1)
dev.off()

# 14 · ARIMA -----------------------------------------------------------------
out("arima")
fit <- arima(log(AirPassengers), order = c(0, 1, 1), seasonal = c(0, 1, 1))
pr <- predict(fit, 12)
t <- time(pr$pred)
plot(AirPassengers, col = NAVY, lwd = 3, xlim = c(1949, 1962), ylim = c(100, 800), xlab = "", ylab = "passengers, thousands")
polygon(c(t, rev(t)), c(exp(pr$pred + 1.96 * pr$se), rev(exp(pr$pred - 1.96 * pr$se))), col = adjustcolor(GOLD, .25), border = NA)
lines(exp(pr$pred), col = GOLD, lwd = 4)
legend("topleft", bty = "n", lwd = c(3, 4, 10), col = c(NAVY, GOLD, adjustcolor(GOLD, .25)),
       legend = c("observed", "forecast 1961", "95% interval"), cex = 1.1)
dev.off()

# 15 · churn by contract -----------------------------------------------------
ch <- read.csv("materials/churn.csv")
out("churn-contract")
r <- tapply(ch$churn == "yes", ch$contract, mean)
bp <- barplot(r * 100, col = c(GOLD, NAVY, NAVY), border = NA, ylim = c(0, 50), ylab = "churn rate, %", names.arg = names(r))
text(bp, r * 100 + 3, paste0(round(r * 100), "%"), col = "#1c2226", font = 2, cex = 1.2)
dev.off()

cat("figures written to lectures/media/\n")
