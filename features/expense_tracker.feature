Feature: Expense Tracker - core expense management and analytics
  As a user
  I want to record and manage my daily expense and view spending analytics by category and date range
  So that I can understand my spending habits and make better budgeting decisions

  Background:
    Given the Expense Tracker API is running

  # Add Expense
  Scenario: Add an expense with required fields and optional notes
    When I add an expense with date "2026-08-01", business "Coffee Shop", amount 4.50, category "Restaurants" and notes "Latte"
    Then the add expense request should succeed

  Scenario: Add an expense should fail when required fields are missing
    When I add an expense with missing required fields
    Then the add expense request should fail with status code 400

  # View Expenses
  Scenario: View recent expenses returns a list of expenses
    Given I have added an expense for date "2026-08-02" business "Grocer" amount 25.10 category "Groceries"
    When I request expenses for the most recent entries
    Then I should receive a list containing that expense

  Scenario: View expenses filtered by month
    Given I have added an expense for date "2026-08-03" business "Fuel" amount 40.00 category "Gas/Car"
    When I request expenses for month "2026-08"
    Then I should receive a list containing that expense

  # Analyze Spending (date range + category-wise) - Expected by requirements
  Scenario: Category-wise spending for a selected date range
    Given I have added an expense for date "2026-08-04" business "Pizza" amount 18.00 category "Restaurants"
    And I have added an expense for date "2026-08-05" business "Market" amount 32.00 category "Groceries"
    When I request category-wise spending for date range "2026-08-01" to "2026-08-31"
    Then I should receive category totals including "Restaurants" and "Groceries"

  # Update Expense - Expected by requirements
  Scenario: Update an existing expense
    Given I have added an expense for date "2026-08-06" business "Bookstore" amount 12.00 category "School/Office Supplies"
    When I update that expense amount to 15.00 and notes to "Notebook"
    Then the update expense request should succeed
    And viewing recent expenses should show the updated expense

  # Visual Analytics
  Scenario: Monthly overview analytics returns totals grouped by month
    When I request monthly overview analytics
    Then I should receive totals grouped by month
