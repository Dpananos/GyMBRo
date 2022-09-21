test_that("cleaning", {
  case_1 <- clean_tweet("WR - 1 CM - 1 SPIN - 1")
  expect_equal("WR 1 CM 1 SPIN 1", case_1)

  case_2 <- clean_tweet("wr: 20 cm: 9 spin: 0")
  expect_equal("WR 20 CM 9 SPIN 0", case_2)

  case_3 <- clean_tweet("WR- CM- Spin_")
  expect_equal("WR CM SPIN", case_3)

  case_4 <- clean_tweet("WR 103 CM 10 SPIN 6 😉")
  expect_equal("WR 103 CM 10 SPIN 6", case_4)

  case_5 <- clean_tweet("WR 10\nCM 20\n SPIN 30")
  expect_equal("WR 10 CM 20 SPIN 30", case_5)
})


test_that("extraction", {
  case_1 <- "WR 10 CM 20 SPIN 30"
  expect_equal(get_number(case_1, "WR"), 10)
  expect_equal(get_number(case_1, "CM"), 20)
  expect_equal(get_number(case_1, "SPIN"), 30)
  expect_true(is.na(get_number(case_1, "PO")))

  case_2 <- "WRACK WR 20 CM 20 SPIN 20"
  expect_equal(get_number(case_2, "WR"), 20)

  case_3 <- "WR1LD UP WR 20"
  expect_equal(get_number(case_3, "WR"), 20)
})
