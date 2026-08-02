#!/usr/bin/env python3
"""Turso 云数据库封装 - 基于 libsql HTTP API
确保本机关机时数据库依然在线可用
"""

import os
import requests
from datetime import datetime


class TursoDB:
    """Turso 云数据库操作封装"""

    def __init__(self):
        self.db_url = os.getenv("TURSO_DB_URL", "")
        self.auth_token = os.getenv("TURSO_AUTH_TOKEN", "")
        # libsql:// 转为 https://
        if self.db_url.startswith("libsql://"):
            self.http_url = self.db_url.replace("libsql://", "https://")
        elif self.db_url.startswith("http://"):
            self.http_url = self.db_url.replace("http://", "https://")
        else:
            self.http_url = self.db_url
        self.available = bool(self.http_url and self.auth_token)

    def _execute(self, sql, args=None):
        """执行SQL（无返回数据）"""
        if not self.available:
            return None
        try:
            statement = {"sql": sql}
            if args:
                statement["args"] = [{"type": "text", "value": str(a)} for a in args]

            resp = requests.post(
                f"{self.http_url}/v2/execute",
                headers={
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json",
                },
                json={"statements": [statement]},
                timeout=15,
            )
            return resp.json() if resp.status_code == 200 else None
        except Exception:
            return None

    def _query(self, sql, args=None):
        """查询SQL，返回字典列表"""
        if not self.available:
            return []
        try:
            statement = {"sql": sql}
            if args:
                statement["args"] = [{"type": "text", "value": str(a)} for a in args]

            resp = requests.post(
                f"{self.http_url}/v2/query",
                headers={
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json",
                },
                json={"statements": [statement]},
                timeout=15,
            )
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("results", [])
                if results and isinstance(results, list):
                    result = results[0]
                    cols = result.get("cols", {}).get("name", [])
                    rows = result.get("rows", [])
                    parsed = []
                    for row in rows:
                        row_dict = {}
                        for i, cell in enumerate(row):
                            if i < len(cols):
                                val = cell.get("value") if isinstance(cell, dict) else cell
                                row_dict[cols[i]] = val
                        parsed.append(row_dict)
                    return parsed
            return []
        except Exception:
            return []

    def init_tables(self):
        """初始化数据库表"""
        self._execute("""
            CREATE TABLE IF NOT EXISTS systems (
                name TEXT PRIMARY KEY,
                base_url TEXT,
                teacher_id INTEGER,
                default_token TEXT
            )
        """)
        self._execute("""
            CREATE TABLE IF NOT EXISTS students (
                name TEXT PRIMARY KEY,
                student_id TEXT,
                system_name TEXT
            )
        """)
        self._execute("""
            CREATE TABLE IF NOT EXISTS tokens (
                system_name TEXT PRIMARY KEY,
                token TEXT,
                updated_at TEXT
            )
        """)

    def get_token(self, system_name):
        """获取系统Token"""
        rows = self._query("SELECT token FROM tokens WHERE system_name = ?", [system_name])
        if rows:
            return rows[0].get("token")
        return None

    def save_token(self, system_name, token):
        """保存/更新系统Token"""
        now = datetime.now().isoformat()
        self._execute(
            "INSERT OR REPLACE INTO tokens (system_name, token, updated_at) VALUES (?, ?, ?)",
            [system_name, token, now],
        )

    def get_all_students(self):
        """获取所有学生"""
        return self._query("SELECT name, student_id, system_name FROM students")

    def add_student(self, name, student_id, system_name):
        """添加学生"""
        self._execute(
            "INSERT OR REPLACE INTO students (name, student_id, system_name) VALUES (?, ?, ?)",
            [name, student_id, system_name],
        )

    def get_system_config(self, name):
        """获取系统配置"""
        rows = self._query("SELECT * FROM systems WHERE name = ?", [name])
        return rows[0] if rows else None
