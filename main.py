import os
import json
import threading
import time
import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button


# ---------- ЛОГИРОВАНИЕ ----------

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")
os.makedirs(LOG_DIR, exist_ok=True)


def log(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


# ---------- СОСТОЯНИЕ И ТРИГГЕРЫ ----------

TRIGGERS_PATH = "config_triggers.json"


def load_triggers():
    if not os.path.exists(TRIGGERS_PATH):
        return {
            "button_a": ["hello", "start", "go"],
            "button_b": ["world", "stop"]
        }
    try:
        with open(TRIGGERS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log(f"Ошибка чтения триггеров: {e}")
        return {
            "button_a": ["hello", "start", "go"],
            "button_b": ["world", "stop"]
        }


def save_triggers(data):
    try:
        with open(TRIGGERS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        log("Триггеры сохранены")
    except Exception as e:
        log(f"Ошибка сохранения триггеров: {e}")


TRIGGERS = load_triggers()


class AppState:
    scanning = False


state = AppState()


# ---------- ПРОСТЕЙШИЙ EVENT BUS ----------

class EventBus:
    def __init__(self):
        from queue import Queue
        self.q = Queue()

    def push(self, event):
        self.q.put(event)

    def pop(self):
        return self.q.get() if not self.q.empty() else None


event_bus = EventBus()


# ---------- ДЕТЕКТОР ТЕКСТА ----------

def analyze_text(text: str):
    text = text.lower()
    for key, words in TRIGGERS.items():
        for w in words:
            if w.lower() in text:
                return key
    return None


# ---------- ПОТОК НАБЛЮДЕНИЯ ----------

class Watcher(threading.Thread):
    def __init__(self, get_text_callback):
        super().__init__(daemon=True)
        self.get_text = get_text_callback

    def run(self):
        while True:
            if state.scanning:
                text = self.get_text()
                event = analyze_text(text)
                if event:
                    log(f"Обнаружен триггер: {event}")
                    event_bus.push(event)
            time.sleep(0.5)


# ---------- UI ----------

class RootLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=10, spacing=10, **kwargs)

        # Статус
        self.status_label = Label(
            text="Статус: ожидание",
            size_hint_y=None,
            height=40
        )
        self.add_widget(self.status_label)

        # Прогресс
        self.progress = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height=20
        )
        self.add_widget(self.progress)

        # Входящий текст
        self.observe_input = TextInput(
            hint_text="Входящий текст",
            size_hint_y=0.3
        )
        self.add_widget(self.observe_input)

        # Кнопки A/B
        btn_box = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=50,
            spacing=10
        )
        self.button_a = Button(text="A")
        self.button_b = Button(text="B")
        self.button_a.bind(on_press=self.on_button_a)
        self.button_b.bind(on_press=self.on_button_b)
        btn_box.add_widget(self.button_a)
        btn_box.add_widget(self.button_b)
        self.add_widget(btn_box)

        # Панель настроек триггеров
        settings_box = BoxLayout(
            orientation="vertical",
            size_hint_y=0.3,
            spacing=5
        )

        settings_box.add_widget(Label(text="Настройки триггеров"))

        row_a = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=30,
            spacing=5
        )
        row_a.add_widget(Label(text="Триггеры A:"))
        self.triggers_a_input = TextInput(
            text=",".join(TRIGGERS.get("button_a", [])),
            multiline=False
        )
        row_a.add_widget(self.triggers_a_input)
        settings_box.add_widget(row_a)

        row_b = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=30,
            spacing=5
        )
        row_b.add_widget(Label(text="Триггеры B:"))
        self.triggers_b_input = TextInput(
            text=",".join(TRIGGERS.get("button_b", [])),
            multiline=False
        )
        row_b.add_widget(self.triggers_b_input)
        settings_box.add_widget(row_b)

        save_btn = Button(
            text="Сохранить триггеры",
            size_hint_y=None,
            height=40
        )
        save_btn.bind(on_press=self.on_save_triggers)
        settings_box.add_widget(save_btn)

        self.add_widget(settings_box)

        # Кнопка запуска/остановки
        self.toggle_scan_btn = Button(
            text="Запустить",
            size_hint_y=None,
            height=50
        )
        self.toggle_scan_btn.bind(on_press=self.on_toggle_scan)
        self.add_widget(self.toggle_scan_btn)

    # --- Обработчики кнопок ---

    def on_button_a(self, instance):
        self.status_label.text = "Статус: нажата A"
        log("Ручное нажатие A")
        self.animate_status()
        self.pulse_button(self.button_a)

    def on_button_b(self, instance):
        self.status_label.text = "Статус: нажата B"
        log("Ручное нажатие B")
        self.animate_status()
        self.pulse_button(self.button_b)

    def on_toggle_scan(self, instance):
        state.scanning = not state.scanning
        self.toggle_scan_btn.text = "Остановить" if state.scanning else "Запустить"
        self.status_label.text = "Статус: сканирование" if state.scanning else "Статус: ожидание"
        log(f"Сканирование: {'включено' if state.scanning else 'выключено'}")

    def on_save_triggers(self, instance):
        global TRIGGERS
        a = [x.strip() for x in self.triggers_a_input.text.split(",") if x.strip()]
        b = [x.strip() for x in self.triggers_b_input.text.split(",") if x.strip()]
        TRIGGERS = {"button_a": a, "button_b": b}
        save_triggers(TRIGGERS)
        self.status_label.text = "Статус: триггеры сохранены"
        self.animate_status()

    # --- UI эффекты ---

    def animate_status(self):
        self.status_label.color = (1, 0.3, 0.3, 1)
        Clock.schedule_once(lambda dt: self.reset_status_color(), 0.3)

    def reset_status_color(self):
        self.status_label.color = (1, 1, 1, 1)

    def pulse_button(self, btn):
        btn.background_color = (0.3, 0.8, 0.3, 1)
        Clock.schedule_once(lambda dt: self.reset_button_color(btn), 0.2)

    def reset_button_color(self, btn):
        btn.background_color = (1, 1, 1, 1)


# ---------- ПРИЛОЖЕНИЕ ----------

class AutoApp(App):
    def build(self):
        self.title = "Kivy AutoClicker (текст, триггеры, лог, эффекты)"
        self.root_layout = RootLayout()

        # Запуск потока наблюдения
        self.watcher = Watcher(self.get_text)
        self.watcher.start()

        # Обработка событий из EventBus
        Clock.schedule_interval(self.process_events, 0.2)

        # Обновление прогрессбара
        Clock.schedule_interval(self.update_progress, 0.2)

        return self.root_layout

    def get_text(self):
        return self.root_layout.observe_input.text

    def process_events(self, dt):
        event = event_bus.pop()
        if event:
            if event == "button_a":
                self.root_layout.button_a.trigger_action()
                self.root_layout.pulse_button(self.root_layout.button_a)
            elif event == "button_b":
                self.root_layout.button_b.trigger_action()
                self.root_layout.pulse_button(self.root_layout.button_b)

            self.root_layout.status_label.text = f"Статус: авто {event}"
            self.root_layout.animate_status()
            log(f"Авто-нажатие: {event}")

    def update_progress(self, dt):
        p = self.root_layout.progress
        p.value = (p.value + 5) % 100


if __name__ == "__main__":
    AutoApp().run()