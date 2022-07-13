test_that("is_alpha works", {
  expect_true(is_alpha("a"))
  expect_true(is_alpha("A"))
  expect_false(is_alpha("1"))
  expect_false(is_alpha("\t"))
})

test_that("is_digit works", {
  expect_false(is_digit("a"))
  expect_false(is_digit("A"))
  expect_true(is_digit("1"))
  expect_false(is_digit("\t"))
})

test_that("is_alpha_digit works", {
  expect_true(is_alpha_digit("a"))
  expect_true(is_alpha_digit("A"))
  expect_true(is_alpha_digit("1"))
  expect_false(is_alpha_digit("\t"))
})

test_that("is_whitespace works", {
  expect_false(is_whitespace("a"))
  expect_false(is_whitespace("A"))
  expect_false(is_whitespace("1"))
  expect_true(is_whitespace("\t"))
})
