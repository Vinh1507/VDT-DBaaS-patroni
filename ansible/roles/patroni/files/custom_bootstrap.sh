#!/bin/sh

mkdir -p /home/postgres/data
pgbackrest --stanza=demo7  --type=time "--target=2024-08-29 02:30:48" --target-action=promote  restore