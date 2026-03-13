# Routine Inspection Data Visualization Tool (例行巡检数据可视化工具)

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Pandas](https://img.shields.io/badge/pandas-2.x-blue.svg)
![Pyecharts](https://img.shields.io/badge/pyecharts-1.9.x-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

一个高效、自动化的数据处理与可视化工具，旨在将复杂的Excel巡检报告转化为直观、可交互的Web图表报告。

---

## 📖 项目简介

在日常的生产和质量控制中，工程师需要处理大量的例行巡key检数据（如 `Weekly` 和 `Daily` 报告）。这些数据通常记录在格式复杂的Excel表格中。本项目通过自动化的数据清洗、处理和可视化流程，极大地简化了这一过程，帮助团队快速识别关键性能指标（KPI）的趋势和潜在风险。

它解决了以下痛点：
- **手动处理效率低下**: 从复杂格式的Excel中提取有效数据耗时耗力。
- **数据趋势不直观**: 静态的表格难以揭示数据随时间变化的规律和异常。
- **风险预警不及时**: 无法快速定位超出规格（Spec）或存在较大波动风险的KPI。

## ✨ 核心功能

- **智能数据清洗**:
  - 自动处理多层、合并的复杂Excel表头。
  - 保留原始数据的大小写，确保数据准确性。
  - 标准化日期格式，清洗无效数据和空值。

- **动态KPI映射**:
  - 通过外部 `tester_kpi_mapping.csv` 文件维护KPI与测试机台（Tester）、规格上限（USL）、规格下限（LSL）的对应关系，无需修改代码即可更新。

- **交互式可视化报告**:
  - 基于 **Pyecharts** 和 **Jinja2** 动态生成单个HTML报告文件，易于分发和查看。
  - 提供层级清晰的侧边栏导航，用户可先选择 `Tester`，再选择其下的 `KPI` 查看对应图表。
  - 图表支持缩放、平移和详细数据查看。

- **智能分级警报系统**:
  - **图表级警报**: 当数据点超出USL/LSL时，图表中的折线会自动变色（红色），实现即时视觉警报。
  - **KPI级警报**: KPI按钮会根据其数据波动范围相对于规格范围的比例进行颜色编码（红色/黄色），量化潜在风险。
  - **Tester级警报**: Tester按钮的颜色会根据其下所有KPI的最高警报等级进行联动，实现“提纲挈领”的宏观预警。

## 🖼️ 效果演示

*(建议您在此处替换为项目的实际截图)*

**1. 主程序界面 (如果适用)**
![App Screenshot](https://via.placeholder.com/600x400.png?text=Main+Application+UI)

**2. 生成的HTML报告 (关键)**
*报告展示了层级侧边栏、颜色警报和交互式图表。*
![Report Screenshot](https://via.placeholder.com/800x500.png?text=Interactive+HTML+Report+Screenshot)


## 🛠️ 技术栈

- **后端**: Python
- **数据处理**: Pandas, NumPy
- **图表生成**: Pyecharts
- **模板引擎**: Jinja2
- **Excel读写**: openpyxl

## ⚙️ 工作流程

1.  **加载数据**: 用户通过UI界面选择包含 `Weekly` 或 `Daily` sheet的原始Excel文件。
2.  **数据清洗**: 程序在后台对数据进行全自动清洗和格式化。
3.  **生成报告**: 用户点击“开始处理”按钮，并选择日期范围。
4.  **数据可视化**:
    - 程序根据 `tester_kpi_mapping.csv` 的配置，为每个KPI生成带有USL/LSL标记线的折线图。
    - 计算每个KPI和Tester的警报等级。
    - 使用Jinja2模板将所有图表和导航元素渲染成一个独立的HTML文件。
5.  **查看报告**: 程序自动打开生成的HTML文件，用户可以开始交互式分析。

## 🚀 安装与使用

### 1. 环境准备
- 确保您已安装 Python (推荐 3.8 或更高版本)。

### 2. 克隆项目
```bash
git clone [您的项目git地址]
cd [项目文件夹]
```

### 3. 安装依赖
项目依赖的库已在 `requirements.txt` 中列出。建议创建一个虚拟环境。
```bash
# 创建虚拟环境 (可选但推荐)
python -m venv venv
# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```
*如果您还没有 `requirements.txt` 文件，可以通过以下命令生成:*
```bash
pip freeze > requirements.txt
```
*或者直接安装必要的库:*
```bash
pip install pandas numpy pyecharts Jinja2 openpyxl PyQt5
```

### 4. 配置KPI映射
打开 `app/config/tester_kpi_mapping.csv` 文件。根据您的实际情况，添加或修改 `Project`, `Tester`, `KPI`, `USL`, `LSL` 的映射关系。

### 5. 运行程序
执行主程序文件：
```bash
python app/main.py
```

## 📂 文件结构
Data-Processing-Tool/ ├── app/ │ ├── config/ │ │ ├── kpi_mapping.py # 加载KPI映射关系的模块 │ │ └── tester_kpi_mapping.csv # KPI映射关系的配置文件 (核心) │ ├── functions/ │ │ └── visRoutineInspection.py # 核心数据处理与可视化逻辑 │ ├── templates/ │ │ └── visualization_template.html # Pyecharts报告的Jinja2模板 │ ├── view/ │ │ └── dataprocessinggroup.py # PyQt界面逻辑 (部分) │ └── main.py # 主程序入口 ├── backup/ # 代码备份文件夹 └── README.md

# 项目说明文件
## 🤝 贡献
欢迎各种形式的贡献，包括但不限于：
- 提交问题 (Issues)
- 提出新功能建议
- 改进代码和文档 (Pull Requests)

## 📄 许可证
本项目采用 [MIT License](https://opensource.org/licenses/MIT) 授权。

