"""
中国网络环境优化模块

针对中国网络特点优化的网络连接检测和配置功能。
在 Arch ISO 受限环境下安全运行，具备完善的错误处理和超时控制。
"""

import socket
import time
import urllib.error
import urllib.request
from typing import Callable

from archinstall.lib.output import debug, info, warn

# 中国网络环境下的可访问检测点
# 这些是国内可访问的地址，用于检测网络连接状态
CHINA_NETWORK_TEST_ENDPOINTS: list[dict[str, str | int]] = [
	# 阿里云公共 DNS
	{'host': '223.5.5.5', 'port': 53, 'name': 'Alibaba DNS'},
	{'host': '223.6.6.6', 'port': 53, 'name': 'Alibaba DNS Backup'},
	# 腾讯云公共 DNS
	{'host': '119.29.29.29', 'port': 53, 'name': 'Tencent DNS'},
	# 114 DNS
	{'host': '114.114.114.114', 'port': 53, 'name': '114 DNS'},
	# 百度
	{'host': 'www.baidu.com', 'port': 80, 'name': 'Baidu'},
	# 淘宝
	{'host': 'www.taobao.com', 'port': 443, 'name': 'Taobao'},
]

# 国际网络检测点（用于判断是否需要特殊网络配置）
INTERNATIONAL_TEST_ENDPOINTS: list[dict[str, str | int]] = [
	{'host': '1.1.1.1', 'port': 53, 'name': 'Cloudflare DNS'},
	{'host': '8.8.8.8', 'port': 53, 'name': 'Google DNS'},
	{'host': 'archlinux.org', 'port': 443, 'name': 'Arch Linux'},
]

# 全局超时设置（秒）
DEFAULT_SOCKET_TIMEOUT = 3
MAX_SOCKET_TIMEOUT = 5


def test_tcp_connection(host: str, port: int, timeout: int = DEFAULT_SOCKET_TIMEOUT) -> bool:
	"""测试 TCP 连接

	在 Arch ISO 环境下使用保守的超时设置，避免网络检测导致安装器卡死。

	Args:
		host: 目标主机
		port: 目标端口
		timeout: 超时时间（秒），默认3秒

	Returns:
		连接是否成功
	"""
	# 限制超时在合理范围内
	timeout = min(max(timeout, 1), MAX_SOCKET_TIMEOUT)

	try:
		# 设置全局 socket 超时防止挂起
		original_timeout = socket.getdefaulttimeout()
		socket.setdefaulttimeout(timeout)

		try:
			with socket.create_connection((host, port), timeout=timeout):
				return True
		except (socket.timeout, socket.error, OSError):
			return False
	finally:
		# 恢复原始超时设置
		socket.setdefaulttimeout(original_timeout)


def check_network_connectivity(
	endpoints: list[dict[str, str | int]] | None = None,
	timeout: int = DEFAULT_SOCKET_TIMEOUT,
	require_all: bool = False,
) -> dict[str, bool]:
	"""检查网络连接状态

	Args:
		endpoints: 检测点列表，默认为中国网络检测点
		timeout: 每个检测点的超时时间
		require_all: 是否需要所有检测点都通过

	Returns:
		每个检测点的连接状态字典
	"""
	if endpoints is None:
		endpoints = CHINA_NETWORK_TEST_ENDPOINTS

	# 限制超时
	timeout = min(timeout, MAX_SOCKET_TIMEOUT)
	results: dict[str, bool] = {}

	for endpoint in endpoints:
		host = str(endpoint['host'])
		port = int(endpoint['port'])
		name = str(endpoint['name'])

		is_reachable = test_tcp_connection(host, port, timeout)
		results[name] = is_reachable

		debug(f'网络检测 {name} ({host}:{port}): {"✓" if is_reachable else "✗"}')

		if not require_all and is_reachable:
			# 只要有任何一个可达，就认为网络正常
			break

	return results


