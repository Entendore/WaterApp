import json
import os
import csv
import datetime
import math
import random
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.switch import Switch
from kivy.uix.spinner import Spinner
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.graphics import Color, RoundedRectangle, Line, Rectangle, Ellipse

from plyer import notification

# Set default window size for desktop testing
Window.size = (380, 780)
Window.clearcolor = (0.12, 0.14, 0.18, 1) # Dark mode background

Builder.load_string('''
<RoundedButton@Button>:
    background_normal: ''
    background_color: 0, 0, 0, 0
    color: 1, 1, 1, 1
    font_size: 18
    bold: True
    canvas.before:
        Color:
            rgba: self.background_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [10,]

<WaterTank>:
    canvas:
        Color:
            rgba: 0.2, 0.22, 0.27, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [25,]
        
        # Water Fill
        Color:
            rgba: 0.1, 0.7, 1, 0.9
        Rectangle:
            pos: self.x, self.y
            size: self.width, self.height * self.progress
        
        # Moving Wave Shimmer
        Color:
            rgba: 1, 1, 1, 0.15
        Rectangle:
            pos: self.x + root.wave_offset, self.y + (self.height * self.progress) - 4
            size: self.width, 4
        Color:
            rgba: 1, 1, 1, 0.05
        Rectangle:
            pos: self.x - root.wave_offset * 1.5, self.y + (self.height * self.progress) - 8
            size: self.width, 8
            
        # Bubbles
        Color:
            rgba: 1, 1, 1, 0.3
        Ellipse:
            pos: root.b1_pos
            size: 6, 6
        Ellipse:
            pos: root.b2_pos
            size: 8, 8
        Ellipse:
            pos: root.b3_pos
            size: 4, 4
            
        Color:
            rgba: 0.4, 0.5, 0.6, 1
        Line:
            width: 2
            rounded_rectangle: self.x, self.y, self.width, self.height, 25

<BeverageBreakdown>:
    canvas:
        Color:
            rgba: 0.2, 0.22, 0.27, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [10,]
        Color:
            rgba: 0.1, 0.7, 1, 1
        Rectangle:
            pos: self.x + 5, self.y + 5
            size: (self.width - 10) * root.water_ratio, self.height - 10
        Color:
            rgba: 0.6, 0.4, 0.2, 1
        Rectangle:
            pos: self.x + 5 + ((self.width - 10) * root.water_ratio), self.y + 5
            size: (self.width - 10) * root.coffee_ratio, self.height - 10
        Color:
            rgba: 0.9, 0.6, 0.1, 1
        Rectangle:
            pos: self.x + 5 + ((self.width - 10) * (root.water_ratio + root.coffee_ratio)), self.y + 5
            size: (self.width - 10) * root.juice_ratio, self.height - 10

<LogItem>:
    orientation: 'horizontal'
    size_hint_y: None
    height: 45
    spacing: 5
    canvas.before:
        Color:
            rgba: 0.15, 0.17, 0.21, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [8,]
    
    Label:
        text: root.time_str
        color: 0.6, 0.6, 0.6, 1
        size_hint_x: 0.25
        font_size: 14
    Label:
        text: root.bev_type
        color: 0.9, 0.9, 0.9, 1
        size_hint_x: 0.35
        font_size: 14
    Label:
        text: f"{root.amount} ml"
        color: 0.1, 0.9, 1, 1
        bold: True
        size_hint_x: 0.25
        font_size: 14
    Button:
        text: 'X'
        color: 1, 0.5, 0.5, 1
        size_hint_x: 0.15
        background_normal: ''
        background_color: 0.2, 0.22, 0.27, 1
        font_size: 14
        on_press: root.parent_app.delete_entry(root.log_id)

<HistoryGraph>:
    canvas:
        Color:
            rgba: 0.2, 0.22, 0.27, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [10,]
        Color:
            rgba: 0.8, 0.8, 0.8, 0.5
        Line:
            width: 1
            dashed: 4, 3
            points: [self.x, self.y + (self.height * root.goal_ratio), self.right, self.y + (self.height * root.goal_ratio)]
        Color:
            rgba: root.c0
        Rectangle:
            pos: self.x + self.width*0.05, self.y
            size: self.width*0.1, self.height * root.r0
        Color:
            rgba: root.c1
        Rectangle:
            pos: self.x + self.width*0.18, self.y
            size: self.width*0.1, self.height * root.r1
        Color:
            rgba: root.c2
        Rectangle:
            pos: self.x + self.width*0.31, self.y
            size: self.width*0.1, self.height * root.r2
        Color:
            rgba: root.c3
        Rectangle:
            pos: self.x + self.width*0.44, self.y
            size: self.width*0.1, self.height * root.r3
        Color:
            rgba: root.c4
        Rectangle:
            pos: self.x + self.width*0.57, self.y
            size: self.width*0.1, self.height * root.r4
        Color:
            rgba: root.c5
        Rectangle:
            pos: self.x + self.width*0.70, self.y
            size: self.width*0.1, self.height * root.r5
        Color:
            rgba: root.c6
        Rectangle:
            pos: self.x + self.width*0.83, self.y
            size: self.width*0.1, self.height * root.r6

<WaterTracker>:
    orientation: 'vertical'
    padding: 20
    spacing: 8

    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: 0.06
        Label:
            text: 'Hydration Elite'
            font_size: 26
            bold: True
            color: 1, 1, 1, 1
            size_hint_x: 0.6
            halign: 'left'
            valign: 'middle'
            text_size: self.size
        Button:
            text: '🏆'
            font_size: 22
            size_hint_x: 0.13
            background_normal: ''
            background_color: 0.2, 0.3, 0.4, 1
            on_press: root.show_achievements()
        Button:
            text: '📊'
            font_size: 22
            size_hint_x: 0.13
            background_normal: ''
            background_color: 0.2, 0.3, 0.4, 1
            on_press: root.show_history()
        Button:
            text: '⚙'
            font_size: 22
            size_hint_x: 0.13
            background_normal: ''
            background_color: 0.2, 0.3, 0.4, 1
            on_press: root.open_settings_popup()

    FloatLayout:
        id: tracker_area
        size_hint_y: 0.28
        WaterTank:
            id: water_tank
            size_hint: 0.7, 0.9
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
            progress: 0
            wave_offset: 0
            
        Label:
            id: intake_label
            text: '0.0 L'
            font_size: 42
            bold: True
            color: 1, 1, 1, 1
            pos_hint: {'center_x': 0.5, 'center_y': 0.58}
            size_hint: None, None
            
        Label:
            id: goal_label
            text: 'of 0.0 L'
            font_size: 16
            color: 0.8, 0.8, 0.8, 1
            pos_hint: {'center_x': 0.5, 'center_y': 0.48}
            size_hint: None, None
            
        Label:
            id: score_label
            text: 'Score: 0'
            font_size: 14
            bold: True
            color: 0.9, 0.8, 0.2, 1
            pos_hint: {'center_x': 0.5, 'center_y': 0.38}
            size_hint: None, None

    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: 0.04
        spacing: 5
        Label:
            text: 'Intake Breakdown:'
            font_size: 12
            color: 0.6, 0.6, 0.6, 1
            size_hint_x: 0.3
        BeverageBreakdown:
            id: bev_breakdown
            size_hint_x: 0.7
            water_ratio: 0
            coffee_ratio: 0
            juice_ratio: 0

    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: 0.07
        spacing: 10
        Spinner:
            id: bev_spinner
            text: 'Water'
            values: ('Water', 'Coffee/Tea', 'Juice')
            background_normal: ''
            background_color: 0.2, 0.5, 0.8, 1
            color: 1, 1, 1, 1
            font_size: 14
            size_hint_x: 0.4
        TextInput:
            id: custom_input
            multiline: False
            input_filter: 'int'
            hint_text: 'Custom (ml)'
            font_size: 16
            padding: [10, 10, 10, 10]
            background_normal: ''
            background_color: 0.2, 0.22, 0.27, 1
            size_hint_x: 0.35
            on_text_validate: root.add_custom_water()
        RoundedButton:
            text: 'Add'
            size_hint_x: 0.25
            background_color: 0.1, 0.7, 1, 1
            on_press: root.add_custom_water()

    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: 0.09
        spacing: 15
        RoundedButton:
            id: btn1
            text: '+ 250 ml'
            background_color: 0.2, 0.5, 0.8, 1
            on_press: root.add_water(root.btn1_amount, bev_spinner.text)
        RoundedButton:
            id: btn2
            text: '+ 500 ml'
            background_color: 0.2, 0.5, 0.8, 1
            on_press: root.add_water(root.btn2_amount, bev_spinner.text)

    Label:
        text: 'Today\'s Log'
        font_size: 16
        bold: True
        color: 0.8, 0.8, 0.8, 1
        size_hint_y: 0.04
        halign: 'left'
        text_size: self.size
        
    ScrollView:
        size_hint_y: 0.22
        do_scroll_x: False
        GridLayout:
            id: log_container
            cols: 1
            spacing: 5
            size_hint_y: None
            height: self.minimum_height

    BoxLayout:
        orientation: 'vertical'
        size_hint_y: 0.10
        spacing: 2
        canvas.before:
            Color:
                rgba: 0.15, 0.17, 0.21, 1
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [8,]
        Label:
            id: tip_label
            text: ''
            markup: True
            font_size: 13
            color: 0.7, 0.8, 0.9, 1
            halign: 'center'
            valign: 'middle'
            text_size: self.size
            padding: [10, 10]
''')

