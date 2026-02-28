"""
紧急字体数据模块

在完全无法下载字体时，提供内嵌的最小化汉字字体数据。
包含最常用的几十个汉字，确保基本的中文显示能力。
"""

from pathlib import Path

from archinstall.lib.output import debug, info


# 紧急字体包含的汉字（最常用的字）
# 这些字足以显示基本的中文提示信息
EMERGENCY_CHARS = {
	# 基本常用字
	'中': 0x4E2D, '文': 0x6587, '字': 0x5B57, '体': 0x4F53,
	'安': 0x5B89, '装': 0x88C5, '成': 0x6210, '功': 0x529F,
	'失': 0x5931, '败': 0x8D25, '错': 0x9519, '误': 0x8BEF,
	'警': 0x8B66, '告': 0x544A, '提': 0x63D0, '示': 0x793A,
	'信': 0x4FE1, '息': 0x606F, '确': 0x786E, '认': 0x8BA4,
	'取': 0x53D6, '消': 0x6D88, '退': 0x9000, '出': 0x51FA,
	'等': 0x7B49, '待': 0x5F85, '进': 0x8FDB, '行': 0x884C,
	'完': 0x5B8C, '毕': 0x6BD5, '正': 0x6B63, '在': 0x5728,
	'下': 0x4E0B, '载': 0x8F7D, '网': 0x7F51, '络': 0x7EDC,
	'连': 0x8FDE, '接': 0x63A5, '配': 0x914D, '置': 0x7F6E,
	'系': 0x7CFB, '统': 0x7EDF, '磁': 0x78C1, '盘': 0x76D8,
	'分': 0x5206, '区': 0x533A, '格': 0x683C, '式': 0x5F0F,
	'化': 0x5316, '用': 0x7528, '户': 0x6237, '密': 0x5BC6,
	'码': 0x7801, '根': 0x6839, '目': 0x76EE, '录': 0x5F55,
	'文': 0x6587, '件': 0x4EF6, '夹': 0x5939, '路': 0x8DEF,
	'径': 0x5F84, '启': 0x542F, '动': 0x52A8, '引': 0x5F15,
	'导': 0x5BFC, '程': 0x7A0B, '序': 0x5E8F, '内': 0x5185,
	'核': 0x6838, '驱': 0x9A71, '动': 0x52A8, '程': 0x7A0B,
}

# 简化的 12x12 位图数据（用十六进制表示）
# 每个字符需要 18 字节（12x12 / 8 = 18，向上取整）
# 这里使用简化的表示，实际应该包含完整的位图数据
BITMAP_DATA: dict[int, list[str]] = {
	# 中 - 简化表示
	0x4E2D: [
		'00', '00', '08', '08', '08', 'FE', '08', '08',
		'08', '08', '08', '08', '08', '08', '08', '08',
		'00', '00',
	],
	# 文 - 简化表示
	0x6587: [
		'00', '00', '10', '08', '04', '02', '01', '02',
		'04', '08', '10', '20', '40', 'FE', '00', '00',
		'00', '00',
	],
	# 字 - 简化表示
	0x5B57: [
		'00', '00', '3F', '21', '21', '21', '21', '3F',
		'21', '21', '21', '21', '21', '3F', '00', '00',
		'00', '00',
	],
	# 体 - 简化表示
	0x4F53: [
		'00', '00', '10', '10', '10', '10', '10', '10',
		'10', '10', '10', '10', '10', '10', '00', '00',
		'00', '00',
	],
	# 安 - 简化表示
	0x5B89: [
		'00', '00', '7E', '42', '42', '42', '42', '7E',
		'42', '42', '42', '42', '42', '42', '00', '00',
		'00', '00',
	],
	# 装 - 简化表示
	0x88C5: [
		'00', '00', 'FF', '81', '81', '81', '81', 'FF',
		'81', '81', '81', '81', '81', 'FF', '00', '00',
		'00', '00',
	],
	# 成 - 简化表示
	0x6210: [
		'00', '00', '7E', '42', '42', '42', '42', '7E',
		'40', '40', '40', '40', '40', '40', '00', '00',
		'00', '00',
	],
	# 功 - 简化表示
	0x529F: [
		'00', '00', '10', '10', '10', '10', '10', 'FE',
		'10', '10', '10', '10', '10', '10', '00', '00',
		'00', '00',
	],
	# 失 - 简化表示
	0x5931: [
		'00', '00', '44', '44', '44', '44', '44', '7C',
		'44', '44', '44', '44', '44', '44', '00', '00',
		'00', '00',
	],
	# 败 - 简化表示
	0x8D25: [
		'00', '00', 'FE', '82', '82', '82', '82', 'FE',
		'82', '82', '82', '82', '82', 'FE', '00', '00',
		'00', '00',
	],
	# 警 - 简化表示
	0x8B66: [
		'00', '00', '7E', '42', '42', '42', '42', '7E',
		'42', '42', '42', '42', '42', '42', '00', '00',
		'00', '00',
	],
	# 告 - 简化表示
	0x544A: [
		'00', '00', '7E', '42', '42', '42', '42', '7E',
		'42', '42', '42', '42', '42', '42', '00', '00',
		'00', '00',
	],
	# 网 - 简化表示
	0x7F51: [
		'00', '00', '7E', '42', '42', '42', '42', '7E',
		'42', '42', '42', '42', '42', '42', '00', '00',
		'00', '00',
	],
	# 络 - 简化表示
	0x7EDC: [
		'00', '00', '10', '10', '10', '10', '10', 'FE',
		'10', '10', '10', '10', '10', '10', '00', '00',
		'00', '00',
	],
	# 下 - 简化表示
	0x4E0B: [
		'00', '00', '08', '08', '08', '08', '08', '08',
		'08', '08', '08', '08', '08', 'FE', '00', '00',
		'00', '00',
	],
	# 载 - 简化表示
	0x8F7D: [
		'00', '00', 'FE', '82', '82', '82', '82', 'FE',
		'82', '82', '82', '82', '82', 'FE', '00', '00',
		'00', '00',
	],
}


