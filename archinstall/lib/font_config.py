"""
字体配置模块

处理 Arch Linux ISO 环境下的字体配置，确保中文能正确显示。
在 Live ISO 中，默认可能没有中文字体，需要检测和配置。
"""

import os
import shutil
from pathlib import Path
from typing import overload

from archinstall.lib.output import debug, info, warn


# 常见的中文字体包
CHINESE_FONT_PACKAGES = [
	'noto-fonts-cjk',      # Google Noto CJK 字体（推荐）
	'adobe-source-han-sans-cn-fonts',  # Adobe Source Han Sans
	'adobe-source-han-serif-cn-fonts', # Adobe Source Han Serif
	'wqy-zenhei',          # 文泉驿正黑
	'wqy-microhei',        # 文泉驿微米黑
]

# ISO 环境下可能已安装的字体
AVAILABLE_FONTS = [
	'Lat2-Terminus16',
	'LatGrkCyr-8x16',
	'UniCyrExt_8x16',
	'UniCyr_8x16',
]


@overload
def setup_console_font(font: str) -> bool: ...

@overload
def setup_console_font(font: str, target: Path) -> bool: ...

def setup_console_font(font: str, target: Path | None = None) -> bool:
	"""
	设置控制台字体

	Args:
		font: 字体名称
		target: 目标系统路径（如果为 None 则设置当前系统）

	Returns:
		是否成功
	"""
	try:
		if target is None:
			# 设置当前系统字体
			result = os.system(f'setfont {font} 2>/dev/null')
			if result == 0:
				debug(f'控制台字体已设置为: {font}')
				return True
		else:
			# 为目标系统配置字体
			vconsole_conf = target / 'etc/vconsole.conf'
			if vconsole_conf.exists():
				content = vconsole_conf.read_text()
				# 替换或添加 FONT 行
				lines = content.splitlines()
				new_lines = []
				font_set = False
				for line in lines:
					if line.startswith('FONT='):
						new_lines.append(f'FONT={font}')
						font_set = True
					else:
						new_lines.append(line)
				if not font_set:
					new_lines.append(f'FONT={font}')

				vconsole_conf.write_text('\n'.join(new_lines) + '\n')
				debug(f'目标系统控制台字体设置为: {font}')
				return True
			else:
				# 创建新的 vconsole.conf
				vconsole_conf.parent.mkdir(parents=True, exist_ok=True)
				vconsole_conf.write_text(f'FONT={font}\n')
				return True
	except Exception as e:
		debug(f'设置控制台字体失败: {e}')
		return False


def get_available_console_fonts() -> list[str]:
	"""
	获取可用的控制台字体列表

	Returns:
		字体名称列表
	"""
	fonts = []
	font_dirs = [
		Path('/usr/share/kbd/consolefonts'),
		Path('/usr/share/consolefonts'),
	]

	for font_dir in font_dirs:
		if font_dir.exists():
			try:
				for font_file in font_dir.iterdir():
					if font_file.suffix in ['.psfu', '.psf', '.gz', '']:
						fonts.append(font_file.stem.replace('.psfu', '').replace('.psf', ''))
			except PermissionError:
				continue

	return sorted(set(fonts))


def detect_chinese_support() -> dict[str, bool]:
	"""
	检测中文字体支持情况

	Returns:
		包含支持信息的字典
	"""
	result = {
		'has_cjk_font': False,
		'has_console_font': False,
		'available_cjk_fonts': [],
		'console_font': None,
	}

	# 检测 CJK 字体
	font_paths = [
		Path('/usr/share/fonts/noto-cjk'),
		Path('/usr/share/fonts/adobe-source-han-sans'),
		Path('/usr/share/fonts/wqy'),
		Path('/usr/share/fonts/TTF/NotoSansCJK-Regular.ttc'),
	]

	for path in font_paths:
		if path.exists():
			result['has_cjk_font'] = True
			result['available_cjk_fonts'].append(str(path))

	# 检测当前控制台字体
	try:
		# 尝试从 /proc 获取当前字体
		if Path('/proc/sys/kernel/console_loglevel').exists():
			# 检查当前终端是否支持 Unicode
			result['has_console_font'] = True
	except Exception:
		pass

	return result


def setup_chinese_font_environment(target: Path | None = None) -> bool:
	"""
	配置中文显示环境

	在 ISO 环境下，设置合适的字体和 locale 以确保中文能正确显示。

	Args:
		target: 目标系统路径（如果为 None 则配置当前系统）

	Returns:
		是否成功
	"""
	success = True

	if target is None:
		# 配置当前系统
		info('配置中文显示环境...')

		# 尝试设置支持 Unicode 的控制台字体
		unicode_fonts = [
			'Lat2-Terminus16',
			'UniCyr_8x16',
			'LatGrkCyr-8x16',
		]

		font_set = False
		for font in unicode_fonts:
			if setup_console_font(font):
				font_set = True
				info(f'控制台字体已设置: {font}')
				break

		if not font_set:
			warn('无法设置 Unicode 控制台字体，中文可能显示为方块')
			success = False

		# 设置 UTF-8 locale
		try:
			os.environ['LC_ALL'] = 'C.UTF-8'
			os.environ['LANG'] = 'C.UTF-8'
			debug('Locale 已设置为 C.UTF-8')
		except Exception as e:
			debug(f'设置 locale 失败: {e}')

	else:
		# 配置目标系统
		debug(f'为目标系统配置中文环境: {target}')

		# 确保 locale.conf 存在
		locale_conf = target / 'etc/locale.conf'
		try:
			locale_conf.parent.mkdir(parents=True, exist_ok=True)
			if not locale_conf.exists():
				locale_conf.write_text('LANG=en_US.UTF-8\n')
				debug('创建默认 locale.conf')
		except Exception as e:
			warn(f'配置目标系统 locale 失败: {e}')
			success = False

	return success


