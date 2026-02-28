# Archinstall 中国用户指南

## 简介

这是专为 Arch Linux 安装程序 `archinstall` 的中国网络环境优化版本。针对中国大陆网络特点进行了深度优化，包括：

- ✅ 自动检测中国网络环境
- ✅ 内置 14 个国内高速镜像源
- ✅ 智能镜像源速度测试
- ✅ 自动选择最快镜像源
- ✅ 国内 DNS 优化
- ✅ 网络连接状态智能检测

## 支持的镜像源

### 推荐镜像源（默认启用）
| 镜像源 | 位置 | 特点 |
|--------|------|------|
| 清华大学 TUNA | 北京 | 速度快，更新及时 |
| 中科大 USTC | 合肥 | 教育网优选 |
| 阿里云 | 杭州 | 商业用户稳定 |
| 腾讯云 | 广州/深圳 | 华南地区优选 |
| 上海交大 | 上海 | 华东地区优选 |

### 其他可用镜像源
- 华为云、网易、南京大学、北京外国语大学
- 兰州大学、重庆大学、哈工大、浙江大学

## 快速开始

### 在 Arch ISO 中使用

```bash
# 1. 启动 Arch ISO 后，确保网络连接
ping -c 3 baidu.com

# 2. 安装优化的 archinstall
pacman -Sy git

git clone https://github.com/archlinux/archinstall
cd archinstall

# 使用优化版本
python -m archinstall
```

### 自动优化流程

启动安装程序后，会自动执行以下优化：

1. **网络检测** - 检测是否在中国网络环境
2. **镜像选择** - 如无法访问国际网络，自动启用中国镜像源
3. **速度测试** - 自动测试各镜像源速度
4. **最优选择** - 选择最快的 3 个镜像源进行安装

### 手动配置镜像源

如果自动检测未生效，可以手动选择：

```bash
# 在安装程序中选择 "Mirrors and repositories"
# 选择 "Select regions" -> "China"
# 或添加自定义镜像服务器
```

## 配置文件示例

### 使用中国镜像源的自动安装配置

创建 `china_config.json`:

```json
{
  "mirror_config": {
    "mirror_regions": {
      "China": [
        "https://mirrors.tuna.tsinghua.edu.cn/archlinux/",
        "https://mirrors.ustc.edu.cn/archlinux/",
        "https://mirrors.aliyun.com/archlinux/"
      ]
    }
  },
  "locale_config": {
    "sys_lang": "zh_CN.UTF-8",
    "sys_enc": "UTF-8",
    "keyboard_layout": "cn"
  },
  "disk_config": {
    "config_type": "default_layout",
    "device_modifications": []
  },
  "bootloader_config": {
    "bootloader": "systemd-boot"
  },
  "hostname": "archlinux-cn",
  "kernels": ["linux"]
}
```

运行安装：

```bash
python -m archinstall --config china_config.json
```

## 网络问题排查

### 1. 检查网络连接

```bash
# 测试国内网络
ping -c 3 baidu.com

# 测试国际网络
ping -c 3 archlinux.org
```

### 2. 配置 DNS（如需要）

```bash
# 编辑 /etc/resolv.conf
echo "nameserver 223.5.5.5" > /etc/resolv.conf
echo "nameserver 223.6.6.6" >> /etc/resolv.conf
```

### 3. 配置 WiFi

```bash
iwctl
[iwd]# device list
[iwd]# station wlan0 scan
[iwd]# station wlan0 get-networks
[iwd]# station wlan0 connect "Your_WiFi_Name"
```

### 4. 查看详细日志

```bash
python -m archinstall --debug

# 查看日志文件
cat /var/log/archinstall/install.log
```

## 常见问题

### Q: 安装程序启动很慢？
A: 这是正常现象，程序正在测试各镜像源的速度以选择最快的镜像源。

### Q: 如何选择特定的镜像源？
A: 在 "Mirrors and repositories" 菜单中，选择 "Add custom servers" 手动输入镜像源地址。

### Q: 安装过程中下载速度很慢？
A: 可以尝试：
1. 重启安装程序重新进行速度测试
2. 手动选择离你地理位置最近的镜像源
3. 检查网络连接是否稳定

### Q: 能否在国际网络环境下使用？
A: 可以！优化是自动检测的，如果检测到可以访问国际网络，会使用默认的镜像源选择方式。

### Q: 如何更新到最新版本？

```bash
cd archinstall
git pull
python -m archinstall
```

## 高级用法

### 在 Python 脚本中使用

```python
from archinstall.lib.mirrors_china import get_china_mirror_region
from archinstall.lib.networking_china import ChinaNetworkOptimizer

# 分析网络环境
optimizer = ChinaNetworkOptimizer()
optimizer.analyze_network()

# 获取优化的镜像源配置
if optimizer.should_use_china_mirrors:
    mirror_region = get_china_mirror_region(use_speed_test=True)
    print(f"使用镜像源: {mirror_region.name}")
    for url in mirror_region.urls:
        print(f"  - {url}")
```

### 测试镜像源速度

```python
from archinstall.lib.mirrors_china import ChinaMirrorConfig

# 测试所有镜像源速度
fastest = ChinaMirrorConfig.get_fastest_mirrors(top_n=3)
print("最快的 3 个镜像源:")
for mirror in fastest:
    print(f"  {mirror.name} ({mirror.location})")
```

## 技术细节

### 自动检测机制

1. **网络可达性检测** - 使用阿里 DNS、腾讯 DNS、百度等国内节点
2. **国际网络检测** - 尝试连接 Cloudflare DNS 和 Arch Linux 官网
3. **智能决策** - 如无法访问国际网络，自动启用中国镜像源

### 速度测试机制

1. 并发测试最多 5 个镜像源
2. 下载 `core/os/x86_64/core.db` 测试实际速度
3. 5 秒超时保护
4. 自动排序选择最快镜像源

## 获取帮助

### 中文支持

- 查看详细优化文档：[CHINA_OPTIMIZATION.md](CHINA_OPTIMIZATION.md)
- 提交 Issue（中文可接受）

### 官方资源

- [Archinstall 官方文档](https://archinstall.readthedocs.io/)
- [Arch Linux 中文论坛](https://bbs.archlinuxcn.org/)
- [Arch Linux 中文 Wiki](https://wiki.archlinuxcn.org/)

## 贡献代码

欢迎提交改进建议：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目遵循 GPL-3.0-only 许可证，与 Archinstall 保持一致。

## 致谢

感谢以下镜像源提供方：
- 清华大学 TUNA 协会
- 中国科学技术大学
- 阿里云
- 腾讯云
- 以及其他所有镜像源维护者

---

**注意**：此优化版本非 Arch Linux 官方发布，但所有代码修改都遵循官方代码规范，并尽量保持向后兼容。
