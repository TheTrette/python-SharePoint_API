import requests
import json
import re

from .site import Site


class ShrPnt(object):
    """ """

    def __init__(self, client_id, client_secret, root_url):
        self.client_id = client_id
        self.client_secret = client_secret
        self.root_url = root_url

        self.accept = "application/json;odata=nometadata"
        self.authenticate = self.Authenticate(self.client_id, self.client_secret, self.root_url)
        self.token = self.get_token()
        self._auth = self.auth()

    # Auth child Class to ShrPnt parent ==========================================
    class Authenticate():

        def __init__(self, c_id, c_scrt, rt_url):
            self.auth_id = '{}'.format(c_id)
            self.auth_scrt = c_scrt
            self.rt_url = re.search(r'\/\/(.*\.com)\/.*', rt_url).group(1)
            self.params = {'grant_type': 'client_credentials'
                ,
                           'resource': '00000003-0000-0ff1-ce00-000000000000/{}'.format(self.rt_url)
                           }
            self.headers = {'Content-type': 'application/x-www-form-urlencoded'}

        def authorize(self):
            post_url = "https://accounts.accesscontrol.windows.net/tokens/OAuth/2"

            self.params['client_id'] = self.auth_id
            self.params['client_secret'] = self.auth_scrt

            response = requests.post(post_url, data=self.params, headers=self.headers).json()

            self.access_token = response['access_token']

            return self.access_token

    def get_token(self):
        return self.authenticate.authorize()

    def auth(self):
        auth_bear = "Bearer {}".format(self.token)
        headers = {'Content-type': 'application/json;odata=verbose'}
        headers.update({'Accept': self.accept
                           , 'Authorization': auth_bear
                        })
        return headers

    def get_site(self, site_name):
        _site_url = "{}{}/".format(self.root_url, site_name)

        _site = Site(self)

        _site.site_url = _site_url
        _site.site_name = site_name

        return _site
