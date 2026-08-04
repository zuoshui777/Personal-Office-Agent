# Router Agent
# 根据用户输入选择 Knowledge / Browser / Document / Workflow 等下游 Agent


def route_user_input(question: str) -> str:
    text = question.lower()

    if any(word in text for word in ("生成ppt", "答辩ppt", "制作ppt", "生成word", "生成excel", "总结文档", "生成报告")):
        return "document"

    if any(word in text for word in (
        "联网",
        "搜索网页",
        "最新",
        "查一下",
        "浏览器",
        "browser agent",
        "browser_search",
        "现在几点",
        "几点",
        "时间",
        "今天几号",
        "今天日期",
        "日期",
        "几号",
        "date",
        "天气",
        "实时",
        "github仓库"
    )):
        return "browser"

    if any(word in text for word in ("帮我完成", "工作流", "任务", "步骤", "先", "然后")):
        return "workflow"

    return "knowledge"
