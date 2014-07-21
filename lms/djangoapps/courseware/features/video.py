#pylint: disable=C0111

from lettuce import world, step
from lettuce.django import django_url
from common import i_am_registered_for_the_course, section_location

############### ACTIONS ####################

HTML5_SOURCES = [
    'https://s3.amazonaws.com/edx-course-videos/edx-intro/edX-FA12-cware-1_100.mp4',
    'https://s3.amazonaws.com/edx-course-videos/edx-intro/edX-FA12-cware-1_100.webm',
    'https://s3.amazonaws.com/edx-course-videos/edx-intro/edX-FA12-cware-1_100.ogv'
]

@step('when I view the (.*) it has autoplay enabled$')
def does_autoplay_video(_step, video_type):
    assert(world.css_find('.%s' % video_type)[0]['data-autoplay'] == 'True')


@step('the course has a Video component in (.*) mode$')
def view_video(_step, player_mode):
    coursenum = 'test_course'
    i_am_registered_for_the_course(step, coursenum)

    # Make sure we have a video
    add_video_to_course(coursenum, player_mode.lower())
    chapter_name = world.scenario_dict['SECTION'].display_name.replace(" ", "_")
    section_name = chapter_name
    url = django_url('/courses/%s/%s/%s/courseware/%s/%s' %
                    (world.scenario_dict['COURSE'].org, world.scenario_dict['COURSE'].number, world.scenario_dict['COURSE'].display_name.replace(' ', '_'),
                        chapter_name, section_name,))
    world.browser.visit(url)


def add_video_to_course(course, player_mode):
    category = 'video'

    kwargs = {
        'parent_location': section_location(course),
        'category': category,
        'display_name': 'Video'
    }

    if player_mode == 'html5':
        kwargs.update({
            'metadata': {
                'youtube_id_1_0': '',
                'youtube_id_0_75': '',
                'youtube_id_1_25': '',
                'youtube_id_1_5': '',
                'html5_sources': HTML5_SOURCES
            }
        })

    world.ItemFactory.create(**kwargs)


@step('when I view the video it has rendered in (.*) mode$')
def video_is_rendered(_step, mode):
    modes = {
        'html5': 'video',
        'youtube': 'iframe'
    }
    html_tag = modes[mode.lower()]
    assert world.css_find('.video {0}'.format(html_tag)).first

@step('all sources are correct$')
def all_sources_are_correct(_step):
    sources = world.css_find('.video video source')
    assert set(source['src'] for source in sources) == set(HTML5_SOURCES)


