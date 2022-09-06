
import requests
import json

class Fldr(object):

    def __init__(self, object):
        self.site = object
        self.request_digest = self.requestDigest()
        self.sub_fldr_url = None
        self.fldr_pth = None

        self.post_header = {'Content-Type': 'application/octet-stream'
            , 'Accept': 'application/json;odata=verbose'
            , 'Authorization': self.site.shrpnt._auth['Authorization']
            , 'X-HTTP-Method': 'PUT'
            , 'X-RequestDigest': self.request_digest
            , 'If-Match': ''
                            }

    def requestDigest(self):
        post_url = "{}_api/contextinfo".format(self.site.site_url)

        response = requests.post(post_url, headers=self.site.shrpnt._auth, verify=False).json()

        self.request_digest = response['FormDigestValue']

        return self.request_digest

    def download_all_files(self):

        fldr_url = "GetFolderByServerRelativeUrl('{}')".format(self.sub_fldr_url)
        get_url = "{}/_api/web/{}/Files?$select=Name,ServerRelativeUrl".format(self.site.site_url, fldr_url)

        response = requests.get(get_url, headers=self.site.shrpnt._auth, verify=False).json()

        all_files = {}
        for obj in response['value']:
            all_files[obj['Name']] = obj['ServerRelativeUrl']

        new_headers = self.shrpnt._auth
        new_headers['Accept'] = 'application/json;odata=verbose'

        for key, value in all_files.items():
            file_url = "GetFolderByServerRelativeUrl('{}')".format(self.sub_fldr_url)
            get_file_url = "{}_api/web/{}/Files('{}')/$value".format(self.site.site_url, file_url, key)

            response = requests.get(get_file_url, headers=new_headers, verify=False)

            with open(key, "wb") as f:
                f.write(response.content)
                f.close()
                print('{} - has been downloaded'.format(key))

        return

    def download_file_by_name(self, file_name=None):

        new_headers = self.site.shrpnt._auth
        new_headers['Accept'] = 'application/json;odata=verbose'

        file_url = "GetFolderByServerRelativeUrl('{}')".format(self.sub_fldr_url)
        get_file_url = "{}_api/web/{}/Files('{}')/$value".format(self.site.site_url, file_url, file_name)

        response = requests.get(get_file_url, headers=new_headers, verify=False)
        with open(file_name, "wb") as f:
            f.write(response.content)
            f.close()
            print('{} - has been downloaded'.format(file_name))

        return

    def upload_all_files(self, list_files=None):

        if type(list_files) != list:
            return print('File Names are not in a list.')

        post_header = self.post_header

        fldr_url = "GetFolderByServerRelativeUrl('{}')".format(self.sub_fldr_url)
        base_post_url = "{}_api/web/{}/Files".format(self.site.site_url, fldr_url)

        for file in list_files:
            with open(file, "rb") as f:
                post_url = "{}/Add(url='{}', overwrite=true)".format(base_post_url, file)
                response = requests.post(post_url, data=f.read(), headers=post_header, verify=False)
                print('{} - has been uploaded'.format(file))

        return

    def upload_file_by_name(self, file_name=None):

        post_header = self.post_header

        fldr_url = "GetFolderByServerRelativeUrl('{}')".format(self.sub_fldr_url)
        post_url = "{}_api/web/{}/Files/Add(url='{}', overwrite=true)".format(self.site.site_url, fldr_url, file_name)

        with open(file_name, "rb") as f:
            response = requests.post(post_url, data=f.read(), headers=post_header, verify=False)
            print('{} - has been uploaded'.format(file_name))

        return

    def list_fldr_files(self):

        fldr_fls = {} # Empty dict to return folders/files

        #Get folders within the given folder path
        fldr_url = "GetFolderByServerRelativeUrl('{}')".format(self.sub_fldr_url)
        get_fldr_url = "{}/_api/web/{}/Folders?$select=Name,ServerRelativeUrl".format(self.site.site_url, fldr_url)
        fldr_resp = requests.get(get_fldr_url, headers=self.site.shrpnt._auth, verify=False).json()

        fldr_nms = [folder['Name'] for folder in fldr_resp['value']]

        # Get files within the given folder path
        get_fl_url = "{}/_api/web/{}/Files?$select=Name,ServerRelativeUrl".format(self.site.site_url, fldr_url)
        fl_resp = requests.get(get_fl_url, headers=self.site.shrpnt._auth, verify=False).json()

        fl_nms = [file['Name'] for file in fl_resp['value']]

        fldr_fls['Folders'] = fldr_nms
        fldr_fls['Files'] = fl_nms       

        return fldr_fls

    def create_sub_fldr(self, fldr_nm):

        post_header = self.post_header
        post_header['Content-Type'] = "application/json"

        fldr_url = "GetFolderByServerRelativeUrl('{}')".format(self.sub_fldr_url)
        post_url = "{}_api/web/{}/Folders/Add(url='{}')".format(self.site.site_url, fldr_url, fldr_nm)

        response = requests.post(post_url, headers=post_header, verify=False)

        return

    def delete_file(self, file_name=None):

        new_headers = self.post_header
        new_headers['X-HTTP-Method'] = "DELETE"

        file_url = "GetFileByServerRelativeUrl('/{}/{}')".format(self.sub_fldr_url, file_name)
        get_file_url = "{}_api/web/{}".format(self.site.site_url, file_url)

        response = requests.post(get_file_url, headers=new_headers, verify=False)

        print('{} - has been deleted'.format(file_name))

        return

    def view_link(self, file_name=None):

        new_headers = self.site.shrpnt._auth
        new_headers['Accept'] = 'application/json;odata=nometadata'

        file_url = "GetFileByServerRelativeUrl('/{}/{}')".format(self.sub_fldr_url, file_name)
        get_file_url = "{}_api/web/{}".format(self.site.site_url, file_url, file_name)

        response = requests.get(get_file_url, headers=new_headers, verify=False).json()

        link = response['LinkingUri']

        return link
    
    def download_link(self, file_name=None):

        rt_st = '/'.join(self.site.site_url.split('/')[:-2])

        link = '{site}{sub_fldr_url}/{file}'.format(site=rt_st, sub_fldr_url=self.sub_fldr_url, file=file_name).replace(' ', '%20')

        return link

