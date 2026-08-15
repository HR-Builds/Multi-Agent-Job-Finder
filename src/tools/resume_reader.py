from pathlib import Path
import re

from docx import Document
from langchain_core.tools import tool
from pypdf import PdfReader

from src.config import settings


def clean_text(text: str) -> str:
    """
    Clean extracted resume text.
    """

    text = text.replace("\r", "")
    text = text.replace("\t", " ")

    text = re.sub(r"[ ]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def extract_pdf(path: Path) -> str:
    """
    Extract text from a PDF resume.
    """

    try:
        reader = PdfReader(path)

        pages = []

        for page in reader.pages:
            pages.append(
                page.extract_text() or ""
            )

        return "\n".join(pages)

    except Exception as e:
        raise RuntimeError(
            f"Unable to read PDF: {e}"
        )


def extract_docx(path: Path) -> str:
    """
    Extract text from a DOCX resume.
    """

    try:
        document = Document(path)

        paragraphs = []

        for para in document.paragraphs:

            if para.text.strip():
                paragraphs.append(
                    para.text
                )

        return "\n".join(paragraphs)

    except Exception as e:
        raise RuntimeError(
            f"Unable to read DOCX: {e}"
        )


@tool
def read_resume(file_path: str) -> str:
    """
    Read a resume file (PDF/DOCX)
    and return extracted text.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"{file_path} not found."
        )

    extension = path.suffix.lower()

    if extension not in settings.SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    if extension == ".pdf":

        text = extract_pdf(path)

    else:

        text = extract_docx(path)

    return clean_text(text)


# ---------------------------------------------------------
# Local Testing
# ---------------------------------------------------------

if __name__ == "__main__":

    resume_path = (
        "data/sample_resumes/resume.pdf"
    )

    try:

        extracted_text = read_resume.invoke(
            {
                "file_path": resume_path
            }
        )

        print("\n" + "=" * 70)
        print("RESUME TEXT EXTRACTED SUCCESSFULLY")
        print("=" * 70)

        print()
        print(extracted_text)

        print("\n" + "=" * 70)
        print(
            f"Total characters: "
            f"{len(extracted_text)}"
        )
        print("=" * 70)

    except Exception as e:

        print("\nERROR:")
        print(e)