# Genotyping QC

This program compares genotyping summaries from two or more Word (`.docx`)
reports and creates an HTML quality-control (QC) report. It flags results that
disagree or are missing so they can be reviewed.

## Setup

From the repository's main folder, install the required package:

```powershell
python -m pip install -r day03/requirements.txt
```

## Generate fictional demo reports

Create three fictional training reports in `day03/demo_reports/`:

```powershell
python day03/create_demo_reports.py
```

These are synthetic examples, not real laboratory results.

## Run the demo

From the repository's main folder, run:

```powershell
python day03/genotyping_QC.py
```

By default, the program reads `.docx` files from `day03/demo_reports/` and
writes `day03/demo_qc_report.html`. These default paths are relative to the
script, so they also work if you run the command from another folder.

## Use a different input folder or output file

Pass the input folder first and the output HTML path second:

```powershell
python day03/genotyping_QC.py "path\to\reports" "path\to\report.html"
```

Replace the example paths with your own. Custom paths are interpreted relative
to the terminal's current folder unless you provide absolute paths. Temporary
Word files whose names start with `~$` are skipped.

## Expected demo differences

The fictional reports contain two sample–gene combinations to review:

1. `S001`, `Gene_A`: analyst A reports `+`; analysts B and C report `-`.
2. `S002`, `Gene_B`: analysts A and B report `Hom`; analyst C reports `Het`.

The program flags both differences but does not decide which result is correct.

## Comparison rules

- Results are matched by sample ID and gene name, not by row order.
- Prominence columns named `P1` through `P5` are ignored.
- Control rows, including `C+` and `WT`, are included in the comparison.
- The control label `C +` is normalized to `C+`.
- Disagreements and results missing or empty in any report are flagged for
  review. A missing result is not treated as a negative genotype.
- The HTML report labels results with their source filenames.

## Limitations

The reader supports the demonstrated genotyping-summary table format: a table
with a `Sample` header and gene columns. Other report layouts may need changes
to the reader. The program identifies disagreements and missing results, but
does not determine which analyst or result is correct.

## Prompt summary

The project was built step by step: inspect the example Word reports, write a
reader for their genotyping summary tables, compare reports by sample and gene,
create an HTML QC report, and then add command-line input and output paths.
Fictional reports were also created to test the comparison without copying
real laboratory data.

## Laboratory data and repository

Real laboratory reports in `day03/sample_reports/` are excluded from the
repository by `.gitignore`. Do not add real laboratory reports to version
control.
