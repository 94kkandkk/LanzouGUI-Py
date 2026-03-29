from playwright.sync_api import sync_playwright
import requests
import time
import os
import threading
from concurrent.futures import ThreadPoolExecutor
import random

class LanzouEdgeAutoLogin:
    """
    ✅ Windows自带Edge浏览器自动登录
    ✅ 所有蓝奏云挂载工具的官方实现方式
    ✅ 后台隐形运行，用户无感知
    """
    def __init__(self):
        self.cookie = None
        self.session = requests.Session()
        self.base_url = "https://pc.woozooo.com"
        self.upload_file_counter = 0
        
        # 尝试从文件加载Cookie
        try:
            with open("lanzou_cookies.txt", "r") as f:
                content = f.read()
                self.cookie = eval(content)
                # 确保cookie是列表格式
                if not isinstance(self.cookie, list):
                    print("⚠️ Cookie格式错误，将使用浏览器登录")
                    self.cookie = None
                else:
                    print("✅ 从文件加载Cookie成功")
        except:
            print("⚠️ 未找到Cookie文件，将使用浏览器登录")

    def simulate_human_slide(self, page, slider_handle, distance):
        """模拟人类滑动行为"""
        try:
            # 获取滑块的位置
            slider_bbox = slider_handle.bounding_box()
            if not slider_bbox:
                print("❌ 无法获取滑块位置")
                return False
            
            # 计算滑动的起点和终点
            start_x = slider_bbox['x'] + slider_bbox['width'] / 2
            start_y = slider_bbox['y'] + slider_bbox['height'] / 2
            end_x = start_x + distance
            end_y = start_y
            
            # 模拟人类滑动的轨迹（包含随机抖动）
            steps = random.randint(30, 40)  # 增加步骤数，使滑动更平滑
            duration = random.uniform(1.0, 1.8)  # 增加滑动时间，更像人类
            
            # 开始滑动
            page.mouse.move(start_x, start_y)
            time.sleep(random.uniform(0.2, 0.4))  # 鼠标悬停一段时间
            page.mouse.down()
            time.sleep(random.uniform(0.15, 0.35))  # 按下后的短暂停顿
            
            # 分段滑动，模拟人类的加速度和减速度
            for i in range(steps):
                # 计算当前步骤的位置
                t = i / steps
                # 使用更复杂的缓动函数模拟人类滑动
                if t < 0.3:
                    # 开始阶段，加速度
                    ease_t = (t / 0.3) ** 2
                elif t < 0.7:
                    # 中间阶段，匀速
                    ease_t = 0.1 + (t - 0.3) * 0.8 / 0.4
                else:
                    # 结束阶段，减速度
                    ease_t = 0.9 - ((t - 0.7) / 0.3) ** 2 * 0.8
                
                current_x = start_x + (end_x - start_x) * ease_t
                # 添加随机抖动，中间阶段抖动较小，开始和结束阶段抖动较大
                if t < 0.1 or t > 0.9:
                    current_y = start_y + random.uniform(-3, 3)
                else:
                    current_y = start_y + random.uniform(-1, 1)
                
                # 移动到当前位置
                page.mouse.move(current_x, current_y)
                # 控制每步的时间间隔
                time.sleep(duration / steps)
            
            # 松开鼠标
            time.sleep(random.uniform(0.15, 0.25))
            page.mouse.up()
            
            print(f"✅ 模拟人类滑动完成，距离: {distance}px, 持续时间: {duration:.2f}s, 步骤数: {steps}")
            return True
        except Exception as e:
            print(f"❌ 模拟滑动失败: {str(e)}")
            return False
    
    def get_cookie_with_edge(self, username=None, password=None):
        """【核心】自动调用Edge浏览器，登录并抓取Cookie"""
        print("🔐 正在启动系统Edge浏览器，自动登录蓝奏云...")

        # 调用 Windows 原生 Edge 浏览器
        with sync_playwright() as p:
            # headless=True = 后台隐形运行（不弹出窗口，和挂载工具一样）
            browser = p.chromium.launch(
                headless=True,  # 无头模式，后台运行
                channel="msedge",
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--window-size=1920,1080",  # 设置窗口大小，确保元素可见
                    "--no-sandbox",  # 避免沙箱限制
                    "--disable-dev-shm-usage"  # 避免内存限制
                ]  # 强制使用系统自带的Edge，绝不使用第三方浏览器
            )
            page = browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0"
            )

            # 访问蓝奏云官方登录页
            page.goto("https://up.woozooo.com/account.php?action=login")
            time.sleep(5)  # 增加等待时间，确保页面完全加载
            
            # 绕过自动化检测
            page.evaluate("() => { Object.defineProperty(navigator, 'webdriver', { get: () => undefined }); }")
            page.evaluate("() => { delete navigator.__proto__.webdriver; }")
            page.evaluate("() => { window.chrome = { runtime: {} }; }")
            page.evaluate("() => { Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en'] }); }")
            page.evaluate("() => { Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] }); }")
            
            # 检查是否需要刷新页面
            try:
                if page.locator('text=哎呀，出错了，点击刷新再来一次').is_visible():
                    print("⚠️ 页面出错，正在刷新...")
                    page.reload()
                    time.sleep(3)
            except:
                print("⚠️ 页面检查失败，继续执行")

            # 输入账号密码
            if username and password:
                print("📝 正在自动输入账号密码...")
                try:
                    # 输入用户名
                    username_input = page.locator("input[name='username']")
                    if username_input.is_visible():
                        # 模拟人类输入（逐字输入）
                        for char in username:
                            username_input.type(char)
                            time.sleep(random.uniform(0.05, 0.15))
                        
                    # 输入密码
                    password_input = page.locator("input[name='password']")
                    if password_input.is_visible():
                        # 模拟人类输入（逐字输入）
                        for char in password:
                            password_input.type(char)
                            time.sleep(random.uniform(0.05, 0.15))
                except Exception as e:
                    print(f"❌ 输入账号密码失败: {str(e)}")
                    browser.close()
                    return None
                
                # 处理滑动验证码
                print("🔍 正在检测滑动验证码...")
                try:
                    # 等待滑动验证码出现
                    time.sleep(3)
                    
                    # 查找滑块元素（支持多种类型的滑动验证码）
                    slider_handle = None
                    slide_distance = 0
                    
                    # 查找腾讯云滑动验证码
                    if page.locator("#tcaptcha_drag_thumb").is_visible():
                        slider_handle = page.locator("#tcaptcha_drag_thumb")
                        # 计算滑动距离
                        slide_distance = random.randint(160, 190)
                    # 查找网易云滑动验证码
                    elif page.locator("#nc_1_n1z").is_visible():
                        slider_handle = page.locator("#nc_1_n1z")
                        # 计算滑动距离
                        slide_distance = random.randint(280, 320)  # 网易云滑动验证码距离通常更长
                        print("✅ 发现网易云滑动验证码")
                    # 查找其他类型的滑动验证码
                    elif page.locator(".slider-handle, .drag-handle, .slide-btn").is_visible():
                        slider_handle = page.locator(".slider-handle, .drag-handle, .slide-btn").first
                        # 计算滑动距离
                        slide_distance = random.randint(150, 200)
                    
                    if slider_handle and slide_distance > 0:
                        print("✅ 发现滑动验证码")
                        
                        # 模拟人类滑动
                        success = self.simulate_human_slide(page, slider_handle, slide_distance)
                        
                        # 等待验证结果
                        time.sleep(3)
                        
                        # 检查验证是否成功
                        verification_success = False
                        
                        # 检查方式1：滑块是否消失
                        if not slider_handle.is_visible():
                            print("✅ 滑动验证成功！滑块已消失")
                            verification_success = True
                        
                        # 检查方式2：滑块是否显示成功状态（网易云滑动验证码）
                        try:
                            slider_class = slider_handle.get_attribute("class")
                            if "btn_ok" in slider_class:
                                print("✅ 滑动验证成功！滑块显示成功状态")
                                verification_success = True
                            
                            # 检查是否显示验证通过文本
                            success_text = page.locator(".nc-lang-cnt[data-nc-lang='_yesTEXT']")
                            if success_text.is_visible():
                                print("✅ 滑动验证成功！显示验证通过文本")
                                verification_success = True
                        except:
                            pass
                        
                        # 如果验证失败，尝试再次滑动
                        if not verification_success:
                            print("⚠️ 滑动验证可能失败，正在检查...")
                            # 检查是否需要重新滑动
                            if slider_handle.is_visible():
                                print("⚠️ 滑动验证失败，尝试再次滑动...")
                                # 再次尝试滑动，调整距离
                                slide_distance = random.randint(slide_distance - 10, slide_distance + 10)
                                success = self.simulate_human_slide(page, slider_handle, slide_distance)
                                time.sleep(3)
                                
                                # 再次检查验证是否成功
                                try:
                                    slider_class = slider_handle.get_attribute("class")
                                    if "btn_ok" in slider_class:
                                        print("✅ 第二次滑动验证成功！")
                                        verification_success = True
                                    
                                    success_text = page.locator(".nc-lang-cnt[data-nc-lang='_yesTEXT']")
                                    if success_text.is_visible():
                                        print("✅ 第二次滑动验证成功！")
                                        verification_success = True
                                except:
                                    pass
                        
                        if verification_success:
                            print("✅ 滑动验证最终成功！")
                        else:
                            print("❌ 滑动验证失败，可能需要手动验证")
                            browser.close()
                            return None
                    
                    else:
                        print("⚠️ 未发现滑动验证码，可能已经通过验证")
                    
                except Exception as e:
                    print(f"❌ 处理滑动验证码失败: {str(e)}")
                    browser.close()
                    return None
                
                # 点击登录按钮
                try:
                    login_button = page.locator("input[type='submit']")
                    if login_button.is_visible():
                        print("🔐 正在点击登录按钮...")
                        login_button.click()
                        time.sleep(2)  # 等待登录请求
                    else:
                        print("❌ 未找到登录按钮")
                        browser.close()
                        return None
                except Exception as e:
                    print(f"❌ 点击登录按钮失败: {str(e)}")
                    browser.close()
                    return None
            else:
                # 等待用户手动输入账号密码和完成滑动验证
                print("⚠️ 请在打开的浏览器中手动输入账号密码并完成滑动验证，然后点击登录按钮...")

            # 等待页面跳转，超时300秒
            try:
                page.wait_for_url("https://up.woozooo.com/mydisk.php", timeout=300000)
                print("✅ 登录成功！页面已跳转")
            except Exception as e:
                print(f"❌ 登录失败，页面未跳转: {str(e)}")
                browser.close()
                return None

            # 自动提取登录后的Cookie（挂载工具核心步骤）
            browser_cookies = page.context.cookies()
            print("📋 获取到的Cookie：", browser_cookies)
            browser.close()

        # 筛选蓝奏云必备的Cookie并保存为列表格式
        target_cookie = []
        for c in browser_cookies:
            if c["name"] in ["ylogin", "phpdisk_info", "uag", "folder_id_c"]:
                target_cookie.append({
                    'name': c['name'],
                    'value': c['value'],
                    'domain': c['domain'],
                    'path': c['path'],
                    'expires': c['expires']
                })

        if target_cookie:
            self.cookie = target_cookie
            # 保存Cookie到文件
            with open("lanzou_cookies.txt", "w") as f:
                f.write(str(target_cookie))
            print("✅ Edge 自动登录成功！Cookie 获取完成：")
            print(self.cookie)
            return target_cookie
        print("⚠️ 未获取到完整Cookie，可能是登录未成功或需要手动验证")
        print("📋 当前获取到的Cookie：", browser_cookies)
        return None

    # ===================== 蓝奏云文件管理功能 =====================
    def init_api(self):
        """使用自动获取的Cookie初始化网盘接口"""
        if not self.cookie:
            print("❌ Cookie为空，无法初始化API")
            return False
            
        # 处理Cookie格式
        if isinstance(self.cookie, list):
            # 转换为字典格式
            cookie_dict = {}
            for cookie in self.cookie:
                if isinstance(cookie, dict) and 'name' in cookie and 'value' in cookie:
                    cookie_dict[cookie['name']] = cookie['value']
            self.session.cookies.update(cookie_dict)
        else:
            self.session.cookies.update(self.cookie)
            
        self.session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Edg/130.0.0.0",
            "Referer": f"{self.base_url}/mydisk.php"
        }
        
        # 验证登录状态并获取vei参数
        resp = self.session.get(f"{self.base_url}/mydisk.php")
        if resp.status_code == 200:
            print(f"✅ Cookie有效，登录状态正常")
            # 提取vei参数
            self.vei = self._extract_vei(resp.text)
            if self.vei:
                print(f"✅ 成功提取vei参数: {self.vei}")
            else:
                print(f"⚠️ 无法提取vei参数，使用默认值")
                self.vei = "V1NTUVVWBwsHBVJWWVI%3D"
            return True
        else:
            print(f"❌ Cookie无效，登录状态失效")
            return False
    
    def _extract_vei(self, html):
        """从HTML中提取vei参数"""
        import re
        # 查找vei参数
        match = re.search(r"'vei':'([^']+)'", html)
        if match:
            return match.group(1)
        # 尝试另一种格式
        match = re.search(r"vei=([^&]+)", html)
        if match:
            return match.group(1)
        # 尝试从folder函数调用中提取
        match = re.search(r"folder\(folder_id\);.*?'vei':'([^']+)',", html, re.DOTALL)
        if match:
            return match.group(1)
        # 尝试从more函数调用中提取
        match = re.search(r"more\(folder_id\);.*?'vei':'([^']+)',", html, re.DOTALL)
        if match:
            return match.group(1)
        return None

    def get_file_list(self, folder_id=None):
        """获取文件和文件夹列表"""
        # 从cookie中获取用户信息
        user_id = None
        try:
            for cookie in self.cookie:
                if isinstance(cookie, dict) and cookie.get('name') == 'ylogin':
                    user_id = cookie.get('value')
                    break
        except Exception as e:
            print(f"❌ 解析Cookie失败: {str(e)}")
            return None
        
        if not user_id:
            print("❌ 无法从Cookie中获取用户ID")
            return None
        
        # 如果没有传入folder_id，从cookie中获取当前文件夹ID
        if folder_id is None:
            folder_id = "-1"  # 默认根目录
            try:
                for cookie in self.cookie:
                    if isinstance(cookie, dict) and cookie.get('name') == 'folder_id_c':
                        folder_id = cookie.get('value', '-1')
                        break
            except Exception as e:
                print(f"❌ 解析Cookie失败: {str(e)}")
        
        print(f"📁 正在获取文件夹 {folder_id} 中的文件和文件夹列表")
        
        # 发送POST请求获取文件夹列表
        folder_resp = self.session.post(
            f"{self.base_url}/doupload.php?uid={user_id}",
            data={"task": "47", "folder_id": folder_id, "vei": self.vei},
            headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"{self.base_url}/mydisk.php?item=files&action=index&u={user_id}"
            }
        )
        
        # 发送POST请求获取文件列表
        file_resp = self.session.post(
            f"{self.base_url}/doupload.php?uid={user_id}",
            data={"task": "5", "folder_id": folder_id, "pg": "1", "vei": self.vei},
            headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"{self.base_url}/mydisk.php?item=files&action=index&u={user_id}"
            }
        )
        
        if folder_resp.status_code == 200 and file_resp.status_code == 200:
            print(f"✅ 文件和文件夹列表获取成功")
            # 合并文件夹和文件列表
            result = {
                'zt': 1,
                'folders': folder_resp.json().get('text', []),
                'files': file_resp.json().get('text', [])
            }
            return result
        else:
            print(f"❌ 文件和文件夹列表获取失败")
            print(f"文件夹列表请求状态码: {folder_resp.status_code}")
            print(f"文件列表请求状态码: {file_resp.status_code}")
            return None
    
    def create_folder(self, folder_name, parent_id="0"):
        """创建文件夹"""
        # 从cookie中获取当前文件夹ID
        folder_id = "0"
        for cookie in self.cookie:
            if cookie['name'] == 'folder_id_c':
                folder_id = cookie['value']
                break
        
        resp = self.session.post(
            f"{self.base_url}/doupload.php",
            data={"task": "2", "parent_id": folder_id, "folder_name": folder_name, "folder_description": ""}
        )
        if resp.status_code == 200:
            print(f"✅ 文件夹 {folder_name} 创建成功")
            return True
        else:
            print(f"❌ 文件夹 {folder_name} 创建失败")
            return False
    
    def delete_file(self, file_id):
        """删除文件"""
        resp = self.session.post(
            f"{self.base_url}/doupload.php",
            data={"task": "6", "file_id": file_id},
            headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"{self.base_url}/mydisk.php"
            }
        )
        if resp.status_code == 200:
            print(f"✅ 文件 {file_id} 删除成功")
            return True
        else:
            print(f"❌ 文件 {file_id} 删除失败")
            return False
    
    def delete_folder(self, folder_id):
        """删除文件夹"""
        resp = self.session.post(
            f"{self.base_url}/doupload.php",
            data={"task": "3", "folder_id": folder_id},
            headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"{self.base_url}/mydisk.php"
            }
        )
        if resp.status_code == 200:
            print(f"✅ 文件夹 {folder_id} 删除成功")
            return True
        else:
            print(f"❌ 文件夹 {folder_id} 删除失败")
            return False
    
    def upload_file(self, file_path, max_retries=3, split_size=10*1024*1024, folder_id=None):
        """上传文件"""
        import mimetypes
        import time
        
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        # 自动检测文件类型
        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = 'application/octet-stream'
        
        # 如果没有传入folder_id，从cookie中获取当前文件夹ID
        if folder_id is None:
            folder_id = "0"
            try:
                for cookie in self.cookie:
                    if isinstance(cookie, dict) and cookie.get('name') == 'folder_id_c':
                        folder_id = cookie.get('value', '0')
                        break
            except Exception as e:
                print(f"❌ 解析Cookie失败: {str(e)}")
        
        # 构建完整的请求头
        headers = {
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/mydisk.php",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0"
        }
        
        # 检查文件大小，如果超过split_size，则创建文件夹并分割上传
        if file_size <= split_size:
            # 小文件直接上传
            return self._upload_single_file(file_path, filename, file_size, content_type, folder_id, headers, max_retries)
        else:
            # 大文件分割上传
            return self._upload_large_file(file_path, filename, file_size, content_type, folder_id, headers, max_retries, split_size)
    
    def _upload_single_file(self, file_path, filename, file_size, content_type, folder_id, headers, max_retries):
        """上传单个小文件"""
        # 生成文件唯一标识
        self.upload_file_counter += 1
        file_id = f"WU_FILE_{self.upload_file_counter}"
        
        # 尝试上传
        for attempt in range(max_retries):
            try:
                with open(file_path, "rb") as f:
                    files = {"upload_file": (filename, f, content_type)}
                    data = {
                        "task": "1",
                        "vie": "2",
                        "ve": "2",
                        "id": file_id,
                        "name": filename,
                        "type": content_type,
                        "size": str(file_size),
                        "folder_id_bb_n": folder_id,
                        "lastModifiedDate": time.strftime('%a %b %d %Y %H:%M:%S GMT+0800 (中国标准时间)', time.localtime())
                    }
                    resp = self.session.post(
                        f"{self.base_url}/html5up.php",
                        files=files,
                        data=data,
                        headers=headers,
                        timeout=300
                    )
                
                if resp.status_code == 200:
                    print(f"✅ 文件 {filename} 上传成功")
                    return True
                else:
                    print(f"❌ 文件 {filename} 上传失败，状态码: {resp.status_code}")
                    if attempt < max_retries - 1:
                        print(f"🔄 正在重试 ({attempt + 1}/{max_retries})...")
                        time.sleep(2)
            except Exception as e:
                print(f"❌ 文件 {filename} 上传出错: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"🔄 正在重试 ({attempt + 1}/{max_retries})...")
                    time.sleep(2)
        
        print(f"❌ 文件 {filename} 上传失败，已达到最大重试次数")
        return False
    
    def _upload_large_file(self, file_path, filename, file_size, content_type, folder_id, headers, max_retries, split_size):
        """上传大文件（分割上传）"""
        # 创建与文件名同名的文件夹
        folder_name = os.path.splitext(filename)[0]
        sub_folder_id = self.create_folder(folder_name, folder_id)
        
        # 如果返回的是True而不是文件夹ID，尝试查找新创建的文件夹
        if sub_folder_id is True:
            # 尝试通过获取文件夹列表来查找新创建的文件夹
            try:
                # 获取父文件夹中的所有文件夹
                list_data = self.get_file_list(folder_id)
                if list_data and isinstance(list_data, dict) and list_data.get('zt') == 1:
                    folders = list_data.get('folders', [])
                    for folder in folders:
                        if isinstance(folder, dict) and folder.get('name') == folder_name:
                            sub_folder_id = folder.get('fol_id')
                            if sub_folder_id:
                                print(f"✅ 找到新创建的文件夹，ID: {sub_folder_id}")
                                break
            except Exception as e:
                print(f"❌ 查找文件夹ID失败: {str(e)}")
            
            # 如果仍然无法获取文件夹ID，使用父文件夹ID
            if sub_folder_id is True:
                print(f"⚠️ 无法获取新创建的文件夹ID，使用父文件夹ID: {folder_id}")
                sub_folder_id = folder_id
        elif not sub_folder_id:
            print(f"❌ 创建文件夹失败，无法上传大文件")
            return False
        
        print(f"📁 最终使用的上传目标文件夹ID: {sub_folder_id}")
        
        # 计算分割信息
        total_chunks = (file_size + split_size - 1) // split_size
        uploaded_chunks = 0
        lock = threading.Lock()
        
        # 生成分割文件的名称
        def create_split_filename(original_name, index, total):
            name, ext = os.path.splitext(original_name)
            return f"{name}.z{index:03d}{ext}"
        
        # 上传单个分割文件的函数
        def upload_split_file(chunk_index):
            nonlocal uploaded_chunks
            
            # 计算分割文件的范围
            start_byte = chunk_index * split_size
            end_byte = min((chunk_index + 1) * split_size, file_size)
            chunk_size = end_byte - start_byte
            
            # 生成分割文件名
            split_filename = create_split_filename(filename, chunk_index + 1, total_chunks)
            
            # 生成文件唯一标识
            self.upload_file_counter += 1
            file_id = f"WU_FILE_{self.upload_file_counter}"
            
            # 尝试上传
            for attempt in range(max_retries):
                try:
                    # 创建文件流，只读取当前分割的部分
                    with open(file_path, "rb") as f:
                        f.seek(start_byte)
                        chunk_data = f.read(chunk_size)
                        
                        files = {"upload_file": (split_filename, chunk_data, content_type)}
                        data = {
                            "task": "1",
                            "vie": "2",
                            "ve": "2",
                            "id": file_id,
                            "name": split_filename,
                            "type": content_type,
                            "size": str(chunk_size),
                            "folder_id_bb_n": sub_folder_id,
                            "lastModifiedDate": time.strftime('%a %b %d %Y %H:%M:%S GMT+0800 (中国标准时间)', time.localtime())
                        }
                        print(f"📤 上传分割文件 {split_filename} 到文件夹ID: {sub_folder_id}")
                        
                        # 创建新的会话以支持并行上传
                        session = requests.Session()
                        for cookie in self.cookie:
                            if isinstance(cookie, dict):
                                session.cookies.set(cookie.get('name'), cookie.get('value'))
                        
                        resp = session.post(
                            f"{self.base_url}/html5up.php",
                            files=files,
                            data=data,
                            headers=headers,
                            timeout=300
                        )
                    
                    if resp.status_code == 200:
                        with lock:
                            nonlocal uploaded_chunks
                            uploaded_chunks += 1
                            print(f"🔄 上传进度: {uploaded_chunks}/{total_chunks} ({int(uploaded_chunks/total_chunks*100)}%)")
                        return True
                    else:
                        print(f"❌ 分割文件 {split_filename} 上传失败，状态码: {resp.status_code}")
                        if attempt < max_retries - 1:
                            print(f"🔄 正在重试 ({attempt + 1}/{max_retries})...")
                            time.sleep(2)
                except Exception as e:
                    print(f"❌ 分割文件 {split_filename} 上传出错: {str(e)}")
                    if attempt < max_retries - 1:
                        print(f"🔄 正在重试 ({attempt + 1}/{max_retries})...")
                        time.sleep(2)
            
            # 所有重试都失败
            print(f"❌ 分割文件 {split_filename} 上传失败")
            return False
        
        # 使用线程池并行上传
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for i in range(total_chunks):
                future = executor.submit(upload_split_file, i)
                futures.append(future)
            
            # 等待所有上传完成
            results = [future.result() for future in futures]
            
            # 检查是否所有分割文件都上传成功
            if all(results):
                print(f"✅ 文件 {filename} 上传成功（已分割为 {total_chunks} 部分）")
                return True
            else:
                print(f"❌ 文件 {filename} 上传失败，部分分割文件上传失败")
                return False
    
    def create_folder(self, folder_name, parent_id="0"):
        """创建文件夹"""
        # 使用传入的父文件夹ID，而不是从cookie中获取
        folder_id = parent_id
        
        resp = self.session.post(
            f"{self.base_url}/doupload.php",
            data={"task": "2", "parent_id": folder_id, "folder_name": folder_name, "folder_description": ""},
            headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"{self.base_url}/mydisk.php"
            }
        )
        
        print(f"📁 创建文件夹请求响应: {resp.status_code}")
        
        if resp.status_code == 200:
            try:
                result = resp.json()
                print(f"📁 创建文件夹响应内容: {result}")
                if isinstance(result, dict):
                    # 检查是否创建成功
                    if result.get('zt') == 1:
                        # 尝试从不同位置获取文件夹ID
                        folder_id = None
                        
                        # 情况1: text直接是文件夹ID（字符串）
                        folder_info = result.get('text')
                        if isinstance(folder_info, str) and folder_info.isdigit():
                            folder_id = folder_info
                        
                        # 情况2: text是字典
                        elif isinstance(folder_info, dict):
                            folder_id = folder_info.get('fol_id')
                        
                        # 情况3: text是列表
                        elif isinstance(folder_info, list) and folder_info:
                            first_item = folder_info[0]
                            if isinstance(first_item, dict):
                                folder_id = first_item.get('fol_id')
                        
                        # 情况4: 直接在result中查找
                        if not folder_id:
                            folder_id = result.get('fol_id')
                        
                        if folder_id:
                            print(f"✅ 文件夹 {folder_name} 创建成功，ID: {folder_id}")
                            return folder_id
            except Exception as e:
                print(f"❌ 解析创建文件夹响应失败: {str(e)}")
            
            # 如果无法获取文件夹ID，尝试通过获取文件夹列表来查找
            try:
                # 获取父文件夹中的所有文件夹
                list_data = self.get_file_list(parent_id)
                print(f"📁 父文件夹 {parent_id} 中的文件夹列表: {list_data}")
                if list_data and isinstance(list_data, dict) and list_data.get('zt') == 1:
                    folders = list_data.get('folders', [])
                    for folder in folders:
                        if isinstance(folder, dict) and folder.get('name') == folder_name:
                            folder_id = folder.get('fol_id')
                            if folder_id:
                                print(f"✅ 文件夹 {folder_name} 创建成功，通过列表查找获取ID: {folder_id}")
                                return folder_id
            except Exception as e:
                print(f"❌ 查找文件夹ID失败: {str(e)}")
            
            # 如果仍然无法获取文件夹ID，返回True表示创建成功
            print(f"✅ 文件夹 {folder_name} 创建成功")
            return True
        else:
            print(f"❌ 文件夹 {folder_name} 创建失败")
            return False
    
    def recover_file(self, folder_id, save_path):
        """恢复分割上传的文件"""
        try:
            # 获取文件夹中的所有文件
            files = self.get_file_list(folder_id)
            if not files:
                print(f"❌ 文件夹中没有文件")
                return False
            
            # 筛选出分割文件（以.z001, .z002等结尾的文件）
            split_files = []
            for file in files:
                if hasattr(file, 'name') and file.name.endswith('.z001'):
                    # 找到第一个分割文件，然后查找所有相关的分割文件
                    base_name = file.name.rsplit('.z', 1)[0]
                    ext = file.name.rsplit('.', 1)[1].split('.z')[0]
                    original_name = f"{base_name}.{ext}"
                    
                    # 收集所有分割文件
                    for f in files:
                        if hasattr(f, 'name') and base_name in f.name and '.z' in f.name:
                            # 提取序号
                            try:
                                index = int(f.name.rsplit('.z', 1)[1].split('.')[0])
                                split_files.append((index, f))
                            except:
                                pass
                    break
            
            if not split_files:
                print(f"❌ 未找到分割文件")
                return False
            
            # 按序号排序
            split_files.sort(key=lambda x: x[0])
            
            # 合并文件
            with open(save_path, 'wb') as output:
                for index, file in split_files:
                    if hasattr(file, 'id'):
                        # 下载分割文件
                        temp_path = f"{save_path}.tmp.{index}"
                        if self.download_file(file.id, temp_path):
                            # 读取并写入输出文件
                            with open(temp_path, 'rb') as temp:
                                output.write(temp.read())
                            # 删除临时文件
                            os.remove(temp_path)
                            print(f"✅ 合并分割文件 {index}/{len(split_files)}")
                        else:
                            print(f"❌ 下载分割文件失败")
                            return False
            
            print(f"✅ 文件恢复成功，保存为: {save_path}")
            return True
        except Exception as e:
            print(f"❌ 恢复文件失败: {str(e)}")
            return False
    
    def get_share_info(self, file_id):
        """获取文件分享信息"""
        try:
            # 从cookie中获取用户信息
            user_id = None
            for cookie in self.cookie:
                if isinstance(cookie, dict) and cookie.get('name') == 'ylogin':
                    user_id = cookie.get('value')
                    break
            
            if not user_id:
                print("❌ 无法从Cookie中获取用户ID")
                return None
            
            # 发送请求获取文件分享信息
            resp = self.session.post(
                f"{self.base_url}/doupload.php",
                data={"task": "22", "file_id": file_id},
                headers={
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": f"{self.base_url}/mydisk.php?item=files&action=index&u={user_id}"
                }
            )
            
            if resp.status_code == 200:
                result = resp.json()
                if isinstance(result, dict) and result.get('zt') == 1:
                    info = result.get('info', {})
                    if isinstance(info, dict):
                        share_url = info.get('is_newd') + '/' + info.get('f_id')
                        password = info.get('pwd')
                        return {
                            'share_url': share_url,
                            'password': password
                        }
            
            print(f"❌ 获取分享信息失败")
            return None
        except Exception as e:
            print(f"❌ 获取分享信息失败: {str(e)}")
            return None
    
    def check_file_password(self, file_id):
        """检查文件是否有密码"""
        try:
            # 从cookie中获取用户信息
            user_id = None
            for cookie in self.cookie:
                if isinstance(cookie, dict) and cookie.get('name') == 'ylogin':
                    user_id = cookie.get('value')
                    break
            
            if not user_id:
                print("❌ 无法从Cookie中获取用户ID")
                return {"has_password": False, "password": ""}
            
            # 发送POST请求检查文件密码
            resp = self.session.post(
                f"{self.base_url}/doupload.php",
                data={"task": "22", "file_id": file_id},
                headers={
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": f"{self.base_url}/mydisk.php?item=files&action=index&u={user_id}"
                }
            )
            
            if resp.status_code == 200:
                result = resp.json()
                if isinstance(result, dict) and result.get('zt') == 1:
                    info = result.get('info', {})
                    if isinstance(info, dict):
                        has_password = info.get('onof') == "1"
                        password = info.get('pwd', "")
                        return {"has_password": has_password, "password": password}
            return {"has_password": False, "password": ""}
        except Exception as e:
            print(f"❌ 检查文件密码失败: {str(e)}")
            return {"has_password": False, "password": ""}
    
    def set_file_password(self, file_id, password="1234"):
        """设置文件密码"""
        try:
            # 从cookie中获取用户信息
            user_id = None
            for cookie in self.cookie:
                if isinstance(cookie, dict) and cookie.get('name') == 'ylogin':
                    user_id = cookie.get('value')
                    break
            
            if not user_id:
                print("❌ 无法从Cookie中获取用户ID")
                return False
            
            # 发送POST请求设置文件密码
            resp = self.session.post(
                f"{self.base_url}/doupload.php",
                data={"task": "23", "file_id": file_id, "shows": "1", "shownames": password},
                headers={
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": f"{self.base_url}/mydisk.php?item=files&action=index&u={user_id}"
                }
            )
            
            if resp.status_code == 200:
                result = resp.json()
                if isinstance(result, dict) and result.get('zt') == 1:
                    print(f"✅ 文件密码设置成功: {password}")
                    return True
            print("❌ 文件密码设置失败")
            return False
        except Exception as e:
            print(f"❌ 设置文件密码失败: {str(e)}")
            return False
    
    def parse_direct_link(self, share_url, password=None):
        """解析获取直链"""
        try:
            # 访问分享链接
            resp = self.session.get(share_url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0"
            })
            
            if resp.status_code != 200:
                print(f"❌ 访问分享链接失败，状态码: {resp.status_code}")
                return None
            
            html = resp.text
            
            # 检查是否需要密码
            if 'function down_p()' in html:
                if not password:
                    print("❌ 分享链接需要密码")
                    return None
                
                # 提取必要的参数
                import re
                sign_match = re.search(r"'sign':'(.*?)',", html)
                ajaxm_match = re.search(r"ajaxm\.php\?file=(\d+)", html)
                
                if not sign_match or not ajaxm_match:
                    print("❌ 解析分享页面失败")
                    return None
                
                sign = sign_match.group(1)
                ajaxm_url = f"{share_url.split('/')[0]}//{share_url.split('/')[2]}/ajaxm.php?file={ajaxm_match.group(1)}"
                
                # 发送POST请求获取直链信息
                post_data = {
                    "action": "downprocess",
                    "sign": sign,
                    "p": password,
                    "kd": 1
                }
                
                resp = self.session.post(ajaxm_url, data=post_data, headers={
                    "Referer": share_url,
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0"
                })
            else:
                # 无密码情况
                # 提取iframe链接
                import re
                iframe_match = re.search(r'<iframe.*?src="(/.*?)".*?>', html)
                if not iframe_match:
                    print("❌ 解析分享页面失败")
                    return None
                
                iframe_url = f"{share_url.split('/')[0]}//{share_url.split('/')[2]}{iframe_match.group(1)}"
                
                # 访问iframe页面
                iframe_resp = self.session.get(iframe_url, headers={
                    "Referer": share_url,
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0"
                })
                
                if iframe_resp.status_code != 200:
                    print(f"❌ 访问iframe页面失败，状态码: {iframe_resp.status_code}")
                    return None
                
                iframe_html = iframe_resp.text
                
                # 提取必要的参数
                wp_sign_match = re.search(r"wp_sign = '(.*?)'", iframe_html)
                ajaxdata_match = re.search(r"ajaxdata = '(.*?)'", iframe_html)
                ajaxm_match = re.search(r"ajaxm\.php\?file=(\d+)", iframe_html)
                
                if not wp_sign_match or not ajaxdata_match or not ajaxm_match:
                    print("❌ 解析iframe页面失败")
                    return None
                
                websignkey = ajaxdata_match.group(1)
                signs = ajaxdata_match.group(1)
                sign = wp_sign_match.group(1)
                ajaxm_url = f"{share_url.split('/')[0]}//{share_url.split('/')[2]}/ajaxm.php?file={ajaxm_match.group(1)}"
                
                # 发送POST请求获取直链信息
                post_data = {
                    "action": "downprocess",
                    "websignkey": websignkey,
                    "signs": signs,
                    "sign": sign,
                    "websign": '',
                    "kd": 1,
                    "ves": 1
                }
                
                resp = self.session.post(ajaxm_url, data=post_data, headers={
                    "Referer": iframe_url,
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0"
                })
            
            # 解析响应
            if resp.status_code == 200:
                result = resp.json()
                if isinstance(result, dict) and result.get('zt') == 1:
                    direct_url = f"{result.get('dom')}/file/{result.get('url')}"
                    return direct_url
            
            print(f"❌ 获取直链失败")
            return None
        except Exception as e:
            print(f"❌ 解析直链失败: {str(e)}")
            return None
    
    def get_download_url(self, file_id):
        """获取文件下载链接"""
        try:
            # 首先获取分享信息
            share_info = self.get_share_info(file_id)
            if not share_info:
                # 如果获取分享信息失败，使用备用方法
                resp = self.session.get(
                    f"{self.base_url}/file_down.php?action=down&ids={file_id}"
                )
                if resp.status_code == 200:
                    return f"{self.base_url}/file_down.php?action=down&ids={file_id}"
                return None
            
            # 使用新的解析器获取直链
            from lanzou_parser import parse_lanzou_url
            result = parse_lanzou_url(share_info['share_url'], share_info['password'])
            if result:
                direct_url = result[0]  # 第一个元素是直链
                return direct_url
            
            print(f"❌ 获取下载链接失败")
            return None
        except Exception as e:
            print(f"❌ 获取下载链接失败: {str(e)}")
            return None
    
    def download_file(self, file_id, save_dir):
        """下载文件"""
        try:
            # 检查文件是否有密码
            password_info = self.check_file_password(file_id)
            if not password_info["has_password"]:
                print("⚠️ 文件无密码，设置密码为1234")
                self.set_file_password(file_id, "1234")
            else:
                print(f"📝 文件当前密码: {password_info['password']}")
            
            # 尝试从分享信息中获取文件名
            share_info = self.get_share_info(file_id)
            filename = None
            if share_info:
                from lanzou_parser import parse_lanzou_url
                _, _, filename = parse_lanzou_url(share_info['share_url'], share_info['password'])
            
            # 如果没有获取到文件名，使用默认名称
            if not filename:
                filename = f"file_{file_id}"
            
            # 构建保存路径
            import os
            save_path = os.path.join(save_dir, filename)
            
            # 获取下载链接
            down_url = self.get_download_url(file_id)
            if not down_url:
                # 如果获取失败，使用备用方法
                resp = self.session.get(
                    f"{self.base_url}/file_down.php?action=down&ids={file_id}"
                )
                if resp.status_code != 200:
                    print(f"❌ 文件 {file_id} 下载失败，HTTP状态码: {resp.status_code}")
                    return False
                with open(save_path, "wb") as f:
                    f.write(resp.content)
                print(f"✅ 文件 {filename} 下载成功，保存到 {save_path}")
                return True
            
            # 使用新的下载模块
            import downloader
            
            # 调用下载模块
            downloaded_path = downloader.download_file(down_url, save_path, filename=filename)
            if downloaded_path:
                print(f"✅ 文件 {filename} 下载成功，保存到 {downloaded_path}")
                return True
            else:
                print(f"❌ 文件 {filename} 下载失败")
                return False
        except Exception as e:
            print(f"❌ 文件下载失败: {str(e)}")
            return False
    
    def download_file_content(self, file_id):
        """下载文件内容并返回"""
        try:
            # 获取下载链接
            down_url = self.get_download_url(file_id)
            if not down_url:
                # 如果获取失败，使用备用方法
                resp = self.session.get(
                    f"{self.base_url}/file_down.php?action=down&ids={file_id}"
                )
                if resp.status_code != 200:
                    print(f"❌ 文件内容下载失败，HTTP状态码: {resp.status_code}")
                    return None
                return resp.content
            
            # 发送请求下载文件
            resp = self.session.get(down_url, timeout=300)
            
            if resp.status_code == 200:
                return resp.content
            else:
                print(f"❌ 文件内容下载失败，状态码: {resp.status_code}")
                return None
        except Exception as e:
            print(f"❌ 文件内容下载失败: {str(e)}")
            return None

# ===================== 运行测试（全自动！） =====================
if __name__ == "__main__":
    lz = LanzouEdgeAutoLogin()
    
    # 尝试使用Cookie登录
    if lz.cookie:
        if lz.init_api():
            # 启动GUI界面
            print("🚀 启动蓝奏云文件管理器界面...")
            from ui import LanzouUI
            LanzouUI(lz)
        else:
            # Cookie无效，使用浏览器登录
            lz.get_cookie_with_edge()
            if lz.init_api():
                # 登录成功后启动GUI界面
                print("🚀 启动蓝奏云文件管理器界面...")
                from ui import LanzouUI
                LanzouUI(lz)
