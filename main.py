# fitness_tracker_app.py
# Enhanced Kivy Android Fitness App with time tracker, calendar log, custom exercise add-on, and improved UI

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy_garden.graph import Graph, LinePlot
from kivy.uix.scrollview import ScrollView
import datetime
import csv
import os

# Personalized Workout Plan
workout_data = {
    'Monday': [('Push-ups', '3 sets x 12 reps'), ('Dumbbell Rows', '3 sets x 10 reps'), ('Jump Rope', '3 min')],
    'Tuesday': [('Yoga Stretching', '15 min'), ('Light Resistance Band Pulls', '2 sets x 15 reps')],
    'Wednesday': [('Pull-ups', '3 sets'), ('Hand Gripper', '3 sets x 20 reps')],
    'Thursday': [('Squats', '3 sets x 15 reps'), ('Shoulder Band Press', '3 sets x 12 reps'), ('Jump Rope', '5 min')],
    'Friday': [('Planks', '3 sets x 1 min'), ('Push-ups', '2 sets x 10 reps')],
    'Saturday': [('Stretching & Recovery', '15 min'), ('Light Jump Rope', '3 min')],
    'Sunday': [('Full Routine', 'All exercises from above with reduced sets')]
}

weight_log = []  # [(date, weight)]
exercise_log = set()  # Dates user completed workout

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text='🏋️ Welcome to Fitness Tracker App', font_size=24))
        layout.add_widget(Button(text='📋 View Workout Routine', font_size=18, size_hint=(1, 0.2), on_press=self.goto_workout))
        layout.add_widget(Button(text='📈 Weight Tracker', font_size=18, size_hint=(1, 0.2), on_press=self.goto_weight))
        layout.add_widget(Button(text='🗓️ Calendar Log', font_size=18, size_hint=(1, 0.2), on_press=self.goto_calendar))
        layout.add_widget(Button(text='❌ Exit', font_size=18, size_hint=(1, 0.2), on_press=lambda x: App.get_running_app().stop()))
        self.add_widget(layout)

    def goto_workout(self, instance):
        self.manager.current = 'workout'

    def goto_weight(self, instance):
        self.manager.current = 'weight'

    def goto_calendar(self, instance):
        self.manager.current = 'calendar'

class WorkoutScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.label = Label(text='', font_size=22, size_hint_y=None, height=50)
        self.layout.add_widget(self.label)

        scroll = ScrollView(size_hint=(1, 0.6))
        self.exercise_grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.exercise_grid.bind(minimum_height=self.exercise_grid.setter('height'))
        scroll.add_widget(self.exercise_grid)
        self.layout.add_widget(scroll)

        self.custom_name = TextInput(hint_text='Exercise Name', size_hint_y=None, height=40)
        self.custom_detail = TextInput(hint_text='Exercise Details', size_hint_y=None, height=40)
        self.layout.add_widget(self.custom_name)
        self.layout.add_widget(self.custom_detail)
        self.layout.add_widget(Button(text='➕ Add Custom Exercise', size_hint_y=None, height=40, on_press=self.add_custom_exercise))

        self.timer_label = Label(text='Time: 0 sec', font_size=18, size_hint_y=None, height=40)
        self.layout.add_widget(self.timer_label)
        self.timer = 0

        self.start_btn = Button(text='▶️ Start Workout Timer', font_size=18, on_press=self.start_timer)
        self.stop_btn = Button(text='⏹ Stop Timer', font_size=18, on_press=self.stop_timer)
        self.layout.add_widget(self.start_btn)
        self.layout.add_widget(self.stop_btn)

        self.back_button = Button(text='🔙 Back to Main Menu', size_hint=(1, 0.2), on_press=lambda x: setattr(self.manager, 'current', 'main'))
        self.layout.add_widget(self.back_button)

        self.add_widget(self.layout)
        self.refresh_workout()

    def refresh_workout(self):
        self.exercise_grid.clear_widgets()
        today = datetime.datetime.today().strftime('%A')
        self.label.text = f"🗓️ Workout for {today}"
        for name, desc in workout_data.get(today, []):
            self.exercise_grid.add_widget(Label(text=f"✅ {name}: {desc}", font_size=18, size_hint_y=None, height=30))

    def add_custom_exercise(self, instance):
        name = self.custom_name.text.strip()
        desc = self.custom_detail.text.strip()
        if name and desc:
            self.exercise_grid.add_widget(Label(text=f"✅ {name}: {desc}", font_size=18, size_hint_y=None, height=30))
            self.custom_name.text = ''
            self.custom_detail.text = ''

    def start_timer(self, instance):
        self.timer = 0
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)
        self.start_btn.disabled = True
        # log today's date
        today_date = datetime.datetime.today().strftime('%Y-%m-%d')
        exercise_log.add(today_date)

    def stop_timer(self, instance):
        if hasattr(self, 'timer_event'):
            self.timer_event.cancel()
        self.start_btn.disabled = False

    def update_timer(self, dt):
        self.timer += 1
        self.timer_label.text = f"Time: {self.timer} sec"

class WeightTrackerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        layout.add_widget(Label(text='⚖️ Enter your weight (kg):', font_size=20))
        self.input = TextInput(multiline=False, input_filter='float', font_size=18)
        layout.add_widget(self.input)

        layout.add_widget(Button(text='➕ Log Weight', font_size=18, on_press=self.log_weight))
        layout.add_widget(Button(text='📈 Show Graph', font_size=18, on_press=self.show_graph))
        layout.add_widget(Button(text='📄 Export to CSV', font_size=18, on_press=self.export_csv))
        layout.add_widget(Button(text='🔙 Back to Main Menu', font_size=18, on_press=lambda x: setattr(self.manager, 'current', 'main')))

        self.graph_label = Label(text='Graph display here', font_size=16)
        layout.add_widget(self.graph_label)

        self.add_widget(layout)

    def log_weight(self, instance):
        try:
            weight = float(self.input.text)
            date = datetime.datetime.today().strftime('%Y-%m-%d')
            weight_log.append((date, weight))
            self.graph_label.text = f"✅ Logged: {weight}kg on {date}"
            self.input.text = ''
        except ValueError:
            self.graph_label.text = '⚠️ Invalid input! Please enter a number.'

    def show_graph(self, instance):
        if not weight_log:
            self.graph_label.text = '❌ No data to plot yet.'
            return
        graph = Graph(xlabel='Entry', ylabel='Weight (kg)', x_ticks_minor=1, x_ticks_major=1, y_ticks_major=1,
                      y_grid_label=True, x_grid_label=True, padding=5, x_grid=True, y_grid=True,
                      xmin=0, xmax=len(weight_log), ymin=min(w[1] for w in weight_log) - 1,
                      ymax=max(w[1] for w in weight_log) + 1)
        plot = LinePlot(line_width=1.5, color=[0, 1, 0, 1])
        plot.points = [(i, w[1]) for i, w in enumerate(weight_log)]
        graph.add_plot(plot)
        self.clear_widgets()
        self.add_widget(graph)
        self.add_widget(Button(text='🔙 Back', on_press=lambda x: setattr(self.manager, 'current', 'main')))

    def export_csv(self, instance):
        path = os.path.join(os.getcwd(), 'weight_log.csv')
        with open(path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Date', 'Weight (kg)'])
            writer.writerows(weight_log)
        self.graph_label.text = f'📅 CSV saved to {path}'

class CalendarScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text='🗓️ Workout Calendar Log', font_size=22))

        today = datetime.datetime.today()
        grid = GridLayout(cols=7, spacing=5, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        for i in range(1, 32):
            date_str = today.replace(day=i).strftime('%Y-%m-%d')
            completed = date_str in exercise_log
            color = (0, 1, 0, 1) if completed else (1, 0, 0, 1)
            btn = Button(text=str(i), background_color=color)
            grid.add_widget(btn)

        scroll = ScrollView(size_hint=(1, 0.7))
        scroll.add_widget(grid)
        layout.add_widget(scroll)
        layout.add_widget(Button(text='🔙 Back to Main Menu', font_size=18, on_press=lambda x: setattr(self.manager, 'current', 'main')))
        self.add_widget(layout)

class FitnessApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(WorkoutScreen(name='workout'))
        sm.add_widget(WeightTrackerScreen(name='weight'))
        sm.add_widget(CalendarScreen(name='calendar'))
        return sm

if __name__ == '__main__':
    FitnessApp().run()
