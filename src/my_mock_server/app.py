import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# 1. 初始化 FastMCP 服务，服务名为 HospitalMockServer
mcp = FastMCP("HospitalMockServer")

# 2. 动态定位同目录下的 mock.json 文件路径
MOCK_FILE_PATH = Path(__file__).parent / "mock.json"

def load_mock_data():
    """读取并解析 mock.json 数据"""
    if not MOCK_FILE_PATH.exists():
        return {"error": "mock.json 文件不存在"}
    with open(MOCK_FILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

@mcp.tool()
def get_all_patients() -> str:
    """获取所有模拟患者列表数据"""
    data = load_mock_data()
    return json.dumps(data, ensure_ascii=False, indent=2)

@mcp.tool()
def query_patient_by_id(patient_id: str) -> str:
    """根据患者 ID (如 P001) 查询特定的患者详细信息"""
    data = load_mock_data()
    patients = data.get("patients", [])
    for p in patients:
        if p.get("id") == patient_id:
            return json.dumps(p, ensure_ascii=False, indent=2)
    return f"未找到 ID 为 {patient_id} 的患者信息"

def main():
    """主入口函数，提供给 pyproject.toml 调用"""
    mcp.run()

if __name__ == "__main__":
    main()
