#!/usr/bin/env bash
# s05 - Report (PBIR) conflict: participants create the two branches themselves
source "$(dirname "$0")/_common.sh"
start_from module/2-conflicts
branch s05/shared "$BASE"
finish
