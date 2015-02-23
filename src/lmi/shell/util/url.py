import urlparse
from collections import namedtuple


SCHEME_HTTP = 'http'
SCHEME_HTTPS = 'https'

PORT_CIMXML_HTTP = 5988
PORT_CIMXML_HTTPS = 5989
PORT_WSMAN_HTTP = 5986
PORT_WSMAN_HTTPS = 5987

LOCALHOST_VARIANTS = (
    'localhost',
    'localhost.localdomain',
    'localhost4',
    'localhost4.localdomain4',
    'localhost6',
    'localhost6.localdomain6',
    '127.0.0.1',
    '::1',
)

URLParseResultTuple = namedtuple(
    'URLParseResult',
    ['scheme', 'creds', 'host', 'port', 'path'])


class URLParseResult(URLParseResultTuple):
    '''
    URL parse result.
    '''
    def __str__(self):
        url = u'%s://%s' % (self.scheme, self.host)
        if self.port is not None:
            url += u':%s' % self.port
        if self.path:
            url += u'/%s' % self.path
        return url


def is_localhost(url):
    '''
    Returns True, if url is localhost.
    '''
    return url.lower() in LOCALHOST_VARIANTS


def is_scheme_https(scheme):
    '''
    Returns True, if scheme is 'https'
    '''
    return scheme == SCHEME_HTTPS


def is_wsman_path(path):
    '''
    Returns True, if path is equal to WSMAN path of URL.
    '''
    return path.lower() == '/wsman'


def parse(url):
    '''
    Parses an url into several elements.
    '''
    scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)

    if not netloc and path:
        netloc = path
        path = ''

        if '/' in netloc:
            netloc, path = netloc.split('/', 1)
            path = '/' + path

    try:
        host, port = netloc.split(':')
    except ValueError:
        host = netloc
        port = None

    try:
        creds, host = host.split('@')
        cuser, cpass = tuple(creds.split(':'))
        creds = (cuser, cpass)
    except:
        creds = None

    return URLParseResult(scheme, creds, host, port, path)


def parse_cim(url):
    '''
    Parses an url into several elements. If some element is not present,
    default value is returned instead.
    '''
    scheme, creds, host, port, path = parse(url)

    if not scheme:
        if port:
            port_i = int(port)
            if not is_wsman_path(path) and port_i == PORT_CIMXML_HTTP:
                scheme = SCHEME_HTTP
            elif is_wsman_path(path) and port_i == PORT_WSMAN_HTTP:
                scheme = SCHEME_HTTP
            else:
                scheme = SCHEME_HTTPS
        else:
            scheme = SCHEME_HTTPS

    if port is None:
        if is_wsman_path(path):
            if is_scheme_https(scheme):
                port = PORT_WSMAN_HTTPS
            else:
                port = PORT_WSMAN_HTTP
        else:
            if is_scheme_https(scheme):
                port = PORT_CIMXML_HTTPS
            else:
                port = PORT_CIMXML_HTTP

    return URLParseResult(scheme, creds, host, port, path)
