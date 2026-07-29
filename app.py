"""
童肾营养师 MCP Server
====================
基于 MCP (Model Context Protocol) 的儿童肾脏病营养辅助决策数据查询服务。
提供患儿信息、营养评估、饮食方案、实验室指标、营养干预记录等查询工具，
供"童肾营养师"多智能体系统中的其他智能体调用。

作者: 童肾营养师团队
平台: 华为 Nexent + ModelScope MCP
"""

import json
import os
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

# ──────────────────────────────────────────────
# 1. 创建 MCP Server 实例
# ──────────────────────────────────────────────
mcp = FastMCP(
    name="pediatric-renal-nutrition",
    version="1.0.0",
    description="童肾营养师辅助决策数据查询服务 —— 提供儿童肾脏病营养相关的模拟数据查询能力",
)

# ──────────────────────────────────────────────
# 2. 加载 MOCK 数据（启动时一次性读入内存）
# ──────────────────────────────────────────────
_DATA_PATH = Path(__file__).parent / "mock.json"


def _load_data() -> dict:
    """从 mock.json 加载全部模拟数据。"""
    if not _DATA_PATH.exists():
        raise FileNotFoundError(f"数据文件不存在: {_DATA_PATH}")
    with open(_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


DATA: dict = _load_data()


# ──────────────────────────────────────────────
# 3. 内部辅助函数
# ──────────────────────────────────────────────
def _find_patient(patient_id: str) -> Optional[dict]:
    """根据 patient_id 查找患儿记录。"""
    for p in DATA.get("patients", []):
        if p["patient_id"] == patient_id:
            return p
    return None


def _ok(data) -> str:
    """统一成功返回格式。"""
    return json.dumps({"status": "success", "data": data}, ensure_ascii=False, indent=2)


def _err(msg: str) -> str:
    """统一错误返回格式。"""
    return json.dumps({"status": "error", "message": msg}, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────────
# 4. MCP Tools（供其他智能体调用）
# ──────────────────────────────────────────────

@mcp.tool()
def list_patients() -> str:
    """
    获取所有患儿的基本信息列表。

    返回每位患儿的 ID、姓名、年龄、性别、诊断等摘要信息，
    可用于快速浏览全部在管患儿。

    Returns:
        JSON 字符串，包含患儿列表。
    """
    patients = DATA.get("patients", [])
    summary = [
        {
            "patient_id": p["patient_id"],
            "name": p["name"],
            "age": p["age"],
            "gender": p["gender"],
            "diagnosis": p["diagnosis"],
            "ckd_stage": p.get("ckd_stage", "N/A"),
        }
        for p in patients
    ]
    return _ok(summary)


@mcp.tool()
def get_patient_detail(patient_id: str) -> str:
    """
    查询指定患儿的完整基本信息。

    Args:
        patient_id: 患儿唯一标识，例如 "P001"。

    Returns:
        JSON 字符串，包含患儿的详细基本信息（姓名、年龄、身高、体重、诊断、CKD分期等）。
    """
    patient = _find_patient(patient_id)
    if not patient:
        return _err(f"未找到患儿: {patient_id}")
    # 只返回基本信息部分，不含嵌套的评估/方案
    basic = {k: v for k, v in patient.items() if k not in ("nutrition_assessments", "diet_plans", "lab_results", "interventions")}
    return _ok(basic)


@mcp.tool()
def get_nutrition_assessment(patient_id: str, assessment_id: Optional[str] = None) -> str:
    """
    查询指定患儿的营养评估记录。

    可查询全部评估记录，也可通过 assessment_id 查询某一次评估。
    评估内容包括：SGA评分、BMI、血清白蛋白、能量摄入评估、蛋白质摄入评估等。

    Args:
        patient_id: 患儿唯一标识，例如 "P001"。
        assessment_id: 评估记录ID（可选），例如 "NA001"。不传则返回全部。

    Returns:
        JSON 字符串，包含营养评估数据。
    """
    patient = _find_patient(patient_id)
    if not patient:
        return _err(f"未找到患儿: {patient_id}")

    assessments = patient.get("nutrition_assessments", [])
    if assessment_id:
        assessments = [a for a in assessments if a["assessment_id"] == assessment_id]
        if not assessments:
            return _err(f"未找到评估记录: {assessment_id}")
    return _ok(assessments)


@mcp.tool()
def get_diet_plan(patient_id: str, plan_id: Optional[str] = None) -> str:
    """
    查询指定患儿的饮食方案。

    可查询全部饮食方案，也可通过 plan_id 查询某一个方案。
    方案内容包括：每日能量目标、蛋白质限制、钠/钾/磷限制、推荐食物、禁忌食物、餐次安排等。

    Args:
        patient_id: 患儿唯一标识，例如 "P001"。
        plan_id: 饮食方案ID（可选），例如 "DP001"。不传则返回全部。

    Returns:
        JSON 字符串，包含饮食方案数据。
    """
    patient = _find_patient(patient_id)
    if not patient:
        return _err(f"未找到患儿: {patient_id}")

    plans = patient.get("diet_plans", [])
    if plan_id:
        plans = [p for p in plans if p["plan_id"] == plan_id]
        if not plans:
            return _err(f"未找到饮食方案: {plan_id}")
    return _ok(plans)


@mcp.tool()
def get_lab_results(patient_id: str, test_type: Optional[str] = None) -> str:
    """
    查询指定患儿的实验室检查指标。

    支持按检查类型筛选，如：肾功能、电解质、营养指标、血常规、尿常规等。

    Args:
        patient_id: 患儿唯一标识，例如 "P001"。
        test_type: 检查类型（可选），可选值包括 "renal_function"（肾功能）、
                   "electrolytes"（电解质）、"nutrition_markers"（营养指标）、
                   "blood_routine"（血常规）、"urine"（尿常规）。
                   不传则返回全部检查结果。

    Returns:
        JSON 字符串，包含实验室检查数据。
    """
    patient = _find_patient(patient_id)
    if not patient:
        return _err(f"未找到患儿: {patient_id}")

    labs = patient.get("lab_results", [])
    if test_type:
        labs = [l for l in labs if l.get("test_type") == test_type]
        if not labs:
            return _err(f"未找到类型为 '{test_type}' 的检查记录")
    return _ok(labs)


@mcp.tool()
def get_interventions(patient_id: str, status: Optional[str] = None) -> str:
    """
    查询指定患儿的营养干预记录。

    可按干预状态筛选：ongoing（进行中）、completed（已完成）、adjusted（已调整）。

    Args:
        patient_id: 患儿唯一标识，例如 "P001"。
        status: 干预状态（可选），可选值 "ongoing"、"completed"、"adjusted"。
                不传则返回全部干预记录。

    Returns:
        JSON 字符串，包含营养干预记录。
    """
    patient = _find_patient(patient_id)
    if not patient:
        return _err(f"未找到患儿: {patient_id}")

    interventions = patient.get("interventions", [])
    if status:
        interventions = [i for i in interventions if i.get("status") == status]
        if not interventions:
            return _err(f"未找到状态为 '{status}' 的干预记录")
    return _ok(interventions)


@mcp.tool()
def get_nutrition_knowledge(topic: str) -> str:
    """
    查询儿童肾脏病营养知识库。

    根据主题关键词检索相关的营养知识条目，包括CKD各分期的营养管理要点、
    常见营养问题处理、特殊营养素补充建议等。

    Args:
        topic: 知识主题关键词，例如 "蛋白质限制"、"高钾血症"、"钙磷代谢"、
               "生长迟缓"、"透析营养" 等。

    Returns:
        JSON 字符串，包含匹配的知识条目列表。
    """
    knowledge_base = DATA.get("knowledge_base", [])
    topic_lower = topic.lower()
    matched = [
        k for k in knowledge_base
        if topic_lower in k.get("title", "").lower()
        or topic_lower in k.get("content", "").lower()
        or any(topic_lower in tag.lower() for tag in k.get("tags", []))
    ]
    if not matched:
        return _err(f"未找到与 '{topic}' 相关的知识条目，请尝试其他关键词")
    return _ok(matched)


@mcp.tool()
def get_system_info() -> str:
    """
    获取本 MCP 服务的系统信息和可用工具列表。

    返回服务名称、版本、描述、数据概况（患儿数量、知识条目数量）以及所有可用工具的名称和说明。

    Returns:
        JSON 字符串，包含系统信息。
    """
    tools_info = [
        {"name": "list_patients", "description": "获取所有患儿基本信息列表"},
        {"name": "get_patient_detail", "description": "查询指定患儿完整基本信息"},
        {"name": "get_nutrition_assessment", "description": "查询营养评估记录"},
        {"name": "get_diet_plan", "description": "查询饮食方案"},
        {"name": "get_lab_results", "description": "查询实验室检查指标"},
        {"name": "get_interventions", "description": "查询营养干预记录"},
        {"name": "get_nutrition_knowledge", "description": "查询营养知识库"},
        {"name": "get_system_info", "description": "获取系统信息"},
    ]
    info = {
        "service_name": "pediatric-renal-nutrition",
        "version": "1.0.0",
        "description": "童肾营养师辅助决策数据查询服务",
        "platform": "华为 Nexent + ModelScope MCP",
        "data_summary": {
            "total_patients": len(DATA.get("patients", [])),
            "total_knowledge_entries": len(DATA.get("knowledge_base", [])),
        },
        "available_tools": tools_info,
    }
    return _ok(info)


# ──────────────────────────────────────────────
# 5. 启动入口
# ──────────────────────────────────────────────
if __name__ == "__main__":
    # ModelScope 托管时使用 sse 传输；本地调试可用 stdio
    transport = os.getenv("MCP_TRANSPORT", "sse")
    mcp.run(transport=transport)
