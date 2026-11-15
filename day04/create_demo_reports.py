from pathlib import Path

from docx import Document


DEMO_REPORTS = {
    "analyst_A.docx": {
        "S001": ("+", "WT"),
        "S002": ("-", "Hom"),
        "S003": ("Het", "+"),
        "C+": ("+", "Hom"),
    },
    "analyst_B.docx": {
        "S001": ("-", "WT"),
        "S002": ("-", "Hom"),
        "S003": ("Het", "+"),
        "C+": ("+", "Hom"),
    },
    "analyst_C.docx": {
        "S001": ("-", "WT"),
        "S002": ("-", "Het"),
        "S003": ("Het", "+"),
        "C+": ("+", "Hom"),
    },
}

PROMINENCE_VALUES = {
    "S001": ("92", "88"),
    "S002": ("85", "91"),
    "S003": ("94", "87"),
    "C+": ("99", "96"),
}


def create_demo_reports(output_folder: Path) -> list[Path]:
    """Create three clearly fictional Word reports for QC practice."""
    output_folder.mkdir(parents=True, exist_ok=True)
    created_files = []

    for filename, sample_results in DEMO_REPORTS.items():
        document = Document()
        document.add_heading("Genotyping Summary", level=1)
        document.add_paragraph(
            "FICTIONAL TRAINING DATA — NOT REAL LABORATORY RESULTS"
        )
        document.add_paragraph(f"Report prepared by {filename.removesuffix('.docx')}")

        table = document.add_table(rows=1, cols=5)
        table.style = "Table Grid"
        headers = ["Sample", "Gene_A", "P1", "Gene_B", "P2"]
        for cell, header in zip(table.rows[0].cells, headers):
            cell.text = header

        for sample_id, (gene_a, gene_b) in sample_results.items():
            prominence_1, prominence_2 = PROMINENCE_VALUES[sample_id]
            row_cells = table.add_row().cells
            values = [
                sample_id,
                gene_a,
                prominence_1,
                gene_b,
                prominence_2,
            ]
            for cell, value in zip(row_cells, values):
                cell.text = value

        report_path = output_folder / filename
        document.save(report_path)
        created_files.append(report_path)

    return created_files


if __name__ == "__main__":
    reports_folder = Path(__file__).parent / "demo_reports"
    for report_path in create_demo_reports(reports_folder):
        print(f"Created fictional training report: {report_path.name}")
