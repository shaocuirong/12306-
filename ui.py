import tkinter as tk
from tkinter import ttk
from datetime import datetime
from tkcalendar import DateEntry  # 导入tkcalendar中的DateEntry
import Getticket
import time
import json
import threading

# 实例化 GetTicket 类
web = Getticket.GetTicket()

# 定义保存文件路径
USER_DATA_FILE = "user_data.json"

class TicketUI:
    def __init__(self, root):
        self.root = root
        self.root.title("12306 抢票助手")
        self.root.geometry("800x700")

        # 定义座位类别和限制条件
        self.seat_options = {
            "特等座": ["A", "C", "F"],
            "商务座": ["A", "C", "F"],
            "一等座": ["A", "C", "D", "F"],
            "二等座": ["A", "B", "C", "D", "F"],
            "高级动卧": [""],
            "高级软卧": [""],
            "一等卧": [""],
            "动卧": [""],
            "二等卧": [""],
            "硬座": [""],
            "软座": [""],
            "硬卧": [""],
            "软卧": [""]
        }
        self.seat_position_codes ={
            "特等座": "P",
            "商务座": "9",
            "一等座": "M",
            "二等座": "O",
            "高级动卧": "A",
            "高级软卧": "6",
            "一等卧": "I",
            "动卧": "F",
            "二等卧": "J",
            "硬座": "1",
            "软座": "2",
            "硬卧": "3",
            "软卧": "4"
        }
        # 初始化UI
        self.setup_ui()

        # 加载用户数据
        self.load_user_data()

    def setup_ui(self):
        # 日志框
        self.log_frame = tk.Frame(self.root)
        self.log_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        self.log_text = tk.Text(self.log_frame, wrap=tk.WORD, height=10, font=("楷体", 10))
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar = tk.Scrollbar(self.log_frame, command=self.log_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text['yscrollcommand'] = self.scrollbar.set
        self.log("程序启动成功！")

        # 用户信息设置
        self.user_frame = tk.LabelFrame(self.root, text="用户信息", font=("楷体", 12))
        self.user_frame.pack(pady=10, fill=tk.X)

        tk.Label(self.user_frame, text="姓名:", font=("楷体", 12)).grid(row=0, column=0, padx=5)
        self.name_entry = tk.Entry(self.user_frame, width=20, font=("楷体", 12))
        self.name_entry.grid(row=0, column=1, padx=5)

        tk.Label(self.user_frame, text="性别 (0 男, 1 女):", font=("楷体", 12)).grid(row=0, column=2, padx=5)
        self.gender_entry = tk.Entry(self.user_frame, width=10, font=("楷体", 12))
        self.gender_entry.grid(row=0, column=3, padx=5)

        tk.Label(self.user_frame, text="身份证号:", font=("楷体", 12)).grid(row=1, column=0, padx=5)
        self.id_entry = tk.Entry(self.user_frame, width=25, font=("楷体", 12))
        self.id_entry.grid(row=1, column=1, padx=5)

        tk.Label(self.user_frame, text="手机号:", font=("楷体", 12)).grid(row=1, column=2, padx=5)
        self.phone_entry = tk.Entry(self.user_frame, width=15, font=("楷体", 12))
        self.phone_entry.grid(row=1, column=3, padx=5)

        # 座位等级和位置选择
        tk.Label(self.user_frame, text="座位等级:", font=("楷体", 12)).grid(row=2, column=0, padx=5)
        self.seat_class = ttk.Combobox(self.user_frame, font=("楷体", 12), state="readonly")
        self.seat_class['values'] = list(self.seat_options.keys())
        self.seat_class.grid(row=2, column=1, padx=5)
        self.seat_class.bind("<<ComboboxSelected>>", self.update_seat_positions)

        tk.Label(self.user_frame, text="座位位置:", font=("楷体", 12)).grid(row=2, column=2, padx=5)
        self.seat_position = ttk.Combobox(self.user_frame, font=("楷体", 12), state="readonly")
        self.seat_position.grid(row=2, column=3, padx=5)

        # 行程信息设置
        self.trip_frame = tk.LabelFrame(self.root, text="行程信息", font=("楷体", 12))
        self.trip_frame.pack(pady=10, fill=tk.X)

        tk.Label(self.trip_frame, text="出发城市:", font=("楷体", 12)).grid(row=0, column=0, padx=5)
        self.start_city_entry = tk.Entry(self.trip_frame, width=20, font=("楷体", 12))
        self.start_city_entry.grid(row=0, column=1, padx=5)

        tk.Label(self.trip_frame, text="出发车站:", font=("楷体", 12)).grid(row=0, column=2, padx=5)
        self.start_station_entry = ttk.Combobox(self.trip_frame, width=20, font=("楷体", 12))
        self.start_station_entry.grid(row=0, column=3, padx=5)
        self.start_station_entry.bind('<KeyRelease>', self.update_start_combobox)

        tk.Label(self.trip_frame, text="目的城市:", font=("楷体", 12)).grid(row=1, column=0, padx=5)
        self.end_city_entry = tk.Entry(self.trip_frame, width=20, font=("楷体", 12))
        self.end_city_entry.grid(row=1, column=1, padx=5)

        tk.Label(self.trip_frame, text="目的车站:", font=("楷体", 12)).grid(row=1, column=2, padx=5)
        self.end_station_entry = ttk.Combobox(self.trip_frame, width=20, font=("楷体", 12))
        self.end_station_entry.grid(row=1, column=3, padx=5)
        self.end_station_entry.bind('<KeyRelease>', self.update_end_combobox)

        tk.Label(self.trip_frame, text="乘车日期(YYYY-MM-DD):", font=("楷体", 12)).grid(row=2, column=0, padx=5)
        self.date_entry = DateEntry(self.trip_frame, width=18, font=("楷体", 12), date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=2, column=1, padx=5)
        # self.date_entry.grid(row=2, column=1, padx=5)

        tk.Label(self.trip_frame, text="车次列表 (逗号分隔):", font=("楷体", 12)).grid(row=2, column=2, padx=5)
        self.train_id_entry = tk.Entry(self.trip_frame, width=25, font=("楷体", 12))
        self.train_id_entry.grid(row=2, column=3, padx=5)

        # 抢票时间设置
        self.target_time_label = tk.Label(self.root, text="设置抢票时间 (格式: YYYY-MM-DD HH:MM:SS):", font=("楷体", 12))
        self.target_time_label.pack(pady=5)
        self.target_time_entry = tk.Entry(self.root, width=30, font=("楷体", 12))
        self.target_time_entry.pack(pady=5)
        # 操作按钮
        self.login_button = tk.Button(self.root, text="登录", font=("楷体", 12), command=self.start_login_thread)
        self.login_button.pack(pady=5)

        self.start_button = tk.Button(self.root, text="开始抢票", font=("楷体", 12), command=self.start_ticket_grab_thread)
        self.start_button.pack(pady=5)

    # 更新Combobox的内容
    def update_start_combobox(self,event):
        query = self.start_station_entry.get().lower()  # 获取输入并转为小写
        matched_items = []

        # 根据输入的内容匹配字典的键
        if query:
            for key in web.user.CITYCODE.keys():
                if query in key.lower():  # 如果字典键包含输入字符
                    matched_items.append(key)
        # 更新Combobox的内容，只显示前5项匹配
        self.start_station_entry['values'] = matched_items[:5]
        current_text = self.start_station_entry.get()
        if current_text not in matched_items:
            self.start_station_entry.set(current_text)  # 保持原本输入的文本
    # 更新Combobox的内容
    def update_end_combobox(self, event):
        query = self.end_station_entry.get().lower()  # 获取输入并转为小写
        matched_items = []
        # 根据输入的内容匹配字典的键
        if query:
            for key in web.user.CITYCODE.keys():
                if query in key.lower():  # 如果字典键包含输入字符
                    matched_items.append(key)
        # 更新Combobox的内容，只显示前5项匹配
        self.end_station_entry['values'] = matched_items[:5]
        current_text = self.end_station_entry.get()
        if current_text not in matched_items:
            self.end_station_entry.set(current_text)  # 保持原本输入的文本

    def log(self, message):
        """记录日志信息并实时更新界面"""
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert(tk.END, f"[{time_str}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()  # 强制刷新界面

    def update_seat_positions(self, event):
        """根据座位等级更新可选位置"""
        selected_class = self.seat_class.get()
        positions = self.seat_options.get(selected_class, ["不可选"])
        self.seat_position['values'] = positions
        self.seat_position.current(0)

    def start_login_thread(self):
        """启动登录线程"""
        thread = threading.Thread(target=self.login)
        thread.daemon = True  # 设置为守护线程
        thread.start()

    def login(self):
        """执行登录"""
        try:
            self.save_user_data()
            web.get_cookies()
            self.log("请扫描二维码登录...")
            web.login()
            result = web.check_login_status()
            if result:
                self.log("登录成功！")
            else:
                self.log("登录失败，请重试！")

        except Exception as e:
            self.log(f"登录失败: {str(e)}")

    def start_ticket_grab_thread(self):
        """启动抢票线程"""
        thread = threading.Thread(target=self.start_ticket_grab)
        thread.daemon = True  # 设置为守护线程
        thread.start()

    def start_ticket_grab(self):
        """开始抢票"""
        try:
            # 更新用户信息
            web.user.NAME = self.name_entry.get().strip()
            web.user.GENDER = self.gender_entry.get().strip()
            web.user.ID = self.id_entry.get().strip()
            web.user.PHONE_NUMBER = self.phone_entry.get().strip()
            web.user.TICKET_CLASS = self.seat_position_codes[self.seat_class.get()]
            web.user.choose_seats = self.seat_position.get()
            web.user.start_city = self.start_city_entry.get().strip()
            web.user.start_station = self.start_station_entry.get().strip()
            web.user.end_city = self.end_city_entry.get().strip()
            web.user.end_station = self.end_station_entry.get().strip()
            web.user.train_date = self.date_entry.get().strip()
            web.user.TRAIN_ID_LIST = self.train_id_entry.get().strip().split(',')
            self.save_user_data()
            # 验证时间格式
            target_time_str = self.target_time_entry.get().strip()
            print('检查登陆状态')
            result = web.check_login_status()
            if result:
                self.log(f"登陆状态正常")
            else:
                self.log(f"登录状态异常，请重新登录！")
                return 0
            web.check_login_status()
            target_time = datetime.strptime(target_time_str, "%Y-%m-%d %H:%M:%S")
            self.log(f"抢票设置时间为: {target_time_str}")
            self.log(f"用户: {web.user.NAME}, 车次: {web.user.TRAIN_ID_LIST}, 座位等级: {web.user.TICKET_CLASS}")
            self.log("等待抢票时间到达...")
            last_login_time = datetime.now().minute  # 记录上一次登录的分钟数
            while True:
                now = datetime.now()
                # 每两分钟检查一次登录状态
                if (now.minute % 2) == 0 and now.minute != last_login_time:
                    self.log(f"正在检查登录状态...")
                    result = web.check_login_status()
                    if result:
                        last_login_time = now.minute
                        self.log(f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
                        self.log(f"登陆状态正常")
                    else:
                        self.log(f"登录状态异常，请重新登录！")
                        break  # 登录失败退出循环
                # 判断当前时间是到达目标时间
                if now >= target_time:
                    # 执行抢票程序
                    # time.sleep(0.1)
                    self.log("抢票时间到达，开始抢票...")
                    web.run()
                    result = web.check_login_status()
                    if result:
                        self.log("抢票成功！请10分钟内到在 12306 支付订单。")
                        break
                    else:
                        self.log("抢票失败，请重试！")
                        break  # 执行完退出循环
                time.sleep(1)  # 间隔 1 秒再检查一次
        except ValueError:
            self.log("时间格式错误，请检查输入格式！")
        except ConnectionError:
            self.log("网络异常，请检查网络连接！")
        except Exception as e:
            self.log(f"抢票失败: {str(e)}")

    def save_user_data(self):
        """保存用户输入数据到文件"""
        data = {
            "name": self.name_entry.get().strip(),
            "gender": self.gender_entry.get().strip(),
            "id": self.id_entry.get().strip(),
            "phone": self.phone_entry.get().strip(),
            "seat_class": self.seat_class.get(),
            "seat_position": self.seat_position.get(),
            "start_city": self.start_city_entry.get().strip(),
            "start_station": self.start_station_entry.get().strip(),
            "end_city": self.end_city_entry.get().strip(),
            "end_station": self.end_station_entry.get().strip(),
            # "train_date": self.date_entry.get().strip(),
            "train_id_list": self.train_id_entry.get().strip(),
            "target_time": self.target_time_entry.get().strip()
        }
        with open(USER_DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        self.log("用户数据已保存！")

    def load_user_data(self):
        """从文件加载用户数据"""
        try:
            with open(USER_DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                self.name_entry.insert(0, data.get("name", ""))
                self.gender_entry.insert(0, data.get("gender", ""))
                self.id_entry.insert(0, data.get("id", ""))
                self.phone_entry.insert(0, data.get("phone", ""))
                self.seat_class.set(data.get("seat_class", ""))
                self.seat_position.set(data.get("seat_position", ""))
                self.start_city_entry.insert(0, data.get("start_city", ""))
                self.start_station_entry.insert(0, data.get("start_station", ""))
                self.end_city_entry.insert(0, data.get("end_city", ""))
                self.end_station_entry.insert(0, data.get("end_station", ""))
                # self.date_entry.insert(0, data.get("train_date", ""))
                self.train_id_entry.insert(0, data.get("train_id_list", ""))
                self.target_time_entry.insert(0, data.get("target_time", ""))
                self.log("用户数据已加载！")
        except FileNotFoundError:
            self.log("未找到用户数据文件，使用默认设置")
        except json.JSONDecodeError:
            self.log("用户数据文件格式错误，请检查！")


if __name__ == "__main__":
    root = tk.Tk()
    app = TicketUI(root)
    root.mainloop()
