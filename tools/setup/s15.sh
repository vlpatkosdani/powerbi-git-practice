#!/usr/bin/env bash
# s15 - Revert a bad commit that is already on a shared branch
source "$(dirname "$0")/_common.sh"
start_from module/5-recovery

branch s15/shared "$BASE"

tmdl add-measure "$SALES" "Order Count" --expr "DISTINCTCOUNT ( Sales[Order Number] )" --prop "formatString=#,0"
commit_as "Anna Teammate" "Add Order Count"

tmdl set-measure "$SALES" "Total Quantity" --expr "COUNT ( Sales[Quantity] )" --prop "formatString=0.00"
commit_as "Ben Teammate" "Tidy Total Quantity"   # the bad one: COUNT instead of SUM

tmdl add-measure "$PRODUCT" "Product Count" --expr "COUNTROWS ( Product )" --prop "formatString=#,0"
commit_as "Anna Teammate" "Add Product Count"

finish
