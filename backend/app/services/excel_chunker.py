"""
Excel 专属语义分块引擎
支持行级分块和主题语义分块两种模式
"""
from typing import List, Dict, Any, Optional, Tuple
import uuid
from loguru import logger
from app.models.excel_document import ChunkMode, ChunkPreview, ChunkConfig
from app.services.excel_parser import excel_parser


class ExcelChunker:
    """
    Excel 文档分块器
    提供两种分块模式：
    1. ROW_LEVEL: 行级分块，适用于结构化明细表
    2. TOPIC_SEMANTIC: 主题语义分块，适用于半结构化文档
    """

    def __init__(self):
        self.parser = excel_parser

    def chunk_file(
        self,
        file_path: str,
        chunk_config: ChunkConfig,
        document_id: str,
        document_name: str,
        sheet_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        对 Excel 文件进行分块
        返回分块列表，每项包含: id, document_id, document_name, sheet_name, content, row_range, chunk_index
        """
        chunks = []

        if chunk_config.chunk_mode == ChunkMode.ROW_LEVEL:
            chunks = self._chunk_row_level(
                file_path, chunk_config, document_id, document_name, sheet_name
            )
        elif chunk_config.chunk_mode == ChunkMode.TOPIC_SEMANTIC:
            chunks = self._chunk_topic_semantic(
                file_path, chunk_config, document_id, document_name, sheet_name
            )

        logger.info(f"分块完成: {document_name}, 模式={chunk_config.chunk_mode.value}, 数量={len(chunks)}")
        return chunks

    def preview_chunks(
        self,
        file_path: str,
        chunk_config: ChunkConfig,
        sheet_name: Optional[str] = None,
        max_preview: int = 10
    ) -> List[ChunkPreview]:
        """
        预览分块效果（不入库）
        """
        chunks_data = self.chunk_file(
            file_path, chunk_config,
            document_id="preview",
            document_name="预览",
            sheet_name=sheet_name
        )
        return [
            ChunkPreview(
                chunk_index=c["chunk_index"],
                content=c["content"][:500] + "..." if len(c["content"]) > 500 else c["content"],
                row_range=c.get("row_range"),
                topic=c.get("topic")
            )
            for c in chunks_data[:max_preview]
        ]

    def _chunk_row_level(
        self,
        file_path: str,
        chunk_config: ChunkConfig,
        document_id: str,
        document_name: str,
        sheet_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        行级分块模式
        将表头与行数据绑定为「列名：列值」键值对文本
        一行生成一个独立分块，完整保留上下文
        """
        chunks = []
        chunk_index = 0

        sheets_to_process = [sheet_name] if sheet_name else [s.name for s in self.parser.get_sheets_info(file_path)]

        for sname in sheets_to_process:
            headers, rows = self.parser.parse_sheet_data(file_path, sname)
            if not headers or not rows:
                continue

            for row_idx, row in enumerate(rows, start=2):
                content_parts = []

                if chunk_config.include_headers and headers:
                    header_values = [f"{headers[i]}: {row[i]}" if i < len(row) else f"{headers[i]}: " 
                                   for i in range(len(headers))]
                    content_parts.append("表头上下文: " + " | ".join(header_values[:10]))

                row_values = [str(row[i]) if i < len(row) and row[i] else "" for i in range(len(headers))]
                content_parts.append(" | ".join(row_values[:10]))

                content = "\n".join(content_parts)
                content = content.strip()

                if content and len(content) > 5:
                    chunks.append({
                        "id": f"{document_id}_chunk_{chunk_index}",
                        "document_id": document_id,
                        "document_name": document_name,
                        "sheet_name": sname,
                        "content": content,
                        "chunk_index": chunk_index,
                        "row_range": f"第{row_idx}行",
                        "topic": None
                    })
                    chunk_index += 1

        return chunks

    def _chunk_topic_semantic(
        self,
        file_path: str,
        chunk_config: ChunkConfig,
        document_id: str,
        document_name: str,
        sheet_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        主题语义分块模式
        基于内容相似度进行分组，按业务语义单元拆分
        适用于半结构化文档（笔记、规则、案例库）
        """
        chunks = []
        chunk_index = 0

        sheets_to_process = [sheet_name] if sheet_name else [s.name for s in self.parser.get_sheets_info(file_path)]

        for sname in sheets_to_process:
            headers, rows = self.parser.parse_sheet_data(file_path, sname)
            if not headers or not rows:
                continue

            content_rows = []
            for row_idx, row in enumerate(rows, start=2):
                row_str = " | ".join([
                    f"{headers[i]}: {row[i]}" if i < len(row) and row[i] else ""
                    for i in range(min(len(headers), 10))
                ]).strip()
                if row_str and len(row_str) > 3:
                    content_rows.append({
                        "row_idx": row_idx,
                        "content": row_str,
                        "first_value": row[0] if row else ""
                    })

            if not content_rows:
                continue

            groups = self._group_by_similarity(content_rows, chunk_config.semantic_threshold)

            for group in groups:
                if len(group) == 0:
                    continue

                group_content = []
                row_range_parts = []

                for item in group:
                    group_content.append(item["content"])
                    row_range_parts.append(f"第{item['row_idx']}行")

                content = "\n".join(group_content)

                topic = group[0]["first_value"] if group[0]["first_value"] else f"主题{chunk_index + 1}"

                chunks.append({
                    "id": f"{document_id}_chunk_{chunk_index}",
                    "document_id": document_id,
                    "document_name": document_name,
                    "sheet_name": sname,
                    "content": content,
                    "chunk_index": chunk_index,
                    "row_range": f"第{min(r['row_idx'] for r in group)}-{max(r['row_idx'] for r in group)}行",
                    "topic": str(topic)[:50]
                })
                chunk_index += 1

        return chunks

    def _group_by_similarity(
        self,
        content_rows: List[Dict[str, Any]],
        threshold: float
    ) -> List[List[Dict[str, Any]]]:
        """
        基于首列内容相似度进行分组
        简单实现：相同首列值归为一组
        """
        groups = []
        current_group = []
        current_key = None

        for item in content_rows:
            key = str(item.get("first_value", ""))[:20].lower()

            if current_key is None:
                current_key = key
                current_group = [item]
            elif key == current_key or not key:
                current_group.append(item)
            else:
                if current_group:
                    groups.append(current_group)
                current_group = [item]
                current_key = key

        if current_group:
            groups.append(current_group)

        return groups

    def estimate_chunk_stats(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        统计分块信息
        """
        if not chunks:
            return {"total_chunks": 0, "avg_length": 0, "min_length": 0, "max_length": 0}

        lengths = [len(c["content"]) for c in chunks]
        return {
            "total_chunks": len(chunks),
            "avg_length": sum(lengths) // len(lengths),
            "min_length": min(lengths),
            "max_length": max(lengths),
            "by_sheet": self._count_by_sheet(chunks)
        }

    def _count_by_sheet(self, chunks: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        统计每个 Sheet 的分块数量
        """
        counts = {}
        for chunk in chunks:
            sheet = chunk.get("sheet_name", "未知")
            counts[sheet] = counts.get(sheet, 0) + 1
        return counts


excel_chunker = ExcelChunker()