def is_network_available() -> bool:
	"""检查网络是否可用（使用中国检测点）

	优先使用 DNS 服务器检测，更轻量可靠。
	"""
	# 只测试前两个 DNS（更可靠）
	dns_endpoints = CHINA_NETWORK_TEST_ENDPOINTS[:2]
	results = check_network_connectivity(dns_endpoints, timeout=2)
	return any(results.values())


def is_international_accessible() -> bool:
	"""检查是否可以访问国际网络

	用于判断是否需要使用中国镜像源或代理。

	Returns:
		如果可以访问国际网络返回 True，否则返回 False
	"""
	# 只测试前两个国际端点
	results = check_network_connectivity(
		INTERNATIONAL_TEST_ENDPOINTS[:2],
		timeout=DEFAULT_SOCKET_TIMEOUT
	)
	return any(results.values())


def test_mirror_speed(url: str, timeout: int = DEFAULT_SOCKET_TIMEOUT) -> float | None:
	"""测试镜像源响应速度

	在 Arch ISO 环境下使用轻量级 HEAD 请求而非完整下载。

	Args:
		url: 镜像源 URL
		timeout: 超时时间

	Returns:
		响应速度指标（越大越好），如果失败返回 None
	"""
	test_url = f'{url}core/os/x86_64/core.db'
	timeout = min(timeout, MAX_SOCKET_TIMEOUT)

	try:
		# 设置 socket 超时
		original_timeout = socket.getdefaulttimeout()
		socket.setdefaulttimeout(timeout)

		try:
			start_time = time.perf_counter()
			req = urllib.request.Request(url=test_url, method='HEAD')

			with urllib.request.urlopen(req, timeout=timeout) as response:
				# 检查是否返回 200
				if response.status != 200:
					return None

				# 读取一小部分数据
				_ = response.read(1024)

			elapsed = time.perf_counter() - start_time
			if elapsed > 0:
				# 使用响应时间的倒数作为速度指标
				return 1.0 / elapsed

		finally:
			socket.setdefaulttimeout(original_timeout)

	except (urllib.error.URLError, TimeoutError, OSError) as e:
		debug(f'速度测试失败 {url}: {e}')
	except Exception as e:
		# 捕获所有异常，确保安全
		debug(f'速度测试意外错误 {url}: {e}')

	return None


def get_fastest_mirror(mirrors: list[str], timeout: int = DEFAULT_SOCKET_TIMEOUT) -> tuple[str, float] | None:
	"""从多个镜像源中选择最快的一个

	Args:
		mirrors: 镜像源 URL 列表
		timeout: 测试超时时间

	Returns:
		(最快镜像源 URL, 速度指标) 的元组，如果都失败返回 None
	"""
	import concurrent.futures

	if not mirrors:
		return None

	results: list[tuple[str, float]] = []
	timeout = min(timeout, MAX_SOCKET_TIMEOUT)

	def test_single_mirror(url: str) -> tuple[str, float] | None:
		speed = test_mirror_speed(url, timeout)
		if speed:
			return (url, speed)
		return None

	# 限制并发数，避免资源耗尽
	max_workers = min(3, len(mirrors))

	try:
		with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
			future_to_url = {executor.submit(test_single_mirror, url): url for url in mirrors}

			for future in concurrent.futures.as_completed(future_to_url):
				try:
					result = future.result(timeout=timeout + 1)
					if result:
						results.append(result)
				except concurrent.futures.TimeoutError:
					url = future_to_url[future]
					debug(f'镜像源测试超时: {url}')
				except Exception as e:
					url = future_to_url[future]
					debug(f'镜像源测试出错 {url}: {e}')
	except Exception as e:
		warn(f'镜像源测试线程池出错: {e}')
		return None

	if results:
		# 按速度排序
		results.sort(key=lambda x: x[1], reverse=True)
		best = results[0]
		info(f'最快镜像源: {best[0]}')
		return best

	return None


