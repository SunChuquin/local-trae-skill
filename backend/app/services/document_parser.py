from typing import List, Dict, Any, Optional
import re
from pathlib import Path
from loguru import logger
import markdown
from PyPDF2 import PdfReader
from docx import Document as DocxDocument
from app.config import settings


class DocumentParser:
    def __init__(self):
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap

    def parse_file(self, file_path: str, file_type: str) -> Optional[str]:
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"文件不存在: {file_path}")
                return None

            if file_type == "md" or file_type == "markdown":
                return self.parse_markdown(file_path)
            elif file_type == "txt":
                return self.parse_txt(file_path)
            elif file_type == "pdf":
                return self.parse_pdf(file_path)
            elif file_type == "docx":
                return self.parse_docx(file_path)
            else:
                logger.error(f"不支持的文件类型: {file_type}")
                return None
        except Exception as e:
            logger.error(f"解析文件失败 {file_path}: {str(e)}")
            return None

    def parse_markdown(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"解析 Markdown 文件: {file_path}")
            return content
        except Exception as e:
            logger.error(f"解析 Markdown 失败: {str(e)}")
            raise

    def parse_txt(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"解析文本文件: {file_path}")
            return content
        except Exception as e:
            logger.error(f"解析文本文件失败: {str(e)}")
            raise

    def parse_pdf(self, file_path: str) -> str:
        try:
            reader = PdfReader(file_path)
            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            content = "\n".join(text_parts)
            logger.info(f"解析 PDF 文件: {file_path}，提取 {len(text_parts)} 页")
            return content
        except Exception as e:
            logger.error(f"解析 PDF 失败: {str(e)}")
            raise

    def parse_docx(self, file_path: str) -> str:
        try:
            doc = DocxDocument(file_path)
            text_parts = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)
            content = "\n".join(text_parts)
            logger.info(f"解析 DOCX 文件: {file_path}")
            return content
        except Exception as e:
            logger.error(f"解析 DOCX 失败: {str(e)}")
            raise

    def chunk_text(self, text: str, document_id: str, document_name: str) -> List[Dict[str, Any]]:
        chunks = []
        if not text or not text.strip():
            logger.warning(f"文档内容为空: {document_id}")
            return chunks

        sentences = self._split_into_sentences(text)
        current_chunk = []
        current_length = 0

        for i, sentence in enumerate(sentences):
            sentence_length = len(sentence)

            if current_length + sentence_length > self.chunk_size and current_chunk:
                chunk_text = " ".join(current_chunk)
                chunk_id = f"{document_id}_chunk_{len(chunks)}"

                chunks.append({
                    "id": chunk_id,
                    "text": chunk_text,
                    "document_id": document_id,
                    "document_name": document_name,
                    "chunk_index": len(chunks),
                    "total_chunks": 0
                })

                overlap_start = max(0, len(current_chunk) - self.chunk_overlap // 50)
                current_chunk = current_chunk[overlap_start:]
                current_length = sum(len(s) for s in current_chunk)

            current_chunk.append(sentence)
            current_length += sentence_length

        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunk_id = f"{document_id}_chunk_{len(chunks)}"
            chunks.append({
                "id": chunk_id,
                "text": chunk_text,
                "document_id": document_id,
                "document_name": document_name,
                "chunk_index": len(chunks),
                "total_chunks": len(chunks) + 1
            })

        for chunk in chunks:
            chunk["total_chunks"] = len(chunks)

        logger.info(f"文档 {document_id} 分块完成，共 {len(chunks)} 个块")
        return chunks

    def _split_into_sentences(self, text: str) -> List[str]:
        sentences = re.split(r'[。！？\n]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences


document_parser = DocumentParser()
