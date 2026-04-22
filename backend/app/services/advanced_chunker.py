"""
高级语义分块引擎 v2.0
优化特性：
1. 语义重叠分块（15%-20%）
2. 上下文前缀增强（文档标题、章节路径）
3. 特殊内容保护（代码块、表格、专业条款）
4. 父子块关系维护
"""

from typing import List, Dict, Any, Optional, Tuple
import re
from loguru import logger
from app.config import settings


class AdvancedChunker:
    """
    高级语义分块器
    支持重叠分块、上下文增强、特殊内容保护
    """
    
    def __init__(self):
        self.chunk_size = 500  # 降低块大小，更容易命中短句
        self.chunk_overlap_ratio = 0.3  # 30%语义重叠，确保跨分割点的内容能被检索到
        self.overlap_size = max(150, int(self.chunk_size * self.chunk_overlap_ratio))
    
    def chunk_text(
        self,
        text: str,
        document_id: str,
        document_name: str,
        section_path: str = ""
    ) -> List[Dict[str, Any]]:
        """
        高级分块入口
        1. 检测特殊内容并保护
        2. 智能分块
        3. 添加上下文前缀
        4. 建立父子块关系
        """
        chunks = []
        if not text or not text.strip():
            logger.warning(f"文档内容为空: {document_id}")
            return chunks
        
        # Step 1: 提取并保护特殊内容
        protected_content = self._protect_special_content(text)
        
        # Step 2: 智能分块
        raw_chunks = self._smart_chunk(
            protected_content['cleaned_text'],
            document_id,
            document_name,
            protected_content['special_markers']
        )
        
        # Step 3: 添加上下文前缀
        enhanced_chunks = self._add_context_prefix(
            raw_chunks,
            document_id,
            document_name,
            section_path
        )
        
        # Step 4: 建立父子块关系
        chunks = self._build_parent_child_relations(enhanced_chunks)
        
        # Step 5: 更新元信息
        for i, chunk in enumerate(chunks):
            chunk["chunk_index"] = i
            chunk["total_chunks"] = len(chunks)
        
        logger.info(f"高级分块完成: {document_id}, 共 {len(chunks)} 个块")
        return chunks
    
    def _protect_special_content(self, text: str) -> Dict[str, Any]:
        """
        检测并保护特殊内容
        - 代码块（``` ``` ``` 或 缩进代码）
        - 表格（| 表格 | 格式）
        - 列表项（- 或 1. 格式）
        - 专业条款（编号条款：第X条、第X章）
        """
        special_markers = []
        protected_text = text
        
        # 保护代码块
        code_pattern = r'(```[\s\S]*?```| {4}.+(\n.+)*)'
        for match in re.finditer(code_pattern, text):
            marker = f"[CODE_BLOCK_{len(special_markers)}]"
            special_markers.append({
                "type": "code",
                "marker": marker,
                "content": match.group()
            })
            protected_text = protected_text.replace(match.group(), marker)
        
        # 保护表格
        table_pattern = r'(\|.+\|\n)+(\|[-: ]+\|\n)?(\|.+\|\n?)+'
        for match in re.finditer(table_pattern, protected_text):
            if match.group().strip():
                marker = f"[TABLE_{len(special_markers)}]"
                special_markers.append({
                    "type": "table",
                    "marker": marker,
                    "content": match.group()
                })
                protected_text = protected_text.replace(match.group(), marker)
        
        return {
            "cleaned_text": protected_text,
            "special_markers": special_markers
        }
    
    def _smart_chunk(
        self,
        text: str,
        document_id: str,
        document_name: str,
        special_markers: List[Dict]
    ) -> List[Dict[str, Any]]:
        """
        智能分块策略
        1. 按段落和语义单元分割
        2. 确保特殊内容不被拆分
        3. 应用语义重叠
        """
        chunks = []
        
        # 按段落分割
        paragraphs = self._split_by_paragraphs(text)
        
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para_length = len(para)
            
            # 检查段落是否包含特殊内容标记
            is_special = any(marker in para for marker in 
                           [m['marker'] for m in special_markers])
            
            # 如果是特殊内容（代码、表格），强制完整保留
            if is_special:
                if current_chunk:
                    chunk_text = self._join_chunk_content(current_chunk)
                    if len(chunk_text) > 50:  # 忽略太短的块
                        chunks.append(self._create_chunk(chunk_text, document_id, document_name, len(chunks)))
                    current_chunk = []
                    current_length = 0
                
                # 直接添加整个段落作为块（即使很长也要完整保留）
                if len(para) > 0:
                    chunks.append(self._create_chunk(para, document_id, document_name, len(chunks)))
                continue
            
            # 普通段落处理
            # 稍微放宽限制，让段落可以稍微超过chunk_size（最多1.2倍）
            if current_length + para_length > self.chunk_size * 1.2 and current_chunk:
                chunk_text = self._join_chunk_content(current_chunk)
                if len(chunk_text) > 50:
                    chunks.append(self._create_chunk(chunk_text, document_id, document_name, len(chunks)))
                
                # 语义重叠：保留最后部分作为下一个块的开头
                overlap_content = self._get_overlap_content(current_chunk)
                current_chunk = [overlap_content] if overlap_content else []
                current_length = len(overlap_content) if overlap_content else 0
            
            current_chunk.append(para)
            current_length += para_length
        
        # 处理最后一个块
        if current_chunk:
            chunk_text = self._join_chunk_content(current_chunk)
            if len(chunk_text) > 50:
                chunks.append(self._create_chunk(chunk_text, document_id, document_name, len(chunks)))
        
        # 恢复特殊内容
        for i, chunk in enumerate(chunks):
            chunks[i]['content'] = self._restore_special_content(
                chunk['content'], special_markers
            )
            chunks[i]['text'] = chunks[i]['content']  # 保留原始文本用于嵌入
        
        return chunks
    
    def _split_by_paragraphs(self, text: str) -> List[str]:
        """
        按段落和句子分割，保持语义完整性
        优先按段落分割，如果段落过长再按句子分割，确保短句不被拆分
        """
        # 先按双换行分割大段落
        paragraphs = re.split(r'\n\n+', text)
        
        result = []
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # 如果段落过长（超过块大小的2倍），按句子分割
            if len(para) > self.chunk_size * 2:
                sentences = self._split_into_sentences(para)
                for sentence in sentences:
                    sentence = sentence.strip()
                    if sentence:
                        result.append(sentence)
            # 如果段落超过块大小，按换行分割
            elif len(para) > self.chunk_size:
                sub_paras = [p.strip() for p in para.split('\n') if p.strip()]
                for sub_para in sub_paras:
                    if sub_para:
                        result.append(sub_para)
            else:
                result.append(para)
        
        return result
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        按句子分割，保持句子完整性
        不拆分包含关键词的完整短句
        """
        # 按中文标点分割句子
        sentences = re.split(r'[。！？；\n]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # 合并过短的句子
        merged = []
        current = ""
        for sentence in sentences:
            if len(current) + len(sentence) < self.chunk_size:
                current += sentence + "。"
            else:
                if current:
                    merged.append(current)
                current = sentence
        
        if current:
            merged.append(current)
        
        return merged if merged else sentences
    
    def _join_chunk_content(self, paragraphs: List[str]) -> str:
        """将段落列表合并为块内容"""
        return '\n\n'.join(paragraphs)
    
    def _get_overlap_content(self, paragraphs: List[str]) -> str:
        """
        获取重叠内容（保留完整的段落）
        确保不截断段落的中间部分
        """
        if not paragraphs:
            return ""
        
        # 取最后1-2个段落作为重叠（完整的段落，不截断）
        num_paras = max(1, min(2, len(paragraphs)))
        
        overlap_parts = paragraphs[-num_paras:]
        overlap_text = '\n\n'.join(overlap_parts)
        
        # 如果重叠内容过长，只保留最后一个段落
        max_overlap = int(self.chunk_size * self.chunk_overlap_ratio)
        if len(overlap_text) > max_overlap:
            # 只保留最后一个完整段落
            overlap_text = paragraphs[-1] if paragraphs else ""
        
        return overlap_text
    
    def _create_chunk(self, content: str, document_id: str, document_name: str, index: int) -> Dict[str, Any]:
        """创建分块对象"""
        return {
            "id": f"{document_id}_chunk_{index}",
            "content": content,
            "text": content,
            "document_id": document_id,
            "document_name": document_name,
            "chunk_index": index,
            "is_parent": False,
            "child_ids": []
        }
    
    def _restore_special_content(self, text: str, special_markers: List[Dict]) -> str:
        """恢复特殊内容"""
        result = text
        for marker_info in special_markers:
            result = result.replace(marker_info['marker'], marker_info['content'])
        return result
    
    def _add_context_prefix(
        self,
        chunks: List[Dict[str, Any]],
        document_id: str,
        document_name: str,
        section_path: str
    ) -> List[Dict[str, Any]]:
        """添加上下文前缀，增强语义"""
        for i, chunk in enumerate(chunks):
            prefixes = []
            
            # 文档标题前缀
            prefixes.append(f"【文档】{document_name}")
            
            # 章节路径前缀
            if section_path:
                prefixes.append(f"【位置】{section_path}")
            
            # 块序号前缀（用于定位）
            prefixes.append(f"【段落{i+1}】")
            
            # 组装前缀
            prefix = " | ".join(prefixes)
            
            # 合并到内容
            enhanced_content = f"{prefix}\n\n{chunk['content']}"
            
            chunks[i]['content'] = enhanced_content
        
        return chunks
    
    def _build_parent_child_relations(
        self,
        chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        建立父子块关系
        - 细粒度块（子块）：用于检索
        - 粗粒度块（父块）：包含2-3个相邻子块，用于LLM回答
        """
        if len(chunks) < 3:
            # 块太少，不需要父子关系
            return chunks
        
        # 创建父块：每3个子块创建一个父块
        parent_chunks = []
        for i in range(0, len(chunks), 3):
            child_ids = []
            parent_content_parts = []
            
            for j in range(i, min(i + 3, len(chunks))):
                child_ids.append(chunks[j]['id'])
                parent_content_parts.append(chunks[j]['text'])
            
            parent_id = f"{chunks[i]['document_id']}_parent_{i//3}"
            parent_content = "\n\n---\n\n".join(parent_content_parts)
            parent_document_name = chunks[i].get('document_name', '未知文档')
            
            # 父块添加更完整的上下文
            parent_prefix = f"【文档】{parent_document_name} | 【完整段落组】包含 {len(child_ids)} 个相关段落"
            parent_content = f"{parent_prefix}\n\n{parent_content}"
            
            parent_chunk = {
                "id": parent_id,
                "content": parent_content,
                "text": parent_content,
                "document_id": chunks[i]['document_id'],
                "document_name": parent_document_name,
                "chunk_index": i,
                "is_parent": True,
                "child_ids": child_ids
            }
            
            parent_chunks.append(parent_chunk)
            
            # 更新子块的父块引用
            for child_id in child_ids:
                for chunk in chunks:
                    if chunk['id'] == child_id:
                        chunk['parent_id'] = parent_id
        
        # 合并父子块
        return chunks + parent_chunks
    
    def estimate_stats(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """统计分块信息"""
        if not chunks:
            return {
                "total_chunks": 0,
                "parent_chunks": 0,
                "child_chunks": 0,
                "avg_length": 0
            }
        
        child_chunks = [c for c in chunks if not c.get('is_parent', False)]
        parent_chunks = [c for c in chunks if c.get('is_parent', False)]
        
        lengths = [len(c.get('text', c.get('content', ''))) for c in chunks]
        
        return {
            "total_chunks": len(chunks),
            "parent_chunks": len(parent_chunks),
            "child_chunks": len(child_chunks),
            "avg_length": sum(lengths) // len(lengths) if lengths else 0,
            "min_length": min(lengths) if lengths else 0,
            "max_length": max(lengths) if lengths else 0
        }


advanced_chunker = AdvancedChunker()
