Change Log
----------

These are notable changes in edx-platform.  This is a rolling list of changes,
in roughly chronological order, most recent first.  Add your entries at or near
the top.  Include a label indicating the component affected.

Blades: Took videoalpha out of alpha, replacing the old video player

LMS: Enable beta instructor dashboard. The beta dashboard is a rearchitecture
of the existing instructor dashboard and is available by clicking a link at
the top right of the existing dashboard.

Common: CourseEnrollment has new fields `is_active` and `mode`. The mode will be
used to differentiate different kinds of enrollments (currently, all enrollments
are honor certificate enrollments). The `is_active` flag will be used to
deactivate enrollments without deleting them, so that we know what course you
*were* enrolled in. Because of the latter change, enrollment and unenrollment
logic has been consolidated into the model -- you should use new class methods
to `enroll()`, `unenroll()`, and to check `is_enrolled()`, instead of creating
CourseEnrollment objects or querying them directly.

Studio: Email will be sent to admin address when a user requests course creator
privileges for Studio (edge only).

Studio: Studio course authors (both instructors and staff) will be auto-enrolled
for their courses so that "View Live" works.

Common: Add a new input type ``<formulaequationinput />`` for Formula/Numerical
Responses. It periodically makes AJAX calls to preview and validate the
student's input.

Common: Added ratelimiting to our authentication backend.

Common: Add additional logging to cover login attempts and logouts.

Studio: Send e-mails to new Studio users (on edge only) when their course creator
status has changed. This will not be in use until the course creator table
is enabled.

Studio: Added improvements to Course Creation: richer error messaging, tip
text, and fourth field for course run.

Blades: New features for VideoAlpha player:
1.) Controls are auto hidden after a delay of mouse inactivity - the full video
becomes visible.
2.) When captions (CC) button is pressed, captions stick (not auto hidden after
a delay of mouse inactivity). The video player size does not change - the video
is down-sized and placed in the middle of the black area.
3.) All source code of Video Alpha 2 is written in JavaScript. It is not a basic
conversion from CoffeeScript. The structure of the player has been changed.
4.) A lot of additional unit tests.

LMS: Added user preferences (arbitrary user/key/value tuples, for which
which user/key is unique) and a REST API for reading users and
preferences. Access to the REST API is restricted by use of the
X-Edx-Api-Key HTTP header (which must match settings.EDX_API_KEY; if
the setting is not present, the API is disabled).

LMS: Added endpoints for AJAX requests to enable/disable notifications
(which are not yet implemented) and a one-click unsubscribe page.

Studio: Allow instructors of a course to designate other staff as instructors;
this allows instructors to hand off management of a course to someone else.

Common: Add a manage.py that knows about edx-platform specific settings and projects

Common: Added *experimental* support for jsinput type.

Studio: Remove XML from HTML5 video component editor. All settings are
moved to be edited as metadata.

Common: Added setting to specify Celery Broker vhost

Common: Utilize new XBlock bulk save API in LMS and CMS.

Studio: Add table for tracking course creator permissions (not yet used).
Update rake django-admin[syncdb] and rake django-admin[migrate] so they
run for both LMS and CMS.

LMS: Added *experimental* crowdsource hinting manager page.

XModule: Added *experimental* crowdsource hinting module.

Studio: Added support for uploading and managing PDF textbooks

Common: Student information is now passed to the tracking log via POST instead of GET.

Blades: Added functionality and tests for new capa input type: choicetextresponse.

Common: Add tests for documentation generation to test suite

Blades: User answer now preserved (and changeable) after clicking "show answer" in choice problems

LMS: Removed press releases

Common: Updated Sass and Bourbon libraries, added Neat library

LMS: Add a MixedModuleStore to aggregate the XMLModuleStore and MongoMonduleStore

LMS: Users are no longer auto-activated if they click "reset password"
This is now done when they click on the link in the reset password
email they receive (along with usual path through activation email).

LMS: Fixed a reflected XSS problem in the static textbook views.

LMS: Problem rescoring.  Added options on the Grades tab of the
Instructor Dashboard to allow a particular student's submission for a
particular problem to be rescored.  Provides an option to see a
history of background tasks for a given problem and student.

Blades: Small UX fix on capa multiple-choice problems.  Make labels only
as wide as the text to reduce accidental choice selections.

Studio:
- use xblock field defaults to initialize all new instances' fields and
only use templates as override samples.
- create new instances via in memory create_xmodule and related methods rather
than cloning a db record.
- have an explicit method for making a draft copy as distinct from making a new module.

Studio: Remove XML from the video component editor. All settings are
moved to be edited as metadata.

