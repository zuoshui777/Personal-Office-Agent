# Personal Office Agent 官方 MCP Server

from mcp.server.mcpserver import MCPServer

from poa_mcp.file_mcp import search_files, read_file, create_file
from poa_mcp.browser_mcp import web_search, open_page
from poa_mcp.excel_mcp import read_excel, analyze_excel
from poa_mcp.github_mcp import analyze_repo, generate_readme
from poa_mcp.wechat_mcp import send_notification


server = MCPServer(
    name="personal-office-agent",
    title="Personal Office Agent MCP",
    description="POA 的 MCP 工具服务",
    version="1.0.0"
)


server.tool(name="file_search", description="搜索目录中的文件")(search_files)
server.tool(name="file_read", description="读取本地文件内容")(read_file)
server.tool(name="file_create", description="创建本地文件")(create_file)
server.tool(name="browser_search", description="搜索网页内容")(web_search)
server.tool(name="browser_open", description="打开网页并提取正文")(open_page)
server.tool(name="excel_read", description="读取 Excel 文件")(read_excel)
server.tool(name="excel_analyze", description="分析 Excel 文件")(analyze_excel)
server.tool(name="github_analyze", description="分析本地 GitHub 仓库")(analyze_repo)
server.tool(name="github_generate_readme", description="生成 README")(generate_readme)
server.tool(name="wechat_notify", description="发送企业微信通知")(send_notification)


if __name__ == "__main__":
    server.run("stdio")
