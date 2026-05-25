# -*- coding: utf-8 -*-
import base64
import zipfile
from tflink import TFLinkClient
from datetime import datetime
import io







class WordTemplateFiller:
    def __init__(self, template_base64):
        """
        初始化模板填充器
        :param template_base64: Word模板的base64编码字符串
        """
        self.template_bytes = base64.b64decode(template_base64)

    def _extract_docx_xml(self, docx_bytes):
        """提取Word文档的XML内容"""
        with zipfile.ZipFile(io.BytesIO(docx_bytes), 'r') as docx_zip:
            # 读取文档主体内容
            document_xml = docx_zip.read('word/document.xml').decode('utf-8')

            # 读取其他相关文件
            files_content = {}
            for file_name in docx_zip.namelist():
                if file_name.startswith('word/') and file_name.endswith('.xml'):
                    try:
                        files_content[file_name] = docx_zip.read(file_name).decode('utf-8')
                    except UnicodeDecodeError:
                        continue

            return document_xml, files_content

    def _replace_placeholders(self, xml_content, data_dict):
        """
        替换XML中的占位符
        支持多种占位符格式：{{key}}, [[key]], ${key}
        """
        # 定义占位符模式
        import re

        # 检查是否包含模板占位符，如果没有则创建占位符
        if not any(pattern in xml_content for pattern in ['{{', '[[', '${']):
            # 这是原始模板，需要根据数据自动插入占位符
            xml_content = self._auto_insert_placeholders(xml_content, data_dict)

        # 替换各种格式的占位符
        patterns = [
            (r'\{\{(.*?)\}\}', '{{', '}}'),
            (r'\[\[(.*?)\]\]', '[[', ']]'),
            (r'\$\{(.*?)\}', '${', '}')
        ]

        for pattern, start_delim, end_delim in patterns:
            matches = re.findall(pattern, xml_content)
            for match in matches:
                key = match.strip()
                value = str(data_dict.get(key, f'[{key}]'))  # 默认值
                placeholder = f"{start_delim}{match}{end_delim}"
                xml_content = xml_content.replace(placeholder, value)

        return xml_content

    def _auto_insert_placeholders(self, xml_content, data_dict):
        """
        自动在原始模板中插入占位符
        根据模板结构智能识别可替换的位置
        """
        # 查找常见的字段位置并插入占位符
        replacements = {
            # 在工程名称位置插入占位符
            '施工单位': '{{project_name}}',
            '施工单位': '{{recipient}}',  # 致：施工单位
            '混凝土不达标': '{{subject}}',  # 事由
            '2605190001': '{{notice_no}}',  # 编号
            '2026-05-19': '{{sign_date}}',  # 日期
            # 如果内容区域是固定文本，替换成占位符
            '2号楼混凝土不达标，经检测混凝土强度未达到设计强度等级': '{{content}}'
        }

        for old_text, new_placeholder in replacements.items():
            if old_text in xml_content:
                xml_content = xml_content.replace(old_text, new_placeholder)

        return xml_content

    def fill_template(self, json_data):
        """
        填充模板并返回新的Word文档
        :param json_data: 包含通知单数据的JSON
        :return: 新的Word文档字节流
        """
        # 解析原始模板
        original_xml, other_files = self._extract_docx_xml(self.template_bytes)

        # 提取通知数据
        notification = json_data['structured_output']['structured_output']['notification']

        # 创建数据映射
        data_map = {
            'project_name': notification.get('project_name', '施工单位'),
            'notice_no': notification.get('notice_no', '2605190001'),
            'recipient': notification.get('recipient', '赣县施工单位'),
            'subject': notification.get('subject', '混凝土不达标'),
            'content': notification.get('content', '内容待填写'),
            'sign_date': notification.get('sign_date', datetime.now().strftime('%Y-%m-%d'))
        }

        # 替换XML内容
        filled_xml = self._replace_placeholders(original_xml, data_map)

        # 创建新的Word文档
        new_docx_buffer = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(self.template_bytes), 'r') as original_zip:
            with zipfile.ZipFile(new_docx_buffer, 'w', zipfile.ZIP_DEFLATED) as new_zip:
                for file_name in original_zip.namelist():
                    if file_name == 'word/document.xml':
                        # 写入填充后的XML
                        new_zip.writestr(file_name, filled_xml.encode('utf-8'))
                    elif file_name in other_files:
                        # 更新其他XML文件（如果有需要）
                        updated_content = self._replace_placeholders(other_files[file_name], data_map)
                        new_zip.writestr(file_name, updated_content.encode('utf-8'))
                    else:
                        # 其他文件直接复制
                        new_zip.writestr(file_name, original_zip.read(file_name))

        new_docx_buffer.seek(0)
        return new_docx_buffer.getvalue()

    def convert_to_base64(self, docx_bytes):
        """将Word文档转换为base64"""
        return base64.b64encode(docx_bytes).decode('utf-8')




# 调用的主函数
def main_with_base64(json):
    """
    主函数 - Base64方案
    """
    # 转换为base64
    template_base64 = "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"
    # 创建填充器
    filler = WordTemplateFiller(template_base64)
    # 填充模板
    filled_docx_bytes = filler.fill_template(json)
    # 保存结果
    output_filename = f"filled_notification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    with open(output_filename, 'wb') as f:
        f.write(filled_docx_bytes)
    client = TFLinkClient()
    res = client.upload(output_filename)
    return res.download_link