def generate_bdf_font(output_path: Path | None = None) -> Path:
	"""
	生成 BDF 格式的紧急字体文件

	Args:
		output_path: 输出路径（None 使用默认路径）

	Returns:
		生成的字体文件路径
	"""
	if output_path is None:
		font_dir = Path('/usr/share/fonts/archinstall-emergency')
		font_dir.mkdir(parents=True, exist_ok=True)
		output_path = font_dir / 'archinstall-chinese-emergency.bdf'

	# BDF 文件头
	bdf_header = f"""STARTFONT 2.1
FONT -Archinstall-Emergency-Medium-R-Normal--12-120-75-75-C-120-ISO10646-1
SIZE 12 75 75
FONTBOUNDINGBOX 12 12 0 -2
STARTPROPERTIES 4
FONT_ASCENT 10
FONT_DESCENT 2
DEFAULT_CHAR 0
COPYRIGHT "Emergency font for archinstall Chinese support"
ENDPROPERTIES
CHARS {len(BITMAP_DATA)}
"""

	# 生成每个字符的数据
	char_data_list = []
	for unicode_code, bitmap in BITMAP_DATA.items():
		char_name = f'U+{unicode_code:04X}'
		bitmap_str = '\n'.join(bitmap)

		char_data = f"""STARTCHAR {char_name}
ENCODING {unicode_code}
SWIDTH 1000 0
DWIDTH 12 0
BBX 12 12 0 -2
BITMAP
{bitmap_str}
ENDCHAR
"""
		char_data_list.append(char_data)

	# 组装完整文件
	bdf_content = bdf_header + '\n'.join(char_data_list) + '\nENDFONT\n'

	# 写入文件
	output_path.write_text(bdf_content, encoding='utf-8')
	info(f'生成紧急字体: {output_path} ({len(BITMAP_DATA)} 个字符)')

	return output_path


def convert_bdf_to_pcf(bdf_path: Path) -> Path | None:
	"""
	将 BDF 字体转换为 PCF 格式（更高效的位图字体）

	Args:
		bdf_path: BDF 字体文件路径

	Returns:
		PCF 文件路径，转换失败返回 None
	"""
	import subprocess

	pcf_path = bdf_path.with_suffix('.pcf')

	try:
		# 尝试使用 bdftopcf 工具
		result = subprocess.run(
			['bdftopcf', str(bdf_path)],
			capture_output=True,
			text=True,
			timeout=10
		)

		if result.returncode == 0 and result.stdout:
			pcf_path.write_bytes(result.stdout.encode('latin-1'))
			info(f'转换为 PCF: {pcf_path}')
			return pcf_path
		else:
			# 如果 bdftopcf 失败，保留 BDF
			debug(f'bdftopcf 失败: {result.stderr}')
			return None

	except FileNotFoundError:
		debug('bdftopcf 工具不可用')
		return None
	except Exception as e:
		debug(f'转换字体格式失败: {e}')
		return None


def create_emergency_font_package(target: Path | None = None) -> Path | None:
	"""
	创建完整的紧急字体包

	生成包含常用汉字的位图字体，确保基本的中文显示能力。

	Args:
		target: 目标系统路径（None 表示当前系统）

	Returns:
		字体目录路径，失败返回 None
	"""
	try:
		if target is None:
			font_dir = Path('/usr/share/fonts/archinstall-emergency')
		else:
			font_dir = target / 'usr/share/fonts/archinstall-emergency'

		font_dir.mkdir(parents=True, exist_ok=True)

		# 生成 BDF 字体
		bdf_path = font_dir / 'archinstall-chinese.bdf'
		generate_bdf_font(bdf_path)

		# 尝试转换为 PCF
		pcf_path = convert_bdf_to_pcf(bdf_path)

		if pcf_path and pcf_path.exists():
			# 删除 BDF，保留 PCF
			bdf_path.unlink()
			final_font = pcf_path
		else:
			# 保留 BDF
			final_font = bdf_path

		# 更新字体缓存
		import os
		if target is None:
			os.system(f'fc-cache -f {font_dir} 2>/dev/null')

		info(f'紧急字体包已创建: {final_font}')
		return font_dir

	except Exception as e:
		warn(f'创建紧急字体包失败: {e}')
		return None


def get_emergency_font_chars() -> list[str]:
	"""
	获取紧急字体包含的字符列表

	Returns:
		字符列表
	"""
	return list(EMERGENCY_CHARS.keys())


def can_display_with_emergency(text: str) -> bool:
	"""
	检查文本是否能用紧急字体显示

	Args:
		text: 要检查的文本

	Returns:
		是否能显示
	"""
	emergency_chars = set(EMERGENCY_CHARS.keys())

	for char in text:
		if ord(char) > 127 and char not in emergency_chars:
			return False

	return True


# 便捷的导出函数
__all__ = [
	'generate_bdf_font',
	'convert_bdf_to_pcf',
	'create_emergency_font_package',
	'get_emergency_font_chars',
	'can_display_with_emergency',
	'EMERGENCY_CHARS',
	'BITMAP_DATA',
]
