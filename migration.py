#!/usr/bin/env python3
import argparse
import xml.etree.ElementTree as ET
import ssl
import urllib.request
from urllib.error import HTTPError


class CalendarServer(object):

    def __init__(self, config=None, url_root=None):
        self.config = config or {
            'CALENDAR': 'http://localhost:5232/'
        }
        if url_root is not None:
            self.url_host = url_root
            self.url_root = url_root
        else:
            self.url_host = self.config['CALENDAR']
            self.url_root = self.config['CALENDAR']
        self.opener = self.get_opener()

    @property
    def url(self):
        return self.url_root

    def get_opener(self):
        handlers = []
        if self.url_root.startswith('https'):
            context = ssl._create_unverified_context()
            https_handler = urllib.request.HTTPSHandler(context=context)
            handlers.append(https_handler)
        if self.config.get('CALENDAR_PASSWORD'):
            auth_handler = urllib.request.HTTPBasicAuthHandler()
            auth_handler.add_password(
                'Radicale',
                self.config['CALENDAR'].split('%')[0],
                'radicale',
                self.config['CALENDAR_PASSWORD'])
            handlers.append(auth_handler)
        return urllib.request.build_opener(*handlers)

    def open(self, method='GET', data=None, path=None, headers=None):
        if path:
            if self.url_host not in path:
                url = self.url_host + path
            else:
                url = path
            assert self.url in url
        else:
            url = self.url

        print(
            'Radicale %s on %s' % (method, url))

        kw = dict(
            url=url,
            method=method,
        )
        if headers:
            kw['headers'] = headers

        if data:
            kw['data'] = data.encode('utf-8')
        request = urllib.request.Request(**kw)

        with self.opener.open(request) as answer:
            response = answer.read().decode('utf-8')
            if 200 <= answer.status < 300:
                return response
            raise HTTPError(
                request.full_url, answer.status, response,
                request.headers, request.fp)

    def get(self, href=None, raise_if_not_found=False):
        print('Getting %r %s' % (self, href))
        try:
            kw = {}
            if href is not None:
                kw['path'] = href
            return href, self.open('GET', **kw)
        except HTTPError as e:
            if e.code == 404 and not raise_if_not_found:
                return
            raise

    def propfind(self, href=None, raise_if_not_found=False):
        print('Propfinding %r %s' % (self, href))
        try:
            kw = {}
            if href is not None:
                kw['path'] = href
            kw['headers'] = {'depth': 1}
            return href, self.open('PROPFIND', **kw)
        except HTTPError as e:
            if e.code == 404 and not raise_if_not_found:
                return
            raise

    def put(self, path_data):
        href, data = path_data
        try:
            return self.open('PUT', data, href)
        except HTTPError as e:
            print("Error while putting to %s" % href)

    def find_children_path(self, href=None):
        """ Return list of tuple: (path, is_calendar_resource) """
        if href is None:
            href = '/'
        ns = {
            "DAV": "DAV:",
            "C": "urn:ietf:params:xml:ns:caldav",
            "CS": "http://calendarserver.org/ns/",
            "ICAL": "http://apple.com/ns/ical/",
            "CR": "urn:ietf:params:xml:ns:carddav"}
        path, xml = self.propfind(href)
        root = ET.fromstring(xml)
        children = []
        for response in root.findall('DAV:response', ns):
            if response.find('DAV:href', ns).text != path:
                uri = "DAV:propstat/DAV:prop/DAV:resourcetype/"
                if (response.find(uri + 'C:calendar', ns) is not None or
                        response.find(uri + 'CR:addressbook', ns) is not None):
                    children.append(
                        (response.find('DAV:href', ns).text, False))
                else:
                    children.append((response.find('DAV:href', ns).text, True))
        return children

    def calendar_iterator(self, path=None):
        results = []
        path_list = self.find_children_path(path)
        for path, is_dir in path_list:
            if is_dir:
                results.extend(self.calendar_iterator(path))
            else:
                results.append(path)
        return results

if __name__ == '__main__':

    parser = argparse.ArgumentParser(usage="migration.py <from_url> <to_url>")
    parser.add_argument('from_url')
    parser.add_argument('to_url')
    args = parser.parse_args()

    from_server = CalendarServer({'CALENDAR': args.from_url})
    to_server = CalendarServer(config={'CALENDAR': args.to_url})

    for cal in from_server.calendar_iterator():
        to_server.put(from_server.get(cal))
