#!/usr/bin/env bash
# s12 - Cherry-pick one approved commit from dev to uat
source "$(dirname "$0")/_common.sh"
start_from module/4-promotion

branch s12/uat "$BASE"
branch s12/dev s12/uat

tmdl add-measure "$SALES" "Order Count" --expr "DISTINCTCOUNT ( Sales[Order Number] )" --prop "formatString=#,0"
commit_as "Anna Teammate" "Add Order Count"                                   # A - still in testing

tmdl add-measure "$SALES" "Average Price" --expr "DIVIDE ( [Sales Amount], [Total Quantity] )" --prop "formatString=#,0.00" --after "Sales Amount"
commit_as "Ben Teammate" "Add Average Price [APPROVED for UAT]"             # B - approved

tmdl set-measure "$SALES" "Sales Amount" --expr "SUMX ( Sales, Sales[Quantity] * Sales[Unit Price] )"
commit_as "Anna Teammate" "Sales Amount: use Unit Price (experiment)"         # C - not approved

finish
