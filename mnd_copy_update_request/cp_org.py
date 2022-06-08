import json, requests, os, re, logging, shutil
from cp_prod import copy_prod
from urllib.parse import urljoin

class copy_org:
    source_api_info = {
        'requestType': 'getAllProducts',
        'userKey': '',
        'orgToken': ''
    }

    _url_suffix = "api/v1.3"
    _headers = {'Content-Type': 'application/json'}

    
    def __init__(self, s_org_token: str, s_env: str, s_user_key:str, d_org_token: str, d_env=None, d_user_key=None):
        
        #We are just declaring/instantiating instance variables so we know everything that we use.
        self._products = {}
        self._copy_objects = []
        self._source_org_token = ""
        self._source_endpoint = ""
        self._source_environment = ""
        self._source_user_key = ""
        self._dest_org_token = ""
        self._dest_environment = ""
        self._dest_user_key = ""
        
        logging.info(f"Copying organization with token {s_org_token}")
        self._source_endpoint = s_env
        self._source_environment = urljoin(self._source_endpoint, self._url_suffix)
        self._source_user_key = s_user_key
        self._source_org_token = s_org_token
        
        if d_env == None:
            d_env = s_env
        if d_user_key == None:
            d_user_key = s_user_key
        
        self._dest_environment = d_env
        self._dest_user_key = d_user_key
        self._dest_org_token = d_org_token
        
        self.build_api_request()
        self.get_products()
        self.create_product_structure()
    
    def build_api_request(self):
        self.source_api_info['userKey'] = self._source_user_key
        self.source_api_info['orgToken'] = self._source_org_token
    
    def get_products(self):
        payload = json.dumps(self.source_api_info)
        response = requests.post(self._source_environment, headers=self._headers, data=payload).content
        self._products = json.loads(response)
        
    def create_product_structure(self):
        for product in self._products['products']:
            product_name = product['productName']
            regex = r"[\/:#%&\{\}\\\<\>*? $!\'\"@+`|\=]"    #All characters not allowed in filenames
            subst = "-"
            product_dir = re.sub(regex, subst, product_name, 0)
            product['dir'] = product_dir
            if not os.path.exists(os.path.join(os.getcwd(), product_dir)):
                os.mkdir(os.path.join(os.getcwd(), product_dir))
    
    def get_plugin_audit_file(self):
        for product in self._products['products']:
            cp_object = copy_prod(product['dir'], product['productToken'], self._source_endpoint, self._source_user_key, self._dest_org_token, self._dest_environment, self._dest_user_key)
            os.chdir(product['dir'])
            cp_object.get_plugin_audit_file()
            os.chdir("..")
            if os.listdir(product['dir']) == []:
                shutil.rmtree(product['dir'])
                continue
            
            self._copy_objects.append(cp_object)
    
    def edit_plugin_audit_file(self):
        for product in self._copy_objects:
            os.chdir(product.prod_dir_name)
            product.edit_plugin_audit_file()
            os.chdir("../")
    
    def send_plugin_audit_file(self):
        for product in self._copy_objects:
            os.chdir(product.prod_dir_name)
            product.send_plugin_audit_file()
            os.chdir("../")