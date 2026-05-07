#!/usr/bin/env python3
"""
报告生成器 - 生成多种格式的审查报告
"""

import json
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime
from .analyzer import AnalysisResult, CodeIssue, Severity


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, results: List[AnalysisResult]):
        self.results = results
    
    @property
    def total_issues(self) -> int:
        """总问题数"""
        return sum(r.issue_count for r in self.results)
    
    @property
    def total_files(self) -> int:
        """总文件数"""
        return len(self.results)
    
    @property
    def severity_summary(self) -> Dict[str, int]:
        """严重程度汇总"""
        summary = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for result in self.results:
            for severity, count in result.severity_counts.items():
                summary[severity] += count
        return summary
    
    def generate_terminal_report(self) -> str:
        """生成终端报告（使用Rich格式）"""
        lines = []
        
        # 标题
        lines.append("=" * 80)
        lines.append(" " * 25 + "🔍 AI Code Review Report")
        lines.append("=" * 80)
        lines.append("")
        
        # 汇总信息
        lines.append("📊 Summary")
        lines.append("-" * 80)
        lines.append(f"  Total Files Analyzed: {self.total_files}")
        lines.append(f"  Total Issues Found:   {self.total_issues}")
        lines.append("")
        
        # 严重程度分布
        lines.append("🚨 Issues by Severity")
        lines.append("-" * 80)
        for severity, count in self.severity_summary.items():
            emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵", "info": "⚪"}[severity]
            lines.append(f"  {emoji} {severity.upper():10} : {count:4d}")
        lines.append("")
        
        # 详细问题列表
        if self.total_issues > 0:
            lines.append("📋 Detailed Issues")
            lines.append("-" * 80)
            
            for result in self.results:
                if result.issues:
                    lines.append(f"\n📁 {result.file_path}")
                    lines.append(f"   Language: {result.language} | Lines: {result.total_lines}")
                    
                    for issue in result.issues:
                        emoji = {
                            Severity.CRITICAL: "🔴",
                            Severity.HIGH: "🟠",
                            Severity.MEDIUM: "🟡",
                            Severity.LOW: "🔵",
                            Severity.INFO: "⚪",
                        }.get(issue.severity, "⚪")
                        
                        lines.append(f"\n   {emoji} [{issue.rule_id}] Line {issue.line_number}: {issue.message}")
                        lines.append(f"      📍 {issue.file_path}:{issue.line_number}:{issue.column}")
                        lines.append(f"      💡 {issue.suggestion}")
                        if issue.code_snippet:
                            lines.append(f"      📝 {issue.code_snippet[:80]}")
        
        lines.append("")
        lines.append("=" * 80)
        lines.append(f"Report generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def generate_markdown_report(self) -> str:
        """生成Markdown报告"""
        lines = []
        
        # 标题
        lines.append("# 🔍 AI Code Review Report")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # 汇总
        lines.append("## 📊 Summary")
        lines.append("")
        lines.append(f"- **Total Files Analyzed:** {self.total_files}")
        lines.append(f"- **Total Issues Found:** {self.total_issues}")
        lines.append("")
        
        # 严重程度表格
        lines.append("## 🚨 Issues by Severity")
        lines.append("")
        lines.append("| Severity | Count |")
        lines.append("|----------|-------|")
        for severity, count in self.severity_summary.items():
            lines.append(f"| {severity.upper()} | {count} |")
        lines.append("")
        
        # 详细问题
        if self.total_issues > 0:
            lines.append("## 📋 Detailed Issues")
            lines.append("")
            
            for result in self.results:
                if result.issues:
                    lines.append(f"### 📁 {result.file_path}")
                    lines.append("")
                    lines.append(f"- **Language:** {result.language}")
                    lines.append(f"- **Total Lines:** {result.total_lines}")
                    lines.append(f"- **Issues:** {result.issue_count}")
                    lines.append("")
                    
                    for issue in result.issues:
                        lines.append(f"#### {issue.rule_id} - {issue.message}")
                        lines.append("")
                        lines.append(f"- **Severity:** {issue.severity.value.upper()}")
                        lines.append(f"- **Type:** {issue.issue_type.value}")
                        lines.append(f"- **Location:** `{issue.file_path}:{issue.line_number}:{issue.column}`")
                        lines.append("")
                        lines.append(f"**Suggestion:** {issue.suggestion}")
                        lines.append("")
                        if issue.code_snippet:
                            lines.append("**Code:**")
                            lines.append(f"```python\n{issue.code_snippet}\n```")
                            lines.append("")
        
        return "\n".join(lines)
    
    def generate_json_report(self) -> str:
        """生成JSON报告"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_files": self.total_files,
                "total_issues": self.total_issues,
                "severity_counts": self.severity_summary,
            },
            "results": [result.to_dict() for result in self.results],
        }
        return json.dumps(report, indent=2, ensure_ascii=False)
    
    def generate_sarif_report(self) -> str:
        """生成SARIF报告（GitHub/GitLab兼容）"""
        sarif = {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [{
                "tool": {
                    "driver": {
                        "name": "AI Code Reviewer",
                        "version": "1.0.0",
                        "informationUri": "https://github.com/longxiaokong/ai-code-reviewer",
                    }
                },
                "results": [],
            }]
        }
        
        for result in self.results:
            for issue in result.issues:
                sarif_result = {
                    "ruleId": issue.rule_id,
                    "level": self._severity_to_sarif_level(issue.severity),
                    "message": {
                        "text": issue.message,
                    },
                    "locations": [{
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": issue.file_path,
                            },
                            "region": {
                                "startLine": issue.line_number,
                                "startColumn": issue.column,
                            }
                        }
                    }],
                }
                sarif["runs"][0]["results"].append(sarif_result)
        
        return json.dumps(sarif, indent=2, ensure_ascii=False)
    
    def _severity_to_sarif_level(self, severity: Severity) -> str:
        """将Severity转换为SARIF级别"""
        mapping = {
            Severity.CRITICAL: "error",
            Severity.HIGH: "error",
            Severity.MEDIUM: "warning",
            Severity.LOW: "note",
            Severity.INFO: "note",
        }
        return mapping.get(severity, "warning")
    
    def save_report(self, output_path: str, format: str = "markdown") -> str:
        """保存报告到文件"""
        path = Path(output_path)
        
        if format == "markdown":
            content = self.generate_markdown_report()
            suffix = ".md"
        elif format == "json":
            content = self.generate_json_report()
            suffix = ".json"
        elif format == "sarif":
            content = self.generate_sarif_report()
            suffix = ".sarif"
        else:
            content = self.generate_terminal_report()
            suffix = ".txt"
        
        # 如果路径是目录，生成默认文件名
        if path.is_dir():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = path / f"ai-review-report-{timestamp}{suffix}"
        
        path.write_text(content, encoding="utf-8")
        return str(path)
