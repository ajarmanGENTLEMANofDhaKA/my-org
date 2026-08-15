from fastapi import UploadFile
from langchain_text_splitters import RecursiveCharacterTextSplitter
from docling.document_converter import DocumentConverter
from .base_controller import BaseController
from utils.text_utils import Cleaner
from bson import ObjectId
from utils.enums import ResponseSignals
import os
from utils import get_logger
logger = get_logger(__name__)

class PaperController(BaseController):
    def __init__(self):
        super().__init__()
        self.cleaner = Cleaner()

    async def validfile(self, file: UploadFile):
        """Validate the uploaded file type and size"""
        if file.content_type not in self.app_settings.ALLOWED_FILE_TYPES:
            return False, ResponseSignals.INVALID_FILE_TYPE.value
        if file.size > self.app_settings.MAX_FILE_SIZE:
            return False, ResponseSignals.INVALID_FILE_SIZE.value
        return True, ResponseSignals.VALID_FILE.value

    async def paper_path(self, project_title: str, paper_name: str):
        paper_filename = f"{paper_name}.pdf"
        file_path = self.path_utils.get_paper_path(project_title, paper_filename)
        return file_path

    async def get_pdf_content(self, file_path: str):
        """
        Convert the PDF to markdown text.
        We use docling instead of pymupdf4llm for better handling of complex PDFs including tables.
        """
        converter = DocumentConverter()
        doc = converter.convert(file_path).document
        md_text = doc.export_to_markdown()
        return md_text

    async def create_chunks(self, project_title: str, paper_name: str, paper_path: str, chunk_size: int=500, chunk_overlap: int=75):
        """Generate text chunks from the PDF content.
        - Extract text from PDF
        - Clean the text
        - Split text into sections based on markdown headers
        - Split sections into chunks
        """
        try:
            # Extract text from PDF
            paper_content = await self.get_pdf_content(paper_path)
            if not paper_content or len(paper_content) == 0:
                logger.warning(f"No content extracted from PDF: {paper_name} in project {project_title}")
                return []
            
            # Clean the text
            paper_content = self.cleaner.text_cleaner(paper_content)
    
            # Split content into sections based on markdown headers
            sections = []
            current_section = None
            buffer = []

            for raw_line in paper_content.splitlines():
                # get headers
                match = self.cleaner.HEADER_PATTERN.match(raw_line)
                
                if match:
                    title = match.group(2).strip()
                    level = len(match.group(1))

                    # skip unwanted sections
                    if self.cleaner.REMOVE_HEADER_PATTERN.match(title):
                        current_section = None
                        buffer.clear()
                        continue

                    if current_section:
                        current_section["content"] = "".join(buffer).strip()
                        if current_section["content"]:
                            sections.append(current_section)
                        buffer.clear()

                    current_section = {
                        "section_title": title,
                        "section_level": level,
                        "content": ""
                    }
                else:
                    if current_section:
                        buffer.append(raw_line + "\n")
            
            if current_section:
                current_section["content"] = "".join(buffer).strip()
                if current_section["content"]:
                    sections.append(current_section)

            # Now split sections into chunks
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len
            )

            all_docs = []
            for section in sections:
                section_id = str(ObjectId())    # Unique ID for the section
                chunks = splitter.split_text(section["content"])

                for i, chunk in enumerate(chunks, start=1):
                    metadata = {
                        "project_title": project_title,
                        "paper_name": paper_name,
                        "section_title": section["section_title"],
                        "section_level": section["section_level"],
                        "chunk_index_in_section": i,
                    }
                    all_docs.append({
                        "chunk": chunk,
                        "chunk_section_id": section_id,
                        "chunk_metadata": metadata
                    })

            return all_docs
        except Exception as e:
            logger.error(f"Error generating chunks for paper '{paper_name}': {e}")
            raise

    async def rename_paper_file(self, project_title: str, old_name: str, new_name: str):
        try:
            # Get paths for old and new files
            old_path = self.path_utils.get_paper_path(project_title, f"{old_name}.pdf")
            new_path = self.path_utils.get_paper_path(project_title, f"{new_name}.pdf")

            if not os.path.exists(old_path):
                logger.error(f"Cannot rename paper file: source file does not exist at {old_path}")
                raise FileNotFoundError(f"Source file does not exist: {old_path}")

            if os.path.exists(new_path):
                logger.error(f"Cannot rename paper file: target file already exists at {new_path}")
                raise FileExistsError(f"Target file already exists: {new_path}")
            
            # Rename the file
            os.rename(old_path, new_path)
            logger.info(f"Paper file renamed successfully: {old_name} → {new_name}")

        except Exception as e:
            logger.error(f"Error renaming paper file {old_name} → {new_name}: {e}")
            raise