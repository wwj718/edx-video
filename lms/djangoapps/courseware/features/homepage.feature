Feature: Homepage for web users
  In order to get an idea what edX is about
  As a an anonymous web user
  I want to check the information on the home page

  Scenario: User can see the "Login" button
    Given I visit the homepage
    Then I should see a link called "Log in"

  Scenario: User can see the "Register Now" button
    Given I visit the homepage
    Then I should see a link called "Register Now"

  Scenario Outline: User can see main parts of the page
    Given I visit the homepage
    Then I should see the following links and ids
    | id      | Link   |
    | about   | About  |
    | jobs    | Jobs   |
    | faq     | FAQ    |
    | contact | Contact|
    | press   | Press  |


  # TODO: test according to domain or policy
  Scenario: User can see the partner institutions
    Given I visit the homepage
    Then I should see the following Partners in the Partners section
    | Partner     |
    | MITx        |
    | HarvardX    |
    | BerkeleyX   |
    | UTx         |
    | WellesleyX  |
    | GeorgetownX |

  # # TODO: Add scenario that tests the courses available
  # # using a policy or a configuration file
