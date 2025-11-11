from kivy.clock import mainthread, Clock
from kivy.core.text import LabelBase
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.list import OneLineListItem, MDList, TwoLineListItem
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.label import MDLabel
from kivy.graphics import Color, Line, Rectangle, Ellipse
from kivy.uix.widget import Widget
from kivy.uix.label import Label

import os
from kivy.core.text import LabelBase
from kivy.utils import platform
from peewee import SqliteDatabase, Model, TextField, DateTimeField, AutoField, DateField
from datetime import datetime, date, timedelta
from kivy.metrics import dp
import sys
import csv
import math

# 修复Android模块导入 - 更安全的处理
ANDROID = False
try:
    from kivy import platform
    if platform == 'android':
        ANDROID = True
        print("Android环境检测成功")
except ImportError:
    ANDROID = False
    print("非Android环境，跳过Android模块导入")

# 设置数据库路径 - 更安全的路径处理
if ANDROID:
    try:
        from android.storage import app_storage_path
        DB_DIR = app_storage_path()
        DB_PATH = os.path.join(DB_DIR, "data.db")
        print(f"Android数据库路径: {DB_PATH}")
    except Exception as e:
        print(f"Android路径获取失败: {e}")
        # 备用路径
        DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")

db = SqliteDatabase(DB_PATH)


class Entry(Model):
    id = AutoField()
    title = TextField(null=True)
    value = TextField(null=True)
    created_at = DateTimeField(default=datetime.now)  # 使用本地时间
    date = DateField(null=True)
    period = TextField(null=True)

    class Meta:
        database = db


def _ensure_date(obj):
    """把可能为字符串的 date 字段转换为 datetime.date"""
    if obj is None:
        return None
    if isinstance(obj, date) and not isinstance(obj, datetime):
        return obj
    s = str(obj).strip()
    # 支持 YYYY-MM-DD 或 ISO 格式
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except Exception:
            pass
    try:
        return datetime.fromisoformat(s).date()
    except Exception:
        # 若包含时间部分，尝试解析为 datetime 再取 date
        try:
            return _ensure_datetime(s).date()
        except Exception:
            return None


def _ensure_datetime(obj):
    """把可能为字符串的 datetime 字段转换为 datetime（支持到分钟/秒/ISO）"""
    if obj is None:
        return None
    if isinstance(obj, datetime):
        return obj
    s = str(obj).strip()
    # 去除可能的 BOM/特殊空白
    s = s.replace("\ufeff", "").strip()
    # 常见格式（从精确到毫秒到只到日期）
    fmts = (
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    )
    for fmt in fmts:
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            pass
    # 尝试 fromisoformat，兼容带时区的简易处理
    try:
        # 去掉末尾的 Z
        s2 = s.rstrip("Z")
        return datetime.fromisoformat(s2)
    except Exception:
        # 最后尝试纯数字时间戳（秒）
        try:
            if s.isdigit():
                return datetime.fromtimestamp(int(s))
        except Exception:
            pass
    return None


