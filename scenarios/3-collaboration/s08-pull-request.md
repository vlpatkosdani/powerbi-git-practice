# s08 · Create a PR with a review checklist

Module 3: Collaboration · self-guided: you prepare the starting point yourself, no automatic check

## Why this matters

A PR is where somebody else looks at your changes before they land on the shared branch. It's a formal way to ask your colleagues (or an automation) to check the quality of your code: does your solution meet the expectations and the team's standards, and does it solve what the requirements asked for?

The reviewer goes through all the changes, meaning the diff between your branch and the branch you want to merge into.

For Power BI there are two kinds of diffs to review. The TMDL diff you read like code: what changed in this measure, and does it make sense? The PBIR diff is usually too long to read line by line, so there you check the scope: did this PR only touch the pages it should?

## What it looks like

A typical Power BI PR touches both the model and the report:

```
$ git diff --stat s08/shared s08/feature
 .../visuals/600e50304b3c610932cc/visual.json        | 2 +-
 Contoso.SemanticModel/definition/tables/Sales.tmdl  | 2 +-
 2 files changed, 2 insertions(+), 2 deletions(-)
```

The `.tmdl` part you read like code: is this change right?

```diff
     measure 'Total Cost' = SUMX ( Sales, Sales[Quantity] * Sales[Unit Cost] )
-        formatString: #,0.00
+        formatString: #,0
```

The report part you check for scope. Here it's one value in one visual on the Demo page:

```diff
                 "Literal": {
-                  "Value": "18D"
+                  "Value": "14D"
                 }
```

That matches "Demo page layout" in the PR title. If the same PR touched visuals on three other pages, that's the question to ask.

The repo's PR template (`.github/pull_request_template.md`) gives the reviewer a checklist, so nothing depends on memory. GitHub puts it into the description of every new PR, you'll see it in step 5.

## Start

Starting point: `main`. You prepare a branch with one model change and one report change.

## Steps

This is the one scenario where the pull request itself is the exercise.

**Prepare**

1. Create `s08/shared` from `main` and push it, then create `s08/feature` from it:
   ```bash
   git switch -c s08/shared main
   git push -u origin s08/shared
   git switch -c s08/feature
   ```
2. In Power BI Desktop, change `Total Cost` to 0 decimals. On the `Demo` page, make the table's font smaller (`Format` pane > `Values` > font size). Save.
3. Commit with the message `Total Cost format + Demo page layout`, and publish the branch:

   **VS Code UI:** Stage, commit, then `Publish Branch`.

   **Terminal:**
   ```bash
   git add .
   git commit -m "Total Cost format + Demo page layout"
   git push -u origin s08/feature
   ```

**The pull request**

4. On GitHub, go to `Pull requests` > `New pull request`. Set **base** to `s08/shared` and **compare** to `s08/feature`, then click `Create pull request`.
5. The description is pre-filled with the repo's PR template. Write one or two sentences under **What changed and why**.
6. Open the `Files changed` tab and review both kinds of change:
   - `Sales.tmdl`: read it like code. What changed, and does it make sense?
   - `visual.json`: check the scope. Does it only touch the Demo page, like the title says?
7. Go back to the `Conversation` tab, edit the description, and tick each checklist item you actually checked.
8. Merge the PR with `Merge pull request`.

## How to know it worked

- [ ] The PR description is filled in and the checklist is ticked
- [ ] You looked at both the `.tmdl` and the `visual.json` diff
- [ ] `s08/shared` has the change after the merge
- [ ] `python tools/check.py s08` (run `git fetch origin` first) says all good (it checks the result for you)

## Tips

> Tip: In `Files changed`, the file filter (top left) lets you show only `.tmdl` or only `.json` files. Handy when a PR touches many visuals.

> Tip: Always set the base to `s08/shared`, not `main`, so your practice changes don't end up in `main`.

> Tip: On Azure DevOps the idea is the same, only the clicks differ. You open the PR under `Repos` > `Pull requests` > `New pull request`. The template goes into `.azuredevops/pull_request_template.md`. And instead of a checklist people tick by hand, you can require reviewers and a linked work item with a branch policy on `s08/shared`.
