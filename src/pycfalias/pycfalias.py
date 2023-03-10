import argparse
import requests
from datetime import datetime as dt

from config import get_config, validate_config
from formatting import format_table


cf_uri ="https://api.cloudflare.com/client/v4/zones/{zone}/email/routing/rules"

def get_email_aliases():
    c = get_config()
    headers = {
        "Authorization": "Bearer " + c.get("CF_TOKEN")
    }
    
    r = requests.get(cf_uri.format(zone=c.get("CF_ZONE")), headers=headers)
    
    return r.json()

def create_email_alias(dest):
    c = get_config()
    
    headers = {
        "Authorization": "Bearer " + c.get("CF_TOKEN")
    }

    t = dt.utcnow()
    ts = t.isoformat(timespec='milliseconds') 
    default_name = f"Rule created at {ts}Z"
	
    payload = {
		"actions": [
			{
				"type": "forward",
				"value": [c.get("CF_FORWARD_EMAIL")]
			}
		],
		"enabled": True,
		"matchers": [
			{
				"field": "to",
				"type": "literal",
				"value": dest
			}
		],
		"name": default_name,
		"priority": 0
	}

    r = requests.request("POST", cf_uri.format(zone=c.get("CF_ZONE")), json=payload, headers=headers)

def remove_email_alias(alias):
    ruleid = ""
    c = get_config()
    
    headers = {
        "Authorization": "Bearer " + c.get("CF_TOKEN")
    }

    data = get_email_aliases()
    
    try: 
        ruleid = [i["tag"] for i in data["result"] if i["matchers"][0]["type"] == "literal" and i["matchers"][0]["value"] == alias][0]
    except IndexError:
        exit("Error: Unable to find alias")
    
    r = requests.request("DELETE", cf_uri.format(zone=c.get("CF_ZONE")) + '/' + ruleid, headers=headers)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--list", help="List email aliases", required=False, action="store_true")
    parser.add_argument("-c", "--create", help="Create new email alias", required=False)
    parser.add_argument("-r", "--remove", help="Remove email alias", required=False)

    args = parser.parse_args()

    if args.list:
        table = format_table(get_email_aliases())
        print(table)
    elif args.create:
        create_email_alias(args.create)
    elif args.remove:
        remove_email_alias(args.remove)

if __name__ == "__main__":
    validate_config(get_config())
    main()
