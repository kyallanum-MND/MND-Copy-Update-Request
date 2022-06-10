import logging, argparse, os, shutil
from datetime import datetime
from mnd_copy_update_request.cp_org import copy_org
from mnd_copy_update_request.cp_prod import copy_prod
from mnd_copy_update_request.cp_proj import copy_proj
from mnd_copy_update_request._version import __tool_name__, __version__, __description__

logger = logging.getLogger()
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')

stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

logger.setLevel(logging.INFO)

COPY_PROJ = "proj"
COPY_PROD = "prod"
COPY_ORG = "org"
COPY_TYPES = [COPY_PROJ, COPY_PROD, COPY_ORG]

args = None

def parseargs():
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument("-t", "--type", help="Type of copy (proj, prod, org)", dest="c_type", choices=COPY_TYPES, default="proj")
    parser.add_argument("-se", "--s-env", help="Source Environment", dest="s_env", type=str, required=True)
    parser.add_argument("-sk", "--s-token", help="Token of object to copy", dest="s_token", type=str, required=True)
    parser.add_argument("-su", "--s-userkey", help="Source UserKey", dest="s_user_key", type=str, required=True)
    parser.add_argument("-de", "--d-env", help="The destination environment. If none, same as source environment", dest="d_env", type=str, required=False)
    parser.add_argument("-dk", "--d-token", help="The destination Organization Token.", dest="d_token", type=str, required=True)
    parser.add_argument("-du", "--d-userkey", help="The destination userkey. If none, same as source user key", dest="d_user_key", type=str, required=False)
    parser.add_argument("-o", "--output", help="The output directory", dest="output_dir", type=str, default=".", required=False)
    parser.add_argument("--no-cleanup", action="store_true")
    
    return parser.parse_args()

def init():
    global args
    
    if not args.d_env:
        args.d_env = args.s_env
    if not args.d_user_key:
        args.d_user_key = args.s_user_key
    
    if not os.path.exists(os.path.join(os.getcwd(), args.output_dir)):
        os.mkdir(os.path.join(os.getcwd(), args.output_dir))
    
    os.chdir(os.path.join(os.getcwd(), args.output_dir))
    
    if args.c_type == "proj":
        copy_object = copy_proj(".", args.s_token, args.s_env, args.s_user_key, args.d_token, args.d_env, args.d_user_key)
    elif args.c_type == "prod":
        copy_object = copy_prod(".", args.s_token, args.s_env, args.s_user_key, args.d_token, args.d_env, args.d_user_key)
    elif args.c_type == "org":
        copy_object = copy_org(args.s_token, args.s_env, args.s_user_key, args.d_token, args.d_env, args.d_user_key)
    
    copy_object.get_plugin_audit_file()
    copy_object.edit_plugin_audit_file()
    copy_object.send_plugin_audit_file()


def main():
    global args
    
    start_time=datetime.now()
    args = parseargs()
    logger.info(f"Started running {__description__} Version {__version__}.")
    
    init()
    
    if args.no_cleanup == False:
        os.chdir("../")
        shutil.rmtree(args.output_dir)
    
    logger.info(f"Finished running {__description__}. Run time: {datetime.now() - start_time}")
    
    

if __name__ == '__main__':
    main()