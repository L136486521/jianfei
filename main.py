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
from peewee import SqliteDatabase, Model, TextField, DateTimeField, AutoField, DateField
from datetime import datetime, date, timedelta
from kivy.metrics import dp
import sys
import csv  # 添加这一行
import math

DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")
db = SqliteDatabase(DB_PATH)


class Entry(Model):
    id = AutoField()
    title = TextField(null=True)
    value = TextField(null=True)
    created_at = DateTimeField(default=datetime.utcnow)
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
    db.connect(reuse_if_open=True)
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


def setup_chinese_font():
    """设置中文字体支持：简化版本，只注册中文字体，不覆盖系统字体"""
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
            print("警告: 未找到可用的中文字体，请把 ttf 放到项目的 fonts 目录或安装系统中文字体。")
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

        # 仅覆盖常用文本字体 Roboto 系列，注意：不要覆盖 MaterialIcons / Icons（图标字体）
        roboto_names = [
            "Roboto", "Roboto-Regular", "Roboto-Bold", "Roboto-Medium",
            "Roboto-Thin", "Roboto-Light", "Roboto-Italic"
        ]
        for name in roboto_names:
            try:
                LabelBase.register(name=name, fn_regular=found)
            except Exception:
                pass

        # 尽量更新 KivyMD 的 Roboto 定义，但不触碰图标字体定义
        try:
            from kivymd import font_definitions
            font_definitions.fonts["Roboto"] = {
                "regular": found,
                "bold": found,
                "italic": found,
                "bold_italic": found,
            }
            if hasattr(font_definitions, "font_styles"):
                for k, cfg in font_definitions.font_styles.items():
                    if isinstance(cfg, dict):
                        cfg["font_name"] = "ChineseFont"
        except Exception:
            pass

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
        self._update_canvas()

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
        """更新画布，绘制图表"""
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
            bold=True
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
            bold=True
        )
        label_evening.pos = (self.x + dp(120), legend_y - text_height/2)
        self.add_widget(label_evening)
        self.labels.append(label_evening)
        
        # 添加标题 - 放在按钮上方，增大字体
        title_label = Label(
            text="体重趋势图",
            font_size=dp(25),  # 增大字体
            color=(1, 1, 1, 1),  # 白色字体
            bold=True
        )
        # 标题放在图表顶部，按钮上方
        title_label.pos = (self.x + self.width/2 - dp(50), self.y + self.height - dp(-25))
        self.add_widget(title_label)
        self.labels.append(title_label)


class MainScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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

        # 中间标题
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

        # 下拉菜单
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

        # 按钮区域
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
        self.menu.open()

    def show_trend_chart(self):
        """显示趋势图对话框"""
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
                md_bg_color=(0.2, 0.6, 0.8, 1) if months == 1 else (0.5, 0.5, 0.5, 1)  # 修复按钮颜色
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
        self.trend_dialog.ids.title.font_name = "ChineseFont"
        self.trend_dialog.open()

    def update_chart_range(self, months):
        """更新图表显示的时间范围"""
        if hasattr(self, 'trend_chart'):
            self.trend_chart.set_month_range(months)
        
        # 更新所有按钮颜色
        for month_btn in self.range_buttons.values():
            if month_btn.months == months:
                month_btn.md_bg_color = (0.2, 0.6, 0.8, 1)  # 选中颜色
            else:
                month_btn.md_bg_color = (0.5, 0.5, 0.5, 1)  # 未选中颜色

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
        """导出历史数据到 CSV 文件（时段使用中文，时间到分钟，使用 UTF-8 BOM）"""
        try:
            entries = Entry.select().order_by(Entry.date.desc(), Entry.period.asc(), Entry.created_at.desc())
            period_map = {"morning": "早晨", "evening": "晚间"}
            out_path = os.path.abspath("weight_data.csv")
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
        """从 CSV 文件导入历史数据（兼容中文/英文时段，支持创建时间到分钟），对已存在记录进行更新"""
        try:
            in_path = os.path.abspath("weight_data.csv")
            if not os.path.exists(in_path):
                self._show_error("未找到 weight_data.csv 文件")
                return
            # 支持中文和英文时段映射（对大小写及全角/半角空白容错）
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
                        # 先直接匹配中文/英文原样，再匹配小写
                        period_value = rev_map.get(period_key) or rev_map.get(period_key.lower()) or period_key.lower()

                    # 解析体重（保留两位小数字符串）
                    weight_value = None
                    if weight_raw:
                        try:
                            w = float(weight_raw.replace(",", "").replace(" ", ""))
                            weight_value = f"{w:.2f}"
                        except Exception:
                            weight_value = None

                    if not (date_value and period_value and weight_value):
                        # 跳过不完整或无法解析的行
                        continue

                    # 解析创建时间（可选）
                    created_dt = None
                    if created_raw:
                        created_dt = _ensure_datetime(created_raw)

                    # upsert：同日期+时段则更新，否则创建
                    try:
                        with db.atomic():
                            existing = Entry.get_or_none((Entry.date == date_value) & (Entry.period == period_value))
                            if existing:
                                existing.value = weight_value
                                if created_dt:
                                    existing.created_at = created_dt
                                else:
                                    existing.created_at = datetime.utcnow()
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
                        # 单行失败则跳过，继续导入其他行
                        continue

            self.refresh_list()
            self._show_error(f"导入完成，新增/更新记录: {created_count} 条")
        except Exception as e:
            self._show_error(f"导入失败: {e}")

    def menu_callback(self, text_item):
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

    def exit_app(self):
        """退出应用"""
        MDApp.get_running_app().stop()

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

        d = MDDialog(
            title="关于",
            text=about_text,
            buttons=[MDFlatButton(text="确定", on_release=lambda *a: d.dismiss(), font_name="ChineseFont")]
        )
        # 设置对话框标题的字体
        d.ids.title.font_name = "ChineseFont"
        d.open()

    def show_detailed_history(self):
        """显示详细历史记录：按日期合并一行（左：早，右：晚）"""
        entries = Entry.select().order_by(Entry.date.desc(), Entry.period.asc(), Entry.created_at.desc())
        grouped = {}
        for e in entries:
            entry_date = _ensure_date(e.date) or (_ensure_datetime(e.created_at).date() if e.created_at else date.min)
            if entry_date not in grouped:
                grouped[entry_date] = {}
            grouped[entry_date][(e.period or "morning")] = e

        # 计算需要的高度
        rows = max(len(grouped), 1)
        # 设置最大高度，确保可以滚动
        max_h = dp(600)
        list_height = dp(48) * rows
        scroll_h = min(list_height, max_h)

        content = MDBoxLayout(orientation="vertical", spacing=10, padding=10, size_hint_y=None)
        # 设置内容高度为列表实际高度
        content.height = scroll_h + dp(20)
        
        scroll = MDScrollView(size_hint=(1, 1))
        history_list = MDList()
        history_list.size_hint_y = None
        history_list.height = list_height  # 列表高度为实际内容高度

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
        # 设置对话框标题的字体
        d.ids.title.font_name = "ChineseFont"
        d.open()

    def show_statistics(self):
        """显示全部记录的数据统计（不再限制为最近30天）"""
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
        # 设置对话框标题的字体
        d.ids.title.font_name = "ChineseFont"
        d.open()

    @mainthread
    def refresh_list(self):
        """按日期显示，每天一行：左侧日期/早，右侧晚"""
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

    def open_weight_dialog(self, period):
        tf = MDTextField(
            hint_text="输入体重（斤），例如 70 或 70.5",
            required=True,
            input_filter="float",
            font_name="ChineseFont"
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
        # 设置对话框标题的字体
        self._dialog.ids.title.font_name = "ChineseFont"
        self._dialog.open()

    def _show_error(self, msg):
        d = MDDialog(
            title="提示",
            text=str(msg),
            buttons=[MDFlatButton(text="确定", on_release=lambda *a: d.dismiss(), font_name="ChineseFont")]
        )
        # 设置对话框标题的字体
        d.ids.title.font_name = "ChineseFont"
        d.open()

    def save_weight(self, period, weight):
        today = date.today()
        try:
            with db.atomic():
                e = Entry.get_or_none((Entry.date == today) & (Entry.period == period))
                if e:
                    e.value = f"{weight:.2f}"
                    e.created_at = datetime.utcnow()
                    e.save()
                else:
                    Entry.create(title="体重", value=f"{weight:.2f}", date=today, period=period)
        except Exception:
            self._show_error("保存失败，请稍后重试。")
            return
        self.refresh_list()


class JianFeiApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Teal"

    def build(self):
        init_db()
        setup_chinese_font()
        screen = MainScreen()
        screen.refresh_list()
        return screen


if __name__ == "__main__":
    try:
        JianFeiApp().run()
    except Exception:
        import traceback
        print("应用发生未捕获异常，回溯如下：")
        traceback.print_exc()
        try:
            with open("crash.log", "a", encoding="utf-8") as f:
                traceback.print_exc(file=f)
        except Exception:
            pass