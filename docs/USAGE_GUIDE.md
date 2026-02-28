# Archinstall 中国优化版 - 使用指南

## 目录
1. [重要说明](#重要说明)
2. [快速开始](#快速开始)
3. [安装方法](#安装方法)
4. [使用方式](#使用方式)
5. [配置选项](#配置选项)
6. [故障排除](#故障排除)

---

## 重要说明

### 关于 `archinstall` 命令

**系统自带的 `archinstall` 命令使用的是官方原版，不包含中国优化。**

要使用中国优化版，必须采用以下方式之一：

1. **使用 `python -m archinstall` 从本仓库目录运行（推荐）**
2. **将本仓库代码替换系统版本**
3. **使用提供的安装脚本**

---

## 快速开始

### 在 Arch ISO 中使用（最简单）

```bash
# 1. 连接到互联网
ping -c 3 223.5.5.5

# 2. 克隆本仓库
git clone https://github.com/blycr/archinstall-china-optimized.git

# 3. 进入目录
cd archinstall-china-optimized

# 4. 运行优化版安装器
python -m archinstall
```

**注意**：必须从本仓库目录运行 `python -m archinstall`，直接使用 `archinstall` 命令无效。

### 预期输出

运行后你会看到类似输出：
```
[INFO] 正在初始化中国环境优化...
[INFO] 正在分析网络环境...
[INFO] 中国镜像源速度测试完成，最快的是: Tsinghua University (TUNA)
[INFO] 将使用中国镜像源以获得更好的下载速度
```

---

## 安装方法

### 方法一：直接使用（推荐，零污染）

```bash
# 克隆仓库
git clone https://github.com/blycr/archinstall-china-optimized.git
cd archinstall-china-optimized

# 运行安装器
python -m archinstall
```

**优点**：
- 不修改系统文件
- 即开即用
- 可随时删除，不影响系统

### 方法二：替换系统版本（永久生效）

```bash
# 1. 查找 archinstall 安装位置
python -c "import archinstall; print(archinstall.__path__[0])"

# 2. 备份原版（重要！）
sudo cp -r /usr/lib/python3.11/site-packages/archinstall \
          /usr/lib/python3.11/site-packages/archinstall.backup.$(date +%Y%m%d)

# 3. 复制优化版
sudo cp -r ./archinstall /usr/lib/python3.11/site-packages/

# 4. 现在可以直接使用 archinstall 命令
archinstall
```

**注意**：根据你的 Python 版本调整路径（python3.10、python3.11、python3.12 等）

### 方法三：使用安装脚本

```bash
chmod +x install.sh
sudo ./install.sh
```

此脚本会自动：
- 备份原版
- 复制优化版
- 验证安装

---

## 使用方式

### 基本使用

```bash
# 进入仓库目录
cd archinstall-china-optimized

# 运行安装器
python -m archinstall
```

### 使用配置文件

创建配置文件 `my-config.json`：
```json
{
  "mirror_config": {
    "mirror_regions": ["China"]
  },
  "locale_config": {
    "sys_lang": "zh_CN.UTF-8",
    "kb_layout": "us"
  },
  "disk_config": {
    "main_device": "/dev/sda",
    "partitions": [
      {"mountpoint": "/boot", "size": "512M", "filesystem": "fat32"},
      {"mountpoint": "/", "size": "50G", "filesystem": "ext4"},
      {"mountpoint": "/home", "size": "100%", "filesystem": "ext4"}
    ]
  },
  "bootloader": "systemd-bootctl",
  "hostname": "archlinux-cn",
  "root_password": "your-password",
  "users": [
    {"username": "user", "password": "user-password", "sudo": true}
  ],
  "packages": ["noto-fonts-cjk", "fcitx5-im"]
}
```

运行：
```bash
python -m archinstall --config my-config.json
```

### 离线安装

```bash
python -m archinstall --offline
```

### 调试模式

```bash
python -m archinstall --debug
```

---

## 配置选项

### 镜像源配置

优化版会自动选择最快的镜像源，你也可以手动指定：

```json
{
  "mirror_config": {
    "mirror_regions": ["China"],
    "custom_servers": [
      "https://mirrors.tuna.tsinghua.edu.cn/archlinux/",
      "https://mirrors.ustc.edu.cn/archlinux/"
    ]
  }
}
```

可用镜像源：
- 清华大学 TUNA
- 中国科学技术大学 USTC
- 阿里云
- 腾讯云
- 华为云
- 上海交大
- 等等

### 字体配置

字体配置是自动的，无需手动干预。系统会按以下顺序尝试：
1. 检测现有 CJK 字体
2. 自动下载轻量级字体（文泉驿 4.5MB）
3. 创建内嵌位图字体（60+ 常用汉字）

### 网络检测

优化版会自动检测网络环境：
- 检测国内网络（阿里 DNS、腾讯 DNS、百度、淘宝）
- 检测国际网络（Cloudflare DNS、Google DNS）
- 自动判断是否需要使用中国镜像

---

## 故障排除

### 问题 1：运行 `python -m archinstall` 提示模块未找到

**原因**：不在仓库目录中

**解决**：
```bash
cd archinstall-china-optimized
python -m archinstall
```

### 问题 2：提示 "中国优化模块未加载"

**原因**：Python 路径问题

**解决**：
```bash
# 检查模块是否存在
ls archinstall/lib/mirrors_china.py

# 使用完整路径运行
PYTHONPATH="$(pwd):$PYTHONPATH" python -m archinstall
```

### 问题 3：中文字体显示为方块

**原因**：ISO 环境中缺少中文字体

**解决**：
优化版会自动处理，如果仍有问题：
```bash
# 手动安装字体
pacman -Sy noto-fonts-cjk

# 然后重新运行
python -m archinstall
```

### 问题 4：如何确认使用的是优化版？

**检查方法**：
```bash
# 方法 1：查看启动信息
python -m archinstall 2>&1 | grep -i "中国"

# 方法 2：检查模块加载
python -c "from archinstall.lib.mirrors_china import CHINA_MIRRORS; print(f'优化版已加载，{len(CHINA_MIRRORS)} 个镜像源')"
```

### 问题 5：如何恢复到官方原版？

**如果使用方法一（直接使用）**：
```bash
# 直接删除仓库即可
rm -rf archinstall-china-optimized

# 系统不受影响
```

**如果使用方法二（替换系统版本）**：
```bash
# 恢复备份
sudo rm -rf /usr/lib/python3.11/site-packages/archinstall
sudo mv /usr/lib/python3.11/site-packages/archinstall.backup.20240101 \
        /usr/lib/python3.11/site-packages/archinstall
```

---

## 常见问题

### Q1: 直接运行 `archinstall` 和 `python -m archinstall` 有什么区别？

A: 
- `archinstall`：运行系统安装的官方原版（无中国优化）
- `python -m archinstall`：运行当前目录下的优化版（含中国优化）

### Q2: 为什么不用 `pip install` 安装？

A: 因为本优化版不是官方发布的包，需要通过 Git 克隆使用。

### Q3: 可以在已安装的 Arch 系统中使用吗？

A: 可以，但主要用于 ISO 安装环境。在已安装系统中运行会提示错误。

### Q4: 优化版安全吗？

A: 安全。所有修改都是开源的，你可以查看代码：
- `archinstall/lib/mirrors_china.py` - 镜像源配置
- `archinstall/lib/networking_china.py` - 网络检测
- `archinstall/lib/mirrors.py` - 集成修改（仅添加 try/except 导入）

### Q5: 如何更新到最新版？

A:
```bash
cd archinstall-china-optimized
git pull origin master
```

---

## 总结

**记住三个要点：**

1. **必须使用 `python -m archinstall` 从仓库目录运行**
2. **或者直接替换系统版本后才能使用 `archinstall` 命令**
3. **优化会自动生效，无需额外配置**

**最简单的使用方式：**
```bash
git clone https://github.com/blycr/archinstall-china-optimized.git
cd archinstall-china-optimized
python -m archinstall
```
