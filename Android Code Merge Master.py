import os
import json
import threading
import tkinter as tk
import sys
import datetime
from tkinter import filedialog, messagebox, scrolledtext

# 开启 Windows 高 DPI 适配
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

CONFIG_FILE = "kane_ai_config.json"

class CodeMergerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("KANE AI - 代码合并工具 v5.0.0 (Markdown AI 投喂终极版)")
        self.root.geometry("750x680") # 增加高度适配新组件
        self.root.configure(bg='#1e1e1e')

        self.label_font = ("Segoe UI", 10, "bold")
        self.text_font = ("Consolas", 10)

        # 默认配置，默认输出格式改为 .md
        self.config = {
            "project_path": "",
            "extensions": ".kt, .xml, .java, .kts, .toml, .gradle, .json",
            "exclude_dirs": "build, .git, .idea, .gradle, captures",
            "output_path": os.path.abspath("KANE_AI_FULL_CODE.md")
        }
        self.load_config()

        self.setup_ui()
        
        # 绑定窗口关闭事件，用于保存配置
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_config(self):
        """加载上次的配置文件"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
                    # 智能升级：如果老配置还是txt，自动帮用户升级为md
                    if self.config["output_path"].endswith(".txt"):
                        self.config["output_path"] = self.config["output_path"][:-4] + ".md"
            except Exception:
                pass

    def save_config(self):
        """保存当前的配置"""
        self.config["project_path"] = self.path_entry.get().strip()
        self.config["extensions"] = self.ext_entry.get().strip()
        self.config["exclude_dirs"] = self.exclude_entry.get().strip()
        self.config["output_path"] = self.output_entry.get().strip()
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
        except Exception:
            pass

    def on_closing(self):
        """关闭窗口时的处理"""
        self.save_config()
        self.root.destroy()

    def setup_ui(self):
        # --- 项目路径 ---
        tk.Label(self.root, text="📁 安卓项目路径 (main 目录):", bg='#1e1e1e', fg='#00FF00', font=self.label_font).pack(pady=(15, 0), anchor="w", padx=20)
        path_frame = tk.Frame(self.root, bg='#1e1e1e')
        path_frame.pack(fill="x", padx=20, pady=5)
        
        self.path_entry = tk.Entry(path_frame, bg='#2d2d30', fg='white', insertbackground='white', relief="flat", font=self.text_font)
        self.path_entry.pack(side="left", fill="x", expand=True, ipady=6)
        self.path_entry.insert(0, self.config["project_path"] or r"C:\Users\K\AndroidStudioProjects\firstAPP\app\src\main")

        tk.Button(path_frame, text="浏览...", command=self.browse_dir, bg='#3e3e42', fg='white', relief="flat", padx=10).pack(side="right", padx=(5, 0))

        # --- 后缀过滤 ---
        tk.Label(self.root, text="📄 要合并的文件后缀 (逗号分隔):", bg='#1e1e1e', fg='#00FF00', font=self.label_font).pack(pady=(10, 0), anchor="w", padx=20)
        self.ext_entry = tk.Entry(self.root, bg='#2d2d30', fg='white', insertbackground='white', relief="flat", font=self.text_font)
        self.ext_entry.pack(fill="x", padx=20, pady=5, ipady=6)
        self.ext_entry.insert(0, self.config["extensions"])

        # --- 排除文件夹 ---
        tk.Label(self.root, text="🚫 排除的文件夹 (跳过编译/缓存避免 AI 干扰):", bg='#1e1e1e', fg='#FF5555', font=self.label_font).pack(pady=(10, 0), anchor="w", padx=20)
        self.exclude_entry = tk.Entry(self.root, bg='#2d2d30', fg='white', insertbackground='white', relief="flat", font=self.text_font)
        self.exclude_entry.pack(fill="x", padx=20, pady=5, ipady=6)
        self.exclude_entry.insert(0, self.config["exclude_dirs"])

        # --- 输出路径 ---
        tk.Label(self.root, text="💾 输出保存路径 (强烈建议使用 .md 格式投喂 AI):", bg='#1e1e1e', fg='#00FF00', font=self.label_font).pack(pady=(10, 0), anchor="w", padx=20)
        output_frame = tk.Frame(self.root, bg='#1e1e1e')
        output_frame.pack(fill="x", padx=20, pady=5)
        
        self.output_entry = tk.Entry(output_frame, bg='#2d2d30', fg='white', insertbackground='white', relief="flat", font=self.text_font)
        self.output_entry.pack(side="left", fill="x", expand=True, ipady=6)
        self.output_entry.insert(0, self.config["output_path"])

        tk.Button(output_frame, text="浏览...", command=self.browse_output, bg='#3e3e42', fg='white', relief="flat", padx=10).pack(side="right", padx=(5, 0))

        # --- 执行按钮 ---
        self.btn_merge = tk.Button(self.root, text="🚀 开始提取并生成 Markdown", command=self.start_merge_thread, 
                                   bg='#007ACC', fg='white', font=("Segoe UI", 12, "bold"), 
                                   relief="flat", cursor="hand2", activebackground='#0098FF')
        self.btn_merge.pack(fill="x", padx=20, pady=15)

        # --- 日志显示 ---
        tk.Label(self.root, text="终端日志:", bg='#1e1e1e', fg='#888888', font=self.label_font).pack(anchor="w", padx=20)
        self.log_area = scrolledtext.ScrolledText(self.root, bg='#0f0f0f', fg='#cccccc', font=self.text_font, relief="flat", state=tk.DISABLED)
        self.log_area.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def browse_dir(self):
        directory = filedialog.askdirectory(title="选择项目路径")
        if directory:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, directory)

    def browse_output(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            initialfile="KANE_AI_FULL_CODE.md",
            filetypes=[("Markdown", "*.md"), ("Text Files", "*.txt"), ("All Files", "*.*")],
            title="选择输出文件保存路径"
        )
        if file_path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, file_path)

    def log(self, message):
        def update_log():
            self.log_area.config(state=tk.NORMAL)
            self.log_area.insert(tk.END, message + "\n")
            self.log_area.see(tk.END)
            self.log_area.config(state=tk.DISABLED)
        self.root.after(0, update_log)

    def get_md_language(self, filename):
        """根据后缀映射 Markdown 语言标识，帮助 AI 准确识别语法"""
        ext = os.path.splitext(filename)[1].lower()
        lang_map = {
            '.kt': 'kotlin', '.kts': 'kotlin', '.java': 'java', '.xml': 'xml',
            '.toml': 'toml', '.gradle': 'groovy', '.json': 'json', '.py': 'python',
            '.js': 'javascript', '.ts': 'typescript', '.cpp': 'cpp', '.c': 'c',
            '.h': 'c', '.hpp': 'cpp', '.cs': 'csharp', '.html': 'html', '.css': 'css',
            '.md': 'markdown', '.sh': 'bash', '.yaml': 'yaml', '.yml': 'yaml'
        }
        return lang_map.get(ext, '')

    def start_merge_thread(self):
        self.save_config() # 开始时顺手保存一下配置
        self.btn_merge.config(state=tk.DISABLED, text="⏳ 正在深度提取并构建 AI 知识库...", bg='#555555')
        thread = threading.Thread(target=self.execute_merge, daemon=True)
        thread.start()

    def open_folder(self, path):
        """跨平台打开文件夹"""
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin": # macOS
                import subprocess
                subprocess.Popen(["open", path])
            else: # Linux
                import subprocess
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            self.log(f"⚠️ 自动打开文件夹失败: {e}")

    def execute_merge(self):
        try:
            project_path = self.path_entry.get().strip()
            output_file = self.output_entry.get().strip()
            
            raw_exts = self.ext_entry.get().split(',')
            extensions = tuple(ext.strip() if ext.strip().startswith('.') else f".{ext.strip()}" for ext in raw_exts if ext.strip())
            
            exclude_dirs = set(d.strip() for d in self.exclude_entry.get().split(',') if d.strip())

            if not os.path.exists(project_path):
                self.root.after(0, lambda: messagebox.showerror("错误", "项目路径不存在！"))
                return

            output_dir = os.path.dirname(os.path.abspath(output_file))
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            self.root.after(0, lambda:[self.log_area.config(state=tk.NORMAL), self.log_area.delete(1.0, tk.END), self.log_area.config(state=tk.DISABLED)])
            self.log("▶️ 启动 KANE AI 智能代码提取任务...")
            
            output_abs_path = os.path.abspath(output_file)
            
            # 第一阶段：扫描并收集文件路径 (生成给 AI 看的全局目录)
            self.log("🔍 正在扫描项目文件结构...")
            valid_files =[]
            
            for root, dirs, files in os.walk(project_path):
                # 💥 核心改进1：就地修改 dirs 列表，告诉 os.walk 不要进入被排除的文件夹！极大地节约性能。
                dirs[:] = [d for d in dirs if d not in exclude_dirs]

                for file in files:
                    if file.endswith(extensions):
                        full_path = os.path.join(root, file)
                        
                        if os.path.abspath(full_path) == output_abs_path:
                            continue

                        # 💥 核心改进2：防爆破保护，超过 2MB 的文件直接跳过，防止大模型 Token 被撑爆
                        file_size_mb = os.path.getsize(full_path) / (1024 * 1024)
                        if file_size_mb > 2.0:
                            self.log(f"⚠️ 跳过超大文件 (大于 2MB): {file}")
                            continue
                            
                        valid_files.append((file, full_path))

            if not valid_files:
                self.log("⚠️ 未找到任何匹配的代码文件！")
                self.root.after(0, lambda: messagebox.showwarning("警告", "未找到符合条件的文件！"))
                return

            # 第二阶段：写入 Markdown 格式
            count = 0
            total_lines = 0
            total_chars = 0
            
            self.log("✍️ 正在生成 Markdown 文件...")
            with open(output_file, 'w', encoding='utf-8') as f:
                
                # --- 生成给 AI 预读的全局上下文信息 ---
                f.write(f"# 📦 项目全局代码库 (由 KANE AI 自动提取)\n\n")
                f.write(f"- **提取时间:** `{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n")
                f.write(f"- **根目录:** `{project_path}`\n")
                f.write(f"- **包含文件总数:** `{len(valid_files)}`\n\n")
                
                # --- 生成项目索引列表 (巨幅提升 AI 对项目结构的理解能力) ---
                f.write("## 🗂️ 提取文件目录索引\n\n> 提示 AI: 以下是本次提供源码的文件列表，便于建立全局依赖认知。\n\n")
                for filename, filepath in valid_files:
                    # 获取相对于项目根目录的相对路径
                    rel_path = os.path.relpath(filepath, project_path)
                    f.write(f"- `{rel_path}`\n")
                f.write("\n---\n\n")
                
                f.write("## 💻 详细源代码内容\n\n")

                # 开始遍历读取文件内容
                for file, full_path in valid_files:
                    self.log(f"➕ 提取并格式化: {file}")
                    
                    content_text = None
                    for enc in ['utf-8', 'gbk']:
                        try:
                            with open(full_path, 'r', encoding=enc) as content_file:
                                content_text = content_file.read()
                            break
                        except UnicodeDecodeError:
                            continue
                        except Exception:
                            break
                            
                    if content_text is None:
                        try:
                            with open(full_path, 'r', encoding='utf-8', errors='ignore') as content_file:
                                content_text = content_file.read()
                                self.log(f"⚠️ 强制读取 (包含非法字符): {file}")
                        except Exception as e:
                            self.log(f"❌ 读取失败 {file}: {str(e)}")
                            continue
                    
                    # 💥 核心改进3：使用标准的 Markdown 代码块格式
                    rel_path = os.path.relpath(full_path, project_path)
                    md_lang = self.get_md_language(file)
                    
                    f.write(f"### 📄 目标文件: `{file}`\n")
                    f.write(f"> 相对路径: `{rel_path}`\n\n")
                    f.write(f"```{md_lang}\n") # 例如 ```kotlin 或者 ```xml
                    f.write(content_text)
                    if not content_text.endswith('\n'):
                        f.write("\n")
                    f.write("```\n\n")
                    
                    count += 1
                    total_lines += content_text.count('\n') + 1
                    total_chars += len(content_text)

            # 💥 核心改进4：AI 指标预估 (约 4个字符=1个Token)
            estimated_tokens = total_chars // 4
            self.log("\n" + "★"*30)
            self.log(f"✅ 任务完美完成！共合并 {count} 个文件。")
            self.log(f"📊 统计数据: 约 {total_lines} 行代码, {total_chars} 个字符。")
            self.log(f"🤖 AI Token预估: 约 {estimated_tokens} Tokens。")
            self.log(f"📍 保存在: {output_abs_path}")
            self.log("★"*30)
            
            self.open_folder(output_dir)
            msg = f"Markdown 提取完成！共 {count} 个文件。\n\n预估: {total_lines} 行 | 消耗约 {estimated_tokens} Token\n\nAI投喂建议: 直接将生成的 .md 文件拖入 ChatGPT/Claude 对话框即可！\n\n结果已保存至:\n{output_file}"
            self.root.after(0, lambda: messagebox.showinfo("成功", msg))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("致命错误", str(e)))
        finally:
            self.root.after(0, lambda: self.btn_merge.config(state=tk.NORMAL, text="🚀 开始提取并生成 Markdown", bg='#007ACC'))

if __name__ == "__main__":
    root = tk.Tk()
    app = CodeMergerUI(root)
    root.mainloop()
