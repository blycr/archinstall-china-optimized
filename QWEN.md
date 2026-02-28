# QWEN.md - Archinstall 中国优化版

## 项目概述

这是一个专为中文用户优化的 Arch Linux 安装器（archinstall）分支，解决中国网络环境下的安装痛点。项目在官方 archinstall 基础上添加了中国镜像源支持、中文字体自动配置、网络环境优化等功能。

**核心目标：**
- 提升中国用户的安装速度（5-10倍）
- 解决网络受限环境下的安装问题
- 确保中文正确显示（包括极端无字体环境）
- 保持与官方版本完全兼容

**项目地址：** https://github.com/blycr/archinstall-china-optimized

## 项目类型

**Python 应用程序** - Arch Linux 安装器，基于官方 archinstall 的优化分支

## 技术栈

- **语言：** Python 3.12+
- **构建工具：** setuptools
- **依赖管理：** pip
- **代码检查：** ruff, mypy, pylint, flake8
- **测试：** pytest

## 目录结构

```
archinstall/
├── lib/                          # 核心库代码
│   ├── mirrors_china.py          # 中国镜像源配置（14个镜像源）
│   ├── networking_china.py       # 网络环境检测和优化
│   ├── iso_env.py                # ISO 环境自适应
│   ├── font_config.py            # 字体配置（三层回退）
│   ├── font_downloader.py        # 字体自动下载
│   ├── emergency_font.py         # 紧急位图字体（60+汉字）
│   ├── encoding_utils.py         # 编码安全工具
│   ├── china_utils.py            # 中国用户实用工具
│   ├── china_optimization.py     # 统一优化接口
│   ├── mirrors.py                # [修改] 集成中国镜像
│   └── main.py                   # [修改] 集成网络检测
├── default_profiles/             # 默认安装配置文件
├── examples/                     # 使用示例
├── locales/                      # 国际化文件
├── scripts/                      # 安装脚本（guided, minimal等）
├── tests/                        # 测试代码
└── docs/                         # 文档
    ├── USAGE_GUIDE.md            # 完整使用指南
    ├── QUICK_REFERENCE.md        # 快速参考
    └── CHINA_OPTIMIZATION.md     # 技术实现文档
```

## 核心功能模块

### 1. 智能镜像源管理 (`mirrors_china.py`)
- 14 个中国镜像源配置（清华、中科大、阿里云、腾讯云等）
- 自动速度测试选择最快镜像
- ISO 环境下保守并发策略
- 延迟导入避免循环依赖

### 2. 网络环境检测 (`networking_china.py`)
- 国内/国际网络分层检测
- 多 DNS 检测点（阿里、腾讯、114）
- 智能判断是否需要中国镜像
- 完整超时和错误处理

### 3. 字体三层回退系统
- **font_config.py:** 检测现有 CJK 字体，配置控制台字体
- **font_downloader.py:** 自动下载轻量级字体（文泉驿 4.5MB），多镜像源加速
- **emergency_font.py:** 内嵌 60+ 常用汉字位图，极端环境最后保障

### 4. ISO 环境自适应 (`iso_env.py`)
- 自动检测 Live ISO 环境
- 资源感知（内存、CPU）
- 自适应并发数和超时
- 低内存模式自动切换

## 使用方法

### 方式一：直接使用（推荐）

```bash
git clone https://github.com/blycr/archinstall-china-optimized.git
cd archinstall-china-optimized
python -m archinstall
```

**注意：** 直接运行系统自带的 `archinstall` 命令会使用官方原版，不会包含中国优化。

### 方式二：替换系统版本

```bash
# 查找 archinstall 安装位置
python -c "import archinstall; print(archinstall.__path__[0])"

# 备份并替换
sudo cp -r /usr/lib/python3.11/site-packages/archinstall \
          /usr/lib/python3.11/site-packages/archinstall.backup
sudo cp -r ./archinstall /usr/lib/python3.11/site-packages/
```

### 方式三：使用配置文件

```bash
python -m archinstall --config config.json
```

## 开发命令

### 安装依赖
```bash
pip install -e .
# 或安装开发依赖
pip install -e ".[dev]"
```

### 代码检查
```bash
# ruff 检查
ruff check .

# ruff 格式化
ruff format .

# mypy 类型检查
mypy

# pylint 检查
pylint archinstall
```

### 测试
```bash
pytest
```

### 构建
```bash
python -m build
```

## 代码规范

- **缩进：** 使用 Tab（而非空格）
- **行长度：** 最大 160 字符
- **引号：** 单引号
- **类型注解：** 严格类型检查（mypy --strict）
- **导入：** 绝对导入，禁止使用相对导入

## 关键文件说明

| 文件 | 说明 |
|------|------|
| `archinstall/lib/mirrors_china.py` | 中国镜像源配置，包含14个镜像源 |
| `archinstall/lib/networking_china.py` | 网络环境检测，智能选择镜像策略 |
| `archinstall/lib/font_config.py` | 字体配置，三层回退机制 |
| `archinstall/lib/china_optimization.py` | 统一优化接口，一键启用所有功能 |
| `archinstall/lib/mirrors.py` | [修改] 集成中国镜像 fallback |
| `archinstall/main.py` | [修改] 集成网络环境检测 |
| `pyproject.toml` | 项目配置和依赖 |
| `README.md` | 项目说明（中文） |

## 镜像源列表

| 镜像源 | 地址 | 推荐 |
|--------|------|------|
| 清华大学 TUNA | mirrors.tuna.tsinghua.edu.cn | ⭐ |
| 中科大 USTC | mirrors.ustc.edu.cn | ⭐ |
| 阿里云 | mirrors.aliyun.com | ⭐ |
| 腾讯云 | mirrors.cloud.tencent.com | ⭐ |
| 上海交大 | mirror.sjtu.edu.cn | ⭐ |
| 华为云 | mirrors.huaweicloud.com | |
| 网易 | mirrors.163.com | |

## 故障排除

### 问题：优化未生效
**原因：** 可能运行的是系统原版 `archinstall`
**解决：** 使用 `python -m archinstall` 从仓库目录运行

### 问题：字体显示方块
**解决：**
```bash
pacman -Sy noto-fonts-cjk wqy-zenhei
```

### 问题：网络检测失败
**解决：**
```bash
python -m archinstall --offline
```

## 文档索引

- [README.md](README.md) - 项目主说明
- [docs/USAGE_GUIDE.md](docs/USAGE_GUIDE.md) - 完整使用指南
- [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) - 快速参考
- [docs/CHINA_OPTIMIZATION.md](docs/CHINA_OPTIMIZATION.md) - 技术实现细节
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - 项目总结

## 许可证

基于 Arch Linux 官方 archinstall 的 GPL-3.0 许可证。

## 注意事项

1. 本项目是社区优化版本，非 Arch Linux 官方项目
2. 使用 `python -m archinstall` 运行才能启用中国优化
3. 所有修改都是添加性的，向后兼容官方版本
4. 模块使用 try/except 安全导入，失败时自动降级
