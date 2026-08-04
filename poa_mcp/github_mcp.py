# GitHub MCP

from pathlib import Path


def analyze_repo(path: str):
    root = Path(path)
    if not root.is_dir():
        return {"error": "仓库目录不存在"}

    files = list(root.rglob("*"))
    code_files = [
        str(file) for file in files
        if file.is_file() and file.suffix.lower() in {".py", ".js", ".ts", ".java", ".md", ".json"}
    ]
    readme = root / "README.md"
    readme_text = readme.read_text(encoding="utf-8", errors="ignore")[:3000] if readme.exists() else ""
    return {
        "file_count": len(code_files),
        "readme": readme_text,
        "files": code_files[:50]
    }


def generate_readme(path: str, content: str):
    file = Path(path) / "README.md"
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(content, encoding="utf-8")
    return {"path": str(file)}


def register(register_tool):
    register_tool("github_analyze", "分析本地 GitHub 仓库", analyze_repo)
    register_tool("github_generate_readme", "生成 README", generate_readme, permission="write")
