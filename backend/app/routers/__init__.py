from .knowledge_base import router as knowledge_base_router
from .document import router as document_router
from .vector import router as vector_router
from .skill import router as skill_router
from .system import router as system_router
from .excel_doc import router as excel_doc_router
from .chat import router as chat_router
from .agent import router as agent_router
from .agent_template import router as agent_template_router
from .memory import router as memory_router

__all__ = [
    "knowledge_base_router",
    "document_router",
    "vector_router",
    "skill_router",
    "system_router",
    "excel_doc_router",
    "chat_router",
    "agent_router",
    "agent_template_router",
    "memory_router",
]
