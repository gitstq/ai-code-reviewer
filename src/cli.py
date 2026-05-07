#!/usr/bin/env python3
"""
AI Code Reviewer - 命令行接口
"""

import os
import sys
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from core.analyzer import CodeAnalyzer
from core.llm_client import LLMClientFactory
from core.reporter import ReportGenerator

console = Console()


def print_banner():
    """打印程序横幅"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   🤖 AI Code Reviewer - 智能代码审查工具 v1.0.0           ║
    ║                                                           ║
    ║   轻量级 · 多LLM支持 · 零依赖 · 本地优先                 ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="cyan")


@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='显示版本信息')
@click.pass_context
def cli(ctx, version):
    """AI Code Reviewer - 智能代码审查工具"""
    if version:
        console.print("AI Code Reviewer v1.0.0")
        return
    
    if ctx.invoked_subcommand is None:
        print_banner()
        console.print("\n[bold green]使用方法:[/bold green] ai-review [COMMAND] [OPTIONS]")
        console.print("\n[bold]可用命令:[/bold]")
        console.print("  analyze    分析代码文件或目录")
        console.print("  review     使用AI审查代码")
        console.print("  config     配置管理")
        console.print("\n[bold]示例:[/bold]")
        console.print("  ai-review analyze ./src")
        console.print("  ai-review review ./main.py --provider openai")
        console.print("\n使用 [bold]ai-review --help[/bold] 查看详细帮助")


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--output', '-o', type=str, help='输出报告路径')
@click.option('--format', '-f', type=click.Choice(['terminal', 'markdown', 'json', 'sarif']), 
              default='terminal', help='报告格式')
@click.option('--exclude', '-e', multiple=True, help='排除的目录或文件模式')
def analyze(path: str, output: Optional[str], format: str, exclude: tuple):
    """分析代码文件或目录"""
    print_banner()
    
    analyzer = CodeAnalyzer()
    exclude_patterns = list(exclude) if exclude else None
    
    path_obj = Path(path)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        if path_obj.is_file():
            task = progress.add_task(f"[cyan]分析文件: {path}...", total=None)
            try:
                result = analyzer.analyze_file(path)
                results = [result]
            except Exception as e:
                console.print(f"[red]分析失败: {e}[/red]")
                sys.exit(1)
        else:
            task = progress.add_task(f"[cyan]分析目录: {path}...", total=None)
            try:
                results = analyzer.analyze_directory(path, exclude_patterns)
            except Exception as e:
                console.print(f"[red]分析失败: {e}[/red]")
                sys.exit(1)
    
    # 生成报告
    generator = ReportGenerator(results)
    
    if format == 'terminal':
        console.print(generator.generate_terminal_report())
    elif format == 'markdown':
        content = generator.generate_markdown_report()
        if output:
            output_path = generator.save_report(output, 'markdown')
            console.print(f"[green]报告已保存: {output_path}[/green]")
        else:
            console.print(content)
    elif format == 'json':
        content = generator.generate_json_report()
        if output:
            output_path = generator.save_report(output, 'json')
            console.print(f"[green]报告已保存: {output_path}[/green]")
        else:
            console.print(content)
    elif format == 'sarif':
        content = generator.generate_sarif_report()
        if output:
            output_path = generator.save_report(output, 'sarif')
            console.print(f"[green]报告已保存: {output_path}[/green]")
        else:
            console.print(content)
    
    # 显示汇总
    console.print("\n")
    summary_table = Table(title="📊 分析汇总")
    summary_table.add_column("指标", style="cyan")
    summary_table.add_column("数值", style="green")
    summary_table.add_row("分析文件数", str(generator.total_files))
    summary_table.add_row("发现问题数", str(generator.total_issues))
    console.print(summary_table)


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--provider', '-p', type=click.Choice(['openai', 'anthropic', 'ollama', 'deepseek']),
              help='LLM提供商')
@click.option('--model', '-m', type=str, help='模型名称')
@click.option('--stream', is_flag=True, help='流式输出')
def review(path: str, provider: Optional[str], model: Optional[str], stream: bool):
    """使用AI审查代码"""
    print_banner()
    
    # 确定LLM提供商
    if not provider:
        provider = LLMClientFactory.get_default_provider()
        console.print(f"[yellow]未指定提供商，使用默认: {provider}[/yellow]")
    
    # 读取代码
    try:
        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()
    except Exception as e:
        console.print(f"[red]读取文件失败: {e}[/red]")
        sys.exit(1)
    
    # 创建LLM客户端
    try:
        kwargs = {"model": model} if model else {}
        client = LLMClientFactory.create(provider, **kwargs)
    except Exception as e:
        console.print(f"[red]创建LLM客户端失败: {e}[/red]")
        console.print("[yellow]提示: 请检查API密钥环境变量是否设置[/yellow]")
        sys.exit(1)
    
    console.print(f"[cyan]正在使用 {provider} 审查代码...[/cyan]\n")
    
    # 执行审查
    try:
        if stream:
            console.print("[bold]AI审查结果:[/bold]\n")
            for chunk in client.stream_review(code, context=f"文件: {path}"):
                console.print(chunk, end="")
            console.print("\n")
        else:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task("[cyan]AI正在分析代码...", total=None)
                response = client.review_code(code, context=f"文件: {path}")
            
            console.print(Panel(
                response.content,
                title=f"🤖 AI审查结果 ({response.model})",
                border_style="green"
            ))
            
            if response.usage:
                usage_table = Table(title="📊 Token使用统计")
                usage_table.add_column("类型", style="cyan")
                usage_table.add_column("数量", style="green")
                for key, value in response.usage.items():
                    usage_table.add_row(key, str(value))
                console.print(usage_table)
    
    except Exception as e:
        console.print(f"[red]AI审查失败: {e}[/red]")
        sys.exit(1)


@cli.command()
def config():
    """显示配置信息"""
    print_banner()
    
    console.print("\n[bold]🔧 配置信息[/bold]\n")
    
    # API密钥状态
    api_table = Table(title="API密钥状态")
    api_table.add_column("提供商", style="cyan")
    api_table.add_column("状态", style="green")
    api_table.add_column("环境变量", style="yellow")
    
    providers = {
        "OpenAI": ("OPENAI_API_KEY", bool(os.getenv("OPENAI_API_KEY"))),
        "Anthropic": ("ANTHROPIC_API_KEY", bool(os.getenv("ANTHROPIC_API_KEY"))),
        "DeepSeek": ("DEEPSEEK_API_KEY", bool(os.getenv("DEEPSEEK_API_KEY"))),
    }
    
    for name, (env_var, configured) in providers.items():
        status = "✅ 已配置" if configured else "❌ 未配置"
        api_table.add_row(name, status, env_var)
    
    console.print(api_table)
    
    # 支持的提供商
    console.print("\n[bold]支持的LLM提供商:[/bold]")
    for provider in LLMClientFactory.list_providers():
        console.print(f"  • {provider}")
    
    # 配置示例
    console.print("\n[bold]配置示例:[/bold]")
    console.print("""
