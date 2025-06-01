微信阅读导出的epub中，注脚为图片格式，且内容藏在图片alt属性中，不兼容其他阅读工具。本工具将注脚修改为内链样式，并将注脚中参考资料移动至章节末尾，此外还在元数据中添加了封面路径，便于某些应用识别。

Transfer reference notes from images to internal-links to improve compatibility, for epub files exported from WeRead.

这是一个Python程序，在DeepDeek协助下完成。使用时在进入文件目录，使用命令行工具输入<code>python weread-epub-reference-fix.py</code>，再输入要转换的epub文件路径即可。
