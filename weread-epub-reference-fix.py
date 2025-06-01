import os
import shutil
import re
from bs4 import BeautifulSoup

def convert_footnotes_to_internal_links(epub_path):
    """
    将EPUB中的参考文献注脚图片转换为内链格式
    每个章节末尾添加独立的参考文献列表
    使用外部样式表并优化角标样式
    
    参数:
        epub_path: EPUB文件的路径（字符串）
        
    返回:
        转换后的新EPUB文件路径
    """
    # 创建临时目录
    temp_dir = "temp_epub"
    shutil.unpack_archive(epub_path, temp_dir, 'zip')
    
    print("开始处理EPUB文件内容...")




    # 查找content.opf文件
    oebps_dir = os.path.join(temp_dir, 'OEBPS')
    os.makedirs(oebps_dir, exist_ok=True)
    opf_path = os.path.join(oebps_dir, 'content.opf')  
    
    print(f"找到content.opf文件: {opf_path}")
    
    try:
        # 读取OPF文件内容
        with open(opf_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析XML
        soup = BeautifulSoup(content, 'html.parser')
        
        # 检查是否已存在封面声明
        existing_cover = soup.find('meta', {'name': 'cover'})
        if existing_cover:
            print("封面声明已存在，跳过添加")
            return
        
        # 查找metadata标签
        metadata = soup.find('metadata')
        if not metadata:
            print("警告: 未找到<metadata>标签")
            return
        
        # 创建新的meta标签
        cover_meta = soup.new_tag('meta', attrs={'name': 'cover', 'content': 'Cover1'})
        
        # 添加到metadata的最下方
        metadata.append(cover_meta)
        
        # 保存修改
        with open(opf_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        
        print("成功添加封面元数据声明")
    
    except Exception as e:
        print(f"修改content.opf时出错: {str(e)}")



    #   # 创建或更新外部样式表
    styles_dir = os.path.join(temp_dir, 'OEBPS', 'Styles')
    os.makedirs(styles_dir, exist_ok=True)
    css_path = os.path.join(styles_dir, 'stylesheets.css')  
    # 定义参考文献样式
    footnote_styles = """
    /* 正文中的参考文献标记 */
   .footnote-ref {
      vertical-align: super;
      font-size: 75%;
      cursor: pointer;
      transition: all 0.3s ease;
}
    
    .footnote-ref:hover {
        background: #e6f0ff;
        transform: scale(1.1);
    }
    
    /* 参考文献部分样式 */
    .references-section {
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid #eee;
    }
    
    .reference-item {
        padding: 8px 0;
        margin: 8px 0;
        border-bottom: 1px dashed #e0e0e0;
    }
    
    .reference-number {
        color: #3498db;
        margin-right: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
        display: inline-block;
        min-width: 24px;
    }
    
    .reference-number:hover {
        color: #e74c3c;
        transform: scale(1.1);
    }
    
    .reference-content {
        display: inline;
        font-size: 0.9em;
    }
    """
    
    # 追加样式到外部样式表（避免覆盖已有样式）
    if os.path.exists(css_path):
        with open(css_path, 'a', encoding='utf-8') as css_file:
            css_file.write("\n\n/* 参考文献样式 - 由转换工具添加 */\n")
            css_file.write(footnote_styles)
        print(f"已追加样式到外部样式表: {css_path}")
    else:
        with open(css_path, 'w', encoding='utf-8') as css_file:
            css_file.write("/* EPUB全局样式 */\n")
            css_file.write(footnote_styles)
        print(f"已创建外部样式表: {css_path}")
  
    # 处理每个HTML/XHTML文件
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            if file.lower().endswith(('.html', '.xhtml')):
                file_path = os.path.join(root, file)
                print(f"\n处理文件: {file}")
                
                # 获取不带后缀的文件名
                file_base = os.path.splitext(file)[0]
                
                try:
                    # 读取文件内容
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    try:
                        with open(file_path, 'r', encoding='latin-1') as f:
                            content = f.read()
                    except:
                        print(f"  ! 无法读取文件: {file_path}")
                        continue
                
                soup = BeautifulSoup(content, 'html.parser')
                references = []
                modified = False
                
                # 添加外部样式表链接（如果不存在）
                css_link = soup.find('link', {'href': '../Styles/stylesheets.css'})
                if not css_link:
                    # 计算相对路径
                    relative_css_path = os.path.relpath(css_path, os.path.dirname(file_path))
                    relative_css_path = relative_css_path.replace('\\', '/')
                    
                    # 创建link标签
                    link_tag = soup.new_tag('link', rel='stylesheet', type='text/css')
                    link_tag['href'] = relative_css_path
                    
                    if soup.head:
                        soup.head.append(link_tag)
                        print(f"  已添加外部样式表链接")
                    else:
                        # 如果没有head，创建head标签
                        head_tag = soup.new_tag('head')
                        head_tag.append(link_tag)
                        soup.insert(0, head_tag)
                         # 查找所有注脚图片
                footnote_imgs = soup.find_all('img', class_='qqreader-footnote')
                if footnote_imgs:
                    print(f"  找到 {len(footnote_imgs)} 个参考文献注脚图片")
                
                # 处理每个参考文献
                for i, img in enumerate(footnote_imgs):
                    alt_text = img.get('alt', '')
                    ref_id = i + 1  # 本地编号，从1开始
                    
                    if not alt_text:
                        print(f"    ! 图片缺少alt属性: {img}")
                        continue
                    
                    # 存储参考文献信息
                    references.append({
                        'id': ref_id,
                        'alt': alt_text,
                        'element': img
                    })
                    
                    # 创建上标角标
                    sup = soup.new_tag('sup')
                    
                    # 创建返回锚点 (使用不带后缀的文件名)
                    back_anchor = soup.new_tag('a')
                    back_anchor['href'] = f"#ref-{ref_id}"
                    back_anchor['class'] = "footnote-ref"
                    back_anchor['id'] = f"ref-{ref_id}-back-{file_base}"  # 关键修改：使用file_base
                    back_anchor.string = f"[{ref_id}]"  # 显示数字和方括号
                    
                    # 替换原始图片
                    img.insert_before(back_anchor)
                    img.replace_with()
                    
                    print(f"    + 已替换: [{ref_id}] {alt_text[:30]}...")
                    modified = True
                
                if modified:
                    # 在当前文件末尾添加参考文献部分
                    if references:
                        # 创建参考文献部分
                        section = soup.new_tag('div')
                        section['class'] = "references-section"
                        
                        h2 = soup.new_tag('hr')
                        section.append(h2)
                        
                        # 添加参考文献条目
                        for ref in references:
                            item = soup.new_tag('div')
                            item['class'] = "reference-item"
                            item['id'] = f"ref-{ref['id']}"
                            
                            # 创建带链接的编号（点击返回正文）
                            number_link = soup.new_tag('a')
                            number_link['class'] = "reference-number"
                            # 使用不带后缀的文件名
                            number_link['href'] = f"#ref-{ref['id']}-back-{file_base}"  # 关键修改
                            number_link['title'] = "返回正文"
                            number_link.string = f"[{ref['id']}]"
                            
                            # 添加内容
                            content_span = soup.new_tag('span')
                            content_span['class'] = "reference-content"
                            content_span.string = ref['alt']
                            
                            # 将编号链接和内容添加到条目
                            item.append(number_link)
                            item.append(content_span)
                            
                            section.append(item)
                            print(f"    + 添加参考文献 [{ref['id']}]")
                        
                        # 添加到文档末尾
                        if soup.body:
                            soup.body.append(section)
                        print(f"    √ 参考文献部分已添加到文件末尾")
                
                # 保存修改
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(str(soup))
                    print(f"  √ 文件更新完成")
                except Exception as e:
                    print(f"  ! 写入文件时出错: {str(e)}")
    
    # 重新打包EPUB
    print("\n重新打包EPUB文件...")
    base_name = os.path.splitext(os.path.basename(epub_path))[0]
    new_epub_path = os.path.join(
        os.path.dirname(epub_path), 
        f"{base_name}_converted.epub"
    )
    
    try:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(new_epub_path), exist_ok=True)
        
        # 创建ZIP存档
        temp_zip = os.path.join(os.path.dirname(epub_path), base_name + "_temp.zip")
        shutil.make_archive(temp_zip.replace('.zip', ''), 'zip', temp_dir)
        
        # 重命名为EPUB
        shutil.move(temp_zip, new_epub_path)
        
        print(f"  √ 成功创建新EPUB文件: {new_epub_path}")
    except Exception as e:
        print(f"  ! 重新打包EPUB时出错: {str(e)}")
        return None
    
    # 清理临时目录
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
    except:
        pass
    
    return new_epub_path

if __name__ == "__main__":
    print("EPUB参考文献转换工具")
    print("=" * 40)
    input_epub = input("请输入EPUB文件路径: ").strip()
    
    # 处理Windows路径
    if '\\' in input_epub:
        input_epub = input_epub.replace('\\', '/')
    
    if not os.path.exists(input_epub):
        print(f"错误: 文件 '{input_epub}' 不存在")
        exit(1)
    
    if not input_epub.lower().endswith('.epub'):
        print("错误: 请提供.epub文件")
        exit(1)
    
    try:
        print("\n开始转换EPUB文件...")
        output_epub = convert_footnotes_to_internal_links(input_epub)
        if output_epub:
            print("\n" + "=" * 40)
            print(f"转换成功! 新文件已保存为: {output_epub}")
            print("请在EPUB阅读器中打开新文件测试效果")
            print("=" * 40)
        else:
            print("\n转换失败，请检查错误信息")
    except Exception as e:
        print(f"转换过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()