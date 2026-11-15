# Day 4: Genotyping QC Web Interface

This assignment adds a small local Flask web interface for the genotyping QC
program. It lets you compare Word reports in a browser and view the HTML
comparison report.

## Install dependencies

Run this from the repository root:

```bash
python -m pip install -r day04/requirements.txt
```

## Start the web interface

From the repository root, run:

```bash
python day04/app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser. Select at
least two `.docx` reports and click **Compare reports**. The comparison report
will appear in the browser.

To try the fictional training data, select all three `.docx` files in
`day04/demo_reports`:

- `analyst_A.docx`
- `analyst_B.docx`
- `analyst_C.docx`

The reports are fictional and demonstrate two differences:

- **S001 / Gene_A:** Analyst A reports `+`; Analysts B and C report `-`.
- **S002 / Gene_B:** Analysts A and B report `Hom`; Analyst C reports `Het`.

Stop the server by pressing **Ctrl+C** in the terminal where it is running.

## Run the command-line version

From the repository root, run:

```bash
python day04/genotyping_QC.py
```

This compares the reports in `day04/demo_reports` and writes the generated
HTML report to `day04/demo_qc_report.html`.

## How the web interface works

`app.py` reuses the existing comparison and HTML-report functions from
`genotyping_QC.py`; it does not duplicate their comparison logic. It saves
uploaded files and the intermediate HTML report in a temporary directory, then
returns the report to the browser. The temporary directory is cleaned up when
the request finishes.

The interface requires at least two `.docx` files and checks that filenames
are unique so one upload cannot silently overwrite another. It also reports
clear errors for invalid Word documents and reports without a readable
Genotyping Summary table.

## Day 4 work and checks

The Day 4 prompts requested that the assignment be started by copying the
genotyping QC program, report-generation script, requirements, and fictional
demo reports into `day04`, while excluding sample or real reports, generated
HTML, and the Day 3 README. They then requested Flask be installed using the
VS Code-selected Python interpreter and added alongside `python-docx`.
Finally, they requested this local upload interface, reusing the existing
comparison functions and keeping uploads temporary.

Both versions were checked: the CLI ran successfully, and the web interface
compared the three fictional reports and found the two differences listed
above. `day03` remains unchanged.
