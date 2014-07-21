from django.conf import settings


def notes_enabled_for_course(course):

    '''
    Returns True if the notes app is enabled for the course, False otherwise.

    In order for the app to be enabled it must be:
        1) enabled globally via MITX_FEATURES.
        2) present in the course tab configuration.
    '''

    tab_found = next((True for t in course.tabs if t['type'] == 'notes'), False)
    feature_enabled = settings.MITX_FEATURES.get('ENABLE_STUDENT_NOTES')

    return feature_enabled and tab_found