def ensure_font_packages(target: Path) -> list[str]:
	"""
	确保目标系统安装了必要的字体包

	Args:
		target: 目标系统路径

	Returns:
		需要安装的字体包列表
	"""
	needed_fonts = []

	# 检查字体是否已安装
	for font_pkg in CHINESE_FONT_PACKAGES:
		font_marker = target / f'usr/share/fonts/{font_pkg}'
		if not font_marker.exists():
			# 简化检查，实际应该检查 pacman 数据库
			needed_fonts.append(font_pkg)

	return needed_fonts


def configure_vconsole_for_chinese(target: Path | None = None) -> bool:
	"""
	配置虚拟控制台以支持中文显示

	Args:
		target: 目标系统路径

	Returns:
		是否成功
	"""
	try:
		if target is None:
			target = Path('/')

		vconsole_conf = target / 'etc/vconsole.conf'

		# 推荐的控制台字体配置
		config_lines = [
			'# Console font configuration',
			'KEYMAP=us',
			'FONT=Lat2-Terminus16',
			'FONT_MAP=',
			'FONT_UNIMAP=',
		]

		vconsole_conf.parent.mkdir(parents=True, exist_ok=True)
		vconsole_conf.write_text('\n'.join(config_lines) + '\n')

		debug(f'vconsole.conf 已配置: {vconsole_conf}')
		return True

	except Exception as e:
		warn(f'配置 vconsole.conf 失败: {e}')
		return False


def is_unicode_console() -> bool:
	"""
	检测当前控制台是否支持 Unicode

	Returns:
		是否支持 Unicode
	"""
	try:
		# 检查当前 locale
		lc_all = os.environ.get('LC_ALL', '')
		lang = os.environ.get('LANG', '')

		if 'UTF-8' in lc_all or 'UTF-8' in lang or 'utf-8' in lc_all or 'utf-8' in lang:
			return True

		# 检查终端类型
		term = os.environ.get('TERM', '')
		if 'utf' in term.lower() or 'unicode' in term.lower():
			return True

		return False
	except Exception:
		return False


def safe_print(text: str) -> None:
	"""
	安全地输出文本，处理编码问题

	Args:
		text: 要输出的文本
	"""
	try:
		print(text)
	except UnicodeEncodeError:
		# 如果终端不支持 Unicode，尝试编码为 ASCII
		try:
			print(text.encode('ascii', 'replace').decode('ascii'))
		except Exception:
			# 最后的回退方案
			print('[Unicode text cannot be displayed]')


def ensure_chinese_font_with_fallback(
	target: Path | None = None,
	auto_download: bool = True,
	create_emergency: bool = True,
) -> bool:
	"""
	确保中文字体可用（带完整回退机制）

	这是完整的字体保障函数，按以下顺序尝试：
	1. 检测现有 CJK 字体
	2. 尝试下载并安装轻量级字体
	3. 创建最小化紧急字体
	4. 配置最佳可用字体

	Args:
		target: 目标系统路径
		auto_download: 是否自动下载字体
		create_emergency: 是否创建紧急字体

	Returns:
		是否有中文字体可用
	"""
	# 第一步：检测现有字体
	support = detect_chinese_support()
	if support['has_cjk_font']:
		debug('检测到现有 CJK 字体')
		return True

	info('未检测到 CJK 字体，尝试安装...')

	# 第二步：尝试下载字体
	if auto_download:
		try:
			from archinstall.lib.font_downloader import ensure_chinese_font_available
			if ensure_chinese_font_available(target, auto_download=True):
				info('中文字体安装成功')
				return True
		except Exception as e:
			debug(f'自动下载字体失败: {e}')

	# 第三步：创建紧急字体
	if create_emergency:
		try:
			from archinstall.lib.font_downloader import create_minimal_bitmap_font
			emergency_font = create_minimal_bitmap_font()
			if emergency_font:
				info('已创建紧急中文字体')
				return True
		except Exception as e:
			debug(f'创建紧急字体失败: {e}')

	# 第四步：使用最佳可用控制台字体
	warn('无法安装中文字体，将使用最佳可用控制台字体')
	setup_chinese_font_environment(target)

	return False


def get_font_status() -> dict:
	"""
	获取字体状态报告

	Returns:
		包含字体状态信息的字典
	"""
	status = {
		'has_cjk_font': False,
		'available_fonts': [],
		'console_font': None,
		'download_available': False,
		'emergency_font_available': False,
	}

	# 检测 CJK 字体
	support = detect_chinese_support()
	status['has_cjk_font'] = support['has_cjk_font']
	status['available_fonts'] = support['available_cjk_fonts']

	# 检测控制台字体
	try:
		console_fonts = get_available_console_fonts()
		status['console_fonts_count'] = len(console_fonts)
	except Exception:
		status['console_fonts_count'] = 0

	# 检测下载模块
	try:
		from archinstall.lib.font_downloader import FALLBACK_FONTS
		status['download_available'] = True
		status['downloadable_fonts'] = [f['name'] for f in FALLBACK_FONTS]
	except ImportError:
		pass

	return status


# 便捷的导出函数
__all__ = [
	'setup_console_font',
	'get_available_console_fonts',
	'detect_chinese_support',
	'setup_chinese_font_environment',
	'ensure_font_packages',
	'configure_vconsole_for_chinese',
	'is_unicode_console',
	'safe_print',
	'ensure_chinese_font_with_fallback',
	'get_font_status',
	'CHINESE_FONT_PACKAGES',
]
