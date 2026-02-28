# Archinstall 中国优化版

<img src="https://github.com/archlinux/archinstall/raw/master/docs/logo.png" alt="Arch Linux" width="200"/>

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-GPLv3-green.svg)](LICENSE)

> 专为中文用户优化的 Arch Linux 安装器，解决中国网络环境下的安装痛点

## 核心特性

- **智能镜像源**：自动检测并使用清华、中科大、阿里云、腾讯云等国内镜像源
- **中文字体支持**：自动配置中文字体，支持极端无字体环境
- **网络优化**：针对中国网络环境优化连接检测和超时设置
- **开箱即用**：无需手动配置，启动即自动应用优化
- **向后兼容**：不影响国际用户使用，自动检测环境

## 快速开始

### 在 Arch ISO 中使用

```bash
# 1. 连接到互联网
# 2. 克隆此仓库
git clone https://github.com/blycr/archinstall-china-optimized.git

# 3. 运行优化版安装器
cd archinstall-china-optimized
python -m archinstall
```

**注意**：直接运行系统自带的 `archinstall` 命令会使用官方原版，不会包含中国优化。必须使用 `python -m archinstall` 从本仓库运行。

### 替换系统版本（可选）

如果你想直接使用 `archinstall` 命令运行优化版：

```bash
# 1. 备份原版
sudo cp -r /usr/lib/python3.11/site-packages/archinstall \
          /usr/lib/python3.11/site-packages/archinstall.backup.$(date +%Y%m%d)

# 2. 复制优化版
sudo cp -r archinstall /usr/lib/python3.11/site-packages/

# 3. 现在可以直接使用 archinstall 命令
archinstall
```

**注意**：Python 版本号可能不同，请根据实际情况调整路径（如 python3.10、python3.12 等）

## 使用场景

### 场景一：中国用户快速安装
```bash
git clone https://github.com/blycr/archinstall-china-optimized.git
cd archinstall-china-optimized
python -m archinstall
```
- 自动检测中国网络环境
- 自动使用国内镜像源（清华/中科大/阿里云）
- 自动配置中文字体
- 安装速度提升 5-10 倍

### 场景二：网络受限环境
- 自动检测网络受限情况
- 无法访问 archlinux.org 时自动使用中国镜像
- 支持离线模式安装

### 场景三：无中文字体环境
- 自动下载轻量级中文字体
- 极端环境下创建内嵌位图字体
- 确保中文提示始终可显示

## 文档

- [完整使用指南](docs/USAGE_GUIDE.md) - 详细的安装和配置说明
- [快速参考](docs/QUICK_REFERENCE.md) - 常用命令速查
- [技术文档](docs/CHINA_OPTIMIZATION.md) - 技术实现细节

## 安装方法

### 方法一：直接使用（推荐）

```bash
git clone https://github.com/blycr/archinstall-china-optimized.git
cd archinstall-china-optimized
python -m archinstall
```

### 方法二：替换系统版本

```bash
# 查找 archinstall 安装位置
python -c "import archinstall; print(archinstall.__path__[0])"

# 备份并替换
sudo cp -r /usr/lib/python3.11/site-packages/archinstall \
          /usr/lib/python3.11/site-packages/archinstall.backup
sudo cp -r ./archinstall /usr/lib/python3.11/site-packages/
```

### 方法三：使用配置文件

创建 `config.json`：
```json
{
  "mirror_config": {
    "mirror_regions": ["China"]
  },
  "locale_config": {
    "sys_lang": "zh_CN.UTF-8",
    "kb_layout": "us"
  }
}
```

运行：
```bash
python -m archinstall --config config.json
```

## 常见问题

### Q: 为什么直接运行 `archinstall` 没有优化效果？

A: 因为系统自带的 `archinstall` 是官方原版。要使用优化版，必须：
1. 使用 `python -m archinstall` 从本仓库目录运行，或
2. 将本仓库的 `archinstall` 文件夹替换系统版本

### Q: 如何确认优化已生效？

A: 运行时会显示：
```
[INFO] 正在初始化中国环境优化...
[INFO] 中国镜像源速度测试完成，最快的是: Tsinghua University (TUNA)
```

### Q: 国际用户可以使用吗？

A: 可以。优化版会自动检测网络环境，如果国际网络访问正常，会使用默认行为，不会强制使用中国镜像。

### Q: 如何完全禁用中国优化？

A: 编辑 `archinstall/lib/mirrors.py`，将 `CHINA_MIRROR_SUPPORT` 设为 `False`。

## 技术亮点

- **14 个中国镜像源**：清华、中科大、阿里云、腾讯云、华为云、网易、上海交大等
- **三层字体回退**：系统字体 → 自动下载 → 内嵌紧急字体
- **智能网络检测**：国内/国际网络分层检测，自动选择最佳策略
- **ISO 环境自适应**：根据内存、CPU 自动调整并发策略
- **防御性编程**：所有模块可选加载，失败时自动降级

## 项目结构

```
archinstall/
├── lib/
│   ├── mirrors_china.py          # 中国镜像源配置
│   ├── networking_china.py       # 网络环境检测
│   ├── font_config.py            # 字体配置
│   ├── font_downloader.py        # 字体自动下载
│   ├── emergency_font.py         # 紧急位图字体
│   ├── encoding_utils.py         # 编码安全工具
│   ├── china_utils.py            # 中国用户实用工具
│   ├── china_optimization.py     # 统一优化接口
│   ├── mirrors.py                # [修改] 集成中国镜像
│   └── main.py                   # [修改] 集成网络检测
└── docs/                         # 文档
```

## 贡献

欢迎提交 Issue 和 PR！

## 许可证

基于 Arch Linux 官方 archinstall 的许可证。

## 致谢

- Arch Linux 官方团队
- 清华大学 TUNA 镜像站
- 中国科学技术大学 LUG
- 阿里云、腾讯云等镜像提供方

---

**注意**：本项目是社区优化版本，非 Arch Linux 官方项目。
