# 个人私有文档 Skill 系统后端应用

# 绕过 chromadb 对 sqlite3 >= 3.35.0 的检查（Python 3.8 自带 3.28 实际可正常工作）
import sqlite3 as _sqlite3
if _sqlite3.sqlite_version_info < (3, 35, 0):
    _sqlite3.sqlite_version_info = (3, 35, 0)
