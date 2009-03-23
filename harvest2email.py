import base64
import datetime
import re
import settings
import urllib2

import simplejson

from htmlentities import decode_htmlentities

HEADERS = [
    ('Authorization', ('Basic %s' % base64.encodestring('%s:%s' % (settings.USER, settings.PASSWORD)))[:-1]),
    ('User-Agent', 'harvest2email.py/0.0', ),
]

JSON_HEADERS = HEADERS + [('Accept', 'application/json', )]

XML_HEADERS = HEADERS + [('Accept', 'application/xml', ), ('Content-Type', 'application/xml', )]


json_opener = urllib2.build_opener()
json_opener.addheaders = JSON_HEADERS

xml_opener = urllib2.build_opener()
xml_opener.addheaders = XML_HEADERS


def _call_harvest(url):
    req = urllib2.Request(settings.API_ENDPOINT + url)
    r = json_opener.open(req)
    return simplejson.loads(''.join(r.readlines()))


def _get_project_code(project_id):
    req = urllib2.Request(settings.API_ENDPOINT + ('/projects/%d' % project_id))
    r = xml_opener.open(req)
    xml = ''.join(r.readlines())
    #print xml
    m = re.search(r'<code>(.*)</code>', xml)
    return m.groups(1)[0]


def main():
    TODAY = datetime.date.today()

    day_week_started = (TODAY - datetime.timedelta(days=TODAY.weekday()))
    # If it's a Monday, run last week's report
    if TODAY.weekday() == 0:
        day_week_started = (day_week_started - datetime.timedelta(days=7))

    project_codes = {}

    for i in range(0, 5):
        day = (day_week_started + datetime.timedelta(days=i)).strftime('/%j/%Y')

        data = _call_harvest('/daily' + day)

        if data['day_entries']:
            print data['for_day']
            for entry in data['day_entries']:
                project_id = int(entry['project_id'])
                if project_id not in project_codes:
                    project_codes[project_id] = _get_project_code(project_id)
                print decode_htmlentities('  [%s] %s %s %s:' % (project_codes[project_id], entry['client'], entry['project'], entry['task'])).ljust(56),
                print '%1.2f hours' % entry['hours'],
                if entry['notes']:
                    print '(%s)' % decode_htmlentities(entry['notes'])
                else:
                    print


if __name__ == '__main__':
    main()
