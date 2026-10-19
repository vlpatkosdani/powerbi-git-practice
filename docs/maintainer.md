# Maintainer notes

## Test a scenario locally (no GitHub needed)

```bash
git switch main
NO_PUSH=1 bash tools/setup/s04.sh           # builds branches locally, no push
# ...do the task as a participant would...
python tools/checks/run.py --event push --head-ref s04/shared
```

`run.py` prints the report and `result=passed|failed|skipped`; exit code 1 on failure.

Or the participant's way: `python tools/check.py s04` (local branches, no workflow arguments).

## Add or finish a scenario

1. Entry in `tools/scenarios.json`: graded `head` is a regex, `base` an exact branch name, `via` is `push` (checked when head is pushed) or `pr` (checked on a pull request head -> base). Set `status` to `ready` when done, and add the id to the dropdown in `.github/workflows/start-scenario.yml`.
2. `tools/setup/sNN.sh`: `source _common.sh`, `start_from module/...`, `retire` the branches participants create, then `branch` / `tmdl ...` / `commit_as`, end with `finish`.
3. `tools/checks/sNN.py`: a `run(c: Ctx)` function using the helpers in `checks/common.py`. Every scenario has one, also the self-guided ones: add a `local` entry (`head`, optional `base`) in `scenarios.json` so `python tools/check.py sNN` knows which branch to look at. Plus `time` and `level` for the README table.
4. Content: write `scenarios/<module>/<id>-<slug>.md` directly (copy an existing one for the structure). The md files are the only source, there is no generator.
5. Test locally: one passing run and at least one plausible wrong answer that fails.

## Design notes

- **Template model, not forks.** Participants work in their own copy, so there are
  no fork-PR token limits, no security surface on this repo, and no PR flood here.
  To run a live session with PRs back to *this* repo instead, switch the trigger
  in `check-submission.yml` to `pull_request_target`. That's safe because the
  grader is already loaded from the default branch and never executes PR code.
- **Grader from the default branch.** Scenario branches may carry older copies of
  `tools/`, so the workflow uses `git archive origin/<default> tools`.
- **Result-based checks.** Checks compare measure expressions (whitespace/case
  normalised) and properties, not whole files, because Desktop rewrites
  `lineageTag`s and formatting. History is only checked where it's the lesson
  (cherry-pick count, revert vs reset, linear rebase).
- **Merge conflicts block the check.** GitHub doesn't run `pull_request`
  workflows while a PR has conflicts, so conflict scenarios are graded once
  they're resolved.
- **Demo model.** `Contoso.*` was saved from Power BI Desktop (TMDL + PBIR)
  and its Power Query source switched from a local SQL Server to the CSV files
  on the `data-v1` release (`DataUrl` parameter). The repo stores LF;
  `.gitattributes` checks the model and report files out with CRLF, like Desktop
  writes them, so a save doesn't show up as a whole-file change. `tools/tmdl.py`
  keeps a file's line endings so setup diffs stay small. Shell scripts stay LF.
- **Starting over.** Setup scripts force-push the starting branches and, via
  `retire`, delete branches participants create (`s15/fix`, ...) on origin. They
  can't touch a participant's laptop, so each graded scenario has a *Start over*
  note for the local branches.
- **Publishing the data.** Create a release tagged `data-v1` and attach
  `sales.csv`, `customer.csv`, `product.csv`, `store.csv`, `date.csv`,
  `currencyexchange.csv`. `DataUrl` (`Contoso.SemanticModel/definition/expressions.tmdl`) points to
  `vlpatkosdani/powerbi-git-practice`. It only works once the repo is public.
