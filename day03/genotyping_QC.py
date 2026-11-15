import argparse
from html import escape
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn


def _clean_cell_text(value: str) -> str:
    """Trim whitespace and matching single or double quotes around a cell."""
    value = value.strip()
    while len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        value = value[1:-1].strip()
    return value


def read_genotyping_summary(
    file_path: str | Path,
) -> dict[str, dict[str, str]]:
    """Read the Genotyping Summary as {sample ID: {gene: result}}."""
    document = Document(file_path)
    summary_rows = None
    sample_column = None
    gene_columns = []
    prominence_columns = {f"P{number}" for number in range(1, 6)}

    for table in document.tables:
        rows = table._tbl.tr_lst
        for header_row_number, row in enumerate(rows):
            headers = [
                _clean_cell_text(
                    "".join(
                        text_node.text or ""
                        for text_node in cell.iter(qn("w:t"))
                    )
                )
                for cell in row.tc_lst
            ]
            normalized_headers = [header.casefold() for header in headers]
            if "sample" not in normalized_headers:
                continue

            sample_column = normalized_headers.index("sample")
            gene_columns = [
                (column_number, header)
                for column_number, header in enumerate(headers)
                if column_number != sample_column
                and header
                and header.upper() not in prominence_columns
            ]
            summary_rows = rows[header_row_number + 1 :]
            break
        if summary_rows is not None:
            break

    if summary_rows is None or sample_column is None:
        raise ValueError(
            f"No table with a 'Sample' header was found in {file_path}"
        )

    results = {}
    for row in summary_rows:
        cells = [
            _clean_cell_text(
                "".join(
                    text_node.text or "" for text_node in cell.iter(qn("w:t"))
                )
            )
            for cell in row.tc_lst
        ]
        if sample_column >= len(cells):
            continue

        sample_id = cells[sample_column]
        if not sample_id:
            continue
        if "".join(sample_id.split()).casefold() == "c+":
            sample_id = "C+"

        results[sample_id] = {
            gene: cells[column_number] if column_number < len(cells) else ""
            for column_number, gene in gene_columns
        }

    return results


def compare_reports(
    report_paths: list[str | Path],
) -> list[tuple[str, str, dict[str, str | None]]]:
    """Return differences as (sample ID, gene, {filename: result or None})."""
    if len(report_paths) < 2:
        raise ValueError("Provide at least two reports to compare.")

    reports = {
        Path(report_path).name: read_genotyping_summary(report_path)
        for report_path in report_paths
    }

    sample_ids = set()
    genes_by_sample = {}
    for report_results in reports.values():
        for sample_id, gene_results in report_results.items():
            sample_ids.add(sample_id)
            genes_by_sample.setdefault(sample_id, set()).update(gene_results)

    differences = []
    for sample_id in sorted(sample_ids):
        for gene in sorted(genes_by_sample[sample_id]):
            source_results = {
                filename: (gene_results.get(sample_id, {}).get(gene) or None)
                for filename, gene_results in reports.items()
            }
            present_results = {
                result for result in source_results.values() if result is not None
            }

            if not present_results:
                continue
            if len(present_results) > 1 or any(
                result is None for result in source_results.values()
            ):
                differences.append((sample_id, gene, source_results))

    return differences


def write_html_report(
    differences: list[tuple[str, str, dict[str, str | None]]],
    report_paths: list[str | Path],
    output_path: str | Path | None = None,
) -> Path:
    """Write the comparison results to an HTML file and return its path."""
    if output_path is None:
        output_path = Path(__file__).parent / "qc_report.html"
    output_path = Path(output_path)
    filenames = [Path(report_path).name for report_path in report_paths]

    table_header = "".join(
        f"<th>{escape(filename)}</th>" for filename in filenames
    )
    table_rows = []
    for sample_id, gene, source_results in differences:
        result_cells = "".join(
            "<td>"
            + escape(source_results.get(filename) or "MISSING")
            + "</td>"
            for filename in filenames
        )
        table_rows.append(
            f"<tr><td>{escape(sample_id)}</td>"
            f"<td>{escape(gene)}</td>{result_cells}</tr>"
        )

    if table_rows:
        differences_content = (
            '<table><thead><tr><th>Sample</th><th>Gene</th>'
            f"{table_header}</tr></thead>"
            f"<tbody>{''.join(table_rows)}</tbody></table>"
        )
    else:
        differences_content = "<p>No differences found.</p>"

    escaped_filenames = "".join(
        f"<li>{escape(filename)}</li>" for filename in filenames
    )
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Genotyping QC Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; line-height: 1.5; margin: 2rem; color: #222; }}
    table {{ border-collapse: collapse; margin-top: 1rem; width: 100%; }}
    th, td {{ border: 1px solid #ccc; padding: 0.6rem; text-align: left; }}
    th {{ background: #f0f3f5; }}
    tbody tr:nth-child(even) {{ background: #fafafa; }}
  </style>
</head>
<body>
  <h1>Genotyping QC Report</h1>
  <h2>Compared files</h2>
  <ul>{escaped_filenames}</ul>
  <p>Sample–gene combinations flagged for review: {len(differences)}</p>
  {differences_content}
</body>
</html>
"""
    output_path.write_text(html_content, encoding="utf-8")
    return output_path


if __name__ == "__main__":
    script_folder = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Compare genotyping results from Word reports."
    )
    parser.add_argument(
        "input_folder",
        nargs="?",
        type=Path,
        default=script_folder / "demo_reports",
        help="folder containing .docx reports (default: day03/demo_reports)",
    )
    parser.add_argument(
        "output_html",
        nargs="?",
        type=Path,
        default=script_folder / "demo_qc_report.html",
        help="path for the HTML report (default: day03/demo_qc_report.html)",
    )
    args = parser.parse_args()

    report_paths = sorted(
        path
        for path in args.input_folder.glob("*.docx")
        if not path.name.startswith("~$")
    )
    differences = compare_reports(report_paths)

    report_path = write_html_report(
        differences, report_paths, args.output_html
    )
    if not differences:
        print("No disagreements or missing results found.")
    for sample_id, gene, source_results in differences:
        print(f"Sample {sample_id} | {gene}")
        for filename, result in source_results.items():
            print(f"  {filename}: {result if result is not None else 'MISSING'}")
    print(f"HTML report written to {report_path}")