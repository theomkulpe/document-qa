from pypdf import PdfReader
import requests
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())

def load_url(url: str) -> str:
    response = requests.get(url, timeout = 10)
    soup = BeautifulSoup(response.text, "html.parser")
    # Remove noise
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    return soup.get_text(separator = "\n", strip = True)

def chunk_text(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 50,
        separators = ["\n\n", "\n", ".", " "]
    )
    return splitter.split_text(text)

def ingest(source: str, source_type: str) -> list[str]:
    if source_type == "pdf":
        text = load_pdf(source)
    elif source_type == "url":
        text = load_url(source)
    else:
        raise ValueError("source_type must be 'pdf or 'url'")
    return chunk_text(text)