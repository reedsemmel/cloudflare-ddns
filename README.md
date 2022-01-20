# Dynamic DNS for Cloudflare

This repository contains a script and a container image for checking if your public IP matches your
DNS record in Cloudflare. If they do not match, it will update the record to the address returned
by website giving you your public IP.

## Required Environment Variables

 * `PUBLIC_IP_URL`: A url to a resource that **only** returns your IPv4 address in the body. A
 service that does this is `https://ifconfig.me/ip`.

 * `CLOUDFLARE_DOMAIN`: The domain that you want to update. This script is for updating only a
 single record. For wildcard domains, use `*.your-domain.tld`.

 * `CLOUDFLARE_ZONE`: The domain's zone in the Cloudflare API.

 * `CLOUDFLARE_TOKEN`: Your Cloudflare API token (API key with email not supported). This token
 must have `Zone.DNS:edit` permissions in your domain's zone.

## Using this container

A container is provided at `ghcr.io/reedsemmel/cloudflare-ddns`. Please note that *this is **not**
a background service. It terminates after any error, concluding the IPs match, or after updating
the record*. This is intended to be run as a `CronJob` or `Job` in Kubernetes.

Example manifest (assumes you have a `Secret` with your Cloudflare information):
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: ddns
spec:
  schedule: "@daily"
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: Never
          containers:
          - name: ddns
            image: ghcr.io/reedsemmel/cloudflare-ddns:latest
            env:
            - name: CLOUDFLARE_DOMAIN
              value: "*.your-domain.tld"
            - name: PUBLIC_IP_URL
              value: "https://ifconfig.me/ip"
            - name: CLOUDFLARE_TOKEN
              valueFrom:
                secretKeyRef:
                  name: cloudflare-credentials
                  key: token
            - name: CLOUDFLARE_ZONE
              valueFrom:
                secretKeyRef:
                  name: cloudflare-credentials
                  key: zone
```
