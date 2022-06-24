import logging, argparse, os, shutil
from datetime import datetime
from turtle import down
from mnd_copy_update_request.cp_org import copy_org
from mnd_copy_update_request.cp_prod import copy_prod
from mnd_copy_update_request.cp_proj import copy_proj
from mnd_copy_update_request._version import __tool_name__, __version__, __description__

class _context_filter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, "tabs"):
            record.tabs = ""
        return True

logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(tabs)s%(message)s')

stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.addFilter(_context_filter())

logger.setLevel(logging.INFO)

COPY_PROJ = "proj"
COPY_PROD = "prod"
COPY_ORG = "org"
COPY_TYPES = [COPY_PROJ, COPY_PROD, COPY_ORG]

args = None

def parseargs():
    parser = argparse.ArgumentParser(description=__description__)
    subparsers = parser.add_subparsers()
    copy_parser = subparsers.add_parser('copy', help="Copy Update Requests")
    download_parser = subparsers.add_parser('download', help="Download Update Requests")
    
    copy_parser.add_argument("-t", "--type", help="Type of copy (proj, prod, org)", dest="c_type", choices=COPY_TYPES, default="proj")
    copy_parser.add_argument("-se", "--s-env", help="Source Environment (saas, saas-eu, app, app-eu)", dest="s_env", type=str, required=True)
    copy_parser.add_argument("-sk", "--s-token", help="Token of object to copy", dest="s_token", type=str, required=True)
    copy_parser.add_argument("-su", "--s-userkey", help="Source UserKey", dest="s_user_key", type=str, required=True)
    copy_parser.add_argument("-de", "--d-env", help="The destination environment. If none, same as source environment", dest="d_env", type=str, required=False)
    copy_parser.add_argument("-dk", "--d-token", help="The destination Organization Token.", dest="d_token", type=str, required=True)
    copy_parser.add_argument("-du", "--d-userkey", help="The destination userkey. If none, same as source user key", dest="d_user_key", type=str, required=False)
    copy_parser.add_argument("-o", "--output", help="The output directory", dest="output_dir", type=str, default=".", required=True)
    copy_parser.add_argument("--no-cleanup", help="Do not cleanup the files created for further inspection", action="store_true")
    copy_parser.set_defaults(func=copy)
    
    download_parser.add_argument("-t", "--type", help="Type of copy (proj, prod, org)", dest="c_type", choices=COPY_TYPES, default="proj")
    download_parser.add_argument("-e", "--s-env", help="Environment (saas, saas-eu, app, app-eu)", dest="s_env", type=str, required=True)
    download_parser.add_argument("-k", "--s-token", help="Token of object to copy", dest="s_token", type=str, required=True)
    download_parser.add_argument("-u", "--s-userkey", help="Source UserKey", dest="s_user_key", type=str, required=True)
    download_parser.add_argument("-o", "--output", help="The output directory", dest="output_dir", type=str, default=".", required=True)
    download_parser.set_defaults(func=download)
    
    return parser.parse_args()

def init():
    global args
    
    if "whitesourcesoftware.com" not in args.s_env:
        args.s_env = f"https://{args.s_env}.whitesourcesoftware.com"
        
    
    if not os.path.exists(os.path.join(os.getcwd(), args.output_dir)):
        os.mkdir(os.path.join(os.getcwd(), args.output_dir))
    
    os.chdir(os.path.join(os.getcwd(), args.output_dir))
    
    if args.c_type == "proj":
        copy_object = copy_proj(".", args.s_token, args.s_env, args.s_user_key)
    elif args.c_type == "prod":
        copy_object = copy_prod(".", args.s_token, args.s_env, args.s_user_key)
    elif args.c_type == "org":
        copy_object = copy_org(args.s_token, args.s_env, args.s_user_key)
        
    args.func(args, copy_object)
    
def download(args, copy_object):
    args.no_cleanup = True
    copy_object.get_plugin_audit_file()
    copy_object.edit_plugin_audit_file()

def copy(args, copy_object):
    if not args.d_env:
        args.d_env = args.s_env
    if not args.d_user_key:
        args.d_user_key = args.s_user_key
        
    if "whitesourcesoftware.com" not in args.d_env:
        args.d_env = f"https://{args.d_env}.whitesourcesoftware.com"
    
    copy_object.set_destination(args.d_token, args.d_user_key, args.d_env)
    copy_object.get_plugin_audit_file()
    copy_object.edit_plugin_audit_file()
    
    logger.info(" ")
    logger.info("==========================================Sending Update Requests==========================================")
    copy_object.send_plugin_audit_file()


def main():
    global args
    start_time=datetime.now()
    args = parseargs()
    logger.info(f"Started running {__description__} Version {__version__}")
    
    init()
    
    if args.no_cleanup == False:
        os.chdir("../")
        shutil.rmtree(args.output_dir)
    
    logger.info(f"Finished running {__description__}. Run time: {datetime.now() - start_time}")
    
    

if __name__ == '__main__':
    main()