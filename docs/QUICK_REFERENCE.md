# Archinstall 中国优化版 - 快速参考

## 重要提示

**直接使用 `archinstall` 命令运行的是系统原版，不包含中国优化！**

**正确使用方法：**
```bash
cd archinstall-china-optimized
python -m archinstall
```

---

## 快速开始

### 在 Arch ISO 中

```bash
# 1. 连接网络
# 2. 克隆仓库
git clone https://github.com/blycr/archinstall-china-optimized.git

# 3. 进入目录并运行
cd archinstall-china-optimized
python -m archinstall
```

### 替换系统版本（可选）

```bash
# 备份原版
sudo cp -r /usr/lib/python3.11/site-packages/archinstall \
          /usr/lib/python3.11/site-packages/archinstall.backup.$(date +%Y%m%d)

# 复制优化版（根据实际 Python 版本调整路径）
sudo cp -r ./archinstall /usr/lib/python3.11/site-packages/

# 现在可以直接使用 archinstall 命令
archinstall
```

---

## 常用命令

| 命令 | 说明 |
|------|------|
| `python -m archinstall` | 运行优化版（推荐） |
| `python -m archinstall --config config.json` | 使用配置文件 |
| `python -m archinstall --offline` | 离线模式 |
| `python -m archinstall --debug` | 调试模式 |

**注意**：如果已替换系统版本，可以直接使用 `archinstall`。

---

## 配置文件

### 最小配置

```json
{
  "mirror_config": {
    "mirror_regions": ["China"]
  }
}
```

### 推荐配置

```json
{
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
  "root_password": "your-password",
  "users": [
    {"username": "user", "password": "user-password", "sudo": true}
  ],
  "packages": ["noto-fonts-cjk", "fcitx5-im"]
}
```

保存为 `config.json`，然后：
```bash
python -m archinstall --config config.json
```

---

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

---

## 故障排除

### 字体显示方块

```bash
# 手动安装中文字体
pacman -Sy noto-fonts-cjk wqy-zenhei
```

### 优化未生效

**检查是否正确运行：**
```bash
# 错误：直接运行系统版本
archinstall

# 正确：从仓库目录运行
python -m archinstall
```

**检查是否替换成功：**
```bash
python -c "from archinstall.lib.mirrors_china import CHINA_MIRRORS; print(f'OK: {len(CHINA_MIRRORS)} mirrors')"
```

### 网络检测失败

```bash
# 跳过网络检测
python -m archinstall --offline
```

---

## 验证优化生效

运行时会看到以下输出：

```
[INFO] 正在初始化中国环境优化...
[INFO] 中国镜像源速度测试完成，最快的是: Tsinghua University (TUNA)
[INFO] 将使用中国镜像源以获得更好的下载速度
```

如果未看到这些输出，说明：
1. 你可能运行的是系统原版 `archinstall`
2. 请使用 `python -m archinstall` 从仓库目录运行

---

## 相关文档

- [完整使用指南](USAGE_GUIDE.md)
- [技术文档](CHINA_OPTIMIZATION.md)
- [README](../README.md)
