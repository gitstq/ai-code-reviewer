#!/usr/bin/env python3
"""
测试代码分析器
"""

import tempfile
import os
from pathlib import Path

from core.analyzer import CodeAnalyzer, Severity, IssueType


def test_analyzer_init():
    """测试分析器初始化"""
    analyzer = CodeAnalyzer()
    assert analyzer is not None
    assert "security" in analyzer.rules
    assert "quality" in analyzer.rules
    assert "performance" in analyzer.rules


def test_get_language():
    """测试语言检测"""
    analyzer = CodeAnalyzer()
    
    assert analyzer.get_language("test.py") == "python"
    assert analyzer.get_language("test.js") == "javascript"
    assert analyzer.get_language("test.ts") == "typescript"
    assert analyzer.get_language("test.java") == "java"
    assert analyzer.get_language("test.go") == "go"
    assert analyzer.get_language("test.rs") == "rust"
    assert analyzer.get_language("test.txt") is None


def test_analyze_file_with_security_issues():
    """测试安全漏洞检测"""
    analyzer = CodeAnalyzer()
    
    # 创建包含安全问题的临时文件
    code = '''
# 硬编码密码
password = "secret123"
api_key = "sk-1234567890"

# SQL注入风险
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = %s" % user_id
    execute(query)

# 不安全的反序列化
import pickle
data = pickle.loads(untrusted_data)

# 调试模式
debug = True
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        result = analyzer.analyze_file(temp_path)
        
        assert result.file_path == temp_path
        assert result.language == "python"
        assert result.issue_count > 0
        
        # 检查是否检测到硬编码密码
        password_issues = [i for i in result.issues if "password" in i.message.lower()]
        assert len(password_issues) > 0
        
        # 检查是否检测到SQL注入
        sql_issues = [i for i in result.issues if "sql" in i.message.lower()]
        assert len(sql_issues) > 0
        
    finally:
        os.unlink(temp_path)


def test_analyze_file_with_quality_issues():
    """测试代码质量问题检测"""
    analyzer = CodeAnalyzer()
    
    # 创建包含质量问题的临时文件
    code = '''
# 未使用的导入
import os
import sys
import json

def very_long_function(arg1, arg2, arg3, arg4, arg5, arg6, arg7):
    """这是一个很长的函数"""
    x = 1
    x = 2
    x = 3
    x = 4
    x = 5
    x = 6
    x = 7
    x = 8
    x = 9
    x = 10
    # ... 更多代码
    return x

# TODO: 需要重构
def old_function():
    pass

# 裸except
try:
    risky_operation()
except:
    pass
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        result = analyzer.analyze_file(temp_path)
        
        assert result.issue_count > 0
        
        # 检查是否检测到长函数
        long_func_issues = [i for i in result.issues if "长" in i.message or "long" in i.message.lower()]
        
        # 检查是否检测到裸except
        except_issues = [i for i in result.issues if "except" in i.message.lower()]
        
        # 检查是否检测到TODO
        todo_issues = [i for i in result.issues if "TODO" in i.message]
        assert len(todo_issues) > 0
        
    finally:
        os.unlink(temp_path)


def test_analyze_directory():
    """测试目录分析"""
    analyzer = CodeAnalyzer()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建测试文件
        py_file = Path(tmpdir) / "test.py"
        py_file.write_text("password = 'secret'\n")
        
        js_file = Path(tmpdir) / "test.js"
        js_file.write_text("const password = 'secret';\n")
        
        # 创建子目录
        subdir = Path(tmpdir) / "subdir"
        subdir.mkdir()
        py_file2 = subdir / "test2.py"
        py_file2.write_text("# TODO: fix this\n")
        
        results = analyzer.analyze_directory(tmpdir)
        
        assert len(results) == 3
        
        # 检查是否都检测到问题
        total_issues = sum(r.issue_count for r in results)
        assert total_issues > 0


def test_severity_counts():
    """测试严重程度统计"""
    analyzer = CodeAnalyzer()
    
    code = '''
password = "secret"
debug = True
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        result = analyzer.analyze_file(temp_path)
        
        counts = result.severity_counts
        assert "critical" in counts
        assert "high" in counts
        assert "medium" in counts
        assert "low" in counts
        assert "info" in counts
        
        # 硬编码密码应该是critical
        assert counts["critical"] > 0
        
    finally:
        os.unlink(temp_path)


if __name__ == "__main__":
    test_analyzer_init()
    test_get_language()
    test_analyze_file_with_security_issues()
    test_analyze_file_with_quality_issues()
    test_analyze_directory()
    test_severity_counts()
    print("所有测试通过!")
