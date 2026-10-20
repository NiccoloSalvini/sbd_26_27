# Module 1, in R — lab of Tuesday 20 October 2026
# Every method Prof. Arbia covered, one question and one line each.
# Runs top to bottom on a fresh RStudio with the course packages installed:
#   source("https://sbd-26-27.netlify.app/materials/setup.R")

library(tidyverse)
library(here)

# ---- 1 · Foundations ---------------------------------------------------------
?mtcars                                  # the codebook
summary(mtcars$mpg)
table(mtcars$am)                         # 0 = automatic, 1 = manual
boxplot(mpg ~ am, data = mtcars)

t.test(mtcars$mpg, mu = 20)              # one mean: is the average 20 mpg?
t.test(mpg ~ am, data = mtcars)          # two means: do manual cars use less?

fit <- aov(weight ~ group, data = PlantGrowth)   # three groups
summary(fit)
TukeyHSD(fit)

# ---- 2 · Regression ----------------------------------------------------------
fit1 <- lm(mpg ~ wt, data = mtcars)
summary(fit1)
plot(mpg ~ wt, data = mtcars); abline(fit1)

fit2 <- lm(mpg ~ wt + hp, data = mtcars)
summary(fit2)
predict(fit2, newdata = data.frame(wt = 3, hp = 150), interval = "prediction")

# nonlinear: R-squared always rises with the degree ...
sapply(c(1, 2, 9), function(d) summary(lm(dist ~ poly(speed, d), data = cars))$r.squared)

# ... so cross-validation chooses the degree instead
set.seed(1)
folds <- sample(rep(1:5, length.out = nrow(cars)))
cv_mse <- function(d) mean(sapply(1:5, function(k) {
  fit <- lm(dist ~ poly(speed, d), data = cars[folds != k, ])
  mean((cars$dist[folds == k] - predict(fit, cars[folds == k, ]))^2)
}))
sapply(c(1, 2, 3, 5, 9), cv_mse)

# train and test, the habit
set.seed(1)
idx   <- sample(nrow(mtcars), 0.7 * nrow(mtcars))
train <- mtcars[idx, ]
test  <- mtcars[-idx, ]
fit   <- lm(mpg ~ wt + hp, data = train)
mean((test$mpg - predict(fit, test))^2)

# ---- 3 · GLM -----------------------------------------------------------------
fit <- glm(am ~ wt, family = binomial, data = mtcars)      # a yes/no
exp(coef(fit))
predict(fit, data.frame(wt = c(2.5, 3.5)), type = "response")

fit <- glm(breaks ~ wool + tension, family = poisson, data = warpbreaks)   # a count
exp(coef(fit))

library(survival)                                          # a time to event
fit <- survfit(Surv(time, status) ~ sex, data = lung)
fit
plot(fit, col = c("navy", "goldenrod"))
survdiff(Surv(time, status) ~ sex, data = lung)
coxph(Surv(time, status) ~ sex + age, data = lung)

# ---- 4 · Ridge and LASSO -----------------------------------------------------
summary(lm(mpg ~ ., data = mtcars))      # ten predictors, nothing significant

library(glmnet)
x <- model.matrix(mpg ~ ., data = mtcars)[, -1]
y <- mtcars$mpg
set.seed(1)
cv <- cv.glmnet(x, y, alpha = 1)         # alpha = 1: LASSO; alpha = 0: ridge
plot(cv)
coef(cv, s = "lambda.1se")

# ---- 5 · Time series ---------------------------------------------------------
AirPassengers
frequency(AirPassengers)
plot(AirPassengers)

d <- decompose(AirPassengers, type = "multiplicative")
plot(d)
round(d$figure, 2)

hw <- HoltWinters(AirPassengers, seasonal = "multiplicative")
predict(hw, 12)

fit <- arima(log(AirPassengers), order = c(0, 1, 1), seasonal = c(0, 1, 1))
fit
exp(predict(fit, 12)$pred)
Box.test(residuals(fit), lag = 24, type = "Ljung-Box")

# ---- 6 · A CSV from the course site ------------------------------------------
dir.create(here("data"), showWarnings = FALSE)
download.file("https://sbd-26-27.netlify.app/materials/churn.csv", here("data", "churn.csv"))

churn <- read_csv(here("data", "churn.csv"))
glimpse(churn)

mean(churn$churn == "yes")
t.test(monthly_charge ~ churn, data = churn)
prop.table(table(churn$contract, churn$churn), 1)

churn$churn <- factor(churn$churn)
fit <- glm(churn ~ tenure_months + contract + monthly_charge, family = binomial, data = churn)
exp(coef(fit))
predict(fit, newdata = data.frame(tenure_months = 3, contract = "month-to-month",
                                  monthly_charge = 90), type = "response")

summary(aov(monthly_charge ~ contract, data = churn))              # an honest no
summary(lm(monthly_charge ~ data_gb + phone_lines + streaming_tv, data = churn))

# ---- Your turn ---------------------------------------------------------------
# 1. t.test(tenure_months ~ churn, data = churn)
# 2. tapply(churn$churn == "yes", churn$support_calls, mean)
# 3. add support_calls to the logit; exp(coef(...))
# 4. set.seed(1); split 70/30; predict on test; churn share in the top 10% of predicted probability
