"""
知识库摘要服务 - 自动生成和更新知识库摘要
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
import httpx
import re
from pathlib import Path
from app.services.storage import knowledge_base_storage, document_storage, skill_config_storage, excel_doc_storage
from app.services.excel_parser import excel_parser
from app.utils.logger import logger

LLM_API_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_MODEL = "gpt-4o-mini"

MAX_DOCUMENT_LENGTH = 50000


def _get_llm_config() -> Dict[str, Any]:
    """获取 LLM 配置"""
    config = skill_config_storage.get("llm_config")
    if not config:
        return {
            "api_url": LLM_API_URL,
            "api_key": "",
            "model": DEFAULT_MODEL
        }
    return config


def _extract_excel_content(excel_doc: Dict[str, Any]) -> str:
    """从Excel文档中提取文本内容"""
    try:
        file_path = excel_doc.get("file_path")
        if not file_path or not Path(file_path).exists():
            logger.warning(f"Excel文档文件不存在: {file_path}")
            return f"Excel文件: {excel_doc.get('name')} (文件不存在)"
        
        sheet_count = excel_doc.get("sheet_count", 0)
        sheets = excel_doc.get("sheets", [])
        
        content_parts = []
        # 提取每个sheet的内容
        for sheet_info in sheets:
            sheet_name = sheet_info.get("name")
            if not sheet_name:
                continue
                
            try:
                headers, rows = excel_parser.parse_sheet_data(file_path, sheet_name)
                if headers and rows:
                    # 构建表头
                    header_text = " | ".join([str(h) for h in headers if h])
                    content_parts.append(f"Sheet: {sheet_name}")
                    content_parts.append(f"表头: {header_text}")
                    
                    # 添加部分行数据（前20行作为示例）
                    sample_rows = rows[:20]
                    for i, row in enumerate(sample_rows, start=2):
                        row_text = " | ".join([str(cell) for cell in row])
                        content_parts.append(f"行{i}: {row_text}")
                        
                    content_parts.append(f"... 共{len(rows)}行")
                    content_parts.append("---")
            except Exception as e:
                logger.warning(f"解析Excel sheet {sheet_name} 失败: {str(e)}")
                content_parts.append(f"Sheet: {sheet_name} (解析失败: {str(e)})")
                continue
        
        if content_parts:
            return "\n".join(content_parts)
        else:
            return f"Excel文件: {excel_doc.get('name')} (无有效内容)"
            
    except Exception as e:
        logger.error(f"提取Excel内容失败 {excel_doc.get('name')}: {str(e)}")
        return f"Excel文件: {excel_doc.get('name')} (提取失败: {str(e)})"


def _get_kb_documents(kb_id: str) -> list:
    """获取知识库的所有文档（包括普通文档和Excel文档）"""
    kb_docs = []
    
    # 获取普通文档
    all_docs = document_storage.get_all() or {}
    for doc_id, doc_info in all_docs.items():
        if doc_info.get("knowledge_base_id") == kb_id:
            kb_docs.append(doc_info)
    
    # 获取Excel文档
    all_excel_docs = excel_doc_storage.get_all() or {}
    for key, excel_doc in all_excel_docs.items():
        # 检查是否以excel_doc_前缀开头
        if isinstance(key, str) and key.startswith("excel_doc_"):
            if excel_doc.get("knowledge_base_id") == kb_id:
                # 提取Excel文档内容
                content = _extract_excel_content(excel_doc)
                # 创建类似普通文档的结构
                doc_info = {
                    "id": excel_doc.get("id"),
                    "name": excel_doc.get("name"),
                    "knowledge_base_id": kb_id,
                    "content": content,
                    "document_type": "excel",
                    "file_path": excel_doc.get("file_path"),
                    "size": excel_doc.get("size", 0)
                }
                kb_docs.append(doc_info)
    
    return kb_docs


def _build_summary_prompt(kb_name: str, documents: list) -> str:
    """构建摘要生成的提示词"""
    doc_contents = []
    total_length = 0
    
    for doc in documents:
        content = doc.get("content", "")
        if content and total_length < MAX_DOCUMENT_LENGTH:
            doc_contents.append(f"【{doc.get('name', '未命名')}】\n{content}")
            total_length += len(content)
    
    docs_text = "\n\n---\n\n".join(doc_contents)
    
    if not docs_text:
        return f"知识库 '{kb_name}' 中没有任何文档内容。"
    
    prompt = f"""请分析以下知识库的文档内容，生成一个简洁的摘要。

知识库名称：{kb_name}

文档内容：
{docs_text}

请生成一个包含以下方面的摘要（JSON格式）：
{{
    "summary": "知识库的简要描述，包含主要主题、覆盖范围和用途（200-500字）",
    "topics": ["主题1", "主题2", "主题3"],
    "document_count": 文档总数,
    "key_content": "关键内容要点（100字以内）"
}}

