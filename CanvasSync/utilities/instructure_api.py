"""
CanvasSync by Mathias Perslev
February 2017

--------------------------------------------

instructure_api.py

The InstructureApi object is initialized with a Settings object from the CanvasSync.py module.
This class implements the basic API calling functionality to the Canvas by Instructure server.

requests is used to do https communication with the server. The server domain and authentication token is
loaded from the Settings object. The Instructure API uses the JSON format to transmit data objects over the internet
in attribute-value pairs. The json module is used to easily convert this format into a Python dictionary object.

The InstructureApi object implements various methods that will fetch resources from the server such as lists of courses,
modules and files that the user has authentication to access.
"""
import json
import requests


class InstructureApi(object):
    def __init__(self, settings):
        """
        settings : string | A Settings object used to load domain and token attributes
        """
        self.settings = settings

    def _get(self, api_call):
        """
        [PRIVATE] Implements the basic GET call to the API. The get_json method wraps around this method.

        api_call : string | Any call to the Instructure API ("/api/v1/courses" for instance)
        """
        return requests.get(u"%s%s" % (self.settings.domain, api_call),
                            headers=self.get_auth_header())

    def _post(self, api_call, **kwargs):
        """
        [PRIVATE] Implements the basic POST call to the API. The post_json method wraps around this method.

        api_call : string | Any call to the Instructure API ("/api/v1/courses" for instance)
        """
        headers = {**self.get_auth_header(), **kwargs.pop('headers', {})}
        return requests.post(u"%s%s" % (self.settings.domain, api_call), headers=headers, **kwargs)

    def _put(self, api_call, **kwargs):
        """
        [PRIVATE] Implements the basic PUT call to the API. The put_json method wraps around this method.

        api_call : string | Any call to the Instructure API ("/api/v1/courses" for instance)
        """
        headers = {**self.get_auth_header(), **kwargs.pop('headers', {})}
        return requests.put(u"%s%s" % (self.settings.domain, api_call), headers=headers, **kwargs)

    def get_auth_header(self):
        return {u'Authorization': u"Bearer %s" % self.settings.token}

    def get_json(self, api_call):
        """
        A wrapper around the private _get method that will call _get with a specified API call and return the json
        digested dictionary.

        api_call : string | Any call to the Instructure API ("/api/v1/courses" for instance)
        """
        res = self._get(api_call)
        res.raise_for_status()
        return json.loads(res.text)

    def post_json(self, api_call, body, **kwargs):
        """
        A wrapper around the private _get method that will call _post with a specified API call and return the json
        digested dictionary.

        api_call : string | Any call to the Instructure API ("/api/v1/courses" for instance)
        body     : dict   | Dictionary representing the body of the payload
        """
        res = self._post(api_call, data=body, **kwargs)
        res.raise_for_status()
        return json.loads(res.text)

    def put_json(self, api_call, body, **kwargs):
        """
        A wrapper around the private _get method that will call _put with a specified API call and return the json
        digested dictionary.

        api_call : string | Any call to the Instructure API ("/api/v1/courses" for instance)
        body     : object | Dictionary representing the body of the payload
        """
        res = self._put(api_call, data=body, **kwargs)
        res.raise_for_status()
        return json.loads(res.text)

    def get_json_list(self, api_call):
        data = self.get_json(api_call)
        if not isinstance(data, (list, tuple)):
            data = []
        return data

    def get_courses(self):
        """
        Returns a list of course dictionaries.
        """
        return self.get_json_list(u"/api/v1/courses?per_page=100")

    def get_modules_in_course(self, course_id):
        """
        Returns a list of dictionaries on the Canvas modules located in a given course.

        course_id : int | A course ID number
        """
        return self.get_json_list(u"/api/v1/courses/%s/modules?per_page=100" % course_id)

    def get_files_in_folder(self, folder_id):
        """
        Returns a list of dictionaries on the Canvas files located in a given folder

        folder_id : int | A folder ID number
        """
        return self.get_json_list(u"/api/v1/folders/%s/files?per_page=100" % folder_id)

    def get_folders_in_folder(self, folder_id):
        """
        Returns a list of dictionaries on the Canvas folders located in a given folder

        folder_id : int | A folder ID number
        """
        return self.get_json_list(u"/api/v1/folders/%s/folders?per_page=100" % folder_id)

    def get_files_in_course(self, course_id):
        """
        Returns a list of dictionaries on the Canvas files located in a given course.

        course_id : int | A course ID number
        """
        return self.get_json_list(u"/api/v1/courses/%s/files?per_page=100" % course_id)

    def get_folders_in_course(self, course_id):
        """
        Returns a list of dictionaries on the Canvas folders located in a given course.

        course_id : int | A course ID number
        """
        return self.get_json_list(u"/api/v1/courses/%s/folders?per_page=100" % course_id)

    def get_items_in_module(self, course_id, module_id):
        """
        Returns a dictionary of items located in a given module in a given course

        course_id : int | A course ID number
        module_id : int | A module ID number
        """
        return self.get_json(u"/api/v1/courses/%s/modules/%s/items?per_page=100" % (course_id, module_id))

    def download_item_information(self, url):
        """
        Returns a dictionary of information on a specified item

        url : string | The API url pointing to information on a specified file in the Canvas system
        """
        url = url.split(self.settings.domain)[-1]
        return self.get_json(url)

    def download_file_payload(self, donwload_url):
        """
        Returns the payload of a specified file in the Canvas system

        donwload_url : string | The API download url pointing to a file in the Canvas system
        """
        url = donwload_url.split(self.settings.domain)[-1]
        return self._get(url).content

    def get_assignments_in_course(self, course_id):
        """
        Returns a list of dictionaries of information on assignment objects under a course ID

        course_id : int | A course ID number
        """
        return self.get_json_list(u"/api/v1/courses/%s/assignments?per_page=100" % course_id)

    def download_page_information(self, course_id, page_id):
        """
        Returns a dictionaries of information on a Page object

        course_id : int | A course ID number
        page_id : int | A page ID number
        """
        return self.get_json(u"/api/v1/courses/%s/pages/%s" % (course_id, page_id))

    def upload_file(self, course_id, body):
        """
        Uploads a file into Canvas system

        course_id : int  | A course ID number
        body      : dict | Dictionary representing the file to upload
        """
        return self.post_json(u"/api/v1/courses/%s/files" % course_id, body)

    def upload_module_item(self, course_id, module_id, body):
        """
        Uploads an item into a module

        course_id : int | A course ID number
        module_id : int | A module ID number
        """
        return self.post_json(u"/api/v1/courses/%s/modules/%s/items" % (course_id, module_id), json.dumps(body),
                              headers={'content-type': 'application/json'})

    def update_file(self, course_id, body):
        """
        Updates a file in the Canvas system

        course_id : int  | A course ID number
        body      : dict | Dictionary representing the file to update
        """
        return self.put_json(u"/api/v1/courses/%s/files" % course_id, body)

    def get_file_by_id(self, file_id):
        """
        Returns a dictionaries of information on a File object

        file_id: int | A file ID number
        """
        return self.get_json(u"/api/v1/files/%s" % file_id)

    def upload_file_by_folder(self, folder_id, body):
        """
        Uploads a file into Canvas system

        folder_id : int  | A folder ID number
        body      : dict | Dictionary representing the file to upload
        """
        return self.post_json(u"/api/v1/folders/%s/files" % folder_id, body)

    def upload_file_to_url(self, upload_url, upload_params, files):
        """
        Uploads a file into Canvas upload url

        upload_url    : string | Upload url returned from Canvas
        upload_params : dict   | Upload params returned from Canvas
        files         : dict   |  Dictionary representing files to be uploaded
        """
        return requests.post(upload_url,  params=upload_params, files=files)