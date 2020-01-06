import sys, json
import time, datetime
import requests
import urlparse, urllib


class Scraper:

    def __init__(self):
        self.get_overview()

    def get_list_events(self, cursor=None, num_events=1000):
        path='/remote/v1/events'
        params = dict(
            direction='range',
            earliest_event_time=self.earliest_event_time, #1483246800,
            latest_event_time=self.latest_event_time, #1485925200,
            num_events=num_events,
            client='dashboard'
        )
        if cursor is not None:
            params.update(cursor=cursor)
        query_string = urllib.urlencode(params)
        url = urlparse.urlunparse(['https', self.HOST, path, '', query_string, ''])
        resp = requests.get(url, headers=self.HEADERS)
        if resp.status_code != 200:
            raise Exception('Bad status on events endpoint.')
        return resp.json()

    def yield_events(self):
        events = self.get_list_events()
        while events['events']:
            for evt in self.iter_attachments(events):
                yield self.make_attachment_row(evt)
            events = self.get_list_events(cursor=events['cursor'])

    def make_attachment_row(self, attach):
        tipe, singleEvent, singleAttach = attach
        if tipe == 'new_attachment':
            toPush = {}
            toPush['attachment'] = singleAttach['key']
            toPush['key'] = singleEvent['key']
            toPush['child'] = singleEvent['parent_member_display']
            toPush['create_time'] = singleEvent['create_time']
            toPush['mime_type'] = singleAttach['mime_type']
            toPush['comment'] = None
        elif tipe == 'entry':
            tmpKey = singleAttach['attachment']['key']
            toPush = {}
            toPush['attachment'] = tmpKey
            toPush['key'] = singleEvent['key']
            toPush['child'] = singleEvent['parent_member_display']
            toPush['create_time'] = singleEvent['create_time']
            toPush['mime_type'] = singleAttach['attachment']['mime_type']
            toPush['comment'] = None
        if 'note' in singleAttach:
            toPush['comment'] = singleAttach['note']
        return toPush

    def iter_attachments(self, events_response):
        for event in events_response['events']:
            for att in event.get('new_attachments', []):
                yield 'new_attachment', event, att
            for entry in event.get('entries', []):
                if 'attachment' in entry:
                    yield 'entry', event, entry

    def get_overview(self):
        path='/remote/v1/parameters'
        params = {
          'include_all_kids': 'true',
          'include_guardians': 'false'
        }
        query_string = urllib.urlencode(params)
        url = urlparse.urlunparse(['https', self.HOST, path, '', query_string, ''])
        resp = requests.get(url, headers=self.HEADERS)
        if resp.status_code != 200:
            raise Exception('Bad status on overview endpoint.')
        self.parameters = resp.json()
        return self.parameters

    @property
    def earliest_event_time(self):
        return self.parameters['first_event_time']

    @property
    def latest_event_time(self):
        return self.parameters['last_event_time']

    cooke = os.environ['TADPOLES_COOKIE']
    HEADERS = {
      'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0',
      'Accept': 'application/json, text/javascript, */*; q=0.01',
      'Accept-Language': 'en-US,en;q=0.5',
      'Accept-Encoding': 'gzip, deflate, br',
      'X-TADPOLES-UID': 'twneale@gmail.com',
      'X-Requested-With': 'XMLHttpRequest',
      'Connection': 'keep-alive',
      'Referer': 'https://www.tadpoles.com/parents',
      'Cookie': cookie
    }
    HOST = 'www.tadpoles.com'


    def date_to_unix_timestamp(date):
        d = datetime.datetime.strptime(date, '%Y-%m-%d')
        unixtime = time.mktime(d.timetuple())
        return int(unixtime)


if __name__ == '__main__':
    s = Scraper()
    for evt in s.yield_events():
        sys.stdout.write(json.dumps(evt) + '\n')

