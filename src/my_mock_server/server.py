import json
from pathlib import Path
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP

# 1. 初始化 FastMCP 服务，服务名建议根据业务明确命名
mcp = FastMCP("PediatricCKDServer")

# 2. 动态定位同目录下的 mock.json 文件路径
MOCK_FILE_PATH = Path(__file__).parent / "mock.json"

def load_mock_data() -> Dict[str, Any]:
    """读取并解析 mock.json 数据"""
    if not MOCK_FILE_PATH.exists():
        return {"patients": [], "knowledge_base": []}
    with open(MOCK_FILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# ==================== 患者数据相关 Tools ====================

@mcp.tool()
def get_all_patients() -> str:
    """获取所有模拟患者的列表概要信息（包含患者ID、姓名、年龄、诊断、CKD分期及主治医生）。
    适用于需要快速了解所有患者基本情况时调用。
    """
    data = load_mock_data()
    patients = data.get("patients", [])
    
    # 提取精简列表，避免数据过大占用大模型上下文（Context Window）
    summary_list = []
    for p in patients:
        summary_list.append({
            "patient_id": p.get("patient_id"),
            "name": p.get("name"),
            "age": p.get("age"),
            "gender": p.get("gender"),
            "diagnosis": p.get("diagnosis"),
            "ckd_stage": p.get("ckd_stage"),
            "attending_doctor": p.get("attending_doctor")
        })
    return json.dumps(summary_list, ensure_ascii=False, indent=2)

@mcp.tool()
def query_patient_by_id(patient_id: str) -> str:
    """根据患者 ID (如 'P001', 'P002') 查询特定的患者完整详细信息。
    包含评估、饮食计划、实验室检查及干预记录。
    """
    data = load_mock_data()
    patients = data.get("patients", [])
    target_id = patient_id.strip().upper()
    
    for p in patients:
        # 修复：正确读取 patient_id 字段
        if p.get("patient_id", "").upper() == target_id:
            return json.dumps(p, ensure_ascii=False, indent=2)
            
    return json.dumps({"error": f"未找到 ID 为 '{patient_id}' 的患者信息"}, ensure_ascii=False)

@mcp.tool()
def search_patients(keyword: str) -> str:
    """根据关键字模糊搜索患者。
    支持匹配患者姓名、诊断名称、主治医师、营养师或过敏原（如 '海鲜', '牛奶', '重度肥胖', '李主任'）。
    """
    data = load_mock_data()
    patients = data.get("patients", [])
    kw = keyword.strip().lower()
    
    results = []
    for p in patients:
        searchable_text = f"{p.get('name')} {p.get('diagnosis')} {p.get('attending_doctor')} {p.get('nutritionist')} {' '.join(p.get('allergies', []))}".lower()
        if kw in searchable_text:
            results.append(p)
            
    if not results:
        return json.dumps({"message": f"未找到与关键字 '{keyword}' 匹配的患者"}, ensure_ascii=False)
        
    return json.dumps(results, ensure_ascii=False, indent=2)

@mcp.tool()
def get_patient_lab_results(patient_id: str) -> str:
    """快速获取指定患者 (如 'P001') 的所有实验室检查结果（包含肾功能、电解质、营养指标）。"""
    data = load_mock_data()
    patients = data.get("patients", [])
    target_id = patient_id.strip().upper()
    
    for p in patients:
        if p.get("patient_id", "").upper() == target_id:
            return json.dumps({
                "patient_id": p.get("patient_id"),
                "name": p.get("name"),
                "lab_results": p.get("lab_results", [])
            }, ensure_ascii=False, indent=2)
            
    return json.dumps({"error": f"未找到 ID 为 '{patient_id}' 的患者"}, ensure_ascii=False)

@mcp.tool()
def get_patient_diet_plan(patient_id: str) -> str:
    """快速获取指定患者 (如 'P001') 的饮食计划（包含热量目标、蛋白限额、推荐/禁用食物、餐次安排及补充剂）。"""
    data = load_mock_data()
    patients = data.get("patients", [])
    target_id = patient_id.strip().upper()
    
    for p in patients:
        if p.get("patient_id", "").upper() == target_id:
            return json.dumps({
                "patient_id": p.get("patient_id"),
                "name": p.get("name"),
                "diet_plans": p.get("diet_plans", [])
            }, ensure_ascii=False, indent=2)
            
    return json.dumps({"error": f"未找到 ID 为 '{patient_id}' 的患者"}, ensure_ascii=False)

# ==================== 知识库相关 Tools ====================

@mcp.tool()
def query_knowledge_base(keyword: str = "") -> str:
    """检索儿童 CKD 营养临床知识库指导原则。
    若提供 keyword（如 '蛋白质', '高钾', '钙磷代谢', '生长迟缓', '透析', '贫血'），则筛选相关条目；若为空则返回完整知识库。
    """
    data = load_mock_data()
    kb = data.get("knowledge_base", [])
    
    if not keyword.strip():
        return json.dumps(kb, ensure_ascii=False, indent=2)
        
    kw = keyword.strip().lower()
    results = []
    for item in kb:
        text = f"{item.get('title')} {item.get('content')} {' '.join(item.get('tags', []))}".lower()
        if kw in text:
            results.append(item)
            
    if not results:
        return json.dumps({"message": f"知识库中未找到与 '{keyword}' 相关的条目"}, ensure_ascii=False)
        
    return json.dumps(results, ensure_ascii=False, indent=2)


def main():
    """主入口函数，提供给 pyproject.toml 或命令行调用"""
    mcp.run()

if __name__ == "__main__":
    main()
