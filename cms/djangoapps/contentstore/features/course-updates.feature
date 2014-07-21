Feature: Course updates
    As a course author, I want to be able to provide updates to my students

    Scenario: Users can add updates
        Given I have opened a new course in Studio
        And I go to the course updates page
        When I add a new update with the text "Hello"
        Then I should see the update "Hello"
        And I see a "saving" notification

    Scenario: Users can edit updates
        Given I have opened a new course in Studio
        And I go to the course updates page
        When I add a new update with the text "Hello"
        And I modify the text to "Goodbye"
        Then I should see the update "Goodbye"
        And I see a "saving" notification

    Scenario: Users can delete updates
        Given I have opened a new course in Studio
        And I go to the course updates page
        And I add a new update with the text "Hello"
        And I delete the update
        And I confirm the prompt
        Then I should not see the update "Hello"
        And I see a "deleting" notification

    Scenario: Users can edit update dates
        Given I have opened a new course in Studio
        And I go to the course updates page
        And I add a new update with the text "Hello"
        When I edit the date to "June 1, 2013"
        Then I should see the date "June 1, 2013"
        And I see a "saving" notification

    Scenario: Users can change handouts
        Given I have opened a new course in Studio
        And I go to the course updates page
        When I modify the handout to "<ol>Test</ol>"
        Then I see the handout "Test"
        And I see a "saving" notification
