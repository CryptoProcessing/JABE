#!/bin/sh
curl "http://localhost:5000/api/v1/btc/block" -H 'content-type: application/json' -d "$@"
