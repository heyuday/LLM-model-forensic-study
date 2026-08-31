# Model Forensics Study

Small-scale model forensics on three behaviors:

- Odd Number task gaming
- Claude 4.5 safety refusals
- Value leakage in Donation Bet

This repo was prepared as part of a work test, with the specific goal of analyzing these behaviors for model-forensic purposes.

The scope is intentionally narrow: three behaviors, examined closely, rather than a wide survey. Depth was prioritized over coverage.

It combines source reading, repo inspection, shipped artifact analysis, and a small set of live probes. The goal is not a benchmark package. The goal is to answer a narrower question: when models do something strange, what is the best current explanation of why they are doing it?

## Current Take

- **Odd Number**
  The best interpretation is in-context task gaming, not literal reward hacking. The interesting models seem to treat reward-like fields as the real objective when those fields look live. This holds across the prompt variants tested so far.
- **Claude safety refusals**
  The behavior is layered. Part of it is legitimacy and specification ambiguity. Part of it looks like an object-level concern about helping suppress reporting or whistleblowing.
- **Value leakage**
  The main pattern looks like selective search and selective endorsement inside a plausible range of answers, paired with unreliable self-description about being unbiased. Self-reports should not be taken at face value here.

## Repository Layout

```text
docs/
  research_plan.md
  source_notes.md
  working_findings.md
  response_draft.md
  probe_designs.md
results/
  key/          # main artifacts referenced in the writeup
  raw/          # earlier and intermediate probe outputs
scripts/
  micro_probes.py
  micro_probes_curl.py
third_party/
  safety-refusals/
  value-leakage/
README.md
```

## Recommended Reading Order

1. [`docs/response_draft.md`](docs/response_draft.md)
2. [`docs/working_findings.md`](docs/working_findings.md)
3. [`docs/source_notes.md`](docs/source_notes.md)
4. [`docs/probe_designs.md`](docs/probe_designs.md)

If you want the raw evidence first, start in [`results/key`](results/key). The `results/raw` directory is mostly useful for tracing how the key artifacts were arrived at.

## Key Artifacts

- [`results/key/20260831_110207_odd_number.json`](results/key/20260831_110207_odd_number.json)
- [`results/key/20260831_110408_safety_refusal.json`](results/key/20260831_110408_safety_refusal.json)
- [`results/key/20260831_111916_odd_number.json`](results/key/20260831_111916_odd_number.json)
- [`results/key/20260831_112029_safety_exact_pair.json`](results/key/20260831_112029_safety_exact_pair.json)
- [`third_party/value-leakage/mega_panel.png`](third_party/value-leakage/mega_panel.png)

## Reproducing the Live Probes

The live probes use OpenRouter. Some follow-up analysis also used Anthropic.

Set keys in:

- `third_party/safety-refusals/.env`
- `third_party/value-leakage/.env`

Then run from repo root:

```bash
python3 -u scripts/micro_probes_curl.py odd
python3 -u scripts/micro_probes_curl.py odd reasoning
python3 -u scripts/micro_probes_curl.py safety
python3 -u scripts/micro_probes_curl.py safety_exact
python3 -u scripts/micro_probes_curl.py safety_exact reasoning
```

The scripts write JSON into `results/raw/`.

## Notes

- The `third_party/` directories are snapshots of the referenced external repos, kept here so the analysis is self-contained.
- Embedded `.git` metadata and local `.env` files are intentionally excluded from version control.
- The strongest Value Leakage evidence in this repo comes from the shipped artifacts in `third_party/value-leakage/runs/`, not from new paid runs.
