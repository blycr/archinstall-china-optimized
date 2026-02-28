# Archinstall 中国网络环境优化文档

## 概述

本文档详细记录了针对中国网络环境对 Archinstall 进行的优化。由于中国大陆访问国际网络的特殊性，这些优化旨在提升安装程序在国内网络环境下的可用性和下载速度。

## 优化内容

### 1. 新增中国镜像源支持

#### 1.1 文件位置
- `archinstall/lib/mirrors_china.py` - 中国镜像源配置模块

#### 1.2 支持的镜像源

| 镜像源 | 地址 | 位置 | IPv6 | 推荐 |
|--------|------|------|------|------|
| 清华大学 TUNA | mirrors.tuna.tsinghua.edu.cn | 北京 | ✓ | ✓ |
| 中科大 USTC | mirrors.ustc.edu.cn | 合肥 | ✓ | ✓ |
| 阿里云 | mirrors.aliyun.com | 杭州 | ✓ | ✓ |
| 腾讯云 | mirrors.cloud.tencent.com | 广州/深圳 | ✓ | ✓ |
| 华为云 | mirrors.huaweicloud.com | 深圳 | ✓ | |
| 网易 | mirrors.163.com | 杭州 | | |
| 上海交大 | mirror.sjtu.edu.cn | 上海 | ✓ | ✓ |
| 南京大学 | mirrors.nju.edu.cn | 南京 | ✓ | |
| 北京外国语大学 | mirrors.bfsu.edu.cn | 北京 | ✓ | |
| 兰州大学 | mirror.lzu.edu.cn | 兰州 | ✓ | |
| 重庆大学 | mirrors.cqu.edu.cn | 重庆 | ✓ | |
| 哈工大 | mirrors.hit.edu.cn | 哈尔滨 | ✓ | |
| 浙江大学 | mirrors.zju.edu.cn | 杭州 | ✓ | |
| 大连东软 | mirrors.neusoft.edu.cn | 大连 | | |

#### 1.3 核心功能

```python
# 获取中国镜像源配置
from archinstall.lib.mirrors_china import get_china_mirror_region

# 使用速度测试自动选择最快镜像源
china_region = get_china_mirror_region(use_speed_test=True, top_n=3)

# 手动注入中国镜像源（当无法获取远程列表时）
from archinstall.lib.mirrors_china import inject_china_mirrors
inject_china_mirrors(mirror_list_handler)
```

#### 1.4 速度测试功能

```python
from archinstall.lib.mirrors_china import ChinaMirrorConfig

# 自动测试所有镜像源速度并返回最快的 3 个
fastest_mirrors = ChinaMirrorConfig.get_fastest_mirrors(top_n=3, timeout=5)
```

### 2. 网络环境优化

#### 2.1 文件位置
- `archinstall/lib/networking_china.py` - 中国网络环境优化模块

#### 2.2 功能特性

##### 网络连接检测
```python
from archinstall.lib.networking_china import (
    check_network_connectivity,
    is_network_available,
    is_international_accessible,
)

# 检查网络是否可用（使用中国检测点）
if is_network_available():
    print("网络连接正常")

# 检查是否可以访问国际网络
if not is_international_accessible():
    print("建议使用中国镜像源")
```

##### 智能网络分析
```python
from archinstall.lib.networking_china import ChinaNetworkOptimizer

optimizer = ChinaNetworkOptimizer()
optimizer.analyze_network()  # 分析网络环境

if optimizer.should_use_china_mirrors:
    print("将自动使用中国镜像源")

# 获取网络建议
for recommendation in optimizer.recommendations:
    print(recommendation)
```

##### DNS 优化建议
```python
from archinstall.lib.networking_china import optimize_dns_for_china

# 获取适合中国网络的 DNS 列表
dns_servers = optimize_dns_for_china()
# ['223.5.5.5', '223.6.6.6', '119.29.29.29', '114.114.114.114']
```

### 3. 镜像源管理器集成

#### 3.1 文件修改
- `archinstall/lib/mirrors.py` - 集成中国镜像源支持

#### 3.2 自动回退机制

当无法从 `archlinux.org` 获取远程镜像列表时，自动注入中国镜像源：

```python
def load_remote_mirrors(self) -> bool:
    url = 'https://archlinux.org/mirrors/status/json/'
    attempts = 3

    for attempt_nr in range(attempts):
        try:
            mirrorlist = fetch_data_from_url(url)
            self._status_mappings = self._parse_remote_mirror_list(mirrorlist)
            return True
        except Exception as e:
            debug(f'Error while fetching mirror list: {e}')
            time.sleep(attempt_nr + 1)

    # 中国网络环境优化：当无法获取远程镜像列表时，尝试注入中国镜像源
    if CHINA_MIRROR_SUPPORT:
        info('无法从 archlinux.org 获取镜像列表，正在加载中国镜像源...')
        try:
            inject_china_mirrors(self)
            return True
        except Exception as e:
            warn(f'加载中国镜像源失败: {e}')

    debug('Unable to fetch mirror list remotely, falling back to local mirror list')
    return False
```

### 4. 主程序集成

#### 4.1 文件修改
- `archinstall/main.py` - 集成中国网络检测

#### 4.2 启动时网络分析