要求：
1. summary 应该简洁明了，能帮助快速判断这个知识库包含什么内容
2. topics 应该包含 3-5 个主要主题
3. key_content 应该包含最重要的几个内容点
4. 只返回JSON，不要有其他解释
"""
    return prompt


def _clean_json_string(text: str) -> str:
    """清理 LLM 返回的文本，移除 markdown 代码块标记"""
    text = text.strip()
    
    text = re.sub(r'^```json\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^```\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    
    return text.strip()


async def generate_kb_summary(kb_id: str) -> Optional[Dict[str, Any]]:
    """
    为指定的知识库生成摘要
    
    Args:
        kb_id: 知识库ID
    
    Returns:
        包含摘要信息的字典，如果失败返回 None
    """
    try:
        llm_config = _get_llm_config()
        
        if not llm_config.get("api_key"):
            logger.error("KB Summary: 未配置 LLM API Key")
            return None
        
        kb_data = knowledge_base_storage.get(kb_id)
        if not kb_data:
            logger.error(f"KB Summary: 知识库 {kb_id} 不存在")
            return None
        
        kb_name = kb_data.get("name", "未命名")
        documents = _get_kb_documents(kb_id)
        
        if not documents:
            logger.warning(f"KB Summary: 知识库 '{kb_name}' 没有文档")
            summary_text = f"该知识库目前没有文档。主题：{kb_data.get('description', '未定义')}"
            return {
                "summary": summary_text,
                "topics": [],
                "key_content": "暂无内容"
            }
        
        prompt = _build_summary_prompt(kb_name, documents)
        
        api_url = llm_config.get("api_url", LLM_API_URL)
        api_key = llm_config.get("api_key", "")
        model = llm_config.get("model", DEFAULT_MODEL)
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1500
        }
        
        logger.info(f"KB Summary: 正在为 '{kb_name}' 生成摘要...")
        logger.info(f"KB Summary: 使用 API - {api_url}, 模型 - {model}")
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(api_url, headers=headers, json=payload)
            
            if response.status_code != 200:
                error_detail = response.text
                logger.error(f"KB Summary LLM 调用失败: HTTP {response.status_code} - {error_detail}")
                return None
            
            result = response.json()
            logger.info(f"KB Summary: 收到 LLM 响应")
            
            choices = result.get("choices", [])
            if not choices:
                logger.error(f"KB Summary: LLM 响应中没有 choices: {result}")
                return None
            
            assistant_content = choices[0].get("message", {}).get("content", "")
            
            if not assistant_content:
                logger.error(f"KB Summary: LLM 返回了空内容")
                return None
            
            logger.info(f"KB Summary: 收到响应内容，长度 {len(assistant_content)} 字符")
            
            cleaned_content = _clean_json_string(assistant_content)
            logger.info(f"KB Summary: 清理后长度 {len(cleaned_content)} 字符")
            
            import json
            try:
                summary_data = json.loads(cleaned_content)
                logger.info(f"KB Summary: 成功为 '{kb_name}' 生成摘要")
                
                return {
                    "summary": summary_data.get("summary", ""),
                    "topics": summary_data.get("topics", []),
                    "key_content": summary_data.get("key_content", ""),
                    "document_count": len(documents)
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"KB Summary: 解析LLM响应失败 - {e}")
                logger.error(f"KB Summary: 清理后内容: {cleaned_content[:500]}...")
                return None
                
    except Exception as e:
        logger.error(f"KB Summary: 生成摘要失败 - {str(e)}")
        return None


def update_kb_summary(kb_id: str, summary_data: Dict[str, Any]):
    """
    更新知识库的摘要信息
    
    Args:
        kb_id: 知识库ID
        summary_data: 摘要数据（包含 summary, topics, key_content）
    """
    kb_data = knowledge_base_storage.get(kb_id)
    if not kb_data:
        return False
    
    kb_data["summary"] = summary_data.get("summary", "")
    kb_data["summary_updated_at"] = datetime.now().isoformat()
    knowledge_base_storage.set(kb_id, kb_data)
    
    logger.info(f"KB Summary: 已更新知识库 '{kb_data.get('name')}' 的摘要")
    return True


async def regenerate_all_summaries() -> Dict[str, Any]:
    """
    重新生成所有知识库的摘要
    
    Returns:
        包含成功和失败数量的统计信息
    """
    all_kbs = knowledge_base_storage.get_all() or {}
    
    results = {
        "total": len(all_kbs),
        "success": 0,
        "failed": 0,
        "details": []
    }
    
    for kb_id in all_kbs.keys():
        summary_data = await generate_kb_summary(kb_id)
        
        if summary_data:
            update_kb_summary(kb_id, summary_data)
            results["success"] += 1
            kb_name = all_kbs[kb_id].get("name", kb_id)
            results["details"].append({
                "kb_id": kb_id,
                "kb_name": kb_name,
                "status": "success",
                "summary_preview": summary_data.get("summary", "")[:100] + "..."
            })
        else:
            results["failed"] += 1
            kb_name = all_kbs[kb_id].get("name", kb_id)
            results["details"].append({
                "kb_id": kb_id,
                "kb_name": kb_name,
                "status": "failed"
            })
    
    logger.info(f"KB Summary: 批量更新完成 - 成功 {results['success']}, 失败 {results['failed']}")
    return results


def get_kb_summary_info(kb_id: str) -> Optional[Dict[str, Any]]:
    """
    获取知识库的摘要信息
    
    Args:
        kb_id: 知识库ID
    
    Returns:
        摘要信息字典
    """
    kb_data = knowledge_base_storage.get(kb_id)
    if not kb_data:
        return None
    
    return {
        "summary": kb_data.get("summary"),
        "summary_updated_at": kb_data.get("summary_updated_at"),
        "has_summary": bool(kb_data.get("summary"))
    }
