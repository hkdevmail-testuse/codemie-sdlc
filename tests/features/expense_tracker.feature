Feature: Personal Expense Tracker - Record, manage expenses and view analytics
  As a user
  I want to record and manage my daily expense and view spending analytics by category and date range
  So that I can understand my spending habits and make better budgeting decisions

  Background:
    Given the expense tracker API is running

  # SCRUM-44
  Scenario: Add an expense with date, amount, category, and optional notes
    When I add an expense with date "2026-08-01" business "Coffee Shop" amount "4.50" category "Restaurants" and description "Latte"
    Then the expense is added successfully
    And the recent expenses list contains an expense with business "Coffee Shop" and amount 4.5

  # SCRUM-44
  Scenario: Add expense fails when required fields are missing
    When I add an expense with date "" business "" amount "" category "" and description ""
    Then the API responds with status code 400
    And the error message is "Missing required fields"

  # SCRUM-45
  Scenario: Update expense is not supported by the current API
    Given I have an existing expense with date "2026-08-02" business "Store" amount "10" category "Groceries" and description ""
    When I update that expense amount to "12.00"
    Then the API responds with status code 404

  # SCRUM-46
  Scenario: View recorded expenses returns a list
    When I request recent expenses with limit 10
    Then the API responds with status code 200
    And the response is a JSON array

  # SCRUM-47
  Scenario: Analyze spending by category for a selected month
    Given I have an existing expense with date "2026-08-03" business "Gas Station" amount "30" category "Gas/Car" and description ""
    When I request category totals for month "2026-08"
    Then the API responds with status code 200
    And the category totals include "Gas/Car"

  # SCRUM-48
  Scenario: View visual analytics data for all-time categories
    Given I have an existing expense with date "2026-08-04" business "Market" amount "20" category "Groceries" and description ""
    When I request all-time category totals
    Then the API responds with status code 200
    And the category totals include "Groceries"

  # SCRUM-49
  Scenario: Identify high-spending categories using category totals
    Given I have an existing expense with date "2026-08-05" business "Big Store" amount "200" category "Furniture/Home" and description ""
    And I have an existing expense with date "2026-08-06" business "Small Store" amount "50" category "Clothes" and description ""
    When I request all-time category totals
    Then the highest spending category is "Furniture/Home"
