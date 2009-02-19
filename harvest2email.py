import base64
import datetime
import settings
import urllib2

import simplejson


HEADERS = [
    ('Accept', 'application/json', ),
    ('User-Agent', 'harvest2email.py/0.0', ),
    ('Authorization', ('Basic %s' % base64.encodestring('%s:%s' % (settings.USER, settings.PASSWORD)))[:-1])
]


def main():
    TODAY = datetime.date.today()

    opener = urllib2.build_opener()
    opener.addheaders = HEADERS

    day_week_started = (TODAY - datetime.timedelta(days=TODAY.weekday())).timetuple()[8]
    for i in reversed(range(day_week_started, day_week_started + 7)):
        day = (TODAY - datetime.timedelta(days=i)).strftime('/%j/%Y')
        req = urllib2.Request(settings.API_ENDPOINT + '/daily' + day)
        r = opener.open(req)

        data = simplejson.loads(''.join(r.readlines()))
        if data['day_entries']:
            print data['for_day']
            for entry in data['day_entries']:
                print ('  %s:' % entry['project']).ljust(28),
                print '%1.2f hours' % entry['hours'],
                if entry['notes']:
                    print '(%s)' % entry['notes']
                else:
                    print


if __name__ == '__main__':
    main()
