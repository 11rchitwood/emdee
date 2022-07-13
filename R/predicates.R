#' Predicate functions
#'
#' @param x character
#'
#' @return logical

#' @rdname predicates
is_alpha <- function(x) {
  x %in% c(letters, LETTERS)
}

#' @rdname predicates
is_digit <- function(x) {
  x %in% 0:9
}

#' @rdname predicates
is_alpha_digit <- function(x) {
  is_alpha(x) | is_digit(x)
}

#' @rdname predicates
is_whitespace <- function(x) {
  x %in% c(" ", "\t", "\n", "\r")
}