```python
# 中国网络环境优化：分析网络环境并给出建议
if CHINA_NETWORK_SUPPORT and not arch_config_handler.args.offline:
    info('正在检测网络环境...')
    china_optimizer = ChinaNetworkOptimizer()
    china_optimizer.analyze_network()
    if china_optimizer.should_use_china_mirrors:
        info('将使用中国镜像源以获得更好的下载速度')
```

#### 4.3 优化的网络检测

```python
def _check_online(wifi_handler: WifiHandler | None = None) -> bool:
    # 中国网络环境优化：优先使用中国网络检测点
    if CHINA_NETWORK_SUPPORT:
        if not is_network_available():
            info('网络连接检测失败，尝试配置 WiFi...')
            if wifi_handler is not None:
                success = not wifi_handler.setup()
                if not success:
                    return False
            else:
                return False
        return True

    # 默认检测方式（国际网络）
    try:
        ping('1.1.1.1')
    except OSError as ex:
        # ... 原有代码
```

## 使用方法

### 方式一：自动检测（推荐）

安装程序启动时会自动检测网络环境：
1. 检测网络连接状态
2. 判断是否可以访问国际网络
3. 如无法访问国际网络，自动使用中国镜像源
4. 执行镜像源速度测试，选择最快的镜像

### 方式二：手动配置

在配置文件中指定使用中国镜像源：

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
  }
}
```

### 方式三：脚本中使用

```python
from archinstall.lib.mirrors_china import get_china_mirror_region
from archinstall.lib.networking_china import ChinaNetworkOptimizer

# 网络分析
optimizer = ChinaNetworkOptimizer()
optimizer.analyze_network()

# 获取中国镜像源
if optimizer.should_use_china_mirrors:
    mirror_region = get_china_mirror_region(use_speed_test=True)
    # 使用 mirror_region 进行配置
```

## 网络检测点

### 国内检测点
- 阿里 DNS (223.5.5.5, 223.6.6.6)
- 腾讯 DNS (119.29.29.29)
- 114 DNS (114.114.114.114)
- 百度 (www.baidu.com)
- 淘宝 (www.taobao.com)

### 国际检测点
- Cloudflare DNS (1.1.1.1)
- Google DNS (8.8.8.8)
- Arch Linux (archlinux.org)

## 性能优化

### 速度测试算法
1. 并发测试多个镜像源（最多 5 个并发）
2. 使用 HEAD 请求快速检测可用性
3. 使用 GET 请求测试实际下载速度
4. 自动排序并返回最快的镜像源

### 超时设置
- 单个镜像源测试：5 秒
- DNS 检测：3 秒
- TCP 连接测试：3 秒

## 错误处理

### 网络检测失败
- 自动尝试配置 WiFi
- 提供清晰的错误信息
- 记录详细日志

### 镜像源测试失败
- 跳过失败的镜像源
- 使用默认推荐列表作为回退
- 不影响整体安装流程

## 兼容性

### 向后兼容
- 所有修改都是可选的增强功能
- 不会破坏原有功能
- 使用 `try/except` 确保模块缺失时不影响程序运行

### 模块依赖
```python
try:
    from archinstall.lib.mirrors_china import inject_china_mirrors
    CHINA_MIRROR_SUPPORT = True
except ImportError:
    CHINA_MIRROR_SUPPORT = False
```

## 调试信息

使用 `--debug` 参数可以查看详细的优化日志：

```bash
python -m archinstall --debug
```

日志内容包括：
- 网络检测结果
- 镜像源速度测试详情
- 自动选择的镜像源列表
- 错误和警告信息

## 常见问题

### Q: 如何确认正在使用中国镜像源？
A: 查看安装日志，会显示 "正在加载中国镜像源..." 或 "将使用中国镜像源以获得更好的下载速度"

### Q: 速度测试失败怎么办？
A: 程序会自动回退到默认的推荐镜像源列表（清华、中科大、阿里云、腾讯云）

### Q: 可以手动指定镜像源吗？
A: 可以，在交互式菜单中选择 "Add custom servers" 或修改配置文件

### Q: 这些优化会影响国际用户使用吗？
A: 不会，所有优化都是可选的，仅在检测到中国大陆网络环境时自动启用

## 贡献指南

### 添加新的镜像源

在 `archinstall/lib/mirrors_china.py` 中的 `CHINA_MIRRORS` 列表添加：

```python
ChinaMirror(
    name='Your Mirror Name',
    url='https://your.mirror.url/archlinux/',
    location='City',
    supports_ipv6=True/False,
    is_recommended=True/False,
),
```

### 测试镜像源速度

```bash
python -c "
from archinstall.lib.mirrors_china import ChinaMirrorConfig
mirrors = ChinaMirrorConfig.get_fastest_mirrors(top_n=5)
for m in mirrors:
    print(f'{m.name}: {m.url}')
"
```

## 更新日志

### 2024-XX-XX
- 初始版本发布
- 添加 14 个中国镜像源支持
- 实现自动网络环境检测
- 实现镜像源速度测试功能
- 集成到主安装流程

## 相关链接

- [清华大学 TUNA 镜像站](https://mirrors.tuna.tsinghua.edu.cn/)
- [中科大 USTC 镜像站](https://mirrors.ustc.edu.cn/)
- [阿里云镜像站](https://mirrors.aliyun.com/)
- [腾讯云镜像站](https://mirrors.cloud.tencent.com/)
- [Arch Linux 官方镜像列表](https://archlinux.org/mirrors/status/)

## 许可证

这些优化代码遵循与 Archinstall 相同的 GPL-3.0-only 许可证。
