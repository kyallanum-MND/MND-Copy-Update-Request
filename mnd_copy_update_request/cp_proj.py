from urllib.parse import urljoin, urlencode
import requests, json, os, time, logging

class copy_proj:
    source_api_info = {
        'requestType': 'getPluginAuditFile',
        'userKey': '',
        'requestToken': ''
    }
    _url_suffix = "api/v1.3"
    _headers = {'Content-Type': 'application/json'}

    
    def __init__(self, proj_dir:str, project_token: str, s_env: str, s_user_key: str, d_org_token, d_env=None, d_user_key=None):
        
        #We are just declaring/instantiating instance variables so we know everything that we use.
        self.proj_dir_name = ""
        self._project_token = ""
        self._source_environment = ""
        self._source_user_key = ""
        self._dest_environment = ""
        self._dest_user_key = ""
        self._dest_org_token = ""
        self._request_token = ""
        
        logging.info(f"Copying project with token {project_token}.")
        self._source_environment = urljoin(s_env, self._url_suffix)
        self._source_user_key = s_user_key
        self._project_token = project_token
        
        if d_env == None:
            d_env = s_env
        if d_user_key == None:
            d_user_key = s_user_key
            
        self._dest_environment = d_env
        self._dest_user_key = d_user_key
        self._dest_org_token = d_org_token
        self.proj_dir_name = proj_dir
        
        self.get_project_vitals()
        self.build_api_request()
        
    def get_project_vitals(self) -> None:
        vital_api = {
            'requestType': 'getProjectVitals',
            'userKey': self._source_user_key,
            'projectToken': self._project_token
        }
        
        payload = json.dumps(vital_api)
        vitals = requests.post(self._source_environment, headers=self._headers, data=payload).content
        vitals_obj = json.loads(vitals)
        
        self._request_token = vitals_obj['projectVitals'][0]['requestToken']
    
    def build_api_request(self) -> None:
        self.source_api_info['userKey'] = self._source_user_key
        self.source_api_info['requestToken'] = self._request_token

    def get_plugin_audit_file(self) -> int:
        payload = json.dumps(self.source_api_info)
        update_request = requests.post(self._source_environment, headers=self._headers, data=payload).content
        update_request_obj = json.loads(update_request)
        
        if update_request_obj == {}:
            return 1
        
        logging.info(f"Getting update request for {self._project_token}.")
        with open(os.path.join(os.getcwd(), "update-request.json"), 'w') as file:
            json.dump(update_request_obj, file)
        
        return 0
            
    def edit_plugin_audit_file(self) -> None:
        with open(os.path.join(os.getcwd(), "update-request.json"), 'rb') as file:
            update_request = json.load(file)
            
        if update_request['updateType'] == "":
            update_request['updateType'] = "OVERRIDE"
        if update_request['type'] == "":
            update_request['type'] = "UPDATE"
        if update_request['agent'] == "":
            update_request['agent'] = 'fs-agent'
        if update_request['pluginVersion'] == "":
            version = json.loads(requests.get("https://api.github.com/repos/whitesource/unified-agent-distribution/releases/latest").content)['tagname'][1:]
            update_request['pluginVersion'] = version
        if update_request['product'] == "":
            update_request['product'] = "Py_Script"
        if update_request['timeStamp'] == "":
            update_request['timeStamp'] = int(time.time())
        
        update_request['userKey'] = self._dest_user_key
        del update_request['orgToken']
        update_request['token'] = self._dest_org_token
        
        diff = update_request.pop('projects')
        update_request['diff'] = diff
        
        
        with open(os.path.join(os.getcwd(), "update-request.json"), 'w') as file:
            json.dump(update_request, file)

    def send_plugin_audit_file(self) -> None:
        dest_url = urljoin(self._dest_environment, "agent")
        dest_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        with open(os.path.join(os.getcwd(), "update-request.json"), 'rb') as file:
            update_request_obj = json.load(file)
            
        dest_payload = urlencode(update_request_obj)
        
        logging.info(f"Sending update request for project token: {self._project_token}")
        response = requests.post(dest_url, headers=dest_headers, data=dest_payload)
        logging.debug(response.content)