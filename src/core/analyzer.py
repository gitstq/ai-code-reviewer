#!/usr/bin/env python3
"""
代码分析引擎 - 负责代码解析、规则匹配和问题检测
"""

import re
import ast
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class Severity(Enum):
    """问题严重程度"""
    CRITICAL = "critical"  # 严重 - 必须修复
    HIGH = "high"          # 高 - 强烈建议修复
    MEDIUM = "medium"      # 中 - 建议修复
    LOW = "low"            # 低 - 可选修复
    INFO = "info"          # 信息 - 仅供参考


class IssueType(Enum):
    """问题类型"""
    SECURITY = "security"       # 安全问题
    QUALITY = "quality"         # 代码质量问题
    PERFORMANCE = "performance" # 性能问题
    STYLE = "style"             # 代码风格问题
    MAINTAINABILITY = "maintainability"  # 可维护性问题


@dataclass
class CodeIssue:
    """代码问题数据类"""
    file_path: str
    line_number: int
    column: int
    severity: Severity
    issue_type: IssueType
    rule_id: str
    message: str
    suggestion: str
    code_snippet: str
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column": self.column,
            "severity": self.severity.value,
            "issue_type": self.issue_type.value,
            "rule_id": self.rule_id,
            "message": self.message,
            "suggestion": self.suggestion,
            "code_snippet": self.code_snippet,
        }


@dataclass
class AnalysisResult:
    """分析结果"""
    file_path: str
    language: str
    total_lines: int
    issues: List[CodeIssue]
    
    @property
    def issue_count(self) -> int:
        return len(self.issues)
    
    @property
    def severity_counts(self) -> Dict[str, int]:
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for issue in self.issues:
            counts[issue.severity.value] += 1
        return counts
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "language": self.language,
            "total_lines": self.total_lines,
            "issue_count": self.issue_count,
            "severity_counts": self.severity_counts,
            "issues": [issue.to_dict() for issue in self.issues],
        }


