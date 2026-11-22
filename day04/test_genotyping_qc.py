import tempfile
import unittest
from pathlib import Path

from docx import Document

from genotyping_QC import compare_reports


class CompareReportsTests(unittest.TestCase):
    @staticmethod
    def _create_report(
        directory: Path,
        filename: str,
        sample_results: list[tuple[str, str, str]],
    ) -> Path:
        document = Document()
        table = document.add_table(rows=1, cols=3)
        for cell, header in zip(
            table.rows[0].cells, ("Sample", "Gene_A", "P1")
        ):
            cell.text = header
        for sample_id, genotype, prominence in sample_results:
            cells = table.add_row().cells
            for cell, value in zip(cells, (sample_id, genotype, prominence)):
                cell.text = value

        report_path = directory / filename
        document.save(report_path)
        return report_path

    @staticmethod
    def _create_multi_gene_report(
        directory: Path,
        filename: str,
        sample_results: list[tuple[str, str, str, str]],
    ) -> Path:
        document = Document()
        table = document.add_table(rows=1, cols=4)
        for cell, header in zip(
            table.rows[0].cells, ("Sample", "Gene_A", "Gene_B", "P1")
        ):
            cell.text = header
        for sample_id, gene_a, gene_b, prominence in sample_results:
            cells = table.add_row().cells
            for cell, value in zip(
                cells, (sample_id, gene_a, gene_b, prominence)
            ):
                cell.text = value

        report_path = directory / filename
        document.save(report_path)
        return report_path

    def test_identical_genotype_results_have_no_differences(self) -> None:
        sample_results = [
            ("S001", "+", "P1"),
            ("S002", "Hom", "P2"),
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            report_paths = [
                self._create_report(directory, filename, sample_results)
                for filename in ("analyst_one.docx", "analyst_two.docx")
            ]

            differences = compare_reports(report_paths)

        self.assertEqual(differences, [])

    def test_identical_results_have_no_differences_when_row_order_changes(
        self,
    ) -> None:
        first_report_results = [
            ("S001", "+", "P1"),
            ("S002", "Hom", "P2"),
        ]
        second_report_results = list(reversed(first_report_results))

        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            report_paths = [
                self._create_report(
                    directory, "analyst_A.docx", first_report_results
                ),
                self._create_report(
                    directory, "analyst_B.docx", second_report_results
                ),
            ]

            differences = compare_reports(report_paths)

        self.assertEqual(differences, [])

    def test_reports_return_only_the_genotype_difference(self) -> None:
        analyst_a_results = [
            ("S001", "+", "P1"),
            ("S002", "Hom", "P2"),
        ]
        analyst_b_results = [
            ("S001", "-", "P1"),
            ("S002", "Hom", "P2"),
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            report_paths = [
                self._create_report(
                    directory, "analyst_A.docx", analyst_a_results
                ),
                self._create_report(
                    directory, "analyst_B.docx", analyst_b_results
                ),
            ]

            differences = compare_reports(report_paths)

        self.assertEqual(
            differences,
            [
                (
                    "S001",
                    "Gene_A",
                    {"analyst_A.docx": "+", "analyst_B.docx": "-"},
                )
            ],
        )

    def test_empty_genotype_result_is_reported_as_missing(self) -> None:
        analyst_a_results = [
            ("S001", "-", "P1"),
            ("S002", "Hom", "P2"),
        ]
        analyst_b_results = [
            ("S001", "", "P1"),
            ("S002", "Hom", "P2"),
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            report_paths = [
                self._create_report(
                    directory, "analyst_A.docx", analyst_a_results
                ),
                self._create_report(
                    directory, "analyst_B.docx", analyst_b_results
                ),
            ]

            differences = compare_reports(report_paths)

        self.assertEqual(
            differences,
            [
                (
                    "S001",
                    "Gene_A",
                    {"analyst_A.docx": "-", "analyst_B.docx": None},
                )
            ],
        )

    def test_missing_sample_is_reported_as_missing_result(self) -> None:
        analyst_a_results = [
            ("S001", "-", "P1"),
            ("S002", "Hom", "P2"),
        ]
        analyst_b_results = [
            ("S002", "Hom", "P2"),
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            report_paths = [
                self._create_report(
                    directory, "analyst_A.docx", analyst_a_results
                ),
                self._create_report(
                    directory, "analyst_B.docx", analyst_b_results
                ),
            ]

            differences = compare_reports(report_paths)

        self.assertEqual(
            differences,
            [
                (
                    "S001",
                    "Gene_A",
                    {"analyst_A.docx": "-", "analyst_B.docx": None},
                )
            ],
        )

    def test_three_reports_return_all_disagreements(self) -> None:
        analyst_results = {
            "analyst_A.docx": [
                ("S001", "+", "Hom", "P1"),
                ("S002", "Hom", "Hom", "P2"),
            ],
            "analyst_B.docx": [
                ("S001", "-", "Hom", "P1"),
                ("S002", "Hom", "Hom", "P2"),
            ],
            "analyst_C.docx": [
                ("S001", "-", "Hom", "P1"),
                ("S002", "Hom", "Het", "P2"),
            ],
        }

        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            report_paths = [
                self._create_multi_gene_report(directory, filename, results)
                for filename, results in analyst_results.items()
            ]

            differences = compare_reports(report_paths)

        self.assertCountEqual(
            differences,
            [
                (
                    "S001",
                    "Gene_A",
                    {
                        "analyst_A.docx": "+",
                        "analyst_B.docx": "-",
                        "analyst_C.docx": "-",
                    },
                ),
                (
                    "S002",
                    "Gene_B",
                    {
                        "analyst_A.docx": "Hom",
                        "analyst_B.docx": "Hom",
                        "analyst_C.docx": "Het",
                    },
                ),
            ],
        )


if __name__ == "__main__":
    unittest.main()