XModule: Only write out assets files if the contents have changed.

Studio: Course settings are now saved explicitly.

XModule: Don't delete generated xmodule asset files when compiling (for
instance, when XModule provides a coffeescript file, don't delete
the associated javascript)

Studio: For courses running on edx.org (marketing site), disable fields in
Course Settings that do not apply.

Common: Make asset watchers run as singletons (so they won't start if the
watcher is already running in another shell).

Common: Use coffee directly when watching for coffeescript file changes.

Common: Make rake provide better error messages if packages are missing.

Common: Repairs development documentation generation by sphinx.

LMS: Problem rescoring.  Added options on the Grades tab of the
Instructor Dashboard to allow all students' submissions for a
particular problem to be rescored.  Also supports resetting all
students' number of attempts to zero.  Provides a list of background
tasks that are currently running for the course, and an option to
see a history of background tasks for a given problem.

LMS: Fixed the preferences scope for storing data in xmodules.

LMS: Forums.  Added handling for case where discussion module can get `None` as
value of lms.start in `lms/djangoapps/django_comment_client/utils.py`

Studio, LMS: Make ModelTypes more strict about their expected content (for
instance, Boolean, Integer, String), but also allow them to hold either the
typed value, or a String that can be converted to their typed value. For example,
an Integer can contain 3 or '3'. This changed an update to the xblock library.

LMS: Courses whose id matches a regex in the COURSES_WITH_UNSAFE_CODE Django
setting now run entirely outside the Python sandbox.

Blades: Added tests for Video Alpha player.

Common: Have the capa module handle unicode better (especially errors)

Blades: Video Alpha bug fix for speed changing to 1.0 in Firefox.

Blades: Additional event tracking added to Video Alpha: fullscreen switch, show/hide
captions.

CMS: Allow editors to delete uploaded files/assets

XModules: `XModuleDescriptor.__init__` and `XModule.__init__` dropped the
`location` parameter (and added it as a field), and renamed `system` to `runtime`,
to accord more closely to `XBlock.__init__`

LMS: Some errors handling Non-ASCII data in XML courses have been fixed.

LMS: Add page-load tracking using segment-io (if SEGMENT_IO_LMS_KEY and
SEGMENT_IO_LMS feature flag is on)

Blades: Simplify calc.py (which is used for the Numerical/Formula responses); add trig/other functions.

LMS: Background colors on login, register, and courseware have been corrected
back to white.

LMS: Accessibility improvements have been made to several courseware and
navigation elements.

LMS: Small design/presentation changes to login and register views.

LMS: Functionality added to instructor enrollment tab in LMS such that invited
student can be auto-enrolled in course or when activating if not current
student.

Blades: Staff debug info is now accessible for Graphical Slider Tool problems.

Blades: For Video Alpha the events ready, play, pause, seek, and speed change
are logged on the server (in the logs).

Common: all dates and times are not time zone aware datetimes. No code should create or use struct_times nor naive
datetimes.

Common: Developers can now have private Django settings files.

Common: Safety code added to prevent anything above the vertical level in the
course tree from being marked as version='draft'. It will raise an exception if
the code tries to so mark a node. We need the backtraces to figure out where
this very infrequent intermittent marking was occurring. It was making courses
look different in Studio than in LMS.

Deploy: MKTG_URLS is now read from env.json.

Common: Theming makes it possible to change the look of the site, from
Stanford.

Common: Accessibility UI fixes.

Common: The "duplicate email" error message is more informative.

Studio: Component metadata settings editor.

Studio: Autoplay for Video Alpha is disabled (only in Studio).

Studio: Single-click creation for video and discussion components.

Studio: fixed a bad link in the activation page.

LMS: Changed the help button text.

LMS: Fixed failing numeric response (decimal but no trailing digits).

LMS: XML Error module no longer shows students a stack trace.

Studio: Add feedback to end user if there is a problem exporting a course

Studio: Improve link re-writing on imports into a different course-id

Studio: Allow for intracourse linking in Capa Problems

Blades: Videoalpha.

XModules: Added partial credit for foldit module.

XModules: Added "randomize" XModule to list of XModule types.

XModules: Show errors with full descriptors.

Studio: Add feedback to end user if there is a problem exporting a course

Studio: Improve link re-writing on imports into a different course-id

XQueue: Fixed (hopefully) worker crash when the connection to RabbitMQ is
dropped suddenly.

XQueue: Upload file submissions to a specially named bucket in S3.

Common: Removed request debugger.

Common: Updated Django to version 1.4.5.

Common: Updated CodeJail.

Common: Allow setting of authentication session cookie name.

LMS: Option to email students when enroll/un-enroll them.

