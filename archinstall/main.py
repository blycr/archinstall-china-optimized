"""Arch Linux installer - guided, templates etc."""

import importlib
import os
import sys
import textwrap
import time
import traceback
from pathlib import Path

from archinstall.lib.args import arch_config_handler
from archinstall.lib.disk.utils import disk_layouts
from archinstall.lib.hardware import SysInfo
from archinstall.lib.network.wifi_handler import WifiHandler
from archinstall.lib.networking import ping
from archinstall.lib.output import debug, error, info, warn

# 中国网络环境优化支持
try:
	from archinstall.lib.networking_china import (
		ChinaNetworkOptimizer,
		is_network_available,
	)
	CHINA_NETWORK_SUPPORT = True
except ImportError:
	CHINA_NETWORK_SUPPORT = False
from archinstall.lib.packages.util import check_version_upgrade
from archinstall.lib.pacman.pacman import Pacman
from archinstall.lib.translationhandler import tr
from archinstall.lib.utils.util import running_from_host


def _log_sys_info() -> None:
	# Log various information about hardware before starting the installation. This might assist in troubleshooting
	debug(f'Hardware model detected: {SysInfo.sys_vendor()} {SysInfo.product_name()}; UEFI mode: {SysInfo.has_uefi()}')
	debug(f'Processor model detected: {SysInfo.cpu_model()}')
	debug(f'Memory statistics: {SysInfo.mem_available()} available out of {SysInfo.mem_total()} total installed')
	debug(f'Virtualization detected: {SysInfo.virtualization()}; is VM: {SysInfo.is_vm()}')
	debug(f'Graphics devices detected: {SysInfo._graphics_devices().keys()}')

	# For support reasons, we'll log the disk layout pre installation to match against post-installation layout
	debug(f'Disk states before installing:\n{disk_layouts()}')


def _check_online(wifi_handler: WifiHandler | None = None) -> bool:
	"""
	检查网络连接状态

	在Arch ISO环境下，采用多层次的检测策略：
	1. 首先尝试中国网络检测点（如果支持）
	2. 其次尝试国际网络检测
	3. 如果都失败，尝试配置WiFi
	4. 最终失败后返回False
	"""
	# 第一层：中国网络环境检测（优先但非阻塞）
	if CHINA_NETWORK_SUPPORT:
		try:
			if is_network_available():
				debug('通过中国网络检测点确认网络连接正常')
				return True
			debug('中国网络检测点不可达，尝试其他检测方式')
		except Exception as e:
			debug(f'中国网络检测出错: {e}')

	# 第二层：国际网络检测（经典方式）
	try:
		ping('1.1.1.1')
		debug('通过国际网络检测确认网络连接正常')
		return True
	except OSError as ex:
		error_msg = str(ex)
		if 'Network is unreachable' in error_msg or 'unknown host' in error_msg.lower():
			debug(f'国际网络检测失败: {error_msg}')
			# 网络不可达，尝试WiFi配置
			if wifi_handler is not None:
				info('网络连接检测失败，尝试配置 WiFi...')
				success = not wifi_handler.setup()
				if not success:
					warn('WiFi配置失败或用户取消')
					return False
				# WiFi配置成功后，递归再次检测
				return _check_online(None)  # 避免再次触发WiFi配置
			else:
				warn('网络不可达且WiFi配置不可用')
				return False
		else:
			# 其他类型的OSError，记录但认为网络可能可用
			debug(f'ping返回非网络不可达错误: {error_msg}')
			return True
	except Exception as e:
		# 捕获所有其他异常，避免安装器崩溃
		debug(f'网络检测时发生意外错误: {e}')
		# 即使有异常，也尝试继续（可能是ping命令问题）
		return True

	return True


def _fetch_arch_db() -> bool:
	info('Fetching Arch Linux package database...')
	try:
		Pacman.run('-Sy')
	except Exception as e:
		error('Failed to sync Arch Linux package database.')
		if 'could not resolve host' in str(e).lower():
			error('Most likely due to a missing network connection or DNS issue.')

		error('Run archinstall --debug and check /var/log/archinstall/install.log for details.')

		debug(f'Failed to sync Arch Linux package database: {e}')
		return False

	return True


def _list_scripts() -> str:
	lines = ['The following are viable --script options:']

	for file in (Path(__file__).parent / 'scripts').glob('*.py'):
		if file.stem != '__init__':
			lines.append(f'    {file.stem}')

	return '\n'.join(lines)


def run() -> int:
	"""
	This can either be run as the compiled and installed application: python setup.py install
	OR straight as a module: python -m archinstall
	In any case we will be attempting to load the provided script to be run from the scripts/ folder
	"""
	if '--help' in sys.argv or '-h' in sys.argv:
		arch_config_handler.print_help()
		return 0

	script = arch_config_handler.get_script()

	if script == 'list':
		print(_list_scripts())
		return 0

	if os.getuid() != 0:
		print(tr('Archinstall requires root privileges to run. See --help for more.'))
		return 1

	_log_sys_info()

	# 中国网络环境优化：分析网络环境并给出建议
	# 在ISO环境下，此分析是可选的，不会阻塞安装流程
	if CHINA_NETWORK_SUPPORT and not arch_config_handler.args.offline:
		try:
			info('正在检测网络环境...')
			china_optimizer = ChinaNetworkOptimizer()
			# 设置较短的超时，避免在受限环境中长时间等待
			china_optimizer.analyze_network()
			if china_optimizer.should_use_china_mirrors:
				info('将使用中国镜像源以获得更好的下载速度')
		except Exception as e:
			# 网络分析失败不应阻塞安装流程
			debug(f'网络环境分析失败（非关键错误）: {e}')
			info('继续使用默认网络配置')

	if not arch_config_handler.args.offline:
		if not arch_config_handler.args.skip_wifi_check:
			wifi_handler = WifiHandler()
		else:
			wifi_handler = None

		if not _check_online(wifi_handler):
			return 0

		if not _fetch_arch_db():
			return 1

		if not arch_config_handler.args.skip_version_check:
			upgrade = check_version_upgrade()

			if upgrade:
				text = tr('New version available') + f': {upgrade}'
				info(text)
				time.sleep(3)

	if running_from_host():
		# log which mode we are using
		debug('Running from Host (H2T Mode)...')
	else:
		debug('Running from ISO (Live Mode)...')

	mod_name = f'archinstall.scripts.{script}'
	# by loading the module we'll automatically run the script
	module = importlib.import_module(mod_name)
	module.main()

	return 0


def _error_message(exc: Exception) -> None:
	err = ''.join(traceback.format_exception(exc))
	error(err)

	text = textwrap.dedent(
		"""\
		Archinstall experienced the above error. If you think this is a bug, please report it to
		https://github.com/archlinux/archinstall and include the log file "/var/log/archinstall/install.log".

		Hint: To extract the log from a live ISO
		curl -F 'file=@/var/log/archinstall/install.log' https://0x0.st
		"""
	)
	warn(text)


def main() -> int:
	rc = 0
	exc = None

	try:
		rc = run()
	except Exception as e:
		exc = e
	finally:
		if exc:
			_error_message(exc)
			rc = 1

	return rc


if __name__ == '__main__':
	sys.exit(main())