class CodeAnalyzer:
    """代码分析器"""
    
    # 支持的文件扩展名映射
    LANGUAGE_MAP = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "javascript",
        ".tsx": "typescript",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".cpp": "cpp",
        ".c": "c",
        ".h": "c",
        ".hpp": "cpp",
    }
    
    def __init__(self):
        self.rules = self._load_rules()
    
    def _load_rules(self) -> Dict[str, List[Dict]]:
        """加载检测规则"""
        return {
            "security": self._load_security_rules(),
            "quality": self._load_quality_rules(),
            "performance": self._load_performance_rules(),
        }
    
    def _load_security_rules(self) -> List[Dict]:
        """加载安全规则"""
        return [
            {
                "id": "SEC-001",
                "name": "Hardcoded Secret",
                "pattern": r'(password|secret|token|key|api_key)\s*=\s*["\'][^"\']+["\']',
                "severity": Severity.CRITICAL,
                "message": "检测到硬编码的敏感信息",
                "suggestion": "使用环境变量或密钥管理服务存储敏感信息",
            },
            {
                "id": "SEC-002",
                "name": "SQL Injection Risk",
                "pattern": r'execute\s*\(\s*["\'].*%s.*["\']',
                "severity": Severity.CRITICAL,
                "message": "可能存在SQL注入风险",
                "suggestion": "使用参数化查询或ORM框架",
            },
            {
                "id": "SEC-003",
                "name": "Insecure Deserialization",
                "pattern": r'pickle\.loads|yaml\.load\(',
                "severity": Severity.HIGH,
                "message": "使用不安全的反序列化方法",
                "suggestion": "使用yaml.safe_load替代yaml.load，避免使用pickle处理不受信任的数据",
            },
            {
                "id": "SEC-004",
                "name": "Weak Hash Algorithm",
                "pattern": r'md5|sha1',
                "severity": Severity.MEDIUM,
                "message": "使用了弱哈希算法",
                "suggestion": "使用SHA-256或更强的哈希算法",
            },
            {
                "id": "SEC-005",
                "name": "Debug Mode Enabled",
                "pattern": r'debug\s*=\s*True',
                "severity": Severity.HIGH,
                "message": "调试模式已启用",
                "suggestion": "生产环境应禁用调试模式",
            },
        ]
    
    def _load_quality_rules(self) -> List[Dict]:
        """加载代码质量规则"""
        return [
            {
                "id": "QUAL-001",
                "name": "Too Long Function",
                "check": "function_length",
                "threshold": 50,
                "severity": Severity.MEDIUM,
                "message": "函数过长，建议拆分",
                "suggestion": "将长函数拆分为多个小函数，提高可读性",
            },
            {
                "id": "QUAL-002",
                "name": "Too Many Parameters",
                "check": "parameter_count",
                "threshold": 5,
                "severity": Severity.LOW,
                "message": "函数参数过多",
                "suggestion": "考虑使用对象或字典封装参数",
            },
            {
                "id": "QUAL-003",
                "name": "TODO Comment",
                "pattern": r'#\s*TODO',
                "severity": Severity.INFO,
                "message": "发现TODO注释",
                "suggestion": "及时完成TODO事项或创建Issue跟踪",
            },
            {
                "id": "QUAL-004",
                "name": "Bare Except",
                "pattern": r'except\s*:',
                "severity": Severity.MEDIUM,
                "message": "使用了裸except语句",
                "suggestion": "捕获具体的异常类型，避免隐藏错误",
            },
            {
                "id": "QUAL-005",
                "name": "Unused Import",
                "check": "unused_import",
                "severity": Severity.LOW,
                "message": "存在未使用的导入",
                "suggestion": "删除未使用的导入语句",
            },
        ]
    
    def _load_performance_rules(self) -> List[Dict]:
        """加载性能规则"""
        return [
            {
                "id": "PERF-001",
                "name": "List Concatenation in Loop",
                "pattern": r'\+\s*\[|list\s*\+=',
                "severity": Severity.MEDIUM,
                "message": "循环中使用列表拼接",
                "suggestion": "使用list.append()或列表推导式替代",
            },
            {
                "id": "PERF-002",
                "name": "String Concatenation in Loop",
                "pattern": r'\+\s*["\']',
                "severity": Severity.LOW,
                "message": "循环中使用字符串拼接",
                "suggestion": "使用str.join()或f-string替代",
            },
            {
                "id": "PERF-003",
                "name": "Inefficient Loop",
                "pattern": r'for.*in range\(len\(',
                "severity": Severity.LOW,
                "message": "使用range(len())遍历",
                "suggestion": "直接使用for item in iterable或enumerate()",
            },
        ]
    
    def get_language(self, file_path: str) -> Optional[str]:
        """根据文件路径获取语言类型"""
        ext = Path(file_path).suffix.lower()
        return self.LANGUAGE_MAP.get(ext)
    
    def analyze_file(self, file_path: str) -> AnalysisResult:
        """分析单个文件"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        language = self.get_language(file_path)
        if not language:
            return AnalysisResult(
                file_path=file_path,
                language="unknown",
                total_lines=0,
                issues=[],
            )
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
        
        issues = []
        
        # 应用安全规则
        for rule in self.rules["security"]:
            rule_issues = self._apply_regex_rule(file_path, content, lines, rule, IssueType.SECURITY)
            issues.extend(rule_issues)
        
        # 应用质量规则
        for rule in self.rules["quality"]:
            if "pattern" in rule:
                rule_issues = self._apply_regex_rule(file_path, content, lines, rule, IssueType.QUALITY)
            else:
                rule_issues = self._apply_ast_rule(file_path, content, rule, IssueType.QUALITY)
            issues.extend(rule_issues)
        
        # 应用性能规则
        for rule in self.rules["performance"]:
            rule_issues = self._apply_regex_rule(file_path, content, lines, rule, IssueType.PERFORMANCE)
            issues.extend(rule_issues)
        
        # Python AST分析
        if language == "python":
            ast_issues = self._analyze_python_ast(file_path, content)
            issues.extend(ast_issues)
        
        return AnalysisResult(
            file_path=file_path,
            language=language,
            total_lines=len(lines),
            issues=issues,
        )
    
    def _apply_regex_rule(self, file_path: str, content: str, lines: List[str], 
                          rule: Dict, issue_type: IssueType) -> List[CodeIssue]:
        """应用正则表达式规则"""
        issues = []
        pattern = rule.get("pattern", "")
        if not pattern:
            return issues
        
        for match in re.finditer(pattern, content, re.IGNORECASE):
            # 计算行号
            line_num = content[:match.start()].count('\n') + 1
            col = match.start() - content.rfind('\n', 0, match.start()) - 1
            
            # 获取代码片段
            code_snippet = lines[line_num - 1].strip() if line_num <= len(lines) else ""
            
            issue = CodeIssue(
                file_path=file_path,
                line_number=line_num,
                column=col,
                severity=rule.get("severity", Severity.MEDIUM),
                issue_type=issue_type,
                rule_id=rule.get("id", "UNKNOWN"),
                message=rule.get("message", ""),
                suggestion=rule.get("suggestion", ""),
                code_snippet=code_snippet,
            )
            issues.append(issue)
        
        return issues
    
    def _apply_ast_rule(self, file_path: str, content: str, 
                        rule: Dict, issue_type: IssueType) -> List[CodeIssue]:
        """应用AST规则"""
        issues = []
        # AST规则检查在Python专用分析中实现
        return issues
    
    def _analyze_python_ast(self, file_path: str, content: str) -> List[CodeIssue]:
        """使用Python AST进行深度分析"""
        issues = []
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return issues
        
        for node in ast.walk(tree):
            # 检查函数长度
            if isinstance(node, ast.FunctionDef):
                func_lines = node.end_lineno - node.lineno if node.end_lineno else 0
                if func_lines > 50:
                    issue = CodeIssue(
                        file_path=file_path,
                        line_number=node.lineno,
                        column=node.col_offset,
                        severity=Severity.MEDIUM,
                        issue_type=IssueType.QUALITY,
                        rule_id="QUAL-001",
                        message=f"函数过长 ({func_lines} 行)，建议拆分",
                        suggestion="将长函数拆分为多个小函数，提高可读性和可维护性",
                        code_snippet=content.split('\n')[node.lineno - 1].strip() if node.lineno <= len(content.split('\n')) else "",
                    )
                    issues.append(issue)
                
                # 检查参数数量
                param_count = len(node.args.args) + len(node.args.kwonlyargs)
                if param_count > 5:
                    issue = CodeIssue(
                        file_path=file_path,
                        line_number=node.lineno,
                        column=node.col_offset,
                        severity=Severity.LOW,
                        issue_type=IssueType.QUALITY,
                        rule_id="QUAL-002",
                        message=f"函数参数过多 ({param_count} 个)",
                        suggestion="考虑使用对象或字典封装参数",
                        code_snippet=content.split('\n')[node.lineno - 1].strip() if node.lineno <= len(content.split('\n')) else "",
                    )
                    issues.append(issue)
            
            # 检查裸except
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    issue = CodeIssue(
                        file_path=file_path,
                        line_number=node.lineno,
                        column=node.col_offset,
                        severity=Severity.MEDIUM,
                        issue_type=IssueType.QUALITY,
                        rule_id="QUAL-004",
                        message="使用了裸except语句",
                        suggestion="捕获具体的异常类型，避免隐藏错误",
                        code_snippet=content.split('\n')[node.lineno - 1].strip() if node.lineno <= len(content.split('\n')) else "",
                    )
                    issues.append(issue)
        
        return issues
    
    def analyze_directory(self, directory: str, exclude_patterns: List[str] = None) -> List[AnalysisResult]:
        """分析整个目录"""
        results = []
        exclude_patterns = exclude_patterns or ['venv', '.git', '__pycache__', 'node_modules', '.pytest_cache']
        
        path = Path(directory)
        
        for file_path in path.rglob('*'):
            # 跳过排除的目录
            if any(pattern in str(file_path) for pattern in exclude_patterns):
                continue
            
            # 只分析支持的文件
            if file_path.is_file() and file_path.suffix.lower() in self.LANGUAGE_MAP:
                try:
                    result = self.analyze_file(str(file_path))
                    results.append(result)
                except Exception as e:
                    print(f"分析文件失败 {file_path}: {e}")
        
        return results