# 设置API密钥（添加到 ~/.bashrc 或 ~/.zshrc）
export OPENAI_API_KEY="your-api-key"
export ANTHROPIC_API_KEY="your-api-key"
export DEEPSEEK_API_KEY="your-api-key"

# 使用本地Ollama（无需API密钥）
ollama run codellama
ai-review review ./src --provider ollama
    """)


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--base', '-b', type=str, help='基准分支或commit')
def diff(path: str, base: Optional[str]):
    """分析Git变更（增量审查）"""
    print_banner()
    
    try:
        from git import Repo
    except ImportError:
        console.print("[red]GitPython未安装，无法使用Git功能[/red]")
        sys.exit(1)
    
    try:
        repo = Repo(path, search_parent_directories=True)
    except Exception as e:
        console.print(f"[red]无法找到Git仓库: {e}[/red]")
        sys.exit(1)
    
    # 获取变更文件
    if base:
        try:
            diff_index = repo.head.commit.diff(base)
        except Exception as e:
            console.print(f"[red]获取diff失败: {e}[/red]")
            sys.exit(1)
    else:
        diff_index = repo.index.diff(None)
    
    changed_files = [item.a_path for item in diff_index if item.change_type in ['M', 'A']]
    
    if not changed_files:
        console.print("[yellow]没有检测到变更的文件[/yellow]")
        return
    
    console.print(f"[green]检测到 {len(changed_files)} 个变更文件[/green]\n")
    
    # 分析变更文件
    analyzer = CodeAnalyzer()
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        for file_path in changed_files:
            full_path = Path(repo.working_dir) / file_path
            if full_path.exists() and analyzer.get_language(str(full_path)):
                task = progress.add_task(f"[cyan]分析: {file_path}...", total=None)
                try:
                    result = analyzer.analyze_file(str(full_path))
                    results.append(result)
                except Exception as e:
                    console.print(f"[yellow]跳过 {file_path}: {e}[/yellow]")
    
    # 生成报告
    generator = ReportGenerator(results)
    console.print(generator.generate_terminal_report())


def main():
    """主入口"""
    cli()


if __name__ == '__main__':
    main()
