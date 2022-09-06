
class Itm(object):

    def __init__(self, object):
        self.lst = object


    def update_item(self, field, value):
        _field = field.replace(" " ,"")
        auth_bear = "Bearer {}".format(self.lst.site.shrpnt.token)

        field_data = {'__metadata': {'type': self.lst.list_entity }}
        field_data[_field] = value

        url = "{}/items({})/".format(self.lst.site._list, self.lst.item_id)

        new_headers = self.lst.site.shrpnt._auth
        new_headers['Accept'] = 'application/json;odata=verbose'

        etag = requests.get(url, headers=new_headers).json()['d']['__metadata']['etag']
        self.lst.post_header['If-Match'] = etag
        self.lst.post_header['X-HTTP-Method'] = 'MERGE'
        requests.post(url, data=str(field_data), headers=self.lst.site.post_header, verify=False)

        get_url = "{}/items({})/".format(self.lst.site._list, self.lst.item_id)
        response = requests.get(get_url, headers=self.lst.site.shrpnt._auth, verify=False).json()

        return print("'{}' column has been updated to: '{}''".format(field, response['d'][_field]))
