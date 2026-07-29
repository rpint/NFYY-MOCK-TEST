# 🏥 童肾营养师 MCP Server

> 儿童肾脏病营养辅助决策数据查询服务

## 📌 简介

本 MCP Server 是 **"童肾营养师"多智能体辅助决策系统** 的数据查询模块，
基于华为 Nexent 平台开发，通过 ModelScope MCP 广场对外提供服务。

其他智能体可通过标准 MCP 协议调用本服务，查询患儿营养相关的模拟数据。

## 🔧 可用工具（Tools）

| 工具名称 | 功能说明 |
|---------|---------|
| `list_patients` | 获取所有患儿基本信息列表 |
| `get_patient_detail` | 查询指定患儿完整基本信息 |
| `get_nutrition_assessment` | 查询营养评估记录（SGA、BMI、白蛋白等） |
| `get_diet_plan` | 查询饮食方案（能量/蛋白质/电解质限制等） |
| `get_lab_results` | 查询实验室检查指标（肾功能/电解质/营养指标等） |
| `get_interventions` | 查询营养干预记录 |
| `get_nutrition_knowledge` | 查询儿童肾脏病营养知识库 |
| `get_system_info` | 获取系统信息和可用工具列表 |

## 🚀 快速开始

### 本地运行

```bash
pip install -r requirements.txt
python app.py
