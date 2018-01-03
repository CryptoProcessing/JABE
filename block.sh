#!/bin/sh
curl "http://127.0.0.1:5000/api/v1/btc/block" -H 'content-type: application/json' -d "$@"
