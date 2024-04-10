# FritzBox-netcup-dyndns

## Description

A simple client to trigger periodic updates of your Netcup DNS settings so you can use your Netcup-registered domain for
dynamic DNS (aka DynDNS). The client assumes you own a FritzBox that can be accessed using `fritzconnection`. The client
queries the current IP addresses from the FritzBox API and, if the addresses have changed, it calls the Netcup API to
perform a DNS update. Otherwise the Netcup API is not called. When started, FritzBox is queried immediately and an
update will be performed. Afterwards FritzBox is queried every `FB_NC_DYNDNS_INTERVAL`
seconds.

The client retrieves the DNS records of the specified domain and looks for an A or AAAA record to update. If, i.e., any
A or AAAA record is missing or no IPv6 address could be retrieved from your FritzBox, the update for this record type is
skipped. Multiple A/AAAA records can be specified and must be separated by commas.

## Configuration

All configuration can be done using either environment variables or a `.env` file in the working directory.

The following variables are required:

* `FB_NC_DYNDNS_FB_USER="my-FritzBox-user"` - Your FritzBox user
* `FB_NC_DYNDNS_FB_PASSWORD="my-FritzBox-password"` - Your FritzBox user's password
* `FB_NC_DYNDNS_NC_CUSTNO=12345` - Your Netcup customer number
* `FB_NC_DYNDNS_NC_API_KEY="my-netcup-api-key"` - Your Netcup API key
* `FB_NC_DYNDNS_NC_API_PW="my-netcup-api-password"` - Your Netcup API password
* `FB_NC_DYNDNS_DNS_TARGETS="example.com:@,www;example.org:@,sub` - Zones to update with their records separated by a
  colon and multiple zones separated by a semicolon
* `FB_NC_DYNDNS_IPV6_NODE_ID=":xx:yy"` - The node id of your IPv6 device to be exposed

The following variables are optional (defaults as shown):

* `FB_NC_DYNDNS_FB_ADDRESS="fritz.box"` - The address/hostname of your FritzBox
* `FB_NC_DYNDNS_FB_TLS="True"` - Whether to use TLS to access your FritzBox
* `FB_NC_DYNDNS_FB_TIMEOUT=10` - Timeout for FritzBox communicaiton
* `FB_NC_DYNDNS_INTERVAL=300` - Interval to query for IPv4/IPv6 updates (in seconds)
* `FB_NC_DYNDNS_LOGLEVEL="INFO"` - Default log level for the logger
