import json, requests, os, re, logging, shutil
from mnd_copy_update_request.cp_proj import copy_proj
from urllib.parse import urljoin


class copy_prod:
    source_api_info = {
        'requestType': 'getAllProjects',
        'userKey': '',
        'product_token': ''
    }
    
    _url_suffix = "api/v1.3"
    _headers = {'Content-Type': 'application/json'}
    
    def __init__(self, prod_dir: str, product_token: str, s_env: str, s_user_key: str, child_level: int=0):
        num_tabs = "" if child_level == 0 else child_level * '  '
        tabs = {"tabs": num_tabs}
        
        global logger
        logger = logging.getLogger("__main__")
        logger = logging.LoggerAdapter(logger, tabs)
        
        logger.info(f"Copying product with token {product_token}", extra=tabs)
        
        #We are just declaring/instantiating instance variables so we know everything that we use.
        self._child_level = child_level
        self._projects = {}
        self._copy_objects = []
        self.prod_dir_name = prod_dir
        self._product_token = product_token
        self._source_endpoint = s_env
        self._source_environment = urljoin(self._source_endpoint, self._url_suffix)
        self._source_user_key = s_user_key
        self._dest_org_token = ""
        self._dest_environment = ""
        self._dest_user_key = ""
        
        self.build_api_request()
        self.get_projects()
        self.create_project_structure()
    
    def build_api_request(self):
        self.source_api_info['userKey'] = self._source_user_key
        self.source_api_info['productToken'] = self._product_token
    
    def get_projects(self):
        payload = json.dumps(self.source_api_info)
        response = requests.post(self._source_environment, headers=self._headers, data=payload).content
        self._projects = json.loads(response)
    
    def create_project_structure(self):
        for project in self._projects['projects']:
            os.chdir(os.path.join(os.getcwd(), self.prod_dir_name))
            logger.debug(project)
            project_name = project['projectName']
            regex = r"[\/:#%&\{\}\\\<\>*? $!\'\"@+`|\=]"    #All characters not allowed in filenames
            subst = "-"
            project_dir = re.sub(regex, subst, project_name, 0)
            
            project['dir'] = project_dir
        
            if not os.path.exists(os.path.join(os.getcwd(), project_dir)):
                os.mkdir(os.path.join(os.getcwd(), project_dir))
            
            if self.prod_dir_name != ".":
                os.chdir("../")
    
    def set_destination(self, d_org_token: str, d_user_key: str="", d_env: str=""):
        self._dest_org_token = d_org_token
        self._dest_user_key = self._source_user_key if d_user_key == "" else d_user_key
        self._dest_environment = self._source_environment if d_env == "" else d_env
    
    def get_plugin_audit_file(self):
        logger.debug(self._projects)
        for project in self._projects['projects']:
            cp_object = copy_proj(project['dir'], project['projectToken'], self._source_endpoint, self._source_user_key, self._child_level+1)
            os.chdir(project['dir'])
            error = cp_object.get_plugin_audit_file()
            os.chdir("../")
            if error == 1:
                shutil.rmtree(cp_object.proj_dir_name)
                continue
            
            self._copy_objects.append(cp_object)
      
    def edit_plugin_audit_file(self):
        for project in self._copy_objects:
            os.chdir(project.proj_dir_name)
            project.edit_plugin_audit_file()
            os.chdir("../")

    def send_plugin_audit_file(self): 
        for project in self._copy_objects:
            os.chdir(project.proj_dir_name)
            project.set_destination(self._dest_org_token, d_user_key=self._dest_user_key, d_env=self._dest_environment)
            project.send_plugin_audit_file()
            os.chdir("../")