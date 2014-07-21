Feature: Sign in
  In order to use the edX content
  As a new user
  I want to signup for a student account

  Scenario: Sign up from the homepage
    Given I visit the Studio homepage
    When I click the link with the text "Sign Up"
    And I fill in the registration form
    And I press the Create My Account button on the registration form
    Then I should see an email verification prompt

  Scenario: Login with a valid redirect
    Given I have opened a new course in Studio
    And I am not logged in
    And I visit the url "/MITx/999/course/Robot_Super_Course"
    And I should see that the path is "/signin?next=/MITx/999/course/Robot_Super_Course"
    When I fill in and submit the signin form
    And I wait for "2" seconds
    Then I should see that the path is "/MITx/999/course/Robot_Super_Course"

  Scenario: Login with an invalid redirect
    Given I have opened a new course in Studio
    And I am not logged in
    And I visit the url "/signin?next=http://www.google.com/"
    When I fill in and submit the signin form
    And I wait for "2" seconds
    Then I should see that the path is "/"
