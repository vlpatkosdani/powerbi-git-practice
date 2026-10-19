#!/usr/bin/env bash
# s04 - Same measure edited on both branches (TMDL merge conflict)
source "$(dirname "$0")/_common.sh"
start_from module/2-conflicts

branch s04/shared "$BASE"

# Anna: Margin % should show 0 instead of blank when there are no sales
branch s04/feature-a s04/shared
tmdl set-measure "$SALES" "Margin %" --expr "DIVIDE ( [Margin], [Sales Amount], 0 )"
commit_as "Anna Teammate" "Margin %: show 0 instead of blank"

# Ben: Margin % calculated inline and moved to a Profitability folder
branch s04/feature-b s04/shared
tmdl set-measure "$SALES" "Margin %" --expr "DIVIDE ( [Sales Amount] - [Total Cost], [Sales Amount] )" --prop "displayFolder=Profitability"
commit_as "Ben Teammate" "Margin %: inline calculation + Profitability folder"

finish
