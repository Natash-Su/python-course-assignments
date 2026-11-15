from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import BadZipFile

from docx.opc.exceptions import PackageNotFoundError
from flask import Flask, Response, render_template, request
from lxml.etree import XMLSyntaxError
from werkzeug.utils import secure_filename

from genotyping_QC import compare_reports, write_html_report


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def upload_reports() -> Response | str | tuple[str, int]:
    if request.method == "GET":
        return render_template("index.html")

    uploads = [
        upload
        for upload in request.files.getlist("reports")
        if upload.filename
    ]
    if len(uploads) < 2:
        return (
            render_template(
                "index.html",
                error="Select at least two .docx reports to compare.",
            ),
            400,
        )

    filenames = []
    for upload in uploads:
        original_filename = upload.filename or ""
        if Path(original_filename).suffix.casefold() != ".docx":
            return (
                render_template(
                    "index.html",
                    error=f"{original_filename} is not a .docx file.",
                ),
                400,
            )

        filename = secure_filename(original_filename)
        if not filename:
            return (
                render_template(
                    "index.html",
                    error="One of the uploaded files has an invalid filename.",
                ),
                400,
            )
        filenames.append(filename)

    normalized_filenames = [filename.casefold() for filename in filenames]
    if len(set(normalized_filenames)) != len(normalized_filenames):
        return (
            render_template(
                "index.html",
                error=(
                    "Each uploaded report must have a unique filename. "
                    "Rename duplicate files and try again."
                ),
            ),
            400,
        )

    with TemporaryDirectory(prefix="day04-uploads-") as temporary_directory:
        temporary_path = Path(temporary_directory)
        report_paths = []
        for upload, filename in zip(uploads, filenames):
            report_path = temporary_path / filename
            upload.save(report_path)
            report_paths.append(report_path)

        try:
            differences = compare_reports(report_paths)
            output_path = temporary_path / "comparison.html"
            write_html_report(differences, report_paths, output_path)
            report_html = output_path.read_text(encoding="utf-8")
        except ValueError as error:
            return (
                render_template(
                    "index.html",
                    error=f"Could not read a Genotyping Summary table: {error}",
                ),
                400,
            )
        except (
            BadZipFile,
            KeyError,
            OSError,
            PackageNotFoundError,
            XMLSyntaxError,
        ) as error:
            return (
                render_template(
                    "index.html",
                    error=(
                        "One or more uploads could not be read as valid "
                        f"Word documents (.docx): {error}"
                    ),
                ),
                400,
            )

    return Response(report_html, mimetype="text/html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
