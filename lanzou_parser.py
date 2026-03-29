import requests
import re
from datetime import datetime


def parse_lanzou_url(target_url, password=None):
    """
    解析蓝奏云分享链接，获取直链
    
    Args:
        target_url: 蓝奏云分享链接
        password: 分享密码（如果有）
    
    Returns:
        tuple: (直链URL, 日志列表, 文件名)
    """
    logs = []
    
    def add_log(message, type='info'):
        logs.append({
            'time': datetime.now().strftime('%H:%M:%S'),
            'message': message,
            'type': type
        })
        print(f"[{type.upper()}] {message}")

    add_log('开始解析蓝奏云链接')
    add_log(f'目标URL: {target_url}')

    try:
        # 1. 获取初始页面内容
        add_log('步骤1: 获取初始页面')
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Referer": "https://www.lanzou.com/"
        }
        page1_response = requests.get(target_url, headers=headers)
        
        if not page1_response.ok:
            raise Exception(f'初始页面请求失败: {page1_response.status_code}')

        page1_html = page1_response.text
        add_log('初始页面获取成功', 'success')
        add_log(f'初始页面内容（前 2000 字符）: {page1_html[:2000]}', 'info')

        # 提取文件ID和sign参数
        add_log('步骤2: 提取必要参数')
        file_id_match = re.search(r'file=(\d+)', target_url)
        if not file_id_match:
            file_id_match = re.search(r'file=(\d+)', page1_html)
        if not file_id_match:
            # 尝试从iframe的src中提取
            iframe_match = re.search(r'<iframe.*?src="([^"]+)".*?>', page1_html)
            if iframe_match:
                iframe_src = iframe_match.group(1)
                add_log(f'从iframe提取到src: {iframe_src}', 'info')
                file_id_match = re.search(r'file=(\d+)', iframe_src)
        if not file_id_match:
            # 尝试从JavaScript变量中提取
            js_match = re.search(r'var fid = (\d+);', page1_html)
            if js_match:
                file_id = js_match.group(1)
                add_log(f'从JavaScript变量提取到文件ID: {file_id}', 'success')
            else:
                # 尝试从URL路径中提取
                path_match = re.search(r'/([a-zA-Z0-9]+)$', target_url)
                if path_match:
                    add_log(f'从URL路径提取到: {path_match.group(1)}', 'info')
                raise Exception('无法提取文件ID')
        else:
            file_id = file_id_match.group(1)
            add_log(f'提取到文件ID: {file_id}', 'success')

        # 提取sign参数
        add_log('步骤2.1: 提取sign参数')
        # 从JavaScript代码中提取所有可能的sign参数
        sign_matches = re.findall(r"sign['\"\s]*[:=]\s*['\"]([^'\"]+)['\"]", page1_html)
        if not sign_matches:
            # 显示更多页面内容以便调试
            add_log(f'页面完整内容: {page1_html}', 'info')
            raise Exception('无法提取sign参数，请查看页面内容')
        
        # 过滤掉无效的sign参数
        valid_signs = [s for s in sign_matches if s and s != '<1>' and len(s) > 10]
        if not valid_signs:
            raise Exception('没有找到有效的sign参数')
        
        # 显示所有提取到的sign参数
        for i, s in enumerate(sign_matches):
            add_log(f'提取到sign参数 {i+1}: {s}', 'info')
        
        # 使用第二个有效的sign参数（如果有）
        sign_index = 1 if len(valid_signs) > 1 else 0
        sign = valid_signs[sign_index]
        add_log(f'使用sign参数: {sign}', 'success')

        # 2. 发送POST请求处理密码验证
        add_log('步骤3: 发送密码验证请求')
        # 使用与抓包一致的URL
        ajax_url = f"https://wwbbs.lanzouq.com/ajaxm.php?file={file_id}"
        post_data = {
            "action": "downprocess",
            "sign": sign,
            "kd": "1"
        }
        if password:
            post_data["p"] = password
            add_log(f'使用密码: {password}', 'info')

        # 使用简化的请求头
        post_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": target_url,
            "X-Requested-With": "XMLHttpRequest"
        }
        
        # 手动构建请求数据字符串
        import urllib.parse
        post_data_str = urllib.parse.urlencode(post_data)
        
        add_log(f'POST请求URL: {ajax_url}', 'info')
        add_log(f'POST请求数据: {post_data_str}', 'info')
        
        try:
            # 尝试使用不同的请求方式
            ajax_response = requests.post(ajax_url, data=post_data_str, headers=post_headers, allow_redirects=True)
            add_log(f'请求状态码: {ajax_response.status_code}', 'info')
            add_log(f'响应头: {dict(ajax_response.headers)}', 'info')
            
            ajax_content = ajax_response.text
            add_log(f'AJAX响应: {ajax_content}', 'info')
        except Exception as e:
            add_log(f'请求异常: {str(e)}', 'error')
            raise

        # 3. 解析JSON响应
        add_log('步骤4: 解析JSON响应')
        import json
        try:
            response_data = json.loads(ajax_content)
            add_log(f'解析JSON成功: {response_data}', 'success')
            
            if response_data.get('zt') != 1:
                raise Exception(f'请求失败: {response_data.get("inf", "未知错误")}')
            
            # 构建最终直链
            dom = response_data.get('dom')
            url = response_data.get('url')
            if not dom or not url:
                raise Exception('无法从响应中提取链接信息')
            
            final_url = f"{dom}/file/{url}"
            add_log(f'构建最终直链: {final_url}', 'success')
            add_log(f'文件名: {response_data.get("inf", "未知")}', 'info')
            add_log('✅ 解析完成！', 'success')

            # 确保文件名有效
            filename = response_data.get('inf', '未知')
            # 清理文件名，移除无效字符
            filename = re.sub(r'[^\w\d\u4e00-\u9fa5\.\-]', '_', filename)
            if not filename or filename == '.':
                filename = 'download'
            
            return final_url, logs, filename
        except json.JSONDecodeError as e:
            add_log(f'解析JSON失败: {str(e)}', 'error')
            raise

    except Exception as error:
        add_log(f'解析失败: {str(error)}', 'error')
        raise


if __name__ == "__main__":
    share_link = "https://wwbbs.lanzouq.com/ip0eC3l5bh0d"
    password = "1234"  # 根据抓包信息设置密码
    try:
        final_link, logs, filename = parse_lanzou_url(share_link, password)
        print(f"\n最终的蓝奏云直链: {final_link}")
        print(f"文件名: {filename}")
        
        # 询问是否下载
        download_choice = input("是否下载文件？(y/n): ")
        if download_choice.lower() == 'y':
            # 导入下载模块
            import downloader
            import os
            default_path = os.path.join(os.getcwd(), filename)
            save_path = input(f"请输入保存路径（回车使用默认路径: {default_path}）: ")
            if not save_path:
                save_path = default_path
            downloader.download_file(final_link, save_path, filename=filename)
    except Exception as e:
        print(f"解析失败: {str(e)}")
