#!/usr/bin/env python3
"""
AI Code Reviewer - 轻量级AI代码审查工具
"""

from setuptools import setup, find_packages
import os

# 读取README文件
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
long_description = ""
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="ai-code-reviewer",
    version="1.0.0",
    author="longxiaokong",
    author_email="",
    description="轻量级AI代码审查工具 - Intelligent Code Review CLI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/longxiaokong/ai-code-reviewer",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "rich>=13.0.0",
        "PyYAML>=6.0",
        "GitPython>=3.1.0",
    ],
    extras_require={
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic>=0.18.0"],
        "ollama": ["ollama>=0.1.0"],
        "all": [
            "openai>=1.0.0",
            "anthropic>=0.18.0",
            "ollama>=0.1.0",
            "tree-sitter>=0.20.0",
            "tree-sitter-python>=0.20.0",
            "tree-sitter-javascript>=0.20.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-review=cli:main",
            "acr=cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