def init_db():
    """更安全的数据库初始化"""
    try:
        # 确保数据库目录存在
        db_dir = os.path.dirname(DB_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            print(f"创建数据库目录: {db_dir}")
        
        db.connect()
        db.create_tables([Entry])
        cursor = db.execute_sql("PRAGMA table_info(entry);")
        cols = [row[1] for row in cursor.fetchall()]
        if "date" not in cols:
            db.execute_sql("ALTER TABLE entry ADD COLUMN date TEXT;")
            try:
                db.execute_sql("UPDATE entry SET date = date(created_at) WHERE date IS NULL;")
            except Exception:
                pass
        if "period" not in cols:
            db.execute_sql("ALTER TABLE entry ADD COLUMN period TEXT;")
            db.execute_sql("UPDATE entry SET period = 'morning' WHERE period IS NULL;")
        print("数据库初始化成功")
    except Exception as e:
        print(f"数据库初始化错误: {e}")
        # 尝试重新连接
        try:
            db.close()
            db.connect()
            db.create_tables([Entry])
            print("数据库重新初始化成功")
        except Exception as e2:
            print(f"数据库重新初始化失败: {e2}")

def setup_chinese_font_early():
    """在应用初始化前设置中文字体"""
    try:
        # 可能的字体路径
        font_candidates = [
            os.path.join(os.path.dirname(__file__), "fonts", "simkai.ttf"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "simkai.ttf"),
            "fonts/simkai.ttf",
            "./fonts/simkai.ttf",
        ]
        
        # 如果是Android环境，添加系统字体路径
        if platform == 'android':
            font_candidates.extend([
                "/system/fonts/DroidSansFallback.ttf",
                "/system/fonts/NotoSansCJK-Regular.ttc",
            ])
        
        found_font = None
        for font_path in font_candidates:
            if font_path and os.path.exists(font_path):
                found_font = font_path
                print(f"找到中文字体: {found_font}")
                break
        
        if not found_font:
            print("警告: 未找到中文字体文件，尝试使用系统默认字体")
            # 在Android上使用DroidSansFallback
            if platform == 'android':
                found_font = "DroidSansFallback"
            else:
                # 在Windows上使用系统字体
                import sys
                if sys.platform == 'win32':
                    found_font = "simsun.ttc"  # 宋体
                else:
                    found_font = None
        
        if found_font:
            try:
                # 先检查是否已经注册
                if "ChineseFont" not in LabelBase._fonts:
                    LabelBase.register(
                        name="ChineseFont",
                        fn_regular=found_font,
                    )
                print(f"中文字体注册成功: {found_font}")
                return True
            except Exception as e:
                print(f"字体注册失败: {e}")
        
        return False
        
    except Exception as e:
        print(f"字体设置错误: {e}")
        return False

def setup_chinese_font():
    """设置中文字体支持 - 更安全的版本"""
    try:
        candidates = [
            os.path.join(os.path.dirname(__file__), "fonts", "simkai.ttf"),
        ]
        found = None
        for p in candidates:
            if p and os.path.exists(p):
                found = p
                break

        if not found:
            print("警告: 未找到可用的中文字体，使用默认字体")
            return False

        # 只注册中文字体，不覆盖图标字体
        try:
            LabelBase.register(
                name="ChineseFont",
                fn_regular=found,
                fn_bold=found,
                fn_italic=found,
                fn_bolditalic=found,
            )
        except Exception as e:
            print(f"注册 ChineseFont 失败: {e}")
            return False

        print(f"成功加载中文字体: {found}")
        return True
    except Exception as e:
        print(f"字体设置错误: {e}")
        return False


class TrendChart(Widget):
    def __init__(self, data=None, **kwargs):
        super().__init__(**kwargs)
        self.data = data or []
        self.month_range = 1  # 默认显示1个月
        self.labels = []  # 存储标签引用以便清除
        self.bind(size=self._update_canvas, pos=self._update_canvas)
        # 延迟初始化，避免启动时崩溃
        Clock.schedule_once(lambda dt: self._update_canvas(), 0.1)

    def set_data(self, data):
        """设置图表数据"""
        self.data = data
        self._clear_labels()
        self._update_canvas()

    def set_month_range(self, months):
        """设置显示的时间范围（月数）"""
        self.month_range = months
        self._clear_labels()
        self._update_canvas()
    
    def _clear_labels(self):
        """清除所有标签"""
        for label in self.labels:
            self.remove_widget(label)
        self.labels = []

    def _update_canvas(self, *args):
        """更新画布，绘制图表 - 添加异常处理"""
        try:
            # 清除所有图形指令
            self.canvas.clear()
            
            # 清除所有标签
            self._clear_labels()
            
            # 绘制深色背景
            with self.canvas:
                Color(0.1, 0.1, 0.1, 1)  # 深灰色背景
                Rectangle(pos=self.pos, size=self.size)
            
            if not self.data:
                # 没有数据时显示提示
                no_data_label = Label(
                    text="暂无数据",
                    font_size=dp(18),
                    color=(1, 1, 1, 1),  # 白色字体
                    bold=True
                )
                no_data_label.pos = (
                    self.x + self.width/2 - dp(40),
                    self.y + self.height/2 - dp(10)
                )
                self.add_widget(no_data_label)
                self.labels.append(no_data_label)
                return

            # 计算显示的数据范围
            end_date = date.today()
            start_date = end_date - timedelta(days=30 * self.month_range)
            
            # 过滤数据
            filtered_data = []
            for item in self.data:
                if start_date <= item['date'] <= end_date:
                    filtered_data.append(item)
            
            if not filtered_data:
                # 没有数据时显示提示
                no_data_label = Label(
                    text=f"所选时间段内暂无数据",
                    font_size=dp(16),
                    color=(1, 1, 1, 1)  # 白色字体
                )
                no_data_label.pos = (
                    self.x + self.width/2 - dp(100),
                    self.y + self.height/2 - dp(10)
                )
                self.add_widget(no_data_label)
                self.labels.append(no_data_label)
                return
            
            # 按日期排序
            filtered_data.sort(key=lambda x: x['date'])
            
            # 计算坐标范围和比例
            dates = [item['date'] for item in filtered_data]
            all_weights = []
            for item in filtered_data:
                if item['morning'] is not None:
                    all_weights.append(item['morning'])
                if item['evening'] is not None:
                    all_weights.append(item['evening'])
            
            if not all_weights:
                return
            
            min_weight = min(all_weights)
            max_weight = max(all_weights)
            weight_range = max_weight - min_weight if max_weight != min_weight else 1
            
            # 添加边距
            padding_x = dp(60)
            padding_y = dp(50)
            chart_width = self.width - 2 * padding_x
            chart_height = self.height - 2 * padding_y
            
            # 绘制深灰色网格背景
            with self.canvas:
                Color(0.2, 0.2, 0.2, 1)  # 深灰色背景
                Rectangle(
                    pos=(self.x + padding_x, self.y + padding_y),
                    size=(chart_width, chart_height)
                )
                
                # 绘制坐标轴
                Color(0.8, 0.8, 0.8, 1)  # 浅灰色坐标轴
                Line(
                    points=[
                        self.x + padding_x, self.y + padding_y, 
                        self.x + padding_x, self.y + padding_y + chart_height
                    ],
                    width=dp(1.5)
                )
                Line(
                    points=[
                        self.x + padding_x, self.y + padding_y,
                        self.x + padding_x + chart_width, self.y + padding_y
                    ],
                    width=dp(1.5)
                )
                
                # 绘制网格线和标签
                # Y轴网格和标签（体重）
                weight_steps = 6
                for i in range(weight_steps + 1):
                    y_val = min_weight + (weight_range * i / weight_steps)
                    y_pos = self.y + padding_y + (chart_height * i / weight_steps)
                    
                    # 网格线
                    Color(0.4, 0.4, 0.4, 0.8)  # 中等灰色网格线
                    Line(
                        points=[
                            self.x + padding_x, y_pos, 
                            self.x + padding_x + chart_width, y_pos
                        ],
                        width=dp(0.8)
                    )
                    
                    # Y轴刻度
                    Color(0.8, 0.8, 0.8, 1)  # 浅灰色刻度
                    Line(
                        points=[
                            self.x + padding_x - dp(3), y_pos,
                            self.x + padding_x, y_pos
                        ],
                        width=dp(1.2)
                    )
                
                # X轴网格和标签（日期）
                date_count = min(8, len(filtered_data))
                for i in range(date_count):
                    if i < len(filtered_data):
                        idx = int((len(filtered_data) - 1) * i / (date_count - 1)) if date_count > 1 else 0
                        x_pos = self.x + padding_x + (chart_width * idx / (len(filtered_data) - 1)) if len(filtered_data) > 1 else self.x + padding_x
                        
                        # 垂直网格线
                        Color(0.4, 0.4, 0.4, 0.5)  # 中等灰色网格线
                        Line(
                            points=[
                                x_pos, self.y + padding_y,
                                x_pos, self.y + padding_y + chart_height
                            ],
                            width=dp(0.5)
                        )
                        
                        # X轴刻度
                        Color(0.8, 0.8, 0.8, 1)  # 浅灰色刻度
                        Line(
                            points=[
                                x_pos, self.y + padding_y,
                                x_pos, self.y + padding_y - dp(3)
                            ],
                            width=dp(1.2)
                        )
            
            # 添加Y轴标签（体重数值）
            for i in range(weight_steps + 1):
                y_val = min_weight + (weight_range * i / weight_steps)
                y_pos = self.y + padding_y + (chart_height * i / weight_steps)
                
                # 体重数值标签
                label = Label(
                    text=f"{y_val:.1f}",
                    font_size=dp(12),
                    color=(1, 1, 1, 1),  # 白色字体
                    size=(dp(35), dp(20)),
                    halign='right',
                    valign='middle'
                )
                label.text_size = label.size
                label.pos = (self.x + padding_x - dp(40), y_pos - dp(10))
                self.add_widget(label)
                self.labels.append(label)
            
            # 添加X轴标签（日期）
            for i in range(date_count):
                if i < len(filtered_data):
                    idx = int((len(filtered_data) - 1) * i / (date_count - 1)) if date_count > 1 else 0
                    x_pos = self.x + padding_x + (chart_width * idx / (len(filtered_data) - 1)) if len(filtered_data) > 1 else self.x + padding_x
                    
                    # 日期标签
                    date_str = filtered_data[idx]['date'].strftime("%m/%d")
                    label = Label(
                        text=date_str,
                        font_size=dp(12),
                        color=(1, 1, 1, 1),  # 白色字体
                        size=(dp(40), dp(20)),
                        halign='center',
                        valign='middle'
                    )
                    label.text_size = label.size
                    label.pos = (x_pos - dp(20), self.y + padding_y - dp(25))
                    self.add_widget(label)
                    self.labels.append(label)
            
            # 绘制趋势线和数据点
            with self.canvas:
                morning_points = []
                evening_points = []
                morning_dots = []
                evening_dots = []
                
                for i, item in enumerate(filtered_data):
                    x = self.x + padding_x + (chart_width * i / (len(filtered_data) - 1)) if len(filtered_data) > 1 else self.x + padding_x
                    
                    # 早晨数据
                    if item['morning'] is not None:
                        y = self.y + padding_y + (chart_height * (item['morning'] - min_weight) / weight_range)
                        morning_points.extend([x, y])
                        morning_dots.append((x, y))
                    
                    # 晚间数据
                    if item['evening'] is not None:
                        y = self.y + padding_y + (chart_height * (item['evening'] - min_weight) / weight_range)
                        evening_points.extend([x, y])
                        evening_dots.append((x, y))
                
                # 绘制早晨趋势线（绿色）
                if len(morning_points) >= 4:
                    Color(0.2, 0.9, 0.2, 0.9)  # 更亮的绿色
                    Line(points=morning_points, width=dp(2.5))
                    
                    # 绘制早晨数据点
                    Color(0.1, 0.8, 0.1, 1)
                    for dot_x, dot_y in morning_dots:
                        Ellipse(
                            pos=(dot_x - dp(3), dot_y - dp(3)),
                            size=(dp(6), dp(6))
                        )
                
                # 绘制晚间趋势线（红色）
                if len(evening_points) >= 4:
                    Color(0.9, 0.2, 0.2, 0.9)  # 更亮的红色
                    Line(points=evening_points, width=dp(2.5))
                    
                    # 绘制晚间数据点
                    Color(0.8, 0.1, 0.1, 1)
                    for dot_x, dot_y in evening_dots:
                        Ellipse(
                            pos=(dot_x - dp(3), dot_y - dp(3)),
                            size=(dp(6), dp(6))
                        )
            
            # 添加图例 - 重新设计布局
            legend_y = self.y + self.height - dp(500)  # 降低图例位置，为标题腾出空间
            
            # 早晨图例 - 精确对齐
            with self.canvas:
                Color(0.2, 0.9, 0.2, 1)  # 更亮的绿色
                Line(
                    points=[self.x + dp(35), legend_y, self.x + dp(65), legend_y],
                    width=dp(2.5)
                )
            
            # 早晨文字标签 - 精确垂直居中对齐
            label_morning = Label(
                text="早晨体重",
                font_size=dp(14),
                color=(0.1, 0.1, 0.1, 1),  # 深色字体
                bold=True,
                font_name="ChineseFont",
            )
            # 计算文字高度并精确居中
            text_height = dp(0)  # 估计的文本高度
            label_morning.pos = (self.x + dp(0), legend_y - text_height/2)
            self.add_widget(label_morning)
            self.labels.append(label_morning)
            
            # 晚间图例 - 精确对齐
            with self.canvas:
                Color(0.9, 0.2, 0.2, 1)  # 更亮的红色
                Line(
                    points=[self.x + dp(155), legend_y, self.x + dp(185), legend_y],
                    width=dp(2.5)
                )
            
            # 晚间文字标签 - 精确垂直居中对齐
            label_evening = Label(
                text="晚间体重",
                font_size=dp(14),
                color=(0.1, 0.1, 0.1, 1),  # 深色字体
                bold=True,
                font_name="ChineseFont",
            )
            label_evening.pos = (self.x + dp(120), legend_y - text_height/2)
            self.add_widget(label_evening)
            self.labels.append(label_evening)
            
            # 添加标题 - 放在按钮上方，增大字体
            title_label = Label(
                text="体重趋势图",
                font_size=dp(25),  # 增大字体
                color=(1, 1, 1, 1),  # 白色字体
                bold=True,
                font_name="ChineseFont",
            )
            # 标题放在图表顶部，按钮上方
            title_label.pos = (self.x + self.width/2 - dp(50), self.y + self.height - dp(-25))
            self.add_widget(title_label)
            self.labels.append(title_label)
            
        except Exception as e:
            print(f"图表绘制错误: {e}")
            # 显示错误信息
            error_label = Label(
                text="图表加载失败",
                font_size=dp(16),
                color=(1, 0, 0, 1)
            )
            error_label.pos = (
                self.x + self.width/2 - dp(50),
                self.y + self.height/2 - dp(10)
            )
            self.add_widget(error_label)
            self.labels.append(error_label)


class MainScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 延迟初始化UI组件，避免启动时崩溃
        Clock.schedule_once(self._finish_init, 0.5)

    def _finish_init(self, dt):
        """延迟初始化UI组件"""
        try:
            # 请求Android权限（如果适用）
            if ANDROID:
                self._request_android_permissions()
            
            self._setup_ui()
            self.refresh_list()
            
        except Exception as e:
            print(f"界面初始化错误: {e}")
            self._show_error(f"应用启动失败: {e}")

    def _request_android_permissions(self):
        """在Android上请求权限"""
        try:
            from android.permissions import request_permissions, Permission
            permissions = [Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE]
            request_permissions(permissions)
            print("Android权限请求已发送")
        except Exception as e:
            print(f"权限请求失败: {e}")

    def _setup_ui(self):
        """设置用户界面"""
        # 主布局
        layout = MDBoxLayout(orientation="vertical", spacing=10, padding=10)

        # 顶部自定义工具栏
        top_bar = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(56),
            padding=(8, 0),
            spacing=0,
            md_bg_color=(0.2, 0.6, 0.8, 1),
        )

        # 左侧菜单按钮（标准三条杠）
        self.left_icon = MDIconButton(
            icon="menu",  # 三条杠样式
            icon_size="24sp",
            size_hint_x=None,
            width=dp(56),
            pos_hint={"center_y": 0.5},
        )
        self.left_icon.bind(on_release=lambda x: self.open_menu(x))

        # 中间标题 - 强制使用中文字体
        self.title_label = MDLabel(
            text="减肥数据记录",
            halign="center",
            valign="middle",
            size_hint_x=1,
            theme_text_color="Primary",
            font_name="ChineseFont",
        )

        # 右侧退出按钮（紧急出口 / 小人样式）
        self.right_icon = MDIconButton(
            icon="exit-to-app",  # 紧急出口/出入口小人样式
            icon_size="24sp",
            size_hint_x=None,
            width=dp(56),
            pos_hint={"center_y": 0.5},
        )
        self.right_icon.bind(on_release=lambda x: self.exit_app())

        top_bar.add_widget(self.left_icon)
        top_bar.add_widget(self.title_label)
        top_bar.add_widget(self.right_icon)

        layout.add_widget(top_bar)

        # 下拉菜单 - 强制使用中文字体
        self.menu = MDDropdownMenu(
            caller=self.left_icon,
            items=[
                {
                    "text": "查看详细历史",
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x="history": self.menu_callback(x),
                },
                {
                    "text": "数据统计",
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x="stats": self.menu_callback(x),
                },
                {
                    "text": "趋势图",
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x="trend": self.show_trend_chart(),
                },
                {
                    "text": "关于",
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x="about": self.menu_callback(x),
                },
                {
                    "text": "导出数据",
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x="export": self.export_data_to_csv(),
                },
                {
                    "text": "导入数据",
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x="import": self.import_data_from_csv(),
                },
            ],
            width_mult=4,
        )

        # 按钮区域 - 强制使用中文字体
        button_layout = MDBoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=dp(60))
        self.add_morning_btn = MDRaisedButton(text="记录早晨体重", size_hint_x=0.5, font_name="ChineseFont")
        self.add_evening_btn = MDRaisedButton(text="记录晚间体重", size_hint_x=0.5, font_name="ChineseFont")
        self.add_morning_btn.bind(on_release=lambda *a: self.open_weight_dialog("morning"))
        self.add_evening_btn.bind(on_release=lambda *a: self.open_weight_dialog("evening"))
        button_layout.add_widget(self.add_morning_btn)
        button_layout.add_widget(self.add_evening_btn)
        layout.add_widget(button_layout)

        # 历史记录列表 - 修复滑动问题
        self.scroll = MDScrollView()
        self.list_view = MDList()
        self.scroll.add_widget(self.list_view)
        layout.add_widget(self.scroll)

        self.add_widget(layout)
        self._dialog = None

    def open_menu(self, instance):
        try:
            self.menu.open()
        except Exception as e:
            print(f"打开菜单错误: {e}")
            self._show_error("打开菜单失败")

    def show_trend_chart(self):
        """显示趋势图对话框"""
        try:
            self.menu.dismiss()
            
            # 获取数据并准备图表数据
            entries = Entry.select().order_by(Entry.date.asc())
            chart_data = self._prepare_chart_data(entries)
            
            # 创建图表容器 - 增加高度以容纳更多空间
            chart_container = MDBoxLayout(orientation="vertical", spacing=10, padding=10, size_hint_y=None)
            chart_container.height = dp(520)  # 增加高度以容纳更大的标题
            
            # 时间范围选择
            range_layout = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=10)
            range_label = MDLabel(
                text="显示范围:", 
                size_hint_x=None, 
                width=dp(80), 
                font_name="ChineseFont",
                theme_text_color="Primary"
            )
            range_layout.add_widget(range_label)
            
            # 存储按钮引用以便后续更新
            self.range_buttons = {}
            
            # 时间范围按钮
            for months in [1, 3, 6, 12]:
                btn = MDRaisedButton(
                    text=f"{months}个月",
                    size_hint_x=None,
                    width=dp(70),
                    font_name="ChineseFont",
                    md_bg_color=(0.2, 0.6, 0.8, 1) if months == 1 else (0.5, 0.5, 0.5, 1)
                )
                btn.months = months
                btn.bind(on_release=lambda x: self.update_chart_range(x.months))
                range_layout.add_widget(btn)
                self.range_buttons[months] = btn
            
            chart_container.add_widget(range_layout)
            
            # 图表区域
            self.trend_chart = TrendChart(data=chart_data, size_hint_y=1)
            chart_container.add_widget(self.trend_chart)
            
            # 提示信息
            info_label = MDLabel(
                text="绿色: 早晨体重 | 红色: 晚间体重",
                halign="center",
                theme_text_color="Secondary",
                font_name="ChineseFont",
                size_hint_y=None,
                height=dp(30)
            )
            chart_container.add_widget(info_label)
            
            content = MDBoxLayout(orientation="vertical", spacing=10, padding=10)
            content.add_widget(chart_container)
            
            self.trend_dialog = MDDialog(
                title="体重趋势图",
                type="custom",
                content_cls=content,
                buttons=[
                    MDFlatButton(
                        text="关闭", 
                        on_release=lambda *a: self.trend_dialog.dismiss(), 
                        font_name="ChineseFont"
                    )
                ],
                size_hint=(0.95, 0.9)
            )
            self.trend_dialog.open()
            
        except Exception as e:
            print(f"显示趋势图错误: {e}")
            self._show_error(f"显示趋势图失败: {e}")

    def update_chart_range(self, months):
        """更新图表显示的时间范围"""
        try:
            if hasattr(self, 'trend_chart'):
                self.trend_chart.set_month_range(months)
            
            # 更新所有按钮颜色
            for month_btn in self.range_buttons.values():
                if month_btn.months == months:
                    month_btn.md_bg_color = (0.2, 0.6, 0.8, 1)  # 选中颜色
                else:
                    month_btn.md_bg_color = (0.5, 0.5, 0.5, 1)  # 未选中颜色
        except Exception as e:
            print(f"更新图表范围错误: {e}")

    def _prepare_chart_data(self, entries):
        """准备图表数据"""
        grouped_data = {}
        for entry in entries:
            entry_date = _ensure_date(entry.date) or (_ensure_datetime(entry.created_at).date() if entry.created_at else None)
            if not entry_date:
                continue
                
            if entry_date not in grouped_data:
                grouped_data[entry_date] = {'morning': None, 'evening': None}
            
            if entry.value:
                try:
                    weight = float(entry.value)
                    if entry.period == 'morning':
                        grouped_data[entry_date]['morning'] = weight
                    elif entry.period == 'evening':
                        grouped_data[entry_date]['evening'] = weight
                except ValueError:
                    pass
        
        # 转换为列表格式
        chart_data = []
        for date_key, weights in sorted(grouped_data.items()):
            chart_data.append({
                'date': date_key,
                'morning': weights['morning'],
                'evening': weights['evening']
            })
        
        return chart_data

    def export_data_to_csv(self):
        """导出历史数据到 CSV 文件"""
        try:
            if ANDROID:
                from android.storage import primary_external_storage_path
                export_dir = primary_external_storage_path()
                out_path = os.path.join(export_dir, "Download", "weight_data.csv")
            else:
                out_path = os.path.abspath("weight_data.csv")
                
            entries = Entry.select().order_by(Entry.date.desc(), Entry.period.asc(), Entry.created_at.desc())
            period_map = {"morning": "早晨", "evening": "晚间"}
            
            # 确保目录存在
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            
            with open(out_path, mode="w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file)
                writer.writerow(["日期", "时段", "体重", "创建时间"])
                for entry in entries:
                    # 日期优先使用 entry.date，否则用 created_at 的日期
                    date_obj = _ensure_date(entry.date) or (_ensure_datetime(entry.created_at).date() if entry.created_at else None)
                    date_str = date_obj.strftime("%Y-%m-%d") if date_obj else ""
                    created_at_dt = _ensure_datetime(entry.created_at)
                    created_at_str = created_at_dt.strftime("%Y-%m-%d %H:%M") if created_at_dt else ""
                    period_cn = period_map.get((entry.period or "").lower(), entry.period or "")
                    writer.writerow([date_str, period_cn, entry.value or "", created_at_str])
            self._show_error(f"数据已导出到 {out_path}")
        except Exception as e:
            self._show_error(f"导出失败: {e}")

    def import_data_from_csv(self):
        """从 CSV 文件导入历史数据"""
        try:
            if ANDROID:
                from android.storage import primary_external_storage_path
                import_dir = primary_external_storage_path()
                in_path = os.path.join(import_dir, "Download", "weight_data.csv")
            else:
                in_path = os.path.abspath("weight_data.csv")
                
            if not os.path.exists(in_path):
                self._show_error(f"未找到文件: {in_path}")
                return
                
            # 支持中文和英文时段映射
            rev_map = {
                "早晨": "morning", "早上": "morning", "早": "morning", "morning": "morning",
                "晚间": "evening", "晚上": "evening", "晚": "evening", "evening": "evening"
            }
            created_count = 0
            with open(in_path, mode="r", encoding="utf-8-sig") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # 可能的表头字段，取第一个非空
                    def _get_field(*keys):
                        for k in keys:
                            v = row.get(k)
                            if v is not None:
                                return str(v).strip().replace("\ufeff", "").replace("\u3000", " ")
                        return ""

                    date_raw = _get_field("日期", "date")
                    period_raw = _get_field("时段", "period")
                    weight_raw = _get_field("体重", "weight")
                    created_raw = _get_field("创建时间", "created_at")

                    # 解析日期
                    date_value = _ensure_date(date_raw)
                    if not date_value:
                        dt_try = _ensure_datetime(date_raw)
                        if dt_try:
                            date_value = dt_try.date()

                    # 规范时段
                    period_key = period_raw.strip()
                    period_value = None
                    if period_key:
                        period_value = rev_map.get(period_key) or rev_map.get(period_key.lower()) or period_key.lower()

                    # 解析体重
                    weight_value = None
                    if weight_raw:
                        try:
                            w = float(weight_raw.replace(",", "").replace(" ", ""))
                            weight_value = f"{w:.2f}"
                        except Exception:
                            weight_value = None

                    if not (date_value and period_value and weight_value):
                        continue

                    # 解析创建时间
                    created_dt = None
                    if created_raw:
                        created_dt = _ensure_datetime(created_raw)

                    # upsert
                    try:
                        with db.atomic():
                            existing = Entry.get_or_none((Entry.date == date_value) & (Entry.period == period_value))
                            if existing:
                                existing.value = weight_value
                                if created_dt:
                                    existing.created_at = created_dt
                                else:
                                    existing.created_at = datetime.now()
                                existing.save()
                            else:
                                kwargs = {
                                    "title": "体重",
                                    "value": weight_value,
                                    "date": date_value,
                                    "period": period_value,
                                }
                                if created_dt:
                                    kwargs["created_at"] = created_dt
                                Entry.create(**kwargs)
                            created_count += 1
                    except Exception:
                        continue

            self.refresh_list()
            self._show_error(f"导入完成，新增/更新记录: {created_count} 条")
        except Exception as e:
            self._show_error(f"导入失败: {e}")

    def menu_callback(self, text_item):
        try:
            self.menu.dismiss()
            if text_item == "history":
                self.show_detailed_history()
            elif text_item == "stats":
                self.show_statistics()
            elif text_item == "about":
                self.show_about()
            elif text_item == "export":
                self.export_data_to_csv()
            elif text_item == "import":
                self.import_data_from_csv()
        except Exception as e:
            print(f"菜单回调错误: {e}")

    def exit_app(self):
        """退出应用"""
        try:
            MDApp.get_running_app().stop()
        except Exception as e:
            print(f"退出应用错误: {e}")
            import os
            os._exit(0)

    def show_about(self):
        """显示关于信息"""
        about_text = """减肥数据记录软件

版本: 2.0
功能: 记录每日早晚体重数据，新增趋势图功能
作者: 用户定制版本

新增功能:
- 体重趋势图显示
- 支持1个月、3个月、6个月、12个月数据范围
- 美观的图表界面

使用说明:
- 点击按钮记录早晨/晚间体重
- 通过菜单查看趋势图
- 支持数据导入导出"""

        try:
            d = MDDialog(
                title="关于",
                text=about_text,
                buttons=[MDFlatButton(text="确定", on_release=lambda *a: d.dismiss(), font_name="ChineseFont")]
            )
            d.open()
        except Exception as e:
            print(f"显示关于错误: {e}")

    def show_detailed_history(self):
        """显示详细历史记录：按日期合并一行（左：早，右：晚）"""
        try:
            entries = Entry.select().order_by(Entry.date.desc(), Entry.period.asc(), Entry.created_at.desc())
            grouped = {}
            for e in entries:
                entry_date = _ensure_date(e.date) or (_ensure_datetime(e.created_at).date() if e.created_at else date.min)
                if entry_date not in grouped:
                    grouped[entry_date] = {}
                grouped[entry_date][(e.period or "morning")] = e

            # 计算需要的高度
            rows = max(len(grouped), 1)
            max_h = dp(600)
            list_height = dp(48) * rows
            scroll_h = min(list_height, max_h)

            content = MDBoxLayout(orientation="vertical", spacing=10, padding=10, size_hint_y=None)
            content.height = scroll_h + dp(20)
            
            scroll = MDScrollView(size_hint=(1, 1))
            history_list = MDList()
            history_list.size_hint_y = None
            history_list.height = list_height

            for d in sorted(grouped.keys(), reverse=True):
                if isinstance(d, date):
                    date_str = f"{d:%Y-%m-%d}"
                else:
                    date_str = str(d or "")

                periods = grouped[d]
                morning = periods.get("morning")
                evening = periods.get("evening")

                m_value = (morning.value if morning and morning.value else "--")
                e_value = (evening.value if evening and evening.value else "--")
                m_time = _ensure_datetime(morning.created_at).strftime("%H:%M") if morning and morning.created_at else ""
                e_time = _ensure_datetime(evening.created_at).strftime("%H:%M") if evening and evening.created_at else ""

                row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48), padding=(8, 6))
                label_date = MDLabel(text=date_str, halign="left", size_hint_x=0.25, font_name="ChineseFont")
                label_m = MDLabel(text=f"早：{m_value}  {m_time}", halign="left", size_hint_x=0.375, font_name="ChineseFont")
                label_e = MDLabel(text=f"晚：{e_value}  {e_time}", halign="right", size_hint_x=0.375, font_name="ChineseFont")

                row.add_widget(label_date)
                row.add_widget(label_m)
                row.add_widget(label_e)
                history_list.add_widget(row)

            scroll.add_widget(history_list)
            content.add_widget(scroll)

            d = MDDialog(
                title="详细历史记录",
                type="custom",
                content_cls=content,
                buttons=[MDFlatButton(text="关闭", on_release=lambda *a: d.dismiss(), font_name="ChineseFont")]
            )
            d.open()
        except Exception as e:
            print(f"显示详细历史错误: {e}")
            self._show_error(f"显示历史记录失败: {e}")

    def show_statistics(self):
        """显示全部记录的数据统计"""
        try:
            entries = [e for e in Entry.select() if e.value]
            if not entries:
                stats_text = "当前没有体重记录数据。"
            else:
                weights = [float(e.value) for e in entries if e.value]
                if weights:
                    min_weight = min(weights)
                    max_weight = max(weights)
                    avg_weight = sum(weights) / len(weights)
                    stats_text = f"""全部数据统计:

记录总数: {len(entries)}
最轻体重: {min_weight:.1f} 斤
最重体重: {max_weight:.1f} 斤
平均体重: {avg_weight:.1f} 斤
体重变化: {max_weight - min_weight:.1f} 斤"""
                else:
                    stats_text = "没有有效的体重数据。"

            d = MDDialog(
                title="数据统计",
                text=stats_text,
                buttons=[MDFlatButton(text="关闭", on_release=lambda *a: d.dismiss(), font_name="ChineseFont")]
            )
            d.open()
        except Exception as e:
            print(f"显示统计错误: {e}")
            self._show_error(f"显示统计失败: {e}")

    @mainthread
    def refresh_list(self):
        """按日期显示，每天一行：左侧日期/早，右侧晚"""
        try:
            self.list_view.clear_widgets()
            entries = Entry.select().order_by(Entry.date.desc(), Entry.period.asc(), Entry.created_at.desc())
            grouped = {}
            for e in entries:
                entry_date = _ensure_date(e.date) or (_ensure_datetime(e.created_at).date() if e.created_at else date.min)
                if entry_date not in grouped:
                    grouped[entry_date] = {}
                period = (e.period or "morning")
                grouped[entry_date][period] = e

            for d in sorted(grouped.keys(), reverse=True):
                if isinstance(d, date):
                    date_str = f"{d:%Y-%m-%d}"
                else:
                    date_str = str(d or "")

                periods = grouped[d]
                morning = periods.get("morning")
                evening = periods.get("evening")

                m_value = (morning.value if morning and morning.value else "--")
                e_value = (evening.value if evening and evening.value else "--")
                m_time = _ensure_datetime(morning.created_at).strftime("%H:%M") if morning and morning.created_at else ""
                e_time = _ensure_datetime(evening.created_at).strftime("%H:%M") if evening and evening.created_at else ""

                row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48), padding=(8, 0))
                label_date = MDLabel(text=date_str, halign="left", size_hint_x=0.25, font_name="ChineseFont")
                label_m = MDLabel(text=f"早：{m_value}  {m_time}", halign="left", size_hint_x=0.375, font_name="ChineseFont")
                label_e = MDLabel(text=f"晚：{e_value}  {e_time}", halign="right", size_hint_x=0.375, font_name="ChineseFont")

                row.add_widget(label_date)
                row.add_widget(label_m)
                row.add_widget(label_e)
                self.list_view.add_widget(row)
        except Exception as e:
            print(f"刷新列表错误: {e}")

    def open_weight_dialog(self, period):
        try:
            from kivy.uix.textinput import TextInput
            
            # 使用普通的TextInput并手动设置样式
            tf = TextInput(
                hint_text="输入体重（斤），例如 70 或 70.5",
                multiline=False,
                font_name="ChineseFont",
                size_hint_y=None,
                height=dp(48),
                padding=dp(10),
                background_color=(1, 1, 1, 1),
                foreground_color=(0, 0, 0, 1),
                hint_text_color=(0.5, 0.5, 0.5, 1),
                font_size=dp(16)
            )
            
            content = MDBoxLayout(orientation="vertical", spacing=10, padding=10, size_hint_y=None, height=dp(80))
            content.add_widget(tf)
            title = "记录今日体重（早晨）" if period == "morning" else "记录今日体重（晚间）"

            def _close_dialog(*a):
                if self._dialog:
                    self._dialog.dismiss()
                    self._dialog = None

            def _save_and_close(*a):
                txt = tf.text.strip()
                if not txt:
                    _close_dialog()
                    return
                txt_clean = txt.replace(",", "").replace(" ", "")
                try:
                    weight = float(txt_clean)
                except ValueError:
                    self._show_error("输入格式错误，请输入数字，例如 70 或 70.5")
                    return
                if not (20.0 <= weight <= 400.0):
                    self._show_error("体重数值异常，请输入 20–400 之间的值（斤）")
                    return
                self.save_weight(period, weight)
                _close_dialog()

            self._dialog = MDDialog(
                title=title,
                type="custom",
                content_cls=content,
                buttons=[
                    MDFlatButton(text="取消", on_release=_close_dialog, font_name="ChineseFont"),
                    MDFlatButton(text="保存", on_release=_save_and_close, font_name="ChineseFont")
                ],
            )
            self._dialog.open()
        except Exception as e:
            print(f"打开体重对话框错误: {e}")
            self._show_error("打开输入框失败")

    def _show_error(self, msg):
        """显示错误消息"""
        try:
            d = MDDialog(
                title="提示",
                text=str(msg),
                buttons=[MDFlatButton(text="确定", on_release=lambda *a: d.dismiss(), font_name="ChineseFont")]
            )
            d.open()
        except Exception as e:
            print(f"显示错误对话框失败: {e}")

    def save_weight(self, period, weight):
        """保存体重数据"""
        try:
            today = date.today()
            with db.atomic():
                e = Entry.get_or_none((Entry.date == today) & (Entry.period == period))
                if e:
                    e.value = f"{weight:.2f}"
                    e.created_at = datetime.now()
                    e.save()
                else:
                    Entry.create(title="体重", value=f"{weight:.2f}", date=today, period=period)
        except Exception as e:
            print(f"保存体重错误: {e}")
            self._show_error("保存失败，请稍后重试。")
            return
        self.refresh_list()


class JianFeiApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Teal"
        
        # 设置KivyMD使用中文字体
        self.theme_cls.font_styles.update({
            "H1": ["ChineseFont", 96, False, -1.5],
            "H2": ["ChineseFont", 60, False, -0.5],
            "H3": ["ChineseFont", 48, False, 0],
            "H4": ["ChineseFont", 34, False, 0.25],
            "H5": ["ChineseFont", 24, False, 0],
            "H6": ["ChineseFont", 20, False, 0.15],
            "Subtitle1": ["ChineseFont", 16, False, 0.15],
            "Subtitle2": ["ChineseFont", 14, False, 0.1],
            "Body1": ["ChineseFont", 16, False, 0.5],
            "Body2": ["ChineseFont", 14, False, 0.25],
            "Button": ["ChineseFont", 14, True, 1.25],
            "Caption": ["ChineseFont", 12, False, 0.4],
            "Overline": ["ChineseFont", 10, True, 1.5],
        })
        
        # 设置MDTextField的默认字体
        from kivy.properties import StringProperty
        from kivymd.uix.textfield import MDTextField
        original_init = MDTextField.__init__
        
        def new_init(self, **kwargs):
            kwargs.setdefault('font_name', 'ChineseFont')
            kwargs.setdefault('hint_text_font_name', 'ChineseFont')
            kwargs.setdefault('helper_text_font_name', 'ChineseFont')
            original_init(self, **kwargs)
        
        MDTextField.__init__ = new_init

    def build(self):
        """应用构建"""
        try:
            print("开始初始化应用...")
            
            # 再次确保字体设置
            setup_chinese_font_early()
            
            # 初始化数据库
            init_db()
            
            # 创建主界面
            screen = MainScreen()
            print("应用初始化完成")
            return screen
            
        except Exception as e:
            print(f"应用构建失败: {e}")
            # 返回一个简单的错误界面
            error_label = MDLabel(
                text="应用启动失败，请重启应用",
                halign="center",
                valign="middle",
                font_name="ChineseFont"  # 确保错误信息也使用中文字体
            )
            return error_label


if __name__ == "__main__":
    try:
        JianFeiApp().run()
    except Exception as e:
        print(f"应用崩溃: {e}")
        import traceback
        traceback.print_exc()
        # 尝试记录崩溃日志
        try:
            with open("crash.log", "w", encoding="utf-8") as f:
                traceback.print_exc(file=f)
        except:
            pass
