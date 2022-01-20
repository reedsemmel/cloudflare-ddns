#/usr/bin/env python3

import requests, os, sys, re


CF_ZONE_URL = "https://api.cloudflare.com/client/v4/zones"

def get_environment(env: str) -> str:
    ret = os.getenv(env)
    if ret == None:
        print(f"Required environment variable {env} is not set")
        sys.exit(1)
    return ret

def main():
    # First get our environment
    token = get_environment("CLOUDFLARE_TOKEN")
    zone = get_environment("CLOUDFLARE_ZONE")
    domain = get_environment("CLOUDFLARE_DOMAIN")
    public_ip_url = get_environment("PUBLIC_IP_URL")

    res = requests.get(public_ip_url)

    if not res.ok:
        print(f"Error getting public ip from {public_ip_url}")
        sys.exit(1)

    public_ip = res.text

    if not re.match("\d{1,3}\.\d{1,3}\d{1,3}\.\d{1,3}", public_ip):
        print(f"Response {public_ip} does not appear to be an IPv4 address")
        sys.exit(1)

    print(f"Received public IP {public_ip} from {public_ip_url}")

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    params = {"type": "A", "name": domain}

    res = requests.get(f"{CF_ZONE_URL}/{zone}/dns_records", params=params, headers=headers)

    records = res.json()

    if not records["success"]:
        print("Failed to get DNS records. Cloudflare response:")
        print(records)
        sys.exit(1)

    for record in records["result"]:
        if record["content"] == public_ip:
            print(f"Record {record['id']} matches IP. No update needed. Exiting")
            sys.exit(0)

    if len(records["result"]) == 0:
        print(f"No A records found for {domain}. This script will not create a record")
        sys.exit(1)

    # If a record doesn't match, then we will have to update it.
    id = records["result"][0]['id']

    print(f"Updating record {id}...")

    data = {"type": "A", "name": domain, "content": public_ip, "ttl": 1}

    res = requests.patch(f"{CF_ZONE_URL}/{zone}/dns_records/{id}", json=data, headers=headers)

    if res.ok:
        print(f"Record updated successfully to {public_ip}")
    else:
        print("Update failed. Cloudflare response:")
        print(res.text)
        sys.exit(1)

if __name__ == "__main__":
    main()
