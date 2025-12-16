# 💱 Exchange Rate Dashboard (汇率波动看板)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68%2B-009688.svg?style=flat-square&logo=fastapi)
![HTMX](https://img.shields.io/badge/HTMX-1.9%2B-3D5AFE.svg?style=flat-square)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3.svg?style=flat-square&logo=bootstrap)
![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)

**Exchange Rate Dashboard** 是一个专为跨境电商卖家、外汇交易者及国际旅行者设计的全功能汇率监控与分析平台。

它不仅仅是一个简单的汇率转换器，更是一个集成了**实时数据监控**、**历史趋势分析**、**波动率预警**以及**智能定价计算**的综合性工具。项目采用现代化的 **FastAPI + HTMX** 架构，在保持后端高性能的同时，实现了媲美单页应用（SPA）的流畅前端体验，且无需复杂的构建流程。

---

## 🌟 核心功能详解 (Core Features)

### 1. 🌍 全球汇率实时监控系统
- **多源数据聚合**: 集成 ExchangeRate-API，支持全球 160+ 种货币的实时汇率查询。
- **智能缓存策略**: 内置内存与文件双重缓存机制（默认 5 分钟更新一次），在保证数据时效性的同时，大幅节省 API 调用额度，避免触发频率限制。
- **自动刷新**: 界面采用轮询机制，无需手动刷新页面即可获取最新市场行情。

### 2. 📊 专业级数据可视化
- **交互式历史趋势图**: 
    - 基于 Chart.js 构建，支持查看任意两种货币在过去 30 天内的相对走势。
    - 提供平滑曲线展示，帮助用户直观识别汇率的长期升值或贬值趋势。
- **波动率雷达 (Volatility Radar)**:
    - 独创的雷达图分析，同时展示 USD, EUR, JPY, GBP, AUD 等主要货币的 7 日波动幅度。
    - 帮助用户快速识别当前市场中风险最高和最稳定的货币。
- **CNY 交叉汇率矩阵**:
    - 专为中国用户优化，直观展示人民币对主要货币的实时交叉汇率，一目了然。

### 3. 🧮 跨境贸易专用工具箱
- **采购成本对比器 (Purchase Cost Compare)**:
    - **场景**: 当你有多个供应商分别报价 USD, EUR, JPY 时，如何快速决策？
    - **功能**: 输入不同币种的报价，系统自动统一换算为 CNY 成本，并高亮标记**最低成本方案**，辅助采购决策。
- **智能定价计算器 (Smart Pricing)**:
    - **场景**: 已知国内采购成本 (CNY) 和目标利润率，需要计算海外市场的建议售价。
    - **功能**: 自动结合当前实时汇率和设定的利润率（Margin），一键生成目标市场的建议零售价。

### 4. 🛡️ 风险管理与预警
- **汇率预警设置**: 支持设置自定义阈值（例如：当 USD/CNY > 7.30 时）。
- **操作审计日志**: 系统自动记录所有的换算、定价计算和预警设置操作，支持本地持久化存储，方便随时回溯历史决策。

### 5. 📰 市场情报中心
- **实时新闻聚合**: 集成 Alpha Vantage 新闻 API，实时推送外汇市场的突发新闻和财经快讯。
- **情感分析**: (实验性功能) 辅助判断市场情绪是看多还是看空。

---

## 🏗️ 系统架构 (System Architecture)

本项目采用轻量级、高效率的 **MVT (Model-View-Template)** 架构模式：

- **后端 (Backend)**: 
    - **Python FastAPI**: 提供高性能的异步 API 服务。
    - **Pydantic**: 确保数据交互的类型安全。
    - **HTTPX**: 异步 HTTP 客户端，用于非阻塞地请求外部汇率接口。
- **前端 (Frontend)**:
    - **Jinja2**: 服务端模板渲染，SEO 友好。
    - **HTMX**: 核心交互库。通过 HTML 属性实现 AJAX 请求、CSS 过渡和 WebSocket 通信，极大地简化了前端代码。
    - **Bootstrap 5**: 响应式 UI 框架，适配移动端和桌面端。
- **数据存储 (Data Persistence)**:
    - **JSON Flat File**: 采用本地 JSON 文件存储历史记录和缓存数据。无需安装 MySQL/PostgreSQL 等重型数据库，开箱即用，部署极其简单。

---

## 🚀 安装与部署指南 (Installation)

### 1. 环境准备
确保您的系统已安装 Python 3.8 或更高版本。

```bash
python --version
# Python 3.9.x
```

### 2. 克隆项目与安装依赖

```bash
# 克隆仓库
git clone https://github.com/EcreekLin/Exchange_rate_dashboard.git
cd Exchange_rate_dashboard

# (可选) 创建虚拟环境
python -m venv venv
# Windows 激活
.\venv\Scripts\activate
# macOS/Linux 激活
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置文件设置
项目运行需要 API 密钥。请在项目根目录下创建 `.env` 文件：

1. 复制示例文件：
   ```bash
   cp .env.example .env
   # 或者在 Windows 上手动重命名
   ```

2. 编辑 `.env` 文件填入密钥：
   ```ini
   # 获取免费 Key: https://www.exchangerate-api.com/
   EXCHANGE_API_KEY=your_key_here
   
   # 获取免费 Key: https://www.alphavantage.co/support/#api-key
   ALPHAVANTAGE_API_KEY=your_key_here
   ```

### 4. 启动服务

#### 方式一：一键启动脚本 (推荐)
双击项目根目录下的 `start.bat` 脚本，即可自动启动服务并打开浏览器。

#### 方式二：命令行启动
```bash
uvicorn app.main:app --reload
```

终端显示 `Application startup complete.` 后，打开浏览器访问：
👉 **http://127.0.0.1:8000**

---

## 🎨 个性化与扩展 (Customization)

### 切换主题 (Themes)
点击导航栏右上角的 🎨 图标，即可在以下主题间无缝切换：
- **Default (默认蓝)**: 商务、专业。
- **Emerald (翡翠绿)**: 清新、护眼。
- **Ruby (宝石红)**: 活力、醒目。
- **Amber (琥珀黄)**: 温暖、复古。
- **Amethyst (紫水晶)**: 神秘、优雅。
- **Slate (板岩灰)**: 极简、现代。

### 添加新货币
如果需要支持更多货币，请修改 `app/main.py` 中的 `CURRENCIES` 列表：

```python
# app/main.py
CURRENCIES = ["USD", "CNY", "EUR", "GBP", "JPY", "HKD", "AUD", "CAD", "SGD", "CHF", "BTC", "ETH"] # 添加 BTC, ETH
```

---

## 📂 项目目录结构 (Project Structure)

```text
Exchange_rate_dashboard/
├── app/
│   ├── __init__.py
│   ├── main.py              # 核心应用入口：路由定义、依赖注入
│   ├── locales.py           # i18n 国际化字典 (中/英)
│   └── services/
│       └── exchange_api.py  # 业务逻辑层：API 调用、缓存管理、计算逻辑
├── data/                    # 数据持久化目录
│   ├── daily_rates.json     # 每日汇率缓存
│   └── history_records.json # 用户操作历史
├── static/
│   ├── css/
│   │   └── style.css        # 全局样式与主题定义
│   └── js/
│       └── chart-setup.js   # Chart.js 图表配置与渲染逻辑
├── templates/               # Jinja2 模板
│   ├── index.html           # 主布局文件
│   └── partials/            # HTMX 局部视图 (用于动态刷新)
│       ├── history_list.html
│       ├── news_list.html
│       ├── purchase_result.html
│       ├── rates_table.html
│       └── sale_result.html
├── .env                     # 环境变量 (API Keys)
├── .gitignore               # Git 忽略规则
├── requirements.txt         # Python 依赖包
└── README.md                # 项目文档
```

---

## ❓ 常见问题 (FAQ)

**Q: 为什么汇率不是实时的？**
A: 为了节省 API 调用次数（免费版通常有限制），系统默认缓存汇率 5 分钟。您可以在 `app/services/exchange_api.py` 中修改缓存时间。

**Q: 如何部署到服务器？**
A: 本项目非常轻量，可以使用 Docker 部署，或者直接在 Linux 服务器上使用 Gunicorn + Uvicorn 运行。
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

**Q: 图表不显示怎么办？**
A: 请检查网络连接，图表依赖 `Chart.js` 的 CDN。如果处于内网环境，请下载 `chart.js` 文件到 `static/js/` 目录并修改 `index.html` 引用。

---

## 🤝 贡献 (Contributing)

我们非常欢迎社区贡献！如果您有好的想法：

1. Fork 本仓库。
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)。
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)。
4. 推送到分支 (`git push origin feature/AmazingFeature`)。
5. 开启一个 Pull Request。

## 📄 许可证 (License)

本项目基于 [MIT License](LICENSE) 开源。您可以免费用于个人学习或商业项目。
