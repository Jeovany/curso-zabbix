#!/bin/bash
# /usr/local/bin/check_ssl_expiry.sh
DOMAIN=$1
EXPIRY=$(echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2)
EXPIRY_TS=$(date -d "$EXPIRY" +%s)
NOW=$(date +%s)
echo $(( ($EXPIRY_TS - $NOW) / 86400 ))
