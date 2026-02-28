# Archinstall 中国优化版 - 完整使用指南

## 目录
1. [快速开始](#快速开始)
2. [安装前准备](#安装前准备)
3. [使用方式](#使用方式)
4. [配置选项](#配置选项)
5. [高级用法](#高级用法)
6. [故障排除](#故障排除)
7. [常见问题](#常见问题)

---

## 快速开始

### 方式一：自动模式（推荐）
```bash
# 启动 archinstall 后自动检测并应用中国优化
archinstall
```
优化模块会自动：
- 检测网络环境
- 选择合适的镜像源
- 配置中文字体
- 设置最佳参数

### 方式二：手动启用特定功能
```python
# 在 Python 脚本中使用
from archinstall.lib.china_optimization import quick_setup

# 一键启用所有中国优化
manager = quick_setup()
```

---

## 安装前准备

### 1. 下载优化版 archinstall

**方法一：克隆仓库**
```bash
git clone https://github.com/your-repo/archinstall-china-optimized.git
cd archinstall-china-optimized
python -m archinstall
```

**方法二：替换现有 archinstall**
```bash
# 备份原有版本
sudo cp -r /usr/lib/python3.x/site-packages/archinstall /usr/lib/python3.x/site-packages/archinstall.backup

# 复制优化版本
sudo cp -r ./archinstall /usr/lib/python3.x/site-packages/
```

**方法三：使用 pip 安装**
```bash
pip install archinstall-china-optimized
```

### 2. 验证安装
```bash
python -c "from archinstall.lib.china_optimization import get_china_manager; print('✓ 中国优化模块加载成功')"
```

### 3. 准备网络环境

**推荐网络配置：**
- 有线网络：直接连接即可
- 无线网络：archinstall 会自动提示配置
- 代理环境：模块会自动检测并适配

---

## 使用方式

### 标准安装流程

```bash
# 1. 启动 Arch Linux ISO
# 2. 连接到互联网
# 3. 运行安装器
archinstall

# 4. 按照向导完成安装
#    - 中国优化会自动应用
#    - 无需手动干预
```

### 命令行参数

```bash
# 跳过网络检测（离线模式）
archinstall --offline

# 跳过 WiFi 检测
archinstall --skip-wifi-check

# 跳过版本检查
archinstall --skip-version-check

# 调试模式（查看详细日志）
archinstall --debug

# 使用配置文件
archinstall --config /path/to/config.json

# 使用预置脚本
archinstall --script guided
```

### 配置文件示例

创建 `china-config.json`：
```json
{
  "archinstall-language": "English",
  "locale_config": {
    "sys_lang": "zh_CN.UTF-8",
    "sys_enc": "UTF-8",
    "kb_layout": "us"
  },
  "mirror_config": {
    "mirror_regions": ["China"],
    "custom_servers": [
      "https://mirrors.tuna.tsinghua.edu.cn/archlinux/",
      "https://mirrors.ustc.edu.cn/archlinux/"
    ]
  },
  "network_config": {
    "type": "manual",
    "nic": "eth0",
    "ip": "dhcp"
  },
  "disk_config": {
    "main_device": "/dev/sda",
    "partition_scheme": "gpt",
    "partitions": [
      {
        "mountpoint": "/boot",
        "size": "512M",
        "filesystem": "fat32",
        "boot": true
      },
      {
        "mountpoint": "/",
        "size": "50G",
        "filesystem": "ext4"
      },
      {
        "mountpoint": "/home",
        "size": "100%",
        "filesystem": "ext4"
      }
    ]
  },
  "bootloader": "systemd-bootctl",
  "hostname": "archlinux-cn",
  "root_password": "your-password",
  "users": [
    {
      "username": "user",
      "password": "user-password",
      "sudo": true
    }
  ],
  "profile": "desktop",
  "desktop": "gnome",
  "packages": [
    "noto-fonts-cjk",
    "noto-fonts-emoji",
    "fcitx5-im",
    "fcitx5-chinese-addons"
  ]
}
```

使用配置：
```bash
archinstall --config china-config.json
```

---

## 配置选项

### 1. 镜像源配置

**自动选择（推荐）**
```python
# 自动检测最快的镜像源
from archinstall.lib.mirrors_china import get_china_mirror_region

region = get_china_mirror_region(use_speed_test=True, top_n=3)
```

**手动指定镜像源**
```python
from archinstall.lib.mirrors_china import ChinaMirrorConfig

config = ChinaMirrorConfig()
# 仅使用推荐镜像源
recommended = config.get_recommended_mirrors()
# 按地理位置选择
beijing_mirrors = config.get_mirrors_by_location('Beijing')
# 仅 IPv6 镜像源
ipv6_mirrors = config.get_ipv6_mirrors()
```

**禁用中国镜像源**
```bash
# 使用环境变量
export ARCHINSTALL_DISABLE_CHINA_MIRRORS=1
archinstall
```

### 2. 字体配置

**自动字体配置（默认）**
```python
from archinstall.lib.font_config import ensure_chinese_font_with_fallback

# 完整回退链：现有字体 → 下载字体 → 紧急字体
ensure_chinese_font_with_fallback(
    target=None,           # None=当前系统
    auto_download=True,    # 允许下载
    create_emergency=True  # 允许创建紧急字体
)
```

**仅使用系统字体**
```python
from archinstall.lib.font_config import setup_chinese_font_environment

setup_chinese_font_environment(target=None)
```

**强制下载字体**
```python
from archinstall.lib.font_downloader import download_and_install_font

# 下载特定字体
download_and_install_font(
    font_info=None,  # None=使用默认第一个
    target=None,
    use_cache=True,
    timeout=30
)
```

### 3. 网络检测配置

**自动网络分析**
```python
from archinstall.lib.networking_china import ChinaNetworkOptimizer

optimizer = ChinaNetworkOptimizer()
optimizer.analyze_network()

if optimizer.should_use_china_mirrors:
    print('使用中国镜像源')
    
for rec in optimizer.recommendations:
    print(rec)
```

**自定义网络检测**
```python
from archinstall.lib.networking_china import (
    check_network_connectivity,
    is_network_available,
    is_international_accessible
)

# 检查网络是否可用
if is_network_available():
    print('网络连接正常')

# 检查国际网络访问
if is_international_accessible():
    print('国际网络访问正常')
else:
    print('建议使用中国镜像源')

# 自定义检测点
custom_endpoints = [
    {'host': 'your-dns.com', 'port': 53, 'name': 'Custom DNS'},
]
results = check_network_connectivity(custom_endpoints)
```

### 4. ISO 环境配置

**自动检测和配置**
```python
from archinstall.lib.iso_env import configure_for_environment

configure_for_environment()
```

**手动获取配置建议**
```python
from archinstall.lib.iso_env import (
    detect_iso_environment,
    get_optimal_concurrency,
    get_network_timeout,
    should_use_speed_test
)

env = detect_iso_environment()
print(f"ISO 环境: {env['is_iso']}")
print(f"推荐并发数: {get_optimal_concurrency()}")
print(f"网络超时: {get_network_timeout()}s")
print(f"建议速度测试: {should_use_speed_test()}")
```

---

## 高级用法

### 1. 自定义安装脚本

创建 `custom_install.py`：
```python
#!/usr/bin/env python3
import archinstall
from archinstall.lib.china_optimization import quick_setup
from archinstall.lib.mirrors_china import get_china_mirror_region
from archinstall.lib.disk import DiskLayout

# 初始化中国优化
manager = quick_setup()

# 获取推荐镜像源
mirror_region = get_china_mirror_region(use_speed_test=True)

# 定义磁盘布局
disk_layout = DiskLayout(
    main_device='/dev/sda',
    partitions=[
        {'mountpoint': '/boot', 'size': '512M', 'filesystem': 'fat32'},
        {'mountpoint': '/', 'size': '50G', 'filesystem': 'ext4'},
        {'mountpoint': '/home', 'size': '100%', 'filesystem': 'ext4'},
    ]
)

# 执行安装
with archinstall.Installer(
    target='/mnt',
    disk_config=disk_layout,
    mirror_config=mirror_region
) as installer:
    # 设置时区
    installer.set_timezone('Asia/Shanghai')
    
    # 设置 locale
    installer.set_locale('zh_CN.UTF-8')
    
    # 安装引导程序
    installer.install_bootloader('systemd-bootctl')
    
    # 安装中文字体
    installer.add_additional_packages([
        'noto-fonts-cjk',
        'noto-fonts-emoji',
        'fcitx5-im',
        'fcitx5-chinese-addons',
    ])
    
    # 完成安装
    installer.genfstab()
    installer.enable_service('systemd-timesyncd')
```

运行脚本：
```bash
python custom_install.py
```

### 2. 批量部署配置

创建 `batch-config.yaml`：
```yaml
# 通用配置
template:
  locale: zh_CN.UTF-8
  timezone: Asia/Shanghai
  keymap: us
  bootloader: systemd-bootctl
  
# 镜像源配置
mirrors:
  auto_select: true
  preferred:
    - Tsinghua
    - USTC
    - Alibaba
    
# 软件包
packages:
  base:
    - base
    - base-devel
    - linux
    - linux-firmware
  chinese:
    - noto-fonts-cjk
    - noto-fonts-emoji
    - fcitx5-im
    - fcitx5-chinese-addons
    - wqy-zenhei
  desktop:
    - gnome
    - gnome-tweaks
    
# 用户配置
users:
  - username: admin
    sudo: true
    groups:
      - wheel
      - video
      - audio
```

### 3. 集成到 CI/CD

```yaml
# .github/workflows/archinstall-test.yml
name: Test Archinstall China Optimization

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    container:
      image: archlinux:latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Install dependencies
      run: |
        pacman -Sy --noconfirm python python-pip
        pip install -e .
    
    - name: Run tests
      run: |
        python -m pytest tests/
        python -c "from archinstall.lib.china_optimization import quick_setup; quick_setup()"
```

---

## 故障排除

### 问题 1：无法加载中国优化模块

**症状：**
```
ImportError: No module named 'archinstall.lib.mirrors_china'
```

**解决方案：**
```bash
# 1. 检查安装路径
python -c "import archinstall; print(archinstall.__file__)"

# 2. 手动添加路径
export PYTHONPATH="/path/to/archinstall:$PYTHONPATH"

# 3. 重新安装
pip install -e .
```

### 问题 2：中文字体显示为方块

**症状：**
- 中文显示为 □□□ 或乱码

**解决方案：**
```bash
# 方法一：手动安装字体
pacman -Sy noto-fonts-cjk wqy-zenhei

# 方法二：使用字体下载模块
python -c "
from archinstall.lib.font_downloader import ensure_chinese_font_available
ensure_chinese_font_available(auto_download=True)
"

# 方法三：创建紧急字体
python -c "
from archinstall.lib.emergency_font import create_emergency_font_package
create_emergency_font_package()
"
```

### 问题 3：镜像源速度测试卡死

**症状：**
- 速度测试长时间无响应

**解决方案：**
```python
# 禁用速度测试，使用默认推荐
from archinstall.lib.mirrors_china import get_china_mirror_region

region = get_china_mirror_region(use_speed_test=False)

# 或在 ISO 环境下自动调整
from archinstall.lib.iso_env import should_use_speed_test

if should_use_speed_test():
    region = get_china_mirror_region(use_speed_test=True)
else:
    region = get_china_mirror_region(use_speed_test=False)
```

### 问题 4：网络检测失败

**症状：**
```
网络连接检测失败
```

**解决方案：**
```bash
# 1. 检查网络连接
ping 223.5.5.5

# 2. 手动配置网络
archinstall --skip-wifi-check

# 3. 离线模式
archinstall --offline
```

### 问题 5：字体下载失败

**症状：**
```
字体下载失败: <urlopen error ...>
```

**解决方案：**
```python
# 使用镜像源
from archinstall.lib.font_downloader import FALLBACK_FONTS, MIRROR_URLS

# 查看可用字体
for font in FALLBACK_FONTS:
    print(f"{font['name']}: {font['url']}")

# 手动下载并安装
wget https://downloads.sourceforge.net/project/wqy/wqy-bitmapfont/0.9.9-1/wqy-bitmapfont-pcf-0.9.9-1.tar.gz
tar -xzf wqy-bitmapfont-pcf-0.9.9-1.tar.gz
sudo cp -r wqy-bitmapfont /usr/share/fonts/
sudo fc-cache -fv
```

---

## 常见问题

### Q1: 这个优化版本会影响国际用户使用吗？

**A:** 不会。优化模块采用以下策略确保兼容性：
- 自动检测网络环境
- 国际网络正常时使用默认行为
- 所有修改都是添加性的，不修改原有 API
- 模块缺失时自动降级

### Q2: 如何完全禁用中国优化？

**A:** 有三种方式：
```bash
# 方式 1：环境变量
export ARCHINSTALL_DISABLE_CHINA_OPTIMIZATION=1
archinstall

# 方式 2：命令行参数
archinstall --no-china-optimization

# 方式 3：配置文件
{
  "china_optimization": {
    "enabled": false
  }
}
```

### Q3: 支持哪些桌面环境？

**A:** 所有 Arch Linux 支持的桌面环境都兼容：
- GNOME
- KDE Plasma
- XFCE
- LXDE/LXQt
- i3/sway
- 其他窗口管理器

中文字体和输入法可以在安装后通过包管理器安装。

### Q4: 安装后的系统如何配置中文？

**A:** 安装完成后执行：
```bash
# 1. 安装中文字体
sudo pacman -S noto-fonts-cjk wqy-zenhei

# 2. 安装输入法
sudo pacman -S fcitx5-im fcitx5-chinese-addons

# 3. 配置 locale
sudo localectl set-locale LANG=zh_CN.UTF-8

# 4. 配置输入法环境变量
# 编辑 ~/.bashrc 或 ~/.zshrc
export GTK_IM_MODULE=fcitx
export QT_IM_MODULE=fcitx
export XMODIFIERS=@im=fcitx
```

### Q5: 如何贡献代码？

**A:** 欢迎贡献！可以：
1. 提交 Issue 报告问题
2. 提交 PR 改进代码
3. 补充镜像源
4. 完善文档

---

## 附录

### A. 镜像源列表

| 镜像源 | 地址 | 位置 | IPv6 | 推荐 |
|--------|------|------|------|------|
| 清华大学 TUNA | mirrors.tuna.tsinghua.edu.cn | 北京 | ✓ | ✓ |
| 中科大 USTC | mirrors.ustc.edu.cn | 合肥 | ✓ | ✓ |
| 阿里云 | mirrors.aliyun.com | 杭州 | ✓ | ✓ |
| 腾讯云 | mirrors.cloud.tencent.com | 广州/深圳 | ✓ | ✓ |
| 上海交大 | mirror.sjtu.edu.cn | 上海 | ✓ | ✓ |
| 华为云 | mirrors.huaweicloud.com | 深圳 | ✓ | |
| 网易 | mirrors.163.com | 杭州 | | |

### B. 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `ARCHINSTALL_DISABLE_CHINA_OPTIMIZATION` | 禁用中国优化 | `0` |
| `ARCHINSTALL_DISABLE_CHINA_MIRRORS` | 禁用中国镜像 | `0` |
| `ARCHINSTALL_CHINA_MIRROR_TIMEOUT` | 镜像测试超时 | `5` |
| `ARCHINSTALL_FONT_CACHE_DIR` | 字体缓存目录 | `/var/cache/archinstall/fonts` |

### C. 相关链接

- [Arch Linux 官网](https://archlinux.org)
- [Archinstall 文档](https://archinstall.readthedocs.io)
- [清华镜像站](https://mirrors.tuna.tsinghua.edu.cn)
- [中科大镜像站](https://mirrors.ustc.edu.cn)

---

## 总结

Archinstall 中国优化版提供了：
1. ✅ 智能镜像源选择
2. ✅ 自动字体配置
3. ✅ 网络环境优化
4. ✅ 完整的回退机制
5. ✅ 向后兼容

按照本指南操作，即可在中国网络环境下快速、稳定地安装 Arch Linux。
