"""
Archinstall 中国优化主模块

整合所有中国网络环境优化功能，提供统一的接口。
此模块应在主程序启动时调用，自动配置最佳环境。
"""

import sys
from pathlib import Path

# 确保模块路径
if str(Path(__file__).parent.parent) not in sys.path:
	sys.path.insert(0, str(Path(__file__).parent.parent))

from archinstall.lib.output import debug, info, warn


class ChinaOptimizationManager:
	"""
	中国环境优化管理器

	整合字体、编码、网络、镜像等所有优化功能，
	提供一键配置和自动检测。
	"""

	def __init__(self) -> None:
		self._initialized = False
		self._features: dict[str, bool] = {
			'font_support': False,
			'encoding_support': False,
			'network_support': False,
			'mirror_support': False,
			'utils_support': False,
		}
		self._environment_info: dict = {}

	def _check_features(self) -> None:
		"""检查各功能模块可用性"""
		# 检查字体支持
		try:
			from archinstall.lib.font_config import setup_chinese_font_environment
			self._features['font_support'] = True
		except ImportError:
			debug('字体配置模块不可用')

		# 检查编码支持
		try:
			from archinstall.lib.encoding_utils import ensure_utf8_env
			self._features['encoding_support'] = True
		except ImportError:
			debug('编码工具模块不可用')

		# 检查网络支持
		try:
			from archinstall.lib.networking_china import ChinaNetworkOptimizer
			self._features['network_support'] = True
		except ImportError:
			debug('中国网络模块不可用')

		# 检查镜像支持
		try:
			from archinstall.lib.mirrors_china import CHINA_MIRRORS
			self._features['mirror_support'] = True
		except ImportError:
			debug('中国镜像模块不可用')

		# 检查工具支持
		try:
			from archinstall.lib.china_utils import get_recommended_timezone
			self._features['utils_support'] = True
		except ImportError:
			debug('中国工具模块不可用')

	def initialize(self, auto_configure: bool = True) -> bool:
		"""
		初始化中国环境优化

		Args:
			auto_configure: 是否自动配置环境

		Returns:
			是否成功
		"""
		if self._initialized:
			return True

		info('正在初始化中国环境优化...')

		# 检查功能模块
		self._check_features()

		# 报告可用功能
		available = [k for k, v in self._features.items() if v]
		debug(f'可用优化功能: {", ".join(available)}')

		if auto_configure:
			self._auto_configure()

		self._initialized = True
		info('中国环境优化初始化完成')
		return True

	def _auto_configure(self) -> None:
		"""自动配置环境"""
		# 1. 配置编码环境（最高优先级）
		if self._features['encoding_support']:
			try:
				from archinstall.lib.encoding_utils import ensure_utf8_env
				ensure_utf8_env()
				debug('编码环境已配置')
			except Exception as e:
				debug(f'配置编码环境失败: {e}')

		# 2. 配置字体（带完整回退机制）
		if self._features['font_support']:
			try:
				from archinstall.lib.font_config import ensure_chinese_font_with_fallback
				if ensure_chinese_font_with_fallback(
					target=None,
					auto_download=True,
					create_emergency=True
				):
					debug('中文字体已配置（含下载/紧急回退）')
				else:
					warn('中文字体配置可能不完整')
			except Exception as e:
				debug(f'配置字体环境失败: {e}')

		# 3. 分析网络环境
		if self._features['network_support']:
			try:
				from archinstall.lib.networking_china import ChinaNetworkOptimizer
				optimizer = ChinaNetworkOptimizer()
				optimizer.analyze_network()
				self._environment_info['should_use_china_mirrors'] = optimizer.should_use_china_mirrors
				self._environment_info['recommendations'] = optimizer.recommendations
				debug('网络环境分析完成')
			except Exception as e:
				debug(f'网络环境分析失败: {e}')

	@property
	def features(self) -> dict[str, bool]:
		"""获取可用功能列表"""
		return self._features.copy()

	@property
	def environment_info(self) -> dict:
		"""获取环境信息"""
		return self._environment_info.copy()

	@property
	def should_use_china_mirrors(self) -> bool:
		"""是否应该使用中国镜像源"""
		return self._environment_info.get('should_use_china_mirrors', False)

	def get_recommended_mirrors(self) -> list[dict]:
		"""
		获取推荐的镜像源列表

		Returns:
			镜像源信息列表
		"""
		if not self._features['mirror_support']:
			return []

		try:
			from archinstall.lib.mirrors_china import CHINA_MIRRORS

			mirrors = []
			for mirror in CHINA_MIRRORS:
				if mirror.is_recommended:
					mirrors.append({
						'name': mirror.name,
						'url': mirror.url,
						'location': mirror.location,
						'ipv6': mirror.supports_ipv6,
					})
			return mirrors
		except Exception as e:
			warn(f'获取推荐镜像源失败: {e}')
			return []

	def configure_target_system(self, target: Path) -> bool:
		"""
		配置目标系统（安装后的系统）

		Args:
			target: 目标系统挂载点

		Returns:
			是否成功
		"""
		success = True
		info(f'正在为目标系统配置中国优化: {target}')

		# 1. 配置 pacman
		if self._features['utils_support']:
			try:
				from archinstall.lib.china_utils import configure_pacman_for_china
				if configure_pacman_for_china(target):
					debug('pacman 已优化')
				else:
					success = False
			except Exception as e:
				warn(f'配置 pacman 失败: {e}')
				success = False

		# 2. 配置字体
		if self._features['font_support']:
			try:
				from archinstall.lib.font_config import configure_vconsole_for_chinese
				if configure_vconsole_for_chinese(target):
					debug('控制台字体已配置')
			except Exception as e:
				debug(f'配置控制台字体失败: {e}')

		# 3. 配置 locale
		if self._features['utils_support']:
			try:
				from archinstall.lib.china_utils import setup_china_specific_config
				if setup_china_specific_config(target):
					debug('中国特定配置已应用')
			except Exception as e:
				debug(f'应用中国特定配置失败: {e}')

		return success


def quick_setup() -> ChinaOptimizationManager:
	"""
	快速设置中国环境优化

	Returns:
		配置好的 ChinaOptimizationManager 实例
	"""
	manager = ChinaOptimizationManager()
	manager.initialize(auto_configure=True)
	return manager


# 全局实例
_china_manager: ChinaOptimizationManager | None = None


def get_china_manager() -> ChinaOptimizationManager:
	"""
	获取全局中国优化管理器实例

	Returns:
		ChinaOptimizationManager 实例
	"""
	global _china_manager
	if _china_manager is None:
		_china_manager = ChinaOptimizationManager()
	return _china_manager


# 便捷的导出函数
__all__ = [
	'ChinaOptimizationManager',
	'quick_setup',
	'get_china_manager',
]
