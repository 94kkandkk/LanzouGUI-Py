import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
from bs4 import BeautifulSoup

class LanzouUI:
    def __init__(self, lanzou_instance):
        self.lanzou = lanzou_instance
        self.root = tk.Tk()
        self.root.title("蓝奏云文件管理器")
        self.root.geometry("800x600")
        
        self.current_folder_id = "-1"  # 默认根目录
        self.current_path = ["/"]  # 当前路径
        
        self.create_widgets()
        self.root.mainloop()
    
    def create_widgets(self):
        # 顶部框架
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill=tk.X)
        
        # 登录框架
        login_frame = ttk.Frame(top_frame)
        login_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(login_frame, text="账号:", font=('微软雅黑', 10)).pack(side=tk.LEFT, padx=5)
        self.username_var = tk.StringVar()
        ttk.Entry(login_frame, textvariable=self.username_var, width=20).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(login_frame, text="密码:", font=('微软雅黑', 10)).pack(side=tk.LEFT, padx=5)
        self.password_var = tk.StringVar()
        ttk.Entry(login_frame, textvariable=self.password_var, show="*", width=20).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(login_frame, text="登录", command=self.login).pack(side=tk.LEFT, padx=5)
        
        # 路径导航栏
        path_frame = ttk.Frame(top_frame)
        path_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(path_frame, text="当前路径:", font=('微软雅黑', 10)).pack(side=tk.LEFT, padx=5)
        
        self.path_var = tk.StringVar(value="/")
        ttk.Label(path_frame, textvariable=self.path_var, font=('微软雅黑', 10, 'italic')).pack(side=tk.LEFT, padx=5)
        
        # 返回上一级按钮
        ttk.Button(path_frame, text="返回上一级", command=self.go_back).pack(side=tk.RIGHT, padx=5)
        
        ttk.Label(top_frame, text="蓝奏云文件管理器", font=('微软雅黑', 16)).pack()
        
        # 操作框架
        action_frame = ttk.Frame(self.root, padding=10)
        action_frame.pack(fill=tk.X)
        
        ttk.Button(action_frame, text="创建文件夹", command=self.create_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="上传文件", command=self.upload_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="下载文件", command=self.download_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="删除", command=self.delete_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="刷新文件列表", command=self.refresh_file_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="获取Cookie", command=self.get_cookie).pack(side=tk.LEFT, padx=5)
        
        # 文件列表框架
        list_frame = ttk.Frame(self.root, padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 树状视图
        self.tree = ttk.Treeview(list_frame, yscrollcommand=scrollbar.set)
        self.tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)
        
        # 定义列
        self.tree['columns'] = ('name', 'size', 'date')
        self.tree.column('#0', width=0, stretch=tk.NO)
        self.tree.column('name', anchor=tk.W, width=400)
        self.tree.column('size', anchor=tk.CENTER, width=100)
        self.tree.column('date', anchor=tk.CENTER, width=150)
        
        # 定义表头
        self.tree.heading('name', text='文件名')
        self.tree.heading('size', text='大小')
        self.tree.heading('date', text='修改日期')
        
        # 绑定双击事件
        self.tree.bind('<Double-1>', self.on_double_click)
    
    def create_folder(self):
        folder_name = tk.simpledialog.askstring("创建文件夹", "请输入文件夹名称：")
        if folder_name:
            result = self.lanzou.create_folder(folder_name)
            if result:
                messagebox.showinfo("成功", f"文件夹 {folder_name} 创建成功")
                self.refresh_file_list()
            else:
                messagebox.showerror("失败", f"文件夹 {folder_name} 创建失败")
    
    def upload_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            # 获取当前选择的文件夹
            selected_item = self.tree.selection()
            folder_id = "0"
            if selected_item:
                item = selected_item[0]
                tags = self.tree.item(item, "tags")
                if tags and tags[0].startswith("folder_"):
                    folder_id = tags[0].replace("folder_", "")
            
            result = self.lanzou.upload_file(file_path, folder_id=folder_id)
            if result:
                messagebox.showinfo("成功", f"文件 {file_path} 上传成功")
                self.refresh_file_list()
            else:
                messagebox.showerror("失败", f"文件 {file_path} 上传失败")
    
    def download_file(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请选择要下载的文件")
            return
        
        item = selected_item[0]
        file_id = self.tree.item(item, "tags")[0]
        save_dir = filedialog.askdirectory()
        if save_dir:
            result = self.lanzou.download_file(file_id, save_dir)
            if result:
                messagebox.showinfo("成功", "文件下载成功")
            else:
                messagebox.showerror("失败", "文件下载失败")
    
    def delete_file(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请选择要删除的文件或文件夹")
            return
        
        item = selected_item[0]
        tags = self.tree.item(item, "tags")
        if not tags:
            messagebox.showerror("错误", "无法获取选择项的ID")
            return
        
        item_id = tags[0]
        item_name = self.tree.item(item, "values")[0]
        
        if item_id.startswith("folder_"):
            # 删除文件夹
            folder_id = item_id.replace("folder_", "")
            if messagebox.askyesno("确认删除", f"确定要删除文件夹 {item_name} 吗？"):
                result = self.lanzou.delete_folder(folder_id)
                if result:
                    messagebox.showinfo("成功", f"文件夹 {item_name} 删除成功")
                    self.refresh_file_list()
                else:
                    messagebox.showerror("失败", f"文件夹 {item_name} 删除失败")
        else:
            # 删除文件
            if messagebox.askyesno("确认删除", f"确定要删除文件 {item_name} 吗？"):
                result = self.lanzou.delete_file(item_id)
                if result:
                    messagebox.showinfo("成功", f"文件 {item_name} 删除成功")
                    self.refresh_file_list()
                else:
                    messagebox.showerror("失败", f"文件 {item_name} 删除失败")
    
    def on_double_click(self, event):
        """处理双击事件，打开文件夹"""
        item = self.tree.identify('item', event.x, event.y)
        if not item:
            return
        
        tags = self.tree.item(item, "tags")
        if not tags:
            return
        
        item_id = tags[0]
        if item_id.startswith("folder_"):
            # 打开文件夹
            folder_id = item_id.replace("folder_", "")
            folder_name = self.tree.item(item, "values")[0].replace("📁 ", "")
            
            # 更新当前文件夹信息
            self.current_folder_id = folder_id
            self.current_path.append(folder_name)
            
            # 更新路径显示
            self.update_path_display()
            
            # 刷新文件列表
            self.refresh_file_list()
    
    def go_back(self):
        """返回上一级文件夹"""
        if len(self.current_path) > 1:
            # 移除当前文件夹
            self.current_path.pop()
            
            # 如果回到根目录
            if len(self.current_path) == 1:
                self.current_folder_id = "-1"
            else:
                # 需要获取上一级文件夹的ID
                # 这里简化处理，直接返回根目录
                # 实际应用中可能需要维护文件夹层级关系
                self.current_folder_id = "-1"
            
            # 更新路径显示
            self.update_path_display()
            
            # 刷新文件列表
            self.refresh_file_list()
    
    def update_path_display(self):
        """更新路径显示"""
        path_str = "/".join(self.current_path)
        self.path_var.set(path_str)
    
    def refresh_file_list(self):
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 获取文件和文件夹列表
        list_data = self.lanzou.get_file_list(self.current_folder_id)
        if list_data:
            try:
                # 处理文件夹列表
                if list_data.get('zt') == 1:
                    # 获取文件夹列表
                    folders = list_data.get('folders', [])
                    
                    for folder_item in folders:
                        # 提取文件夹信息
                        name = folder_item.get('name', '')
                        folder_id = folder_item.get('fol_id', '')
                        
                        # 插入到树状视图，文件夹大小显示为--
                        if folder_id:
                            self.tree.insert('', tk.END, values=(f"📁 {name}", "--", ""), tags=(f"folder_{folder_id}"))
                    
                    # 获取文件列表
                    files = list_data.get('files', [])
                    
                    for file_item in files:
                        # 提取文件信息
                        name = file_item.get('name', '')
                        size = file_item.get('size', '--')
                        date = file_item.get('time', '')
                        file_id = file_item.get('id', '')
                        
                        # 插入到树状视图
                        if file_id:
                            self.tree.insert('', tk.END, values=(name, size, date), tags=(file_id))
            except Exception as e:
                messagebox.showerror("解析错误", f"解析文件和文件夹列表失败: {str(e)}")
        else:
            messagebox.showerror("失败", "获取文件和文件夹列表失败")
    
    def login(self):
        """登录蓝奏云"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            messagebox.showwarning("警告", "请输入账号和密码")
            return
        
        try:
            # 调用浏览器登录获取Cookie
            cookie = self.lanzou.get_cookie_with_edge(username, password)
            if cookie:
                # 重新初始化API
                if self.lanzou.init_api():
                    messagebox.showinfo("成功", "登录成功，已更新登录状态")
                    # 刷新文件列表
                    self.refresh_file_list()
                else:
                    messagebox.showerror("失败", "登录成功，但初始化API失败")
            else:
                messagebox.showerror("失败", "登录失败，可能是账号密码错误或滑动验证失败")
        except Exception as e:
            messagebox.showerror("错误", f"登录时出错: {str(e)}")
    
    def get_cookie(self):
        """获取Cookie"""
        try:
            # 调用浏览器登录获取Cookie
            cookie = self.lanzou.get_cookie_with_edge()
            if cookie:
                # 重新初始化API
                if self.lanzou.init_api():
                    messagebox.showinfo("成功", "Cookie获取成功，已更新登录状态")
                    # 刷新文件列表
                    self.refresh_file_list()
                else:
                    messagebox.showerror("失败", "Cookie获取成功，但初始化API失败")
            else:
                messagebox.showerror("失败", "Cookie获取失败")
        except Exception as e:
            messagebox.showerror("错误", f"获取Cookie时出错: {str(e)}")