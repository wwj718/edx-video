Feature: Advanced (manual) course policy
  In order to specify course policy settings for which no custom user interface exists
  I want to be able to manually enter JSON key /value pairs

  Scenario: A course author sees default advanced settings
    Given I have opened a new course in Studio
    When I select the Advanced Settings
    Then I see default advanced settings

  Scenario: Add new entries, and they appear alphabetically after save
    Given I am on the Advanced Course Settings page in Studio
    Then the settings are alphabetized

  Scenario: Test cancel editing key value
    Given I am on the Advanced Course Settings page in Studio
    When I edit the value of a policy key
    And I press the "Cancel" notification button
    Then the policy key value is unchanged
    And I reload the page
    Then the policy key value is unchanged

  Scenario: Test editing key value
    Given I am on the Advanced Course Settings page in Studio
    When I edit the value of a policy key and save
    Then the policy key value is changed
    And I reload the page
    Then the policy key value is changed

  Scenario: Test how multi-line input appears
    Given I am on the Advanced Course Settings page in Studio
    When I create a JSON object as a value for "discussion_topics"
    Then it is displayed as formatted
    And I reload the page
    Then it is displayed as formatted

  Scenario: Test error if value supplied is of the wrong type
    Given I am on the Advanced Course Settings page in Studio
    When I create a JSON object as a value for "display_name"
    Then I get an error on save
    And I reload the page
    Then the policy key value is unchanged

  # This feature will work in Firefox only when Firefox is the active window
  Scenario: Test automatic quoting of non-JSON values
    Given I am on the Advanced Course Settings page in Studio
    When I create a non-JSON value not in quotes
    Then it is displayed as a string
    And I reload the page
    Then it is displayed as a string

  Scenario: Confirmation is shown on save
    Given I am on the Advanced Course Settings page in Studio
    When I edit the value of a policy key
    And I press the "Save" notification button
    Then I see a confirmation that my changes have been saved
