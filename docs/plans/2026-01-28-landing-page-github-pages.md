# Plan: Landing Page + GitHub Pages Deployment

## Goal
构建项目首页并配置 GitHub CI 部署到 GitHub Pages

## Theme
"算法工程师智能体 帮你一键训练所有模型"

## Tasks

### 1. 创建独立首页 (docs/landing/)
- [x] 创建 landing page 目录结构
- [x] 编写 index.html (现代化产品展示页面)
- [x] 内容涵盖：
  - 主题标语：算法工程师智能体 帮你一键训练所有模型
  - FastDistill 核心功能展示
  - 快速开始指引
  - 文档链接
  - GitHub 链接

### 2. 更新 GitHub Actions CI
- [x] 创建新的工作流 `.github/workflows/pages.yml`
- [x] 配置为从 main 分支部署到 GitHub Pages
- [x] 构建步骤：复制静态文件到 _site 目录
- [x] 绕过 Jekyll 处理

### 3. 更新记录
- [x] 2026-01-28: 优化为浅色主题UI
- [x] 2026-01-28: 添加核心技能库展示板块（12个技能卡片）
- [x] 2026-01-28: 优化导航和视觉层次
- [x] 2026-01-28: 重写为 Claude 官网风格 - 温暖奶油色、衬线字体、大量留白

### 4. 待完善项
- [ ] 若需集成 MkDocs 文档，需要配置双站点部署策略
- [ ] GitHub Pages 设置需要在仓库 Settings > Pages 中配置 Source 为 GitHub Actions

## Decision
采用方案：创建独立 landing page 目录，通过 GitHub Actions 直接部署到 Pages
- 保持现有 docs 目录用于 MkDocs 文档
- landing 目录用于产品展示首页
- CI 将 landing 目录内容部署到 Pages root

## Progress
- Created: 2026-01-28
