import gradio as gr
import json
import os
from datetime import datetime

# ========== 数据加载 ==========
MOCK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mock.json")


def load_data():
    with open(MOCK_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ========== MCP 工具函数 ==========

def query_patient(patient_id: str = "", name: str = "") -> str:
    """
    查询患儿基本信息。支持按患者ID或姓名查询，也可查询所有在院患儿列表。

    Args:
        patient_id: 患者ID（如 P20260001），留空则不按ID筛选
        name: 患者姓名关键词，留空则不按姓名筛选
    """
    data = load_data()
    patients = data.get("patients", [])

    if patient_id:
        patients = [p for p in patients if patient_id.upper() in p["patient_id"].upper()]
    if name:
        patients = [p for p in patients if name in p["name"]]

    if not patients:
        return "未找到匹配的患儿信息"

    lines = []
    lines.append("=" * 50)
    lines.append("患儿信息查询结果")
    lines.append("=" * 50)

    for p in patients:
        allergy_str = "、".join(p["allergies"]) if p["allergies"] else "无"
        lines.append("")
        lines.append("【" + p["name"] + "】（" + p["patient_id"] + "）")
        lines.append("  性别/年龄：" + p["gender"] + " / " + str(p["age"]) + p["age_unit"])
        lines.append("  体重/身高：" + str(p["weight_kg"]) + "kg / " + str(p["height_cm"]) + "cm")
        lines.append("  诊断：" + p["diagnosis"])
        lines.append("  CKD分期：" + str(p["ckd_stage"]) + "期")
        lines.append("  原发病：" + p["primary_disease"])
        lines.append("  过敏史：" + allergy_str)
        lines.append("  主治医生：" + p["attending_doctor"])
        lines.append("  状态：" + p["status"])
        lines.append("  备注：" + p["notes"])
        lines.append("-" * 50)

    return "\n".join(lines)


def query_lab_results(patient_id: str) -> str:
    """
    查询患儿的检验结果（肾功能、电解质、营养指标等）。

    Args:
        patient_id: 患者ID（如 P20260001）
    """
    data = load_data()
    labs = data.get("lab_results", [])

    matched = [l for l in labs if l["patient_id"].upper() == patient_id.upper()]

    if not matched:
        return "未找到患者 " + patient_id + " 的检验结果"

    lab = matched[0]
    lines = []
    lines.append("=" * 60)
    lines.append("检验报告（" + lab["test_date"] + "）")
    lines.append("=" * 60)
    lines.append("")
    lines.append("{:<14}{:<14}{:<20}{:<16}{}".format("项目", "结果", "单位", "参考范围", "标志"))
    lines.append("-" * 60)

    for key, item in lab["items"].items():
        flag_icon = "[异常]" if ("↑" in item["flag"] or "↓" in item["flag"]) else "[正常]"
        lines.append("{:<14}{:<14}{:<20}{:<16}{}".format(
            key, str(item["value"]), item["unit"], item["reference"], flag_icon + item["flag"]
        ))

    return "\n".join(lines)


def query_nutrition_assessment(patient_id: str) -> str:
    """
    查询患儿的营养评估报告，包括24小时膳食摄入、目标摄入量、营养风险评级和饮食建议。

    Args:
        patient_id: 患者ID（如 P20260001）
    """
    data = load_data()
    assessments = data.get("nutrition_assessment", [])

    matched = [a for a in assessments if a["patient_id"].upper() == patient_id.upper()]

    if not matched:
        return "未找到患者 " + patient_id + " 的营养评估"

    a = matched[0]
    intake = a["dietary_intake_24h"]
    target = a["target_intake"]
    assess = a["assessment"]

    lines = []
    lines.append("=" * 55)
    lines.append("营养评估报告（" + a["assess_date"] + "）")
    lines.append("=" * 55)
    lines.append("")
    lines.append("【24h膳食摄入 vs 目标】")
    lines.append("{:<18}{:<16}{:<16}{}".format("指标", "实际摄入", "目标值", "状态"))
    lines.append("-" * 55)

    comparisons = [
        ("热量(kcal)", intake["total_calories_kcal"], target["total_calories_kcal"]),
        ("蛋白质(g)", intake["protein_g"], target["protein_g"]),
        ("钠(mg)", intake["sodium_mg"], target["sodium_mg"]),
        ("钾(mg)", intake["potassium_mg"], target["potassium_mg"]),
        ("磷(mg)", intake["phosphorus_mg"], target["phosphorus_mg"]),
        ("钙(mg)", intake["calcium_mg"], target["calcium_mg"]),
        ("液体(mL)", intake["fluid_ml"], target["fluid_ml"]),
    ]

    for cmp_name, actual, tgt in comparisons:
        if actual > tgt * 1.2:
            status = "[超标]"
        elif actual < tgt * 0.8:
            status = "[不足]"
        else:
            status = "[达标]"
        lines.append("{:<18}{:<16}{:<16}{}".format(cmp_name, str(actual), str(tgt), status))

    lines.append("")
    lines.append("【综合评估】")
    lines.append("  BMI：" + str(assess["BMI"]) + "（百分位：" + assess["BMI_percentile"] + "）")
    lines.append("  SGA评分：" + assess["SGA_score"])
    lines.append("  风险等级：" + assess["risk_level"])
    lines.append("  依从性：" + assess["dietary_compliance"])
    lines.append("")
    lines.append("【营养建议】")
    for i, rec in enumerate(assess["recommendations"], 1):
        lines.append("  " + str(i) + ". " + rec)

    return "\n".join(lines)


def query_food(food_name: str = "", ckd_stage: int = 0, category: str = "") -> str:
    """
    查询食物营养数据库。可按食物名称搜索、按CKD分期筛选适合的食物、或按分类查看。

    Args:
        food_name: 食物名称关键词（如 鸡蛋、香蕉），留空则不按名称筛选
        ckd_stage: CKD分期（1-5），筛选该分期适合食用的食物，0表示不筛选
        category: 食物分类（如 优质蛋白、水果、蔬菜、低蛋白主食），留空则不筛选
    """
    data = load_data()
    foods = data.get("food_database", [])

    if food_name:
        foods = [f for f in foods if food_name in f["name"]]
    if ckd_stage and ckd_stage > 0:
        foods = [f for f in foods if int(ckd_stage) in f["suitable_ckd_stage"]]
    if category:
        foods = [f for f in foods if category in f["category"]]

    if not foods:
        return "未找到符合条件的食物"

    lines = []
    lines.append("=" * 60)
    lines.append("食物营养数据库（共" + str(len(foods)) + "条）")
    lines.append("=" * 60)

    for f in foods:
        if f["suitable_ckd_stage"]:
            stages = ",".join([str(s) for s in f["suitable_ckd_stage"]])
        else:
            stages = "无（禁食）"
        lines.append("")
        lines.append("【" + f["name"] + "】（" + f["category"] + "）")
        lines.append("  热量:" + str(f["calories_kcal"]) + "kcal | 蛋白质:" + str(f["protein_g"]) + "g | 钾:" + str(f["potassium_mg"]) + "mg | 磷:" + str(f["phosphorus_mg"]) + "mg | 钠:" + str(f["sodium_mg"]) + "mg")
        lines.append("  适用CKD分期: " + stages)
        lines.append("  备注: " + f["notes"])

    return "\n".join(lines)


def query_meal_plan(patient_id: str = "", plan_date: str = "") -> str:
    """
    查询患儿的营养食谱/膳食计划。可按患者ID或日期查询。

    Args:
        patient_id: 患者ID（如 P20260001），留空则查询所有
        plan_date: 日期（如 2026-07-29），留空则不按日期筛选
    """
    data = load_data()
    plans = data.get("meal_plans", [])

    if patient_id:
        plans = [p for p in plans if p["patient_id"].upper() == patient_id.upper()]
    if plan_date:
        plans = [p for p in plans if plan_date in p["plan_date"]]

    if not plans:
        return "未找到匹配的膳食计划"

    lines = []
    for plan in plans:
        lines.append("=" * 55)
        lines.append("膳食计划（" + plan["plan_date"] + "）— 患者 " + plan["patient_id"] + "（CKD" + str(plan["ckd_stage"]) + "期）")
        lines.append("=" * 55)

        target = plan["target"]
        lines.append("【每日目标】热量:" + str(target["calories_kcal"]) + "kcal | 蛋白:" + str(target["protein_g"]) + "g | 钠:<" + str(target["sodium_mg"]) + "mg | 钾:<" + str(target["potassium_mg"]) + "mg | 磷:<" + str(target["phosphorus_mg"]) + "mg")
        lines.append("")

        meal_names = {"breakfast": "早餐", "lunch": "午餐", "dinner": "晚餐", "snack": "加餐"}
        for meal_key, meal_label in meal_names.items():
            meal = plan["meals"][meal_key]
            lines.append("  [" + meal_label + "]")
            for item in meal["items"]:
                lines.append("    - " + item)
            n = meal["nutrition"]
            lines.append("    营养: 热量" + str(n["calories_kcal"]) + "kcal 蛋白" + str(n["protein_g"]) + "g 钾" + str(n["potassium_mg"]) + "mg 磷" + str(n["phosphorus_mg"]) + "mg")
            lines.append("")

        total = plan["daily_total"]
        lines.append("  [全天合计] 热量:" + str(total["calories_kcal"]) + "kcal | 蛋白:" + str(total["protein_g"]) + "g | 钾:" + str(total["potassium_mg"]) + "mg | 磷:" + str(total["phosphorus_mg"]) + "mg")
        lines.append("  [评价] " + plan["compliance_note"])
        lines.append("")

    return "\n".join(lines)


def query_alerts(patient_id: str = "", level: str = "") -> str:
    """
    查询营养预警信息。可按患者ID或预警级别筛选。

    Args:
        patient_id: 患者ID，留空则查询所有预警
        level: 预警级别（紧急/警告/提示），留空则查询所有级别
    """
    data = load_data()
    alerts = data.get("alerts", [])

    if patient_id:
        alerts = [a for a in alerts if a["patient_id"].upper() == patient_id.upper()]
    if level:
        alerts = [a for a in alerts if level in a["level"]]

    if not alerts:
        return "当前无匹配的预警信息"

    lines = []
    lines.append("=" * 55)
    lines.append("营养预警（共" + str(len(alerts)) + "条）")
    lines.append("=" * 55)

    for a in alerts:
        lines.append("")
        lines.append("[" + a["level"] + "] " + a["type"])
        lines.append("  患者：" + a["patient_id"])
        lines.append("  时间：" + a["created_at"])
        lines.append("  内容：" + a["message"])

    return "\n".join(lines)


def get_ckd_guidelines(stage: int = 0) -> str:
    """
    查询CKD各分期的营养管理指南/原则。可查询特定分期或所有分期。

    Args:
        stage: CKD分期（1-5），0表示查询所有分期
    """
    data = load_data()
    guidelines = data.get("ckd_stage_guidelines", {})

    if stage and stage > 0:
        stage_str = str(int(stage))
        if stage_str not in guidelines:
            return "未找到CKD " + stage_str + "期的指南"
        guidelines = {stage_str: guidelines[stage_str]}

    lines = []
    lines.append("=" * 55)
    lines.append("CKD儿童营养管理指南")
    lines.append("=" * 55)

    for s in sorted(guidelines.keys()):
        g = guidelines[s]
        lines.append("")
        lines.append("【CKD " + s + "期】（eGFR: " + g["eGFR_range"] + "）")
        lines.append("  蛋白质目标：" + g["protein_target"])
        lines.append("  钠限制：" + g["sodium_limit"])
        lines.append("  管理重点：" + g["key_focus"])

    return "\n".join(lines)


def get_dashboard_summary() -> str:
    """
    获取系统总览仪表盘：在院患儿数、预警数、各CKD分期分布等全局统计信息。
    """
    data = load_data()
    patients = data.get("patients", [])
    alerts = data.get("alerts", [])

    stage_dist = {}
    for p in patients:
        s = p["ckd_stage"]
        stage_dist[s] = stage_dist.get(s, 0) + 1

    alert_levels = {}
    for a in alerts:
        alert_levels[a["level"]] = alert_levels.get(a["level"], 0) + 1

    lines = []
    lines.append("=" * 55)
    lines.append("童肾营养师 — 系统总览")
    lines.append("=" * 55)
    lines.append("数据时间：" + datetime.now().strftime("%Y-%m-%d %H:%M"))
    lines.append("")
    lines.append("【在院患儿】共 " + str(len(patients)) + " 人")
    for s in sorted(stage_dist.keys()):
        lines.append("  CKD " + str(s) + "期：" + str(stage_dist[s]) + " 人")

    lines.append("")
    lines.append("【营养预警】共 " + str(len(alerts)) + " 条")
    for lv, count in alert_levels.items():
        lines.append("  " + lv + "：" + str(count) + " 条")

    lines.append("")
    lines.append("【高风险患儿】")
    for p in patients:
        if p["ckd_stage"] >= 4:
            lines.append("  [!] " + p["name"] + "（" + p["patient_id"] + "）— CKD" + str(p["ckd_stage"]) + "期 — " + p["diagnosis"])

    return "\n".join(lines)


# ========== Gradio 界面 ==========
with gr.Blocks(title="童肾营养师 MCP 服务") as demo:

    gr.Markdown("# 童肾营养师 — 多智能体辅助决策系统")
    gr.Markdown("儿童肾脏病营养管理 MCP 服务，提供患儿查询、检验结果、营养评估、食物数据库、膳食计划、预警信息、CKD指南等工具。")

    with gr.Tab("系统总览"):
        dashboard_output = gr.Textbox(label="总览", lines=20)
        gr.Button("刷新总览").click(get_dashboard_summary, outputs=dashboard_output)

    with gr.Tab("患儿查询"):
        with gr.Row():
            pid_input = gr.Textbox(label="患者ID", placeholder="如 P20260001")
            name_input = gr.Textbox(label="姓名", placeholder="如 张小明")
        patient_output = gr.Textbox(label="查询结果", lines=15)
        gr.Button("查询").click(query_patient, inputs=[pid_input, name_input], outputs=patient_output)

    with gr.Tab("检验结果"):
        lab_pid = gr.Textbox(label="患者ID", placeholder="如 P20260001")
        lab_output = gr.Textbox(label="检验报告", lines=18)
        gr.Button("查询").click(query_lab_results, inputs=lab_pid, outputs=lab_output)

    with gr.Tab("营养评估"):
        na_pid = gr.Textbox(label="患者ID", placeholder="如 P20260001")
        na_output = gr.Textbox(label="营养评估", lines=25)
        gr.Button("查询").click(query_nutrition_assessment, inputs=na_pid, outputs=na_output)

    with gr.Tab("食物数据库"):
        with gr.Row():
            food_name_input = gr.Textbox(label="食物名称", placeholder="如 鸡蛋")
            food_stage_input = gr.Textbox(label="CKD分期(0=全部)", placeholder="如 4")
            food_cat_input = gr.Textbox(label="分类", placeholder="如 优质蛋白")
        food_output = gr.Textbox(label="查询结果", lines=20)

        def food_search_wrapper(fn, fs, fc):
            stage_val = 0
            if fs and fs.strip():
                try:
                    stage_val = int(fs.strip())
                except ValueError:
                    stage_val = 0
            return query_food(fn, stage_val, fc)

        gr.Button("查询").click(food_search_wrapper, inputs=[food_name_input, food_stage_input, food_cat_input], outputs=food_output)

    with gr.Tab("膳食计划"):
        mp_pid = gr.Textbox(label="患者ID", placeholder="如 P20260001")
        mp_output = gr.Textbox(label="膳食计划", lines=25)
        gr.Button("查询").click(query_meal_plan, inputs=mp_pid, outputs=mp_output)

    with gr.Tab("预警信息"):
        with gr.Row():
            alert_pid = gr.Textbox(label="患者ID", placeholder="留空查全部")
            alert_level = gr.Textbox(label="级别", placeholder="紧急/警告/提示")
        alert_output = gr.Textbox(label="预警列表", lines=15)
        gr.Button("查询").click(query_alerts, inputs=[alert_pid, alert_level], outputs=alert_output)

    with gr.Tab("CKD指南"):
        guide_stage = gr.Textbox(label="CKD分期(0=全部)", placeholder="如 3")
        guide_output = gr.Textbox(label="指南内容", lines=20)

        def guide_wrapper(gs):
            stage_val = 0
            if gs and gs.strip():
                try:
                    stage_val = int(gs.strip())
                except ValueError:
                    stage_val = 0
            return get_ckd_guidelines(stage_val)

        gr.Button("查询").click(guide_wrapper, inputs=guide_stage, outputs=guide_output)


# ========== 启动 ==========
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        mcp_server=True
    )
