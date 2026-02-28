# Archinstall 中国优化版 - 快速参考

## 🚀 最简使用

```bash
# 启动即自动优化
archinstall
```

## 📋 常用命令

### 基础安装
```bash
# 标准安装（自动检测网络环境）
archinstall

# 离线安装
archinstall --offline

# 调试模式
archinstall --debug

# 使用配置文件
archinstall --config config.json
```

### 网络相关
```bash
# 跳过 WiFi 检测
archinstall --skip-wifi-check

# 手动配置网络后
archinstall --skip-wifi-check
```

## 🔧 配置文件模板

### 最小配置
```json
{
  "mirror_config": {
    "mirror_regions": ["China"]
  },
  "locale_config": {
    "sys_lang": "zh_CN.UTF-8"
  }
}
```

### 完整配置
```json
{
  "archinstall-language": "English",
  "locale_config": {
    "sys_lang": "zh_CN.UTF-8",
    "sys_enc": "UTF-8",
    "kb_layout": "us"
  },
  "mirror_config": {
    "mirror_regions": ["China"]
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
  "root_password": "password",
  "users": [
    {"username": "user", "password": "password", "sudo": true}
  ],
  "packages": ["noto-fonts-cjk", "fcitx5-im"]
}
```

## 🐍 Python API

### 一键优化
```python
from archinstall.lib.china_optimization import quick_setup
manager = quick_setup()
```

### 镜像源
```python
from archinstall.lib.mirrors_china import get_china_mirror_region

# 自动速度测试
region = get_china_mirror_region(use_speed_test=True)

# 使用默认推荐
region = get_china_mirror_region(use_speed_test=False)
```

### 字体
```python
from archinstall.lib.font_config import ensure_chinese_font_with_fallback

# 完整回退链
ensure_chinese_font_with_fallback()
```

### 网络检测
```python
from archinstall.lib.networking_china import ChinaNetworkOptimizer

optimizer = ChinaNetworkOptimizer()
optimizer.analyze_network()

if optimizer.should_use_china_mirrors:
    print("使用中国镜像源")
```

## 🆘 故障排除

### 字体显示问题
```bash
# 手动安装字体
pacman -S noto-fonts-cjk wqy-zenhei

# 或使用自动下载
python -c "
from archinstall.lib.font_downloader import ensure_chinese_font_available
ensure_chinese_font_available(auto_download=True)
"
```

### 镜像源问题
```bash
# 跳过速度测试
export ARCHINSTALL_CHINA_MIRROR_TIMEOUT=1
archinstall
```

### 模块加载失败
```bash
# 检查安装
python -c "from archinstall.lib.china_optimization import get_china_manager"

# 手动添加路径
export PYTHONPATH="/path/to/archinstall:$PYTHONPATH"
```

## 📊 镜像源状态

| 镜像源 | 速度 | 稳定性 |
|--------|------|--------|
| 清华 TUNA | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 中科大 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 阿里云 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 腾讯云 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 上海交大 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

## 🔗 相关链接

- 详细文档：[USAGE_GUIDE.md](./USAGE_GUIDE.md)
- 技术文档：[CHINA_OPTIMIZATION.md](./CHINA_OPTIMIZATION.md)
- 中文指南：[README_CN.md](./README_CN.md)

## 💡 提示

1. **首次使用**：建议直接运行 `archinstall`，让优化自动生效
2. **网络不佳**：会自动切换到离线模式或中国镜像源
3. **字体问题**：模块会自动处理，无需手动干预
4. **兼容性**：不影响国际用户使用，自动检测环境

---

**记住**：最简单的使用方式就是直接运行 `archinstall`，其他都交给自动优化！
