---
# 必须包含的元数据区域
title: "童肾营养师-儿童肾病营养辅助决策MCP"
description: "提供儿童肾病患儿营养评估、饮食方案查询及实验室指标分析的MCP服务"
tags:
  - mcp
  - healthcare
  - nutrition
  - pediatric
license: MIT
python_version: "3.10"
---

# 童肾营养师 MCP Server

这是一个专为“童肾营养师”多智能体系统设计的模型上下文协议服务。它允许智能体查询模拟的儿童肾病临床营养数据。

## 🚀 功能特性

- **患儿信息查询**: 获取患儿的年龄、体重、肾病类型等基础信息。
- **营养状况评估**: 基于生化指标（如白蛋白、血红蛋白）自动评估营养风险。
- **个性化饮食方案**: 根据肾病分期（CKD 1-5期）推荐蛋白质和热量摄入标准。
- **实验室指标解读**: 查询血肌酐、尿素氮等关键指标的参考范围及临床意义。

## 🛠️ 部署与使用

### 本地运行
确保已安装 Python 3.10+ 和 uvx/npm。

```bash
# 使用 uvx 运行 (推荐)
uvx pediatric-renal-nutrition-mcp

# 或使用 pip 安装后运行
pip install -r requirements.txt
python app.py
