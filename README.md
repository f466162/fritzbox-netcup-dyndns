# fritzbox-netcup-dyndns

## Description

A simple client to trigger periodic updates of your Netcup DNS settings so you can use your 
Netcup-registered domain for dynamic DNS (aka DynDNS). The client assumes you own a Fritzbox 
that can be accessed using `fritzconnection`.

The client retrieves the DNS records of the specified domain and looks for an A or AAAA record 
to update. If, i.e., the AAAA record is missing or no IPv6 address could be retrieved from your 
Fritzbox, the update for this record type is skipped.

## Configuration

All configuration can be done using either environment variables or a `.env` file in the working directory.

The following variables are required:

* `FB_NC_DYNDNS_FB_USER="my-fritzbox-user"` - Your Fritzbox user
* `FB_NC_DYNDNS_FB_PASSWORD="my-fritzbox-password"` - Your Fritzbox user's password
* `FB_NC_DYNDNS_NC_CUSTNO="12345"` - Your Netcup customer number
* `FB_NC_DYNDNS_NC_API_KEY="my-netcup-api-key"` - Your Netcup API key
* `FB_NC_DYNDNS_NC_API_PW="my-netcup-api-password"` - Your Netcup API password
* `FB_NC_DYNDNS_DOMAIN="yourdomain.abc"` - Your domain/zone
* `FB_NC_DYNDNS_HOST="your-a-or-aaaa-record"` - Your host in your domain/zone

The following variables are optional (defaults as shown):

* `FB_NC_DYNDNS_FB_ADDRESS="fritz.box"` - The address/hostname of your Fritzbox
* `FB_NC_DYNDNS_FB_TLS="True"` - Whether to use TLS to access your Fritzbox
* `FB_NC_DYNDNS_FB_TIMEOUT="10"` - Timeout for Fritzbox communicaiton
* `FB_NC_DYNDNS_INTERVAL="300"` - Interval to query for IPv4/IPv6 updates (in seconds)
