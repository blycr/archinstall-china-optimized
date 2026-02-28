"""
中国镜像源配置模块

针对中国网络环境优化的 Arch Linux 镜像源配置。
提供国内主流镜像源（清华、中科大、阿里云、腾讯云等）的快速访问。
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from archinstall.lib.output import debug, info, warn

# 安全导入编码工具
try:
	from archinstall.lib.encoding_utils import safe_decode, safe_encode, ensure_utf8_env
	ENCODING_SUPPORT = True
except ImportError:
	ENCODING_SUPPORT = False

if TYPE_CHECKING:
	from archinstall.lib.models.mirrors import MirrorRegion


@dataclass
class ChinaMirror:
	"""中国镜像源定义"""
	name: str
	url: str
	location: str  # 地理位置
	supports_ipv6: bool = True
	is_recommended: bool = False  # 是否推荐

	@property
	def server_url(self) -> str:
		"""返回完整的镜像源 URL"""
		return f'{self.url}$repo/os/$arch'


# 中国主要 Arch Linux 镜像源列表
CHINA_MIRRORS: list[ChinaMirror] = [
	# 清华大学 TUNA 镜像源 - 推荐
	ChinaMirror(
		name='Tsinghua University (TUNA)',
		url='https://mirrors.tuna.tsinghua.edu.cn/archlinux/',
		location='Beijing',
		supports_ipv6=True,
		is_recommended=True,
	),
	# 中国科学技术大学 USTC 镜像源 - 推荐
	ChinaMirror(
		name='University of Science and Technology of China (USTC)',
		url='https://mirrors.ustc.edu.cn/archlinux/',
		location='Hefei',
		supports_ipv6=True,
		is_recommended=True,
	),
	# 阿里云镜像源
	ChinaMirror(
		name='Alibaba Cloud',
		url='https://mirrors.aliyun.com/archlinux/',
		location='Hangzhou',
		supports_ipv6=True,
		is_recommended=True,
	),
	# 腾讯云镜像源
	ChinaMirror(
		name='Tencent Cloud',
		url='https://mirrors.cloud.tencent.com/archlinux/',
		location='Guangzhou/Shenzhen',
		supports_ipv6=True,
		is_recommended=True,
	),
	# 华为云镜像源
	ChinaMirror(
		name='Huawei Cloud',
		url='https://mirrors.huaweicloud.com/archlinux/',
		location='Shenzhen',
		supports_ipv6=True,
		is_recommended=False,
	),
	# 网易镜像源
	ChinaMirror(
		name='NetEase',
		url='https://mirrors.163.com/archlinux/',
		location='Hangzhou',
		supports_ipv6=False,
		is_recommended=False,
	),
	# 上海交通大学镜像源
	ChinaMirror(
		name='Shanghai Jiao Tong University (SJTUG)',
		url='https://mirror.sjtu.edu.cn/archlinux/',
		location='Shanghai',
		supports_ipv6=True,
		is_recommended=True,
	),
	# 南京大学镜像源
	ChinaMirror(
		name='Nanjing University',
		url='https://mirrors.nju.edu.cn/archlinux/',
		location='Nanjing',
		supports_ipv6=True,
		is_recommended=False,
	),
	# 北京外国语大学镜像源
	ChinaMirror(
		name='Beijing Foreign Studies University (BFSU)',
		url='https://mirrors.bfsu.edu.cn/archlinux/',
		location='Beijing',
		supports_ipv6=True,
		is_recommended=False,
	),
	# 兰州大学镜像源
	ChinaMirror(
		name='Lanzhou University',
		url='https://mirror.lzu.edu.cn/archlinux/',
		location='Lanzhou',
		supports_ipv6=True,
		is_recommended=False,
	),
	# 重庆大学镜像源
	ChinaMirror(
		name='Chongqing University',
		url='https://mirrors.cqu.edu.cn/archlinux/',
		location='Chongqing',
		supports_ipv6=True,
		is_recommended=False,
	),
	# 哈尔滨工业大学镜像源
	ChinaMirror(
		name='Harbin Institute of Technology (HIT)',
		url='https://mirrors.hit.edu.cn/archlinux/',
		location='Harbin',
		supports_ipv6=True,
		is_recommended=False,
	),
	# 浙江大学镜像源
	ChinaMirror(
		name='Zhejiang University',
		url='https://mirrors.zju.edu.cn/archlinux/',
		location='Hangzhou',
		supports_ipv6=True,
		is_recommended=False,
	),
	# 大连东软信息学院镜像源
	ChinaMirror(
		name='Neusoft Institute of Information',
		url='https://mirrors.neusoft.edu.cn/archlinux/',
		location='Dalian',
		supports_ipv6=False,
		is_recommended=False,
	),
]


@dataclass
class ChinaMirrorConfig:
	"""中国镜像源配置管理器"""
	mirrors: list[ChinaMirror] = field(default_factory=lambda: CHINA_MIRRORS.copy())
	auto_select_best: bool = True
	preferred_location: str | None = None  # 优先地理位置

	def get_recommended_mirrors(self) -> list[ChinaMirror]:
		"""获取推荐的镜像源列表"""
		return [m for m in self.mirrors if m.is_recommended]

	def get_mirrors_by_location(self, location: str) -> list[ChinaMirror]:
		"""按地理位置获取镜像源"""
		return [m for m in self.mirrors if location.lower() in m.location.lower()]

	def get_ipv6_mirrors(self) -> list[ChinaMirror]:
		"""获取支持 IPv6 的镜像源"""
		return [m for m in self.mirrors if m.supports_ipv6]

	def to_mirror_region(self, selected_mirrors: list[ChinaMirror] | None = None) -> 'MirrorRegion':
		"""转换为中国镜像源区域配置

		Args:
			selected_mirrors: 选定的镜像源列表，如果为 None 则使用所有推荐镜像源

		Returns:
			MirrorRegion 对象用于 archinstall 配置
		"""
		# 延迟导入避免循环导入问题
		from archinstall.lib.models.mirrors import MirrorRegion

		if selected_mirrors is None:
			selected_mirrors = self.get_recommended_mirrors()

		urls = [m.url for m in selected_mirrors]
		return MirrorRegion(name='China', urls=urls)

	@classmethod
	def get_fastest_mirrors(cls, top_n: int = 3, timeout: int = 5) -> list[ChinaMirror]:
		"""通过速度测试获取最快的镜像源

		在Arch ISO受限环境下，使用保守的并发设置和多重超时保护，
		确保不会因网络测试导致安装器卡死。

		Args:
			top_n: 返回最快的 N 个镜像源
			timeout: 每个镜像源测试超时时间（秒）

		Returns:
			按速度排序的镜像源列表
		"""
		import concurrent.futures
		import urllib.error
		import urllib.request

		results: list[tuple[ChinaMirror, float]] = []

		def test_mirror(mirror: ChinaMirror) -> tuple[ChinaMirror, float] | None:
			"""测试单个镜像源的下载速度"""
			test_url = f'{mirror.url}core/os/x86_64/core.db'
			debug(f'测试中国镜像源速度: {mirror.name} ({test_url})')

			try:
				# 使用 HEAD 请求测试响应速度（更轻量）
				req = urllib.request.Request(url=test_url, method='HEAD')
				# 设置 socket 全局超时防止挂起
				import socket
				original_timeout = socket.getdefaulttimeout()
				socket.setdefaulttimeout(timeout)

				try:
					with urllib.request.urlopen(req, timeout=timeout) as response:
						# 检查响应状态
						if response.status != 200:
							debug(f'  {mirror.name} 返回状态码: {response.status}')
							return None

						# 获取响应时间作为速度指标（更轻量）
						import time
						start = time.perf_counter()
						# 读取一小部分数据验证连接质量
						_ = response.read(1024)
						elapsed = time.perf_counter() - start

						if elapsed > 0:
							# 使用响应时间作为质量指标（时间越短越好）
							speed = 1.0 / elapsed  # 倒数作为速度指标
							debug(f'  {mirror.name} 响应时间: {elapsed:.3f}s')
							return (mirror, speed)
				finally:
					socket.setdefaulttimeout(original_timeout)

			except (urllib.error.URLError, TimeoutError, OSError) as e:
				debug(f'  {mirror.name} 测试失败: {e}')
				return None
			except Exception as e:
				# 捕获所有异常，确保单个镜像测试失败不会影响整体
				debug(f'  {mirror.name} 测试时发生意外错误: {e}')
				return None

		# 在受限环境中使用更保守的并发设置
		# max_workers=3 避免资源耗尽，在单核ISO环境中更安全
		max_workers = min(3, len(CHINA_MIRRORS))

		try:
			with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
				# 只测试推荐的镜像源（减少网络负载）
				test_targets = [m for m in CHINA_MIRRORS if m.is_recommended]
				if not test_targets:
					test_targets = CHINA_MIRRORS[:5]  # 回退到前5个

				future_to_mirror = {executor.submit(test_mirror, m): m for m in test_targets}

				for future in concurrent.futures.as_completed(future_to_mirror):
					try:
						result = future.result(timeout=timeout + 2)  # 额外缓冲时间
						if result:
							results.append(result)
					except concurrent.futures.TimeoutError:
						mirror = future_to_mirror[future]
						debug(f'  {mirror.name} 测试超时')
					except Exception as e:
						mirror = future_to_mirror[future]
						debug(f'  {mirror.name} 获取结果时出错: {e}')
		except Exception as e:
			warn(f'镜像源速度测试线程池出错: {e}，使用默认推荐列表')
			return [m for m in CHINA_MIRRORS if m.is_recommended][:top_n]

		# 按速度排序并返回前 N 个
		results.sort(key=lambda x: x[1], reverse=True)

		if results:
			info(f'中国镜像源速度测试完成，最快的是: {results[0][0].name}')
			return [m[0] for m in results[:top_n]]

		# 如果所有测试都失败，返回推荐镜像源
		debug('所有镜像源速度测试失败，使用默认推荐列表')
		return [m for m in CHINA_MIRRORS if m.is_recommended][:top_n]


def get_china_mirror_region(use_speed_test: bool = True, top_n: int = 3) -> 'MirrorRegion':
	"""获取中国镜像源区域配置的便捷函数

	在Arch ISO环境下，速度测试是可选的，默认使用推荐列表以确保可靠性。

	Args:
		use_speed_test: 是否执行速度测试选择最快镜像源（ISO环境下建议关闭）
		top_n: 选择最快的 N 个镜像源

	Returns:
		配置好的 MirrorRegion 对象
	"""
	# 延迟导入避免循环导入问题
	from archinstall.lib.models.mirrors import MirrorRegion

	config = ChinaMirrorConfig()

	if use_speed_test:
		info('正在测试中国镜像源速度，请稍候...')
		try:
			fastest_mirrors = ChinaMirrorConfig.get_fastest_mirrors(top_n=top_n)
			return config.to_mirror_region(fastest_mirrors)
		except Exception as e:
			warn(f'速度测试失败，使用默认推荐列表: {e}')

	# 使用默认推荐列表（更可靠）
	return config.to_mirror_region()


def inject_china_mirrors(mirror_list_handler: 'MirrorListHandler') -> None:
	"""将中国镜像源注入到 MirrorListHandler

	当无法从 archlinux.org 获取远程镜像列表时，使用此函数注入中国镜像源。

	Args:
		mirror_list_handler: MirrorListHandler 实例
	"""
	from archinstall.lib.models.mirrors import MirrorStatusEntryV3

	china_region = get_china_mirror_region(use_speed_test=False)
	mirror_entries: list[MirrorStatusEntryV3] = []

	for mirror in CHINA_MIRRORS:
		entry = MirrorStatusEntryV3(
			url=mirror.url,
			protocol='https',
			active=True,
			country='China',
			country_code='CN',
			isos=True,
			ipv4=True,
			ipv6=mirror.supports_ipv6,
			details=f'{mirror.name} - {mirror.location}',
			score=0,  # 低分数表示高质量
		)
		mirror_entries.append(entry)

	# 注入到中国区域
	if mirror_list_handler._status_mappings is None:
		mirror_list_handler._status_mappings = {}

	mirror_list_handler._status_mappings['China'] = mirror_entries
	mirror_list_handler._fetched_remote = True  # 标记为已获取

	debug(f'已注入 {len(mirror_entries)} 个中国镜像源')
