import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, Frame, Label, Entry, Button
from datetime import datetime, timedelta
import json
import os

# 自动创建可靠的数据存储路径
DATA_DIR = os.path.join(os.path.expanduser("~"), "AppData", "Local", "ToDoList")
os.makedirs(DATA_DIR, exist_ok=True)  # 自动创建目录
DATA_FILE = os.path.join(DATA_DIR, "todolist_data.json")

class ToDoList:
    def __init__(self, root):
        print("数据文件路径：", DATA_FILE)
        self.root = root
        self.root.title("ToDoList")
        self.root.geometry("800x900")
        self.root.minsize(600, 700)
        
        self.tasks = []
        self.search_keyword = tk.StringVar()
        self.start_date = tk.StringVar()
        self.end_date = tk.StringVar()
        
        self.load_data()
        self.create_widgets()
        self.refresh_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        # 顶部输入区域
        management_frame = ttk.LabelFrame(self.root, text="管理任务", padding=10)
        management_frame.pack(fill=tk.X, padx=10, pady=5, anchor="nw")

        # 生成带日期的选项
        days = ["今天", "明天", "后天"]
        today = datetime.today()
        self.date_options = [
            f"{day} ({(today + timedelta(days=i)).strftime('%m-%d')})"
            for i, day in enumerate(days)
        ]
        
        self.date_var = tk.StringVar()
        date_combobox = ttk.Combobox(management_frame, textvariable=self.date_var, 
                                   values=self.date_options, state="readonly")
        date_combobox.current(0)
        date_combobox.pack(side=tk.LEFT, padx=5)

        self.task_entry = ttk.Entry(management_frame)
        self.task_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.task_entry.bind("<Return>", lambda e: self.add_task())

        add_btn = ttk.Button(management_frame, text="添加", command=self.add_task)
        add_btn.pack(side=tk.LEFT)

        # 待办任务区域
        self.task_frame = ttk.LabelFrame(self.root, text="待办任务", padding=10)
        self.task_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 搜索区域
        search_frame = ttk.LabelFrame(self.root, text="完成记录搜索", padding=10)
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(search_frame, text="关键词:").pack(side=tk.LEFT)
        ttk.Entry(search_frame, textvariable=self.search_keyword, width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(search_frame, text="开始日期:").pack(side=tk.LEFT, padx=(10,0))
        ttk.Entry(search_frame, textvariable=self.start_date, width=12).pack(side=tk.LEFT)
        
        ttk.Label(search_frame, text="结束日期:").pack(side=tk.LEFT, padx=(10,0))
        ttk.Entry(search_frame, textvariable=self.end_date, width=12).pack(side=tk.LEFT)
        
        ttk.Button(search_frame, text="搜索", command=self.refresh_ui).pack(side=tk.LEFT, padx=10)

        # 已完成任务区域
        self.completed_frame = ttk.LabelFrame(self.root, text="已完成任务", padding=10)
        self.completed_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def add_task(self):
        task_text = self.task_entry.get().strip()
        if not task_text:
            messagebox.showwarning("提示", "请输入任务内容！")
            return
        
        # 从带日期的选项中解析天数
        selected = self.date_var.get()
        days_map = {
            self.date_options[0]: 0,
            self.date_options[1]: 1,
            self.date_options[2]: 2
        }
        
        due_date = datetime.today() + timedelta(days=days_map[selected])
        
        self.tasks.append({
            "text": task_text,
            "due_date": due_date.strftime("%Y-%m-%d"),
            "completed_date": None,
            "done": False,
            "note": ""
        })
        self.task_entry.delete(0, tk.END)
        self.refresh_ui()

    def refresh_ui(self):
        self.refresh_task_list()
        self.refresh_completed_tasks()

    def refresh_task_list(self):
        for widget in self.task_frame.winfo_children():
            widget.destroy()

        # 创建表头
        header_frame = ttk.Frame(self.task_frame)
        header_frame.pack(fill=tk.X, pady=5)
        ttk.Label(header_frame, text="到期日", width=10, anchor="w").pack(side=tk.LEFT, padx=5)
        ttk.Label(header_frame, text="任务内容", anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(header_frame, text="备注", width=39,anchor="center").pack(side=tk.RIGHT)

        # 分离普通任务和逾期任务
        today = datetime.today().date()
        normal_tasks = []
        overdue_tasks = []
        
        for task in self.tasks:
            if not task["done"]:
                task_date = datetime.strptime(task["due_date"], "%Y-%m-%d").date()
                if task_date < today:
                    overdue_tasks.append(task)
                else:
                    normal_tasks.append(task)

        # 显示普通任务
        for task in normal_tasks:
            self.create_task_row(task)

        # 添加分隔线
        if overdue_tasks:
            ttk.Separator(self.task_frame, orient="horizontal").pack(fill=tk.X, pady=10)

            # 显示逾期任务标题
            overdue_header = ttk.Frame(self.task_frame)
            overdue_header.pack(fill=tk.X)
            ttk.Label(overdue_header, text="【逾期任务】", foreground="red").pack(side=tk.LEFT)

            # 显示逾期任务
            for task in overdue_tasks:
                self.create_task_row(task, overdue=True)

    def create_task_row(self, task, overdue=False):
        frame = ttk.Frame(self.task_frame)
        frame.pack(fill=tk.X, pady=2)

    # 到期日（显示为MM-DD格式）
        task_date = datetime.strptime(task["due_date"], "%Y-%m-%d")
        date_label = ttk.Label(frame, text=task_date.strftime("%m-%d"), width=10, anchor="w")
        date_label.pack(side=tk.LEFT, padx=5)

        # 任务内容
        text_label = ttk.Label(frame, text=task["text"], anchor="w")
        text_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 备注输入框
        note_frame = ttk.Frame(frame)
        note_frame.pack(side=tk.RIGHT, padx=5)
        note_entry = ttk.Entry(note_frame, width=20)
        note_entry.pack(side=tk.LEFT)
        note_entry.insert(0, task.get("temp_note", ""))  # 临时保存未提交的备注

       # 操作按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(side=tk.RIGHT)
        
        if overdue:
            del_btn = ttk.Button(btn_frame, text="删除", width=5, 
                               command=lambda t=task: self.delete_task(t))
            del_btn.pack(side=tk.RIGHT, padx=2)
            
        done_btn = ttk.Button(btn_frame, text="完成", width=5,
                            command=lambda t=task, e=note_entry: self.mark_as_done(t, e))
        done_btn.pack(side=tk.RIGHT, padx=2)


    def refresh_completed_tasks(self):
        for widget in self.completed_frame.winfo_children():
            widget.destroy()

        # 应用搜索条件
        keyword = self.search_keyword.get().lower()
        start_date = self.start_date.get()
        end_date = self.end_date.get()
        
        filtered = []
        for task in self.tasks:
            if task["done"]:
                # 时间范围筛选
                if start_date or end_date:
                    try:
                        comp_date = datetime.strptime(task["completed_date"], "%Y-%m-%d %H:%M")
                        if start_date:
                            start = datetime.strptime(start_date, "%Y-%m-%d")
                            if comp_date.date() < start.date():
                                continue
                        if end_date:
                            end = datetime.strptime(end_date, "%Y-%m-%d")
                            if comp_date.date() > end.date():
                                continue
                    except:
                        pass
                
                # 关键字筛选
                if keyword:
                    if keyword not in task["text"].lower() and keyword not in task["note"].lower():
                        continue
                
                filtered.append(task)

        # 创建滚动容器
        canvas = tk.Canvas(self.completed_frame)
        scrollbar = ttk.Scrollbar(self.completed_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 添加表头
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.pack(fill=tk.X, pady=5)
        ttk.Label(header_frame, text="完成时间", width=20, anchor="w").pack(side=tk.LEFT, padx=5)
        ttk.Label(header_frame, text="任务内容", anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(header_frame, text="备注", width=20, anchor="w").pack(side=tk.RIGHT, padx=5)

        # 添加任务条目
        for task in sorted(filtered, key=lambda x: x["completed_date"], reverse=True):
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill=tk.X, pady=2)
            
            # 完成时间列
            ttk.Label(frame, text=task["completed_date"], width=20, anchor="w").pack(
                side=tk.LEFT, padx=5)
            
            # 任务内容列
            ttk.Label(frame, text=task["text"], anchor="w").pack(
                side=tk.LEFT, fill=tk.X, expand=True)
            
            # 备注列
            ttk.Label(frame, text=task["note"], width=20, anchor="w").pack(
                side=tk.RIGHT, padx=5)

        # 布局滚动组件
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def mark_as_done(self, task, note_entry):
        note = note_entry.get().strip()[:30]  # 限制30个字符
        task["note"] = note
        task["done"] = True
        task["completed_date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.refresh_ui()

    def delete_task(self, task):
        self.tasks.remove(task)
        self.refresh_ui()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.tasks = json.load(f)
            except Exception as e:
                messagebox.showerror("错误", f"加载数据失败：{str(e)}")

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("错误", f"保存数据失败：{str(e)}")

    def on_close(self):
        self.save_data()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ToDoList(root)
    root.mainloop()