class WaterTank(Widget):
    progress = NumericProperty(0.0)
    wave_offset = NumericProperty(0)
    b1_pos = ListProperty([0, 0])
    b2_pos = ListProperty([0, 0])
    b3_pos = ListProperty([0, 0])
    
    def __init__(self, **kwargs):
        super(WaterTank, self).__init__(**kwargs)
        self.b1_y = 0.0
        self.b2_y = 0.3
        self.b3_y = 0.6
        Clock.schedule_interval(self.animate_wave, 1/30)
        Clock.schedule_interval(self.animate_bubbles, 1/30)

    def animate_wave(self, dt):
        self.wave_offset += 2
        if self.wave_offset > self.width:
            self.wave_offset = -self.width

    def animate_bubbles(self, dt):
        # Only animate if there is water
        if self.progress > 0.05:
            self.b1_y = (self.b1_y + 0.01) % 1.0
            self.b2_y = (self.b2_y + 0.015) % 1.0
            self.b3_y = (self.b3_y + 0.008) % 1.0
            
            water_top = self.y + (self.height * self.progress)
            self.b1_pos = (self.x + self.width * 0.3, self.y + (self.b1_y * (self.height * self.progress)))
            self.b2_pos = (self.x + self.width * 0.6, self.y + (self.b2_y * (self.height * self.progress)))
            self.b3_pos = (self.x + self.width * 0.45, self.y + (self.b3_y * (self.height * self.progress)))

