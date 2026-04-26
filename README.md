# DDYL BI Platform

**人人可用的数据可视化神器** — 零代码/低代码商业智能数据分析工具

## 快速开始

### 一键启动
```bash
chmod +x start.sh
./start.sh
```

### 分步启动

**后端 (Python FastAPI):**
```bash
cd backend
chmod +x start.sh
./start.sh
```

**前端 (Vue 3 + Vite):**
```bash
cd frontend
chmod +x start.sh
./start.sh
```

启动后访问：
- 前端: http://localhost:5173
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

### 默认账号
- 用户名: `admin`
- 密码: `admin123`

---

## 技术栈

### 后端
- **Python FastAPI** — 高性能异步Web框架
- **SQLAlchemy 2.0** — 异步ORM
- **SQLite** — 开发数据库（生产可切换MySQL/PostgreSQL）
- **JWT** — 用户认证

### 前端
- **Vue 3** + **TypeScript** — 组合式API
- **Vite** — 快速开发构建
- **Pinia** — 状态管理
- **ECharts** — 30+图表引擎
- **Element Plus** — UI组件库
- **html2canvas** — 导出图片/PDF

## 核心功能

### 多源数据源 (20+种)
MySQL, ClickHouse, StarRocks, PostgreSQL, Excel, CSV, API, Kafka, Redis

### 数据准备
- 数据集创建（数据库表、SQL、文件上传、跨源关联）
- 数据加工（过滤、排序、分组、关联）
- 字段管理

### 可视化图表 (30+种)
- **基础图表**: 柱状图、折线图、饼图、环形图、条形图、雷达图、散点图、面积图、仪表盘、进度条
- **高级图表**: 漏斗图、桑基图、热力图、树图、旭日图、水波图、词云、中国地图、世界地图

### 仪表板设计
- 拖拽式编辑，自由布局
- 图表面板（数据绑定、维度/指标配置）
- 样式自定义（背景、边框、颜色）
- 图表联动、下钻、全局过滤器
- 分享/嵌入（公共链接、Iframe、密码保护）
- 导出图片/PDF

### 模板市场
行业模板（制造、零售、金融、医药、物流、政务、教育），一键复用

## 项目结构
```
ddyl/
├── start.sh                    # 一站式启动脚本
├── backend/                    # Python 后端
│   ├── main.py                 # 应用入口
│   ├── run.py                  # 开发服务器
│   ├── requirements.txt
│   ├── app/
│   │   ├── api/                # API 路由
│   │   ├── models/             # 数据库模型
│   │   ├── schemas/            # Pydantic 模式
│   │   └── core/               # 核心配置
│   └── media/                  # 上传文件
├── frontend/                   # Vue 3 前端
│   ├── index.html
│   ├── src/
│   │   ├── api/                # API 客户端
│   │   ├── stores/             # Pinia 状态
│   │   ├── router/             # 路由
│   │   ├── components/         # 组件
│   │   │   └── charts/         # 图表引擎
│   │   ├── layout/             # 主布局
│   │   ├── types/              # TypeScript类型
│   │   └── views/              # 页面视图
│   └── public/
```
