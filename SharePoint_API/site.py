
import requests
import json
import re
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

from .lists import Lst
from .folders import Fldr


class Site(object):

    def __init__(self, object):
        self.shrpnt = object
        self.site_url = self.shrpnt.root_url


    def get_list_by_name(self, list_nm):
        _lst = Lst(self)

        _lst.list_url = "{}_api/lists/getbytitle('{}')".format(self.site_url, list_nm)
        _lst.list_name = list_nm

        return _lst

    def get_list_of_folders(self):
        get_url = "{}_api/web/Lists?$filter=Hidden eq false and BaseTemplate eq 101 and ListExperienceOptions eq 1".format(self.site_url)

        response = requests.get(get_url, headers=self.shrpnt._auth, verify=False).json()

        folders = {}
        for resp in response['value']:

            folders[resp['Title']] = resp['Id']


        fldr_dir = {}
        for fldr in folders.keys():
            
            fldr_url = "{}_api/web/lists('{}')/items?$select=FileLeafRef,FileRef&$filter=ContentType eq 'Folder'".format(self.site_url, folders.get(fldr))

            fldr_resp = requests.get(fldr_url, headers=self.shrpnt._auth, verify=False).json()

            if fldr == 'Documents':
                fldr = 'Shared Documents'
                
            regex = r"\/sites\/{}\/(.*)".format(fldr)
            sub_fldrs = [resp['FileRef'] for resp in fldr_resp['value'] if resp['FileRef'] is not None]
            sub_fldrs = [re.search(regex, sub_fldr).group(1) for sub_fldr in sub_fldrs]

            fldr_dir[fldr] = sub_fldrs

        return fldr_dir

    def get_folder_by_path(self, fldr_pth=None):

        sub_fldr_url = None
        fldrs = list(filter(None, fldr_pth.split('/')))

        if 'Documents' in fldrs[0]:
            fldr_pth.replace('Documents','Shared Documents')

            act_fldrs = ['Shared Documents']
            act_fldrs.extend(fldrs[1:])

        if 'Form Templates' in fldrs[0]:
            fldr_pth.replace('Form Templates','FormServerTemplates')

            act_fldrs = ['FormServerTemplates']
            act_fldrs.extend(fldrs[1:])


        act_fldrs_pth = "/".join(act_fldrs)

        url_insert = "/sites/{}/{}".format(self.site_name, act_fldrs_pth)
        fldr_url = "{}_api/web/GetFolderByServerRelativeUrl('{}')".format(self.site_url, url_insert)

        response = requests.get(fldr_url, headers=self.shrpnt._auth, verify=False).json()

        try:
            sub_fldr_url = response['ServerRelativeUrl']
            sub_fldr_nm = response['Name']

        except KeyError:
            raise KeyError(""" Double check Folder Path Name, spelling and case needs to be exact.""")

        _fldr = Fldr(self)
        _fldr.sub_fldr_url = sub_fldr_url
        _fldr.sub_fldr_nm = sub_fldr_nm
        _fldr.fldr_pth = fldr_pth

        return _fldr