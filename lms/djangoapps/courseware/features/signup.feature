Feature: Sign in
  In order to use the edX content
  As a new user
  I want to signup for a student account

  # CHROME ONLY, firefox will not redirect properly
  Scenario: Sign up from the homepage
    Given I visit the homepage
    When I click the link with the text "Register Now"
    And I fill in "email" on the registration form with "robot2@edx.org"
    And I fill in "password" on the registration form with "test"
    And I fill in "username" on the registration form with "robot2"
    And I fill in "name" on the registration form with "Robot Two"
    And I check the checkbox named "terms_of_service"
    And I check the checkbox named "honor_code"
    And I submit the registration form
    Then I should see "THANKS FOR REGISTERING!" in the dashboard banner
