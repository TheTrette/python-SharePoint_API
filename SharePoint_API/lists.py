import requests
import json
import pandas as pd
from urllib3.exceptions import InsecureRequestWarning
from .items import Itm
from .sharepoint_utils import *

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


class Lst(object):

    def __init__(self, object):
        self.site = object
        self._list_url = None
        self.list_name = None
        self.request_digest = self.requestDigest()

        self.post_header = {'Content-Type': 'application/json;odata=verbose'
            , 'Accept': 'application/json;odata=verbose'
            , 'Authorization': self.site.shrpnt._auth['Authorization']
            , 'X-HTTP-Method': ''
            , 'X-RequestDigest': self.request_digest
            , 'If-Match': ''
                            }

    @property
    def list_url(self):
        return self._list_url

    @list_url.setter
    def list_url(self, value):

        self._list_url = value

        if not self.list_url == None:
            self.list_entity = self.listEntity()
            self.list_id = self.listID()
            self.list_schema = self.get_schema()

    def requestDigest(self):
        post_url = "{}_api/contextinfo".format(self.site.site_url)

        response = requests.post(post_url, headers=self.site.shrpnt._auth, verify=False).json()

        self.request_digest = response['FormDigestValue']

        return self.request_digest

    def list_info(self):
        response = requests.get(self.list_url, headers=self.site.shrpnt._auth, verify=False).json()
        return print('{} - ID: {}'.format(response['Title'], response['Id']))

    def listID(self):
        url = "{}?$select=ID".format(self.list_url)

        response = requests.get(url, headers=self.site.shrpnt._auth, verify=False).json()

        self.list_id = response['Id']

        return self.list_id

    def listEntity(self):
        url = "{}?$select=ListItemEntityTypeFullName".format(self.list_url)

        response = requests.get(url, headers=self.site.shrpnt._auth, verify=False).json()

        self.list_entity = response['ListItemEntityTypeFullName']

        return self.list_entity

    # TODO remove reference to Title, leverage static name field
    def get_all_items(self, title_nm='Title', orient='records'):
        fields = self.get_fields()
        fields.remove(title_nm)
        fields.append('Title')
        ids = ['ID', 'GUID']
        fields.extend(ids)

        all_items = []
        url = "{}/items?$top=5000".format(self.list_url)
        response = requests.get(url, headers=self.site.shrpnt._auth, verify=False).json()

        for result in response['value']:
            items = {}
            for field in fields:
                if field == 'Title':
                    items[title_nm] = result['Title']
                else:
                    items[field] = result[field]

            all_items.append(items)

        if orient == 'dataframe':
            all_items = to_dataframe(all_items)

        elif orient == 'records':
            all_items

        elif orient == None:
            print("""Please select a structure for the list items to return in:
            'records': a list of dictionaries
            'dataframe': a pandas DataFrame
            """)

        return all_items

    # TODO remove reference to Title, leverage static name field
    def upload_all_items(self, title_nm='Title', data=None, action=None):

        if type(data) != pd.core.frame.DataFrame:
            print("""Please convert data into a pandas DataFrame""")

        data_types = {}
        for key in self.list_schema.keys():
            data_types[key] = self.list_schema[key]['TypeAsString']

        data = convert_dtypes(df=data, data_types=data_types)

        if action == 'override':

            get_url = "{}_api/lists('{}')/items".format(self.site.site_url, self.list_id)

            new_head = {'Content-Type': 'application/json;odata=nometadata'
                , 'Accept': 'application/json;odata=nometadata'
                , 'Authorization': self.site.shrpnt._auth['Authorization']
                , 'X-HTTP-Method': ''
                , 'X-RequestDigest': self.request_digest
                , 'If-Match': ''
                        }

            get_resp = requests.get(get_url, headers=new_head, verify=False).json()

            rec_ids = []
            for rec in get_resp['value']:
                rec_ids.append(rec['ID'])

            url = "{}_api/lists('{}')".format(self.site.site_url, self.list_id)

            self.post_header["X-HTTP-Method"] = "DELETE"
            self.post_header["If-Match"] = "*"

            for rec_id in rec_ids:
                rec_url = "{}/items({})".format(url, rec_id)

                del_resp = requests.post(rec_url, headers=self.post_header, verify=False)

        fields = self.get_fields()

        url = "{}_api/lists('{}')/items".format(self.site.site_url, self.list_id)

        self.post_header["X-HTTP-Method"] = ""
        self.post_header["If-Match"] = ""

        # lst_nm = self.site._list_name
        item_data = {'__metadata': {'type': self.list_entity}}
        for row in data:
            for key in row.keys():
                if key in fields and key != title_nm:
                    if row[key] == 'None':
                        row[key] = None

                    item_data[key] = row[key]

                elif key in fields and key == title_nm:
                    if row[key] == 'None':
                        row[key] = None

                    item_data['Title'] = row[key]
                else:
                    pass

            self.response = requests.post(url, data=str(json.dumps(item_data)), headers=self.post_header, verify=False)

        return print('Records are uploaded to List...')

    def get_fields(self):
        url = "{}/fields?$filter=Hidden eq false and ReadOnlyField eq false and JSLink ne null and InternalName ne 'Attachments'".format(
            self.list_url)
        self.response = requests.get(url, headers=self.site.shrpnt._auth, verify=False).json()

        fields = []
        for resp in self.response['value']:
            fields.append(resp['Title'])

        schema = {}
        for resp in self.response['value']:
            schema[resp['Title']] = {"StaticName": resp['StaticName']
                , "Title": resp['Title']
                , "FieldTypeKind": resp['FieldTypeKind']
                , "TypeAsString": resp['TypeAsString']
                , "TypeDisplayName": resp['TypeDisplayName']}

        self.list_schema = schema

        return fields


    def get_schema(self):
        url = "{}/fields?$filter=Hidden eq false and ReadOnlyField eq false and JSLink ne null and InternalName ne 'Attachments'".format(
            self.list_url)
        self.response = requests.get(url, headers=self.site.shrpnt._auth, verify=False).json()

        schema = {}
        for resp in self.response['value']:
            schema[resp['Title']] = {"StaticName": resp['StaticName']
                , "Title": resp['Title']
                , "FieldTypeKind": resp['FieldTypeKind']
                , "TypeAsString": resp['TypeAsString']
                , "TypeDisplayName": resp['TypeDisplayName']}

        return schema
