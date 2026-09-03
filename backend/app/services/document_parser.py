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

    def parse_file(self, file_path: str, file_type: str, keep_original: bool = False) -> Optional[str]:
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
                # keep_original=True 时返回 (原始文本, 剔除页眉页脚后文本)
                return self.parse_pdf(file_path, keep_original=keep_original)
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

    # 页眉/页脚判定：文本行在页面顶部/底部的边缘比例（相对页高）
    _EDGE_RATIO_TOP = 0.10
    _EDGE_RATIO_BOTTOM = 0.08
    # 用于页眉/页脚匹配的数字归一化（页眉常含页码，如 "… v1.1 3/122"，去掉数字差异才能识别重复）
    _NUM_RE = re.compile(r'\d+')

    def parse_pdf(self, file_path: str, keep_original: bool = False):
        """解析 PDF：用 pdfplumber 保表格结构，并剔除跨页重复的页眉页脚。

        流程：
        1. 逐页提取"结构化事件"（带坐标的文本行 + 表格块）；
        2. 统计所有页面顶部/底部边缘重复出现的文本行，识别页眉/页脚；
        3. 剔除页眉页脚后组装文本（每页以 【第N页】 标记溯源，表格用
           <<<TABLE>>>...<<<END_TABLE>>> 包裹保持原子性）。

        keep_original=True 时返回 (原始文本, 剔除后文本) 元组，供对比预览用；
        默认返回剔除后的文本字符串。
        """
        try:
            import pdfplumber
            pages = []
            with pdfplumber.open(file_path) as pdf:
                for pno, page in enumerate(pdf.pages, 1):
                    pages.append(self._extract_page_structured(page, pno))
            headers, footers = self._detect_headers_footers(pages)
            cleaned_parts = []
            for pno, height, events in pages:
                rendered = self._render_page(pno, height, events, headers, footers)
                if rendered:
                    cleaned_parts.append(rendered)
            cleaned = "\n".join(cleaned_parts)
            logger.info(f"解析 PDF 文件: {file_path}，提取 {len(cleaned_parts)} 页（pdfplumber 保表格）")
            if keep_original:
                # 剔除前：不做页眉/页脚过滤的完整渲染（表格处理逻辑一致，便于对比）
                orig_parts = []
                for pno, height, events in pages:
                    rendered = self._render_page(pno, height, events, set(), set())
                    if rendered:
                        orig_parts.append(rendered)
                return "\n".join(orig_parts), cleaned
            return cleaned
        except Exception as e:
            logger.error(f"解析 PDF 失败: {str(e)}")
            raise

    # ---- 以下为 PDF 表格解析辅助方法（pdfplumber） ----

    _CAPTION_RE = re.compile(r'^(Table|Figure|表|图)\s*[\d.]+', re.I)

    def _extract_page_structured(self, page, pno: int):
        """提取单页为结构化事件列表：文本行 (top, bottom, text) + 表格 (top, table, idx)。

        保留坐标供页眉/页脚识别；表格以独立事件保留，不参与页眉页脚判定。
        """
        tables = page.find_tables()
        words = page.extract_words(x_tolerance=1.5, y_tolerance=3)
        tb = [t.bbox for t in tables]

        def in_table(w) -> bool:
            x0, t0, x1, b1 = w['x0'], w['top'], w['x1'], w['bottom']
            for bx0, btop, bx1, bbottom in tb:
                if x0 >= bx0 - 1 and x1 <= bx1 + 1 and t0 >= btop - 1 and b1 <= bbottom + 1:
                    return True
            return False

        outside = [w for w in words if not in_table(w)]
        lines = self._group_lines(outside)  # list of (top, bottom, text)
        events = [line for line in lines]
        for t_idx, t in enumerate(tables):
            events.append((t.bbox[1], t.bbox[1], t, t_idx))  # (top, _, table, idx)
        events.sort(key=lambda e: e[0])
        return (pno, page.height, events)

    def _norm_header_text(self, text: str) -> str:
        """把文本中的数字序列归一化为 '#'，用于跨页统计页眉/页脚重复
        （页眉常含页码，归一化后才能把 '… 3/122'、'4/122 …' 合并为同一页眉）。"""
        return self._NUM_RE.sub('#', text.strip())

    def _detect_headers_footers(self, pages):
        """跨页统计页面顶部/底部边缘重复出现的文本行，识别页眉/页脚。

        文本先做数字归一化再统计（页眉常含页码，逐页不同需归一化）；
        仅当文本行位于页面边缘 且 在多页重复出现（>= 一半页数 且 至少 2 页）时，
        才判定为页眉/页脚，避免误删正文。
        """
        from collections import Counter
        total = len(pages)
        if total < 2:
            return set(), set()
        top_counter = Counter()
        bottom_counter = Counter()
        for _pno, height, events in pages:
            for ev in events:
                if not isinstance(ev[2], str):
                    continue
                top, bottom, text = ev[0], ev[1], self._norm_header_text(ev[2])
                if not text:
                    continue
                if top < height * self._EDGE_RATIO_TOP:
                    top_counter[text] += 1
                elif bottom > height * (1 - self._EDGE_RATIO_BOTTOM):
                    bottom_counter[text] += 1
        threshold = max(2, int(total * 0.5))
        headers = {t for t, c in top_counter.items() if c >= threshold}
        footers = {t for t, c in bottom_counter.items() if c >= threshold}
        if headers or footers:
            logger.info(f"识别到页眉 {len(headers)} 条、页脚 {len(footers)} 条，向量化前剔除")
        return headers, footers

    def _render_page(self, pno: int, height, events, headers, footers) -> str:
        """把结构化事件组装为页面文本，剔除页眉/页脚，表格渲染为 Markdown。"""
        header = f"【第{pno}页】\n"
        out = []
        for i, ev in enumerate(events):
            if not isinstance(ev[2], str):
                # 表格事件
                t, t_idx = ev[2], ev[3]
                caption = self._find_caption(events, i, t)
                md = self._table_to_markdown(t.extract())
                if caption:
                    out.append(f"<<<TABLE|第{pno}页|{caption}>>>\n{caption}\n{md}\n<<<END_TABLE>>>")
                else:
                    out.append(f"<<<TABLE|第{pno}页>>>\n{md}\n<<<END_TABLE>>>")
            else:
                top, bottom, text = ev[0], ev[1], ev[2].strip()
                if not text:
                    continue
                # 剔除页眉/页脚（仅当边缘位置 + 跨页重复都命中，文本先做数字归一化匹配）
                if top < height * self._EDGE_RATIO_TOP:
                    n = self._norm_header_text(text)
                    # 完全匹配 或 为某识别页眉的前缀（处理部分页面页眉无页码的情况）
                    if n in headers or any(h.startswith(n) for h in headers):
                        continue
                if bottom > height * (1 - self._EDGE_RATIO_BOTTOM) and self._norm_header_text(text) in footers:
                    continue
                out.append(text)
        if not out:
            return ""
        return header + "\n".join(out)

    def _group_lines(self, words):
        """把词按纵向（top）聚合成行，行内按 x0 排序拼接为一行文本。"""
        words = sorted(words, key=lambda w: (round(w['top'], 1), w['x0']))
        lines = []
        cur, cur_top, cur_bottom = [], None, None
        for w in words:
            if cur_top is None or abs(w['top'] - cur_top) <= 4:
                cur.append(w)
                cur_top = cur_top if cur_top is not None else w['top']
                cur_bottom = max(cur_bottom or 0, w['bottom'])
            else:
                lines.append((cur_top, cur_bottom, " ".join(x['text'] for x in cur)))
                cur, cur_top, cur_bottom = [w], w['top'], w['bottom']
        if cur:
            lines.append((cur_top, cur_bottom, " ".join(x['text'] for x in cur)))
        return lines

    def _find_caption(self, events, table_event_idx, table):
        """尝试从表格正上方紧邻的文本行捕获编号/标题（如 "Table 4 — ..."）。"""
        top = table.bbox[1]
        candidates = [ev for ev in events[:table_event_idx] if isinstance(ev[2], str)]
        if not candidates:
            return None
        prev = candidates[-1]
        # 仅当紧邻上方且形如编号标题时才认定是标题，避免误并正文
        if abs(prev[0] - top) < 40 and self._CAPTION_RE.match(prev[2].strip()):
            return prev[2].strip()
        return None

    def _table_to_markdown(self, rows) -> str:
        """把 pdfplumber 的表格行转成 Markdown 表格（首行为表头）。"""
        if not rows:
            return ""
        ncols = max((len(r) for r in rows), default=0)

        def cell(c):
            return "" if c is None else str(c).replace("\n", " ").strip()

        norm = [[cell(c) for c in r] + [""] * (ncols - len(r)) for r in rows]
        md = ["| " + " | ".join(norm[0]) + " |"]
        md.append("|" + "---|" * ncols)
        for r in norm[1:]:
            md.append("| " + " | ".join(r) + " |")
        return "\n".join(md)

    def _detect_page(self, text: str) -> Optional[int]:
        """从 chunk 文本里找出最后一个页面标记，用于溯源元数据。"""
        m = re.findall(r'【第(\d+)页】', text)
        return int(m[-1]) if m else None

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
                chunks.append(self._build_chunk(
                    current_chunk, document_id, document_name, len(chunks)))

                overlap_start = max(0, len(current_chunk) - self.chunk_overlap // 50)
                current_chunk = current_chunk[overlap_start:]
                current_length = sum(len(s) for s in current_chunk)

            current_chunk.append(sentence)
            current_length += sentence_length

        if current_chunk:
            chunks.append(self._build_chunk(
                current_chunk, document_id, document_name, len(chunks)))

        for chunk in chunks:
            chunk["total_chunks"] = len(chunks)

        logger.info(f"文档 {document_id} 分块完成，共 {len(chunks)} 个块")
        return chunks

    def _build_chunk(self, sentences, document_id, document_name, index) -> Dict[str, Any]:
        """构造一个 chunk，附带 page 与 source 溯源元数据。"""
        chunk_text = " ".join(sentences)
        page = self._detect_page(chunk_text)
        return {
            "id": f"{document_id}_chunk_{index}",
            "text": chunk_text,
            "document_id": document_id,
            "document_name": document_name,
            "chunk_index": index,
            "total_chunks": 0,
            "page": page,
            "source": f"{document_name} 第{page}页" if page else document_name,
        }

    def _split_into_sentences(self, text: str) -> List[str]:
        sentences = []
        # 表格块（<<<TABLE>>>...<<<END_TABLE>>>）作为整体保留，避免被句子切分（编号同 chunk）
        parts = re.split(r'(<<<TABLE.*?>>>.*?<<<END_TABLE>>>)', text, flags=re.S)
        for part in parts:
            if part.startswith('<<<TABLE'):
                s = part.strip()
                if s:
                    sentences.append(s)
            else:
                for s in re.split(r'[。！？\n]+', part):
                    s = s.strip()
                    if s:
                        sentences.append(s)
        return sentences


document_parser = DocumentParser()
