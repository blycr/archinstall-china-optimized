"""
ISO 环境检测与自适应配置模块

检测当前是否运行在 Arch Linux Live ISO 环境中，
并根据环境特点自动调整配置以优化性能和兼容性。
"""

import os
import sys
from functools import lru_cache
from pathlib import Path

from archinstall.lib.output import debug, info


@lru_cache(maxsize=1)
def detect_iso_environment() -> dict[str, bool]:
	"""
	检测当前运行环境是否为 Arch Linux Live ISO

	Returns:
		包含环境信息的字典:
		- is_iso: 是否在 ISO 环境中
		- is_live: 是否 Live 模式
		- is_readonly_root: 根文件系统是否只读
		- has_pacman_cache: 是否有 pacman 缓存
		- memory_size_mb: 可用内存(MB)
		- cpu_count: CPU 核心数
	"""
	env_info = {
		'is_iso': False,
		'is_live': False,
		'is_readonly_root': False,
		'has_pacman_cache': False,
		'memory_size_mb': 0,
		'cpu_count': 1,
	}

	# 检测 ISO 标志文件
	iso_markers = [
		'/run/archiso',
		'/etc/archiso',
		'/dev/disk/by-label/ARCH_',
	]

	for marker in iso_markers:
		if Path(marker).exists():
			env_info['is_iso'] = True
			debug(f'检测到 ISO 环境标志: {marker}')
			break

	# 检查 cmdline 中的 archiso 参数
	try:
		with open('/proc/cmdline', 'r') as f:
			cmdline = f.read()
			if 'archiso' in cmdline:
				env_info['is_iso'] = True
				env_info['is_live'] = True
				debug('从 /proc/cmdline 检测到 ISO 环境')
	except (FileNotFoundError, PermissionError):
		pass

	# 检测根文件系统是否只读
	try:
		with open('/proc/mounts', 'r') as f:
			for line in f:
				parts = line.split()
				if len(parts) >= 4 and parts[1] == '/':
					options = parts[3].split(',')
					if 'ro' in options:
						env_info['is_readonly_root'] = True
						debug('检测到只读根文件系统')
					break
	except (FileNotFoundError, PermissionError):
		pass

	# 检测 pacman 缓存
	env_info['has_pacman_cache'] = Path('/var/cache/pacman/pkg').exists()

	# 获取系统资源信息
	try:
		# 获取可用内存
		with open('/proc/meminfo', 'r') as f:
			for line in f:
				if line.startswith('MemAvailable:'):
					kb = int(line.split()[1])
					env_info['memory_size_mb'] = kb // 1024
					break
	except (FileNotFoundError, ValueError):
		pass

	# 获取 CPU 核心数
	env_info['cpu_count'] = os.cpu_count() or 1

	return env_info


def get_iso_environment() -> dict[str, bool]:
	"""获取 ISO 环境信息（非缓存版本）"""
	detect_iso_environment.cache_clear()
	return detect_iso_environment()


def is_iso_environment() -> bool:
	"""快速检测是否在 ISO 环境中"""
	return detect_iso_environment()['is_iso']


def get_optimal_concurrency() -> int:
	"""
	获取适合当前环境的并发数

	在 ISO 环境中，考虑到内存和 CPU 限制，
	返回保守的并发设置。
	"""
	env = detect_iso_environment()
	cpu_count = env['cpu_count']
	memory_mb = env['memory_size_mb']

	# 基础并发数
	if env['is_iso']:
		# ISO 环境下更保守
		base_workers = min(2, cpu_count)
		# 内存小于 2GB 时进一步减少
		if memory_mb < 2048:
			base_workers = min(base_workers, 2)
		if memory_mb < 1024:
			base_workers = 1
	else:
		# 正常环境使用更多资源
		base_workers = min(4, cpu_count)

	debug(f'当前环境并发数设置: {base_workers} (CPU: {cpu_count}, 内存: {memory_mb}MB)')
	return max(1, base_workers)


def get_network_timeout() -> int:
	"""
	获取适合当前环境的网络超时时间

	在 ISO 环境下，网络可能不稳定，使用稍长的超时。
	"""
	env = detect_iso_environment()

	if env['is_iso']:
		# ISO 环境下网络可能较慢
		return 10

	return 5


def should_use_speed_test() -> bool:
	"""
	判断是否应执行速度测试

	在资源受限的 ISO 环境中，跳过速度测试以提高可靠性。
	"""
	env = detect_iso_environment()

	if not env['is_iso']:
		return True

	# ISO 环境下根据资源决定是否测试
	if env['memory_size_mb'] < 1024:
		debug('内存不足，跳过速度测试')
		return False

	if env['cpu_count'] < 2:
		debug('单核 CPU，跳过速度测试')
		return False

	return True


def get_mirror_recommendation_count() -> int:
	"""
	获取推荐的镜像源数量

	在受限环境中使用较少的镜像源以减少网络负载。
	"""
	env = detect_iso_environment()

	if env['is_iso']:
		return 3  # ISO 环境下使用 3 个镜像源

	return 5  # 正常环境下使用 5 个


def configure_for_environment() -> None:
	"""
	根据环境自动配置优化参数

	在主程序启动时调用，自动调整全局配置。
	"""
	env = detect_iso_environment()

	if env['is_iso']:
		info('检测到 Arch Linux Live ISO 环境，应用优化配置')

		if env['is_readonly_root']:
			debug('检测到只读根文件系统，某些功能可能受限')

		if env['memory_size_mb'] < 1024:
			info(f'内存较低 ({env["memory_size_mb"]}MB)，将使用保守模式')

		debug(f'ISO 环境配置: 并发={get_optimal_concurrency()}, '
		      f'超时={get_network_timeout()}s, '
		      f'速度测试={should_use_speed_test()}')
	else:
		debug('检测到正常安装环境，使用标准配置')


# 便捷的导出函数
__all__ = [
	'detect_iso_environment',
	'get_iso_environment',
	'is_iso_environment',
	'get_optimal_concurrency',
	'get_network_timeout',
	'should_use_speed_test',
	'get_mirror_recommendation_count',
	'configure_for_environment',
]
