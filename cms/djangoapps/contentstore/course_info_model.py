from xmodule.modulestore.exceptions import ItemNotFoundError
from xmodule.modulestore import Location
from xmodule.modulestore.django import modulestore
from lxml import html, etree
import re
from django.http import HttpResponseBadRequest
import logging
import django.utils

# # TODO store as array of { date, content } and override  course_info_module.definition_from_xml
# # This should be in a class which inherits from XmlDescriptor
log = logging.getLogger(__name__)


def get_course_updates(location):
    """
    Retrieve the relevant course_info updates and unpack into the model which the client expects:
    [{id : location.url() + idx to make unique, date : string, content : html string}]
    """
    try:
        course_updates = modulestore('direct').get_item(location)
    except ItemNotFoundError:
        modulestore('direct').create_and_save_xmodule(location)
        course_updates = modulestore('direct').get_item(location)

    # current db rep: {"_id" : locationjson, "definition" : { "data" : "<ol>[<li><h2>date</h2>content</li>]</ol>"} "metadata" : ignored}
    location_base = course_updates.location.url()

    # purely to handle free formed updates not done via editor. Actually kills them, but at least doesn't break.
    try:
        course_html_parsed = html.fromstring(course_updates.data)
    except:
        log.error("Cannot parse: " + course_updates.data)
        escaped = django.utils.html.escape(course_updates.data)
        course_html_parsed = html.fromstring("<ol><li>" + escaped + "</li></ol>")

    # Confirm that root is <ol>, iterate over <li>, pull out <h2> subs and then rest of val
    course_upd_collection = []
    if course_html_parsed.tag == 'ol':
        # 0 is the newest
        for idx, update in enumerate(course_html_parsed):
            if (len(update) == 0):
                continue
            elif (len(update) == 1):
                # could enforce that update[0].tag == 'h2'
                content = update[0].tail
            else:
                content = "\n".join([html.tostring(ele) for ele in update[1:]])

            # make the id on the client be 1..len w/ 1 being the oldest and len being the newest
            course_upd_collection.append({"id": location_base + "/" + str(len(course_html_parsed) - idx),
                                          "date": update.findtext("h2"),
                                          "content": content})

    return course_upd_collection


def update_course_updates(location, update, passed_id=None):
    """
    Either add or update the given course update. It will add it if the passed_id is absent or None. It will update it if
    it has an passed_id which has a valid value. Until updates have distinct values, the passed_id is the location url + an index
    into the html structure.
    """
    try:
        course_updates = modulestore('direct').get_item(location)
    except ItemNotFoundError:
        return HttpResponseBadRequest()

    # purely to handle free formed updates not done via editor. Actually kills them, but at least doesn't break.
    try:
        course_html_parsed = html.fromstring(course_updates.data)
    except:
        log.error("Cannot parse: " + course_updates.data)
        escaped = django.utils.html.escape(course_updates.data)
        course_html_parsed = html.fromstring("<ol><li>" + escaped + "</li></ol>")

    # if there's no ol, create it
    if course_html_parsed.tag != 'ol':
        # surround whatever's there w/ an ol
        if course_html_parsed.tag != 'li':
            # but first wrap in an li
            li = etree.Element('li')
            li.append(course_html_parsed)
            course_html_parsed = li
        ol = etree.Element('ol')
        ol.append(course_html_parsed)
        course_html_parsed = ol

    # No try/catch b/c failure generates an error back to client
    new_html_parsed = html.fromstring('<li><h2>' + update['date'] + '</h2>' + update['content'] + '</li>')

    # ??? Should this use the id in the json or in the url or does it matter?
    if passed_id is not None:
        idx = get_idx(passed_id)
        # idx is count from end of list
        course_html_parsed[-idx] = new_html_parsed
    else:
        course_html_parsed.insert(0, new_html_parsed)

        idx = len(course_html_parsed)
        passed_id = course_updates.location.url() + "/" + str(idx)

    # update db record
    course_updates.data = html.tostring(course_html_parsed)
    modulestore('direct').update_item(location, course_updates.data)

    if (len(new_html_parsed) == 1):
        content = new_html_parsed[0].tail
    else:
        content = "\n".join([html.tostring(ele) for ele in new_html_parsed[1:]])

    return {"id": passed_id,
            "date": update['date'],
            "content": content}


def delete_course_update(location, update, passed_id):
    """
    Delete the given course_info update from the db.
    Returns the resulting course_updates b/c their ids change.
    """
    if not passed_id:
        return HttpResponseBadRequest()

    try:
        course_updates = modulestore('direct').get_item(location)
    except ItemNotFoundError:
        return HttpResponseBadRequest()

    # TODO use delete_blank_text parser throughout and cache as a static var in a class
    # purely to handle free formed updates not done via editor. Actually kills them, but at least doesn't break.
    try:
        course_html_parsed = html.fromstring(course_updates.data)
    except:
        log.error("Cannot parse: " + course_updates.data)
        escaped = django.utils.html.escape(course_updates.data)
        course_html_parsed = html.fromstring("<ol><li>" + escaped + "</li></ol>")

    if course_html_parsed.tag == 'ol':
        # ??? Should this use the id in the json or in the url or does it matter?
        idx = get_idx(passed_id)
        # idx is count from end of list
        element_to_delete = course_html_parsed[-idx]
        if element_to_delete is not None:
            course_html_parsed.remove(element_to_delete)

        # update db record
        course_updates.data = html.tostring(course_html_parsed)
        store = modulestore('direct')
        store.update_item(location, course_updates.data)

    return get_course_updates(location)


def get_idx(passed_id):
    """
    From the url w/ idx appended, get the idx.
    """
    idx_matcher = re.search(r'.*?/?(\d+)$', passed_id)
    if idx_matcher:
        return int(idx_matcher.group(1))
