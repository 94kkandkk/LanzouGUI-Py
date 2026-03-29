import requests
import re
import time
from datetime import datetime


def download_file(url, save_path=None, headers=None, filename=None):
    """
    下载文件，支持处理验证页面
    
    Args:
        url: 要下载的文件URL
        save_path: 保存路径，如果为None则使用文件名
        headers: 请求头，如果为None则使用默认头
        filename: 文件名，如果为None则自动提取
    
    Returns:
        str: 保存的文件路径
    """
    if headers is None:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
    
    session = requests.Session()
    session.headers.update(headers)
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 开始下载: {url}")
    
    # 第一次请求
    response = session.get(url, allow_redirects=True)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 初始响应状态码: {response.status_code}")
    
    # 检查是否需要验证
    if "验证并下载" in response.text:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 检测到需要验证")
        
        # 提取验证所需参数
        file_match = re.search(r"'file':'([^']+)',", response.text)
        sign_match = re.search(r"'sign':'([^']+)',", response.text)
        
        if file_match and sign_match:
            file_param = file_match.group(1)
            sign_param = sign_match.group(1)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 提取到验证参数: file={file_param}, sign={sign_param}")
            
            # 发送验证请求
            verify_url = response.url.split('/file/')[0] + "/ajax.php"
            verify_data = {
                'file': file_param,
                'el': '1',
                'sign': sign_param
            }
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 发送验证请求: {verify_url}")
            verify_response = session.post(verify_url, data=verify_data)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 验证响应状态码: {verify_response.status_code}")
            
            try:
                verify_data = verify_response.json()
                if verify_data.get('zt') == '1' and verify_data.get('url'):
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 验证成功，获取到真实下载链接")
                    download_url = verify_data['url']
                    # 再次请求真实下载链接
                    response = session.get(download_url, allow_redirects=True)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 真实下载链接响应状态码: {response.status_code}")
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 验证失败: {verify_data}")
                    raise Exception("验证失败")
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 验证过程出错: {str(e)}")
                raise
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 无法提取验证参数")
            raise Exception("无法提取验证参数")
    
    # 如果没有提供文件名，自动提取
    if filename is None:
        # 检查响应是否为文件
        if 'Content-Disposition' in response.headers:
            # 从响应头获取文件名
            content_disposition = response.headers['Content-Disposition']
            filename_match = re.search(r'filename="?([^"]+)"?', content_disposition)
            if filename_match:
                filename = filename_match.group(1)
            else:
                # 尝试从URL参数中提取文件名
                import urllib.parse
                parsed_url = urllib.parse.urlparse(url)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                # 检查是否有inf参数（通常包含文件名）
                if 'inf' in query_params:
                    filename = query_params['inf'][0]
                else:
                    # 从URL路径提取文件名
                    filename = parsed_url.path.split('/')[-1] or 'download'
        else:
            # 尝试从URL参数中提取文件名
            import urllib.parse
            parsed_url = urllib.parse.urlparse(url)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            # 检查是否有inf参数（通常包含文件名）
            if 'inf' in query_params:
                filename = query_params['inf'][0]
            else:
                # 从URL路径提取文件名
                filename = parsed_url.path.split('/')[-1] or 'download'
        
        # 确保文件名有扩展名
        if '.' not in filename:
            # 尝试从响应头获取文件类型
            if 'Content-Type' in response.headers:
                content_type = response.headers['Content-Type']
                # 根据Content-Type添加扩展名
                ext_map = {
                    'application/exe': '.exe',
                    'application/x-msdownload': '.exe',
                    'application/pdf': '.pdf',
                    'image/jpeg': '.jpg',
                    'image/png': '.png',
                    'image/gif': '.gif',
                    'text/plain': '.txt',
                    'text/html': '.html',
                    'application/zip': '.zip',
                    'application/rar': '.rar',
                    'application/7z': '.7z',
                    'audio/mp3': '.mp3',
                    'video/mp4': '.mp4'
                }
                for mime, ext in ext_map.items():
                    if mime in content_type:
                        filename += ext
                        break
            else:
                # 默认添加.exe扩展名
                filename += '.exe'
    
    # 清理文件名，移除可能的乱码或无效字符
    import re
    # 移除非ASCII字符和无效文件名字符
    filename = re.sub(r'[^\w\d\u4e00-\u9fa5\.\-]', '_', filename)
    # 确保文件名不为空
    if not filename or filename == '.':
        filename = 'download.exe'
    
    # 如果没有指定保存路径，使用当前目录
    if save_path is None:
        import os
        save_path = os.path.join(os.getcwd(), filename)
    
    # 确保保存目录存在
    import os
    save_dir = os.path.dirname(save_path)
    if save_dir and not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # 下载文件
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 开始保存文件: {save_path}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 响应内容类型: {response.headers.get('Content-Type', 'unknown')}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 响应编码: {response.encoding}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 响应头: {dict(response.headers)}")
    
    # 检查是否为文本文件还是二进制文件
    content_type = response.headers.get('Content-Type', '')
    # 先根据内容类型判断
    is_text = 'text' in content_type or 'html' in content_type
    
    # 再根据文件扩展名辅助判断
    import os
    file_ext = os.path.splitext(filename)[1].lower()
    text_extensions = ['.txt', '.log', '.csv', '.json', '.xml', '.html', '.css', '.js', '.py', '.md']
    if file_ext in text_extensions:
        is_text = True
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 文件扩展名: {file_ext}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 是否为文本文件: {is_text}")
    
    # 检查响应内容的前几个字节，判断是否为文本
    content_sample = response.content[:100]
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 响应内容前100字节: {content_sample}")
    
    # 尝试检测是否为有效的文本
    try:
        content_sample.decode('utf-8')
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 内容可以用UTF-8解码")
    except UnicodeDecodeError:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 内容无法用UTF-8解码，可能是二进制")
    
    # 检查是否为压缩内容
    content_encoding = response.headers.get('Content-Encoding', '')
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 内容编码: {content_encoding}")
    is_compressed = 'br' in content_encoding or 'gzip' in content_encoding or 'deflate' in content_encoding
    
    # 根据内容类型选择打开模式
    if is_text:
        # 文本文件，使用文本模式
        encoding = response.encoding or 'utf-8'
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 使用文本模式打开，编码: {encoding}")
        # 先尝试用指定编码解码
        try:
            # 尝试手动处理压缩内容
            content = response.content
            if is_compressed:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 尝试解压缩内容")
                try:
                    import brotli
                    content = brotli.decompress(content)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Brotli解压缩成功")
                except ImportError:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 缺少brotli库，无法解压缩")
                except Exception as e:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 解压缩失败: {str(e)}")
            
            # 解码为文本
            text_content = content.decode(encoding)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 响应文本长度: {len(text_content)}")
            
            # 检查文本内容是否有效
            if text_content:
                with open(save_path, 'w', encoding=encoding) as f:
                    f.write(text_content)
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 响应文本为空，尝试使用二进制模式")
                with open(save_path, 'wb') as f:
                    f.write(response.content)
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 文本模式写入失败: {str(e)}")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 尝试使用二进制模式")
            with open(save_path, 'wb') as f:
                f.write(response.content)
    else:
        # 二进制文件，使用二进制模式
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 使用二进制模式打开")
        with open(save_path, 'wb') as f:
            f.write(response.content)
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 下载完成: {save_path}")
    return save_path


def main():
    """
    主函数，支持命令行输入直链进行下载
    """
    import sys
    
    if len(sys.argv) > 1:
        # 从命令行参数获取URL
        url = sys.argv[1]
        save_path = sys.argv[2] if len(sys.argv) > 2 else None
    else:
        # 交互式输入
        url = input("请输入蓝奏云直链: ")
        save_path = input("请输入保存路径（回车使用默认路径）: ")
        if not save_path:
            save_path = None
    
    try:
        saved_path = download_file(url, save_path)
        print(f"\n✅ 下载成功！文件保存至: {saved_path}")
    except Exception as e:
        print(f"❌ 下载失败: {str(e)}")


if __name__ == "__main__":
    main()