def optimize_dns_for_china() -> list[str]:
	"""获取适合中国网络的 DNS 服务器列表

	Returns:
		推荐的 DNS 服务器地址列表
	"""
	# 优先使用国内 DNS，速度更快
	return [
		'223.5.5.5',    # 阿里 DNS
		'223.6.6.6',    # 阿里 DNS 备用
		'119.29.29.29', # 腾讯 DNS
		'114.114.114.114', # 114 DNS
	]


def check_dns_resolution(hostname: str = 'archlinux.org', timeout: int = DEFAULT_SOCKET_TIMEOUT) -> bool:
	"""检查 DNS 解析是否正常

	Args:
		hostname: 用于测试解析的主机名
		timeout: 超时时间

	Returns:
		DNS 解析是否正常
	"""
	timeout = min(timeout, MAX_SOCKET_TIMEOUT)

	try:
		socket.setdefaulttimeout(timeout)
		socket.getaddrinfo(hostname, None)
		return True
	except socket.gaierror:
		return False
	except Exception as e:
		debug(f'DNS 解析检查出错: {e}')
		return False
	finally:
		socket.setdefaulttimeout(None)


def get_network_recommendations() -> list[str]:
	"""获取针对中国网络环境的建议

	Returns:
		建议列表
	"""
	recommendations: list[str] = []

	# 检查网络连接
	if not is_network_available():
		recommendations.append('⚠️ 网络连接异常，请检查网络配置')
		return recommendations

	# 检查国际网络访问
	if not is_international_accessible():
		recommendations.append('ℹ️ 检测到无法直接访问国际网络，将自动使用中国镜像源')
		recommendations.append('💡 建议：使用清华、中科大、阿里云等国内镜像源以获得最佳速度')
	else:
		recommendations.append('✓ 国际网络访问正常')

	# 检查 DNS
	if not check_dns_resolution():
		recommendations.append('⚠️ DNS 解析可能存在问题，建议配置可靠的 DNS 服务器')
		recommendations.append('💡 推荐 DNS: 223.5.5.5, 223.6.6.6 (阿里), 119.29.29.29 (腾讯)')

	return recommendations


class ChinaNetworkOptimizer:
	"""中国网络环境优化器

	提供针对中国网络环境的自动优化功能。
	在 Arch ISO 环境下安全运行，具备完善的错误处理。
	"""

	def __init__(self) -> None:
		self._network_checked: bool = False
		self._is_international_accessible: bool = True
		self._recommendations: list[str] = []
		self._china_mirrors_recommended: bool = False

	def analyze_network(self) -> None:
		"""分析网络环境"""
		if self._network_checked:
			return

		info('正在分析网络环境...')

		try:
			self._is_international_accessible = is_international_accessible()
			self._recommendations = get_network_recommendations()
			self._china_mirrors_recommended = not self._is_international_accessible

			for rec in self._recommendations:
				info(rec)

		except Exception as e:
			warn(f'网络分析过程出错: {e}')
			self._recommendations = ['⚠️ 网络分析过程出错，将使用默认配置']
			# 出错时保守起见，建议使用中国镜像源
			self._china_mirrors_recommended = True

		self._network_checked = True

	@property
	def should_use_china_mirrors(self) -> bool:
		"""是否应该使用中国镜像源"""
		if not self._network_checked:
			self.analyze_network()
		return self._china_mirrors_recommended

	@property
	def recommendations(self) -> list[str]:
		"""获取网络建议"""
		if not self._network_checked:
			self.analyze_network()
		return self._recommendations

	def reset(self) -> None:
		"""重置网络分析状态，允许重新检测"""
		self._network_checked = False


# 便捷函数：快速检查是否需要中国镜像源
def should_use_china_mirrors_quick_check() -> bool:
	"""快速检查是否应该使用中国镜像源

	这是一个轻量级检查，只测试国际访问性，不执行完整分析。

	Returns:
		如果建议使用中国镜像源返回 True
	"""
	return not is_international_accessible()