class BeverageBreakdown(Widget):
    water_ratio = NumericProperty(0)
    coffee_ratio = NumericProperty(0)
    juice_ratio = NumericProperty(0)

class LogItem(BoxLayout):
    time_str = StringProperty('')
    bev_type = StringProperty('')
    amount = StringProperty('0')
    log_id = NumericProperty(0)
    parent_app = None

class HistoryGraph(Widget):
    r0 = NumericProperty(0); r1 = NumericProperty(0); r2 = NumericProperty(0)
    r3 = NumericProperty(0); r4 = NumericProperty(0); r5 = NumericProperty(0)
    r6 = NumericProperty(0)
    c0 = ListProperty([0.1, 0.7, 1, 1]); c1 = ListProperty([0.1, 0.7, 1, 1])
    c2 = ListProperty([0.1, 0.7, 1, 1]); c3 = ListProperty([0.1, 0.7, 1, 1])
    c4 = ListProperty([0.1, 0.7, 1, 1]); c5 = ListProperty([0.1, 0.7, 1, 1])
    c6 = ListProperty([0.1, 0.7, 1, 1])
    goal_ratio = NumericProperty(1.0)

class WaterTracker(BoxLayout):
    daily_goal_ml = NumericProperty(0)
    current_intake_ml = NumericProperty(0)
    btn1_amount = NumericProperty(250)
    btn2_amount = NumericProperty(500)
    
    today_log = ListProperty([])
    reminder_event = None
    settings = {}
    history = {}
    next_log_id = 0

    def __init__(self, **kwargs):
        super(WaterTracker, self).__init__(**kwargs)
        self.load_data()
        self.update_daily_tip()
        Clock.schedule_once(self.update_ui, 0.5)
        Clock.schedule_interval(self.update_score_and_pace, 60)

    def update_score_and_pace(self, *args):
        if self.daily_goal_ml == 0:
            self.ids.score_label.text = ""
            return

        # Calculate Hydration Score (0-100)
        progress = min(self.current_intake_ml / self.daily_goal_ml, 1.0)
        progress_score = progress * 80
        
        total_eff = sum(e['eff_amount'] for e in self.today_log)
        if total_eff > 0:
            w_eff = sum(e['eff_amount'] for e in self.today_log if e['bev'] == 'Water')
            quality_score = (w_eff / total_eff) * 20
        else:
            quality_score = 20
            
        total_score = int(progress_score + quality_score)
        self.ids.score_label.text = f"Score: {total_score} / 100"
        
        # Color based on score
        if total_score >= 90:
            self.ids.score_label.color = (0.1, 1, 0.5, 1)
        elif total_score >= 50:
            self.ids.score_label.color = (0.9, 0.8, 0.2, 1)
        else:
            self.ids.score_label.color = (1, 0.4, 0.4, 1)

    def update_daily_tip(self):
        day_of_year = datetime.datetime.now().timetuple().tm_yday
        tips = [
            "[b]Tip:[/b] Drink a glass of water right after waking up to kickstart your metabolism.",
            "[b]Tip:[/b] Keep a reusable bottle on your desk as a visual reminder to drink.",
            "[b]Tip:[/b] If you feel hungry, you might actually just be thirsty. Try water first!",
            "[b]Tip:[/b] Hydration improves cognitive function. Drink up before a big task!",
            "[b]Tip:[/b] Monitor your urine color. Pale yellow is the sign of optimal hydration.",
            "[b]Tip:[/b] Eat water-rich foods like cucumbers, watermelon, and oranges.",
            "[b]Tip:[/b] Don't wait until you're thirsty. Thirst means you're already 1-2% dehydrated."
        ]
        self.ids.tip_label.text = tips[day_of_year % len(tips)]

    def load_data(self):
        if os.path.exists('water_data.json'):
            try:
                with open('water_data.json', 'r') as f:
                    data = json.load(f)
                    self.settings = data.get('settings', {})
                    self.history = data.get('history', {})
                    
                    today = datetime.date.today().isoformat()
                    last_date = self.settings.get('last_date', today)
                    
                    if last_date != today:
                        if self.settings.get('current_intake_ml', 0) > 0:
                            self.history[last_date] = self.settings.get('current_intake_ml', 0)
                        self.settings['current_intake_ml'] = 0
                        self.settings['today_log'] = []
                        self.settings['last_date'] = today
                        self.save_data()
                    
                    self.daily_goal_ml = self.settings.get('daily_goal_ml', 0)
                    self.today_log = self.settings.get('today_log', [])
                    self.next_log_id = self.settings.get('next_log_id', 0)
                    self.current_intake_ml = sum(entry['eff_amount'] for entry in self.today_log)
                    self.btn1_amount = self.settings.get('btn1_amount', 250)
                    self.btn2_amount = self.settings.get('btn2_amount', 500)
                    if 'achievements' not in self.settings:
                        self.settings['achievements'] = []
            except Exception as e:
                print("Data corrupted, resetting. Error:", e)
                self.reset_data()
        else:
            self.reset_data()

    def reset_data(self):
        self.settings = {
            'last_date': datetime.date.today().isoformat(),
            'weight_val': 160,
            'weight_unit': 'lbs',
            'activity_level': 'sedentary',
            'environment': 'normal',
            'reminder_interval': 30,
            'reminders_enabled': False,
            'today_log': [],
            'next_log_id': 0,
            'goal_mode': 'auto',
            'manual_goal_ml': 2500,
            'achievements': []
        }
        self.history = {}
        self.save_data()

    def save_data(self):
        self.settings['daily_goal_ml'] = self.daily_goal_ml
        self.settings['current_intake_ml'] = self.current_intake_ml
        self.settings['btn1_amount'] = self.btn1_amount
        self.settings['btn2_amount'] = self.btn2_amount
        self.settings['today_log'] = self.today_log
        self.settings['next_log_id'] = self.next_log_id
        
        sorted_history = sorted(self.history.items(), key=lambda x: x[0])[-7:]
        self.history = dict(sorted_history)

        data = {'settings': self.settings, 'history': self.history}
        with open('water_data.json', 'w') as f:
            json.dump(data, f)

    def calculate_goal(self, weight, unit, activity_level, env, manual_goal=0, mode='auto'):
        if mode == 'manual' and manual_goal > 0:
            self.daily_goal_ml = int(manual_goal)
        else:
            if unit == 'lbs':
                weight_kg = float(weight) * 0.453592
            else:
                weight_kg = float(weight)
                
            base_goal = int(weight_kg * 35)
            if activity_level == 'light': base_goal += 500
            elif activity_level == 'moderate': base_goal += 1000
            elif activity_level == 'intense': base_goal += 1500
            
            # Environment adjustments
            if env == 'hot': base_goal += 700
            elif env == 'altitude': base_goal += 500
            elif env == 'cold': base_goal -= 250
            
            self.daily_goal_ml = base_goal
            
        self.save_data()
        self.update_ui()

    def get_hydration_multiplier(self, beverage):
        if beverage == 'Coffee/Tea': return 0.7
        elif beverage == 'Juice': return 0.9
        return 1.0

    def add_water(self, amount, beverage_type='Water'):
        if self.daily_goal_ml == 0: return
        
        if amount >= 1500:
            self.show_overhydration_warning()
            return

        multiplier = self.get_hydration_multiplier(beverage_type)
        effective_amount = int(amount * multiplier)
        
        entry = {
            'id': self.next_log_id,
            'time': datetime.datetime.now().strftime('%I:%M %p'),
            'bev': beverage_type,
            'amount': amount,
            'eff_amount': effective_amount,
            'timestamp': datetime.datetime.now().isoformat()
        }
        self.today_log.append(entry)
        self.next_log_id += 1
        
        prev_intake = self.current_intake_ml
        self.current_intake_ml += effective_amount
        
        if self.current_intake_ml > self.daily_goal_ml * 1.5 and self.daily_goal_ml > 0:
            self.show_overhydration_warning()
        
        if self.current_intake_ml >= self.daily_goal_ml and prev_intake < self.daily_goal_ml:
            self.send_achievement_notification()
            self.unlock_achievement("Hydration Hero")
            
        if datetime.datetime.now().hour < 9:
            self.unlock_achievement("Early Bird")

        self.save_data()
        self.update_ui()

    def add_custom_water(self):
        text = self.ids.custom_input.text
        bev = self.ids.bev_spinner.text
        if text:
            self.add_water(int(text), bev)
            self.ids.custom_input.text = ''

    def delete_entry(self, log_id):
        self.today_log = [e for e in self.today_log if e['id'] != log_id]
        self.current_intake_ml = sum(entry['eff_amount'] for entry in self.today_log)
        self.save_data()
        self.update_ui()

    def reset_day(self):
        self.today_log = []
        self.current_intake_ml = 0
        self.next_log_id = 0
        self.save_data()
        self.update_ui()

    def unlock_achievement(self, ach_name):
        if ach_name not in self.settings['achievements']:
            self.settings['achievements'].append(ach_name)
            self.save_data()
            self.show_achievement_popup(ach_name)

    def show_achievement_popup(self, ach_name):
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        emojis = {
            "Hydration Hero": "🦸‍♂️",
            "Early Bird": "🐦",
            "Triple Threat": "🔥"
        }
        descriptions = {
            "Hydration Hero": "You met your daily hydration goal!",
            "Early Bird": "You logged a drink before 9:00 AM!",
            "Triple Threat": "You hit your goal 3 days in a row!"
        }
        
        content.add_widget(Label(text=emojis.get(ach_name, "🏆"), font_size=60))
        content.add_widget(Label(text=ach_name, font_size=24, bold=True, color=(1, 0.8, 0.2, 1)))
        content.add_widget(Label(text=descriptions.get(ach_name, "Achievement Unlocked!"), font_size=16, color=(0.9,0.9,0.9,1)))
        
        close_btn = RoundedButton(text='Awesome!', size_hint_y=0.2, background_color=(0.8, 0.6, 0.1, 1))
        content.add_widget(close_btn)
        
        popup = Popup(title='Achievement Unlocked!', content=content, size_hint=(0.8, 0.6), background_color=(0.15, 0.12, 0.08, 1), separator_color=(0.8, 0.6, 0.1, 1))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def show_overhydration_warning(self):
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        warning_label = Label(
            text="Warning: Exertional Hyponatremia Risk.\n\nDrinking too much water too quickly can dilute sodium levels in your blood, leading to dangerous health effects.\n\nPlease sip slowly throughout the day.",
            color=(1, 0.4, 0.4, 1),
            font_size=16,
            halign='center',
            valign='middle',
            text_size=(self.width, None)
        )
        content.add_widget(warning_label)
        close_btn = RoundedButton(text='I Understand', size_hint_y=0.2, background_color=(0.8, 0.2, 0.2, 1))
        content.add_widget(close_btn)
        
        popup = Popup(title='⚠ Overhydration Warning', content=content, size_hint=(0.85, 0.7), background_color=(0.15, 0.1, 0.1, 1), separator_color=(0.8, 0.2, 0.2, 1))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def update_ui(self, *args):
        goal_l = self.daily_goal_ml / 1000.0
        current_l = self.current_intake_ml / 1000.0
        
        self.ids.goal_label.text = f"of {goal_l:.1f} L"
        self.ids.intake_label.text = f"{current_l:.1f} L"
        self.ids.btn1.text = f"+ {self.btn1_amount} ml"
        self.ids.btn2.text = f"+ {self.btn2_amount} ml"
        
        if self.daily_goal_ml > 0:
            progress_val = min(self.current_intake_ml / self.daily_goal_ml, 1.0)
            anim = Animation(progress=progress_val, duration=0.8, t='out_quad')
            anim.start(self.ids.water_tank)
            
            if self.current_intake_ml >= self.daily_goal_ml:
                self.ids.intake_label.color = (0.1, 1, 0.5, 1)
                self.ids.goal_label.text = "Goal Achieved!"
            else:
                self.ids.intake_label.color = (1, 1, 1, 1)

        total_eff = sum(e['eff_amount'] for e in self.today_log)
        if total_eff > 0:
            w_eff = sum(e['eff_amount'] for e in self.today_log if e['bev'] == 'Water')
            c_eff = sum(e['eff_amount'] for e in self.today_log if e['bev'] == 'Coffee/Tea')
            j_eff = sum(e['eff_amount'] for e in self.today_log if e['bev'] == 'Juice')
            
            self.ids.bev_breakdown.water_ratio = w_eff / total_eff
            self.ids.bev_breakdown.coffee_ratio = c_eff / total_eff
            self.ids.bev_breakdown.juice_ratio = j_eff / total_eff
        else:
            self.ids.bev_breakdown.water_ratio = 0
            self.ids.bev_breakdown.coffee_ratio = 0
            self.ids.bev_breakdown.juice_ratio = 0

        log_container = self.ids.log_container
        log_container.clear_widgets()
        
        if not self.today_log:
            empty_label = Label(text="No drinks logged yet. Time to hydrate! 💧", color=(0.5, 0.5, 0.5, 1), font_size=14, size_hint_y=None, height=40)
            log_container.add_widget(empty_label)
        else:
            for entry in reversed(self.today_log):
                item = LogItem(
                    time_str=entry['time'],
                    bev_type=entry['bev'],
                    amount=str(entry['amount']),
                    log_id=entry['id']
                )
                item.parent_app = self
                log_container.add_widget(item)
                
        self.update_score_and_pace()

    def toggle_reminders(self, active, interval):
        if active:
            if self.reminder_event: self.reminder_event.cancel()
            seconds = int(interval) * 60
            self.reminder_event = Clock.schedule_interval(self.send_reminder_notification, seconds)
            self.send_reminder_notification(0)
        else:
            if self.reminder_event:
                self.reminder_event.cancel()
                self.reminder_event = None

    def send_reminder_notification(self, dt):
        current_hour = datetime.datetime.now().hour
        if current_hour >= 22 or current_hour < 7: return
        if self.daily_goal_ml == 0: return
        
        current_l = self.current_intake_ml / 1000.0
        goal_l = self.daily_goal_ml / 1000.0
        remaining_ml = self.daily_goal_ml - self.current_intake_ml
        
        if remaining_ml > 0 and remaining_ml <= 250:
            message = f"You're so close! Just {int(remaining_ml)} ml left to hit your goal!"
        elif remaining_ml <= 0:
            return
        else:
            message = f"You are at {current_l:.1f}L of {goal_l:.1f}L. Time to drink water!"
            
        try:
            notification.notify(title="Hydration Reminder 💧", message=message, app_name="Hydration Elite", timeout=10)
        except Exception as e:
            print("Notification Error:", e)

    def send_achievement_notification(self):
        try:
            notification.notify(title="Goal Achieved! 🎉", message="Congratulations! You've met your hydration goal for today.", app_name="Hydration Elite", timeout=10)
        except Exception as e:
            print("Notification Error:", e)

    def export_csv(self):
        filename = f"hydration_export_{datetime.date.today().isoformat()}.csv"
        try:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Date', 'Time', 'Beverage', 'Amount (ml)', 'Effective Hydration (ml)'])
                today_str = datetime.date.today().isoformat()
                for entry in self.today_log:
                    writer.writerow([today_str, entry['time'], entry['bev'], entry['amount'], entry['eff_amount']])
                writer.writerow([])
                writer.writerow(['Historical Date', 'Total Intake (ml)'])
                for date, intake in sorted(self.history.items()):
                    writer.writerow([date, intake])
            return True
        except Exception as e:
            print("CSV Export Error:", e)
            return False

    def open_settings_popup(self):
        content = BoxLayout(orientation='vertical', padding=15, spacing=8)
        weight_input = TextInput(text=str(self.settings.get('weight_val', 160)), multiline=False, input_filter='float')
        unit_spinner = Spinner(text=self.settings.get('weight_unit', 'lbs'), values=('lbs', 'kg'))
        activity_spinner = Spinner(text=self.settings.get('activity_level', 'sedentary').capitalize(), values=('Sedentary', 'Light', 'Moderate', 'Intense'))
        env_spinner = Spinner(text=self.settings.get('environment', 'normal').capitalize(), values=('Normal', 'Hot', 'Altitude', 'Cold'))
        goal_mode_spinner = Spinner(text=self.settings.get('goal_mode', 'auto').capitalize(), values=('Auto', 'Manual'))
        manual_goal_input = TextInput(text=str(self.settings.get('manual_goal_ml', 2500)), multiline=False, input_filter='int')
        interval_spinner = Spinner(text=str(self.settings.get('reminder_interval', 30)), values=('15', '30', '60'))
        reminder_switch = Switch(active=self.settings.get('reminders_enabled', False))
        btn1_input = TextInput(text=str(self.btn1_amount), multiline=False, input_filter='int')
        btn2_input = TextInput(text=str(self.btn2_amount), multiline=False, input_filter='int')

        def row(label_text, widget):
            box = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=10)
            box.add_widget(Label(text=label_text, color=(0.9,0.9,0.9,1), size_hint_x=0.5))
            box.add_widget(widget)
            return box

        content.add_widget(row('Goal Mode:', goal_mode_spinner))
        content.add_widget(row('Manual Goal (ml):', manual_goal_input))
        content.add_widget(row('Weight:', weight_input))
        content.add_widget(row('Unit:', unit_spinner))
        content.add_widget(row('Activity Level:', activity_spinner))
        content.add_widget(row('Environment:', env_spinner))
        content.add_widget(row('Quick Add Btn 1:', btn1_input))
        content.add_widget(row('Quick Add Btn 2:', btn2_input))
        content.add_widget(row('Reminder Interval:', interval_spinner))
        content.add_widget(row('Enable Reminders:', reminder_switch))

        def save_settings(instance):
            self.settings['weight_val'] = float(weight_input.text)
            self.settings['weight_unit'] = unit_spinner.text
            self.settings['activity_level'] = activity_spinner.text.lower()
            self.settings['environment'] = env_spinner.text.lower()
            self.settings['goal_mode'] = goal_mode_spinner.text.lower()
            self.settings['manual_goal_ml'] = int(manual_goal_input.text) if manual_goal_input.text else 2500
            self.settings['reminder_interval'] = int(interval_spinner.text)
            self.settings['reminders_enabled'] = reminder_switch.active
            self.btn1_amount = int(btn1_input.text) if btn1_input.text else 250
            self.btn2_amount = int(btn2_input.text) if btn2_input.text else 500
            
            self.calculate_goal(
                self.settings['weight_val'], 
                self.settings['weight_unit'], 
                self.settings['activity_level'],
                self.settings['environment'],
                self.settings['manual_goal_ml'],
                self.settings['goal_mode']
            )
            self.toggle_reminders(reminder_switch.active, interval_spinner.text)
            popup.dismiss()

        save_btn = RoundedButton(text='Save Settings', size_hint_y=0.12, background_color=(0.1, 0.7, 1, 1))
        save_btn.bind(on_press=save_settings)
        content.add_widget(save_btn)

        popup = Popup(title='Settings', content=content, size_hint=(0.9, 0.95), background_color=(0.12, 0.14, 0.18, 1), separator_color=(0.1, 0.7, 1, 1))
        popup.open()

    def show_achievements(self):
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        scroll = ScrollView()
        
        all_achievements = {
            "Early Bird": "Log a drink before 9:00 AM.",
            "Hydration Hero": "Meet your daily hydration goal.",
            "Triple Threat": "Hit your goal 3 days in a row."
        }
        
        unlocked = self.settings.get('achievements', [])
        
        text = "[b]Achievements[/b]\n\n"
        for name, desc in all_achievements.items():
            if name in unlocked:
                text += f"[color=0.1,1,0.5,1]✔ {name}[/color]\n"
                text += f"[color=0.8,0.8,0.8,1]{desc}[/color]\n\n"
            else:
                text += f"[color=0.5,0.5,0.5,1]🔒 {name}[/color]\n"
                text += f"[color=0.5,0.5,0.5,1]{desc}[/color]\n\n"

        label = Label(text=text, markup=True, size_hint_y=None, valign='top', halign='left', font_size=18, color=(0.9, 0.9, 0.9, 1))
        label.bind(texture_size=label.setter('size'))
        label.bind(width=lambda *x: label.setter('text_size')(label, (label.width, None)))
        scroll.add_widget(label)
        
        close_btn = RoundedButton(text='Close', size_hint_y=0.1, background_color=(0.1, 0.7, 1, 1))
        content.add_widget(scroll)
        content.add_widget(close_btn)
        
        popup = Popup(title='Your Achievements', content=content, size_hint=(0.9, 0.85), background_color=(0.12, 0.14, 0.18, 1), separator_color=(0.8, 0.6, 0.1, 1))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def show_history(self):
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        today = datetime.date.today()
        dates = [(today - datetime.timedelta(days=i)).isoformat() for i in range(6, -1, -1)]
        
        graph = HistoryGraph(size_hint_y=0.4)
        scale_base = self.daily_goal_ml if self.daily_goal_ml > 0 else 2000
        graph.goal_ratio = 1.0
        
        stats_text = "[b]7-Day History[/b]\n\n"
        valid_intakes = []
        streak = 0
        
        if self.current_intake_ml >= self.daily_goal_ml and self.daily_goal_ml > 0:
            streak = 1
            for i in range(1, 7):
                prev_day = (today - datetime.timedelta(days=i)).isoformat()
                if self.history.get(prev_day, 0) >= self.daily_goal_ml:
                    streak += 1
                else:
                    break
                    
            if streak >= 3:
                self.unlock_achievement("Triple Threat")
                
        elif self.daily_goal_ml > 0:
            prev_day = (today - datetime.timedelta(days=1)).isoformat()
            if self.history.get(prev_day, 0) >= self.daily_goal_ml:
                streak = 1 
                stats_text += "(Streak ends today if goal not met!)\n"

        for i, date_str in enumerate(dates):
            intake = self.history.get(date_str, 0)
            if date_str == today.isoformat():
                intake = self.current_intake_ml
            if intake > 0:
                valid_intakes.append(intake)
            
            ratio = min(intake / scale_base, 1.2) 
            color = [0.1, 1, 0.5, 1] if intake >= scale_base else [0.1, 0.7, 1, 1]
            setattr(graph, f"r{i}", ratio)
            setattr(graph, f"c{i}", color)

        avg_intake = sum(valid_intakes) / len(valid_intakes) if valid_intakes else 0
        stats_text += f"Current Streak: {streak} days\n"
        stats_text += f"Average Intake (logged days): {avg_intake/1000.0:.1f} L\n\n"
        stats_text += "Legend: [color=0.1,1,0.5,1]Green = Goal Met[/color] | [color=0.1,0.7,1,1]Blue = Under Goal[/color]\n"
        stats_text += "Dashed line represents your daily goal limit.\n\n"

        scroll = ScrollView(size_hint_y=0.5)
        label = Label(text=stats_text, markup=True, size_hint_y=None, valign='top', halign='left', font_size=16, color=(0.9, 0.9, 0.9, 1))
        label.bind(texture_size=label.setter('size'))
        label.bind(width=lambda *x: label.setter('text_size')(label, (label.width, None)))
        scroll.add_widget(label)
        
        content.add_widget(graph)
        content.add_widget(scroll)
        
        def do_export(instance):
            if self.export_csv():
                export_label.text = "[color=0.1,1,0.5,1]Export Successful! Check folder for CSV.[/color]"
            else:
                export_label.text = "[color=1,0.4,0.4,1]Export Failed.[/color]"

        export_btn = RoundedButton(text='Export to CSV', size_hint_y=0.1, background_color=(0.2, 0.5, 0.8, 1))
        export_btn.bind(on_press=do_export)
        export_label = Label(text="", markup=True, size_hint_y=0.05, font_size=14)
        close_btn = RoundedButton(text='Close', size_hint_y=0.1, background_color=(0.1, 0.7, 1, 1))
        
        content.add_widget(export_btn)
        content.add_widget(export_label)
        content.add_widget(close_btn)
        
        popup = Popup(title='Your History', content=content, size_hint=(0.9, 0.95), background_color=(0.12, 0.14, 0.18, 1), separator_color=(0.1, 0.7, 1, 1))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def show_research(self):
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        scroll = ScrollView()
        
        research_text = """[b]Academic Basis for Hydration Goals[/b]

[u]1. How Much Water Do You Need?[/u]
This app uses a weight-based clinical formula: [b]35 ml per kg of body weight[/b].
(Sawka et al., 2005; Institute of Medicine). 

[u]2. Activity Multiplier[/u]
The ACSM recommends adding [b]400 to 600 ml per hour of exercise[/b] to compensate for sweat loss (Sawka et al., 2007).

[u]3. Environmental Adjustments[/u]
[b]Hot/Humid:[/b] Sweating increases dramatically to maintain thermoregulation. (+700 ml)
[b]High Altitude:[/b] Water loss through respiration increases due to dry air and increased breathing rate (+500 ml).
[b]Cold:[/b] Cold-induced diuresis and reduced sweating slightly lower baseline needs (-250 ml), though respiratory loss still occurs (Institute of Medicine, 2005).

[u]4. Beverage Types & Diuretics[/u]
[b]Coffee/Tea:[/b] Hydration multiplier applied: [b]0.7[/b] (Maughan et al., 2003).
[b]Juice:[/b] High sugar slows gastric emptying. Hydration multiplier: [b]0.9[/b].

[u]5. Hyponatremia Warning[/u]
Drinking too much water too quickly can lead to Exercise-Associated Hyponatremia (EAH). This app limits single logs to under 1500ml to prevent accidental overconsumption (Hew-Butler et al., 2015).

[u]References:[/u]
- Institute of Medicine (US). (2005). Dietary Reference Intakes for Water.
- Sawka, M. N., et al. (2007). ACSM position stand on Exercise and Fluid Replacement.
- Maughan, R. J., et al. (2003). Hydration and health. Journal of the American College of Nutrition.
- Hew-Butler, T., et al. (2015). Statement of the 3rd International Exercise-Associated Hyponatremia Consensus Development Conference.
"""
        label = Label(text=research_text, markup=True, size_hint_y=None, valign='top', halign='left', font_size=16, color=(0.9, 0.9, 0.9, 1))
        label.bind(texture_size=label.setter('size'))
        label.bind(width=lambda *x: label.setter('text_size')(label, (label.width, None)))
        scroll.add_widget(label)
        
        close_btn = RoundedButton(text='Close', size_hint_y=0.1, background_color=(0.1, 0.7, 1, 1))
        content.add_widget(scroll)
        content.add_widget(close_btn)
        
        popup = Popup(title='Hydration Research', content=content, size_hint=(0.9, 0.85), background_color=(0.12, 0.14, 0.18, 1), separator_color=(0.1, 0.7, 1, 1))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

class WaterApp(App):
    def build(self):
        return WaterTracker()

if __name__ == '__main__':
    WaterApp().run()