# pylint: disable=C0111
# pylint: disable=W0621

from lettuce import world, step
from lettuce.django import django_url


@step('I register for the course "([^"]*)"$')
def i_register_for_the_course(_step, course):
    cleaned_name = world.scenario_dict['COURSE'].display_name.replace(' ', '_')
    url = django_url('courses/%s/%s/%s/about' % (world.scenario_dict['COURSE'].org, course, cleaned_name))
    world.browser.visit(url)
    world.css_click('section.intro a.register')

    assert world.is_css_present('section.container.dashboard')


@step(u'I should see an empty dashboard message')
def i_should_see_empty_dashboard(_step):
    empty_dash_css = 'section.empty-dashboard-message'
    assert world.is_css_present(empty_dash_css)


@step(u'I should( NOT)? see the course numbered "([^"]*)" in my dashboard$')
def i_should_see_that_course_in_my_dashboard(_step, doesnt_appear, course):
    course_link_css = 'section.my-courses a[href*="%s"]' % course
    if doesnt_appear:
        assert world.is_css_not_present(course_link_css)
    else:
        assert world.is_css_present(course_link_css)


@step(u'I unregister for the course numbered "([^"]*)"')
def i_unregister_for_that_course(_step, course):
    unregister_css = 'section.info a[href*="#unenroll-modal"][data-course-number*="%s"]' % course
    world.css_click(unregister_css)
    button_css = 'section#unenroll-modal input[value="Unregister"]'
    world.css_click(button_css)
