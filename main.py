import requests
from datetime import datetime
from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView

FIREBASE_URL = "https://factoryleaveapp-default-rtdb.firebaseio.com/applications"

class LeaveApp(App):
    def build(self):
        self.title = "Subh Paper - Worker Leave Portal"
        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        root.add_widget(Label(text="[b]SUBH PAPER COMPANY[/b]\nWorker Leave Portal", markup=True,
                              font_size="20sp", size_hint_y=None, height=dp(65)))

        scroll = ScrollView()
        form = BoxLayout(orientation="vertical", spacing=dp(7), size_hint_y=None)
        form.bind(minimum_height=form.setter("height"))

        self.emp_code = self.field(form, "Employee Code", "L001")
        self.leave_type = Spinner(text="Casual Leave",
                                  values=("Casual Leave", "Sick Leave", "Earned Leave"),
                                  size_hint_y=None, height=dp(46))
        form.add_widget(Label(text="Leave Type", size_hint_y=None, height=dp(24)))
        form.add_widget(self.leave_type)
        self.start_date = self.field(form, "Start Date (YYYY-MM-DD)", datetime.now().strftime("%Y-%m-%d"))
        self.end_date = self.field(form, "End Date (YYYY-MM-DD)", datetime.now().strftime("%Y-%m-%d"))
        self.total_days = self.field(form, "Total Days", "1")
        self.reason = self.field(form, "Reason for Leave", "")
        self.reason.multiline = True
        self.reason.height = dp(70)

        send = Button(text="SEND APPLICATION", size_hint_y=None, height=dp(52), bold=True)
        send.bind(on_press=self.send_application)
        form.add_widget(send)
        status = Button(text="CHECK MY STATUS", size_hint_y=None, height=dp(52), bold=True)
        status.bind(on_press=self.check_status)
        form.add_widget(status)
        scroll.add_widget(form)
        root.add_widget(scroll)
        return root

    def field(self, parent, title, default):
        parent.add_widget(Label(text=title, size_hint_y=None, height=dp(24)))
        t = TextInput(text=default, multiline=False, size_hint_y=None, height=dp(46))
        parent.add_widget(t)
        return t

    def show_popup(self, title, message):
        box = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        box.add_widget(Label(text=message, halign="center", valign="middle"))
        b = Button(text="OK", size_hint_y=None, height=dp(44))
        box.add_widget(b)
        p = Popup(title=title, content=box, size_hint=(0.88, 0.42))
        b.bind(on_press=p.dismiss)
        p.open()

    def validate(self):
        code = self.emp_code.text.strip().upper()
        reason = self.reason.text.strip()
        try:
            start = datetime.strptime(self.start_date.text.strip(), "%Y-%m-%d")
            end = datetime.strptime(self.end_date.text.strip(), "%Y-%m-%d")
            if end < start:
                raise ValueError("End date cannot be before start date")
            days = (end - start).days + 1
        except ValueError:
            self.show_popup("Invalid Date", "Date YYYY-MM-DD format me bharein aur End Date >= Start Date rakhein.")
            return None
        if not code or not reason:
            self.show_popup("Error", "Employee Code aur Reason required hain.")
            return None
        self.total_days.text = str(days)
        return code, days

    def send_application(self, _):
        result = self.validate()
        if not result:
            return
        code, days = result
        payload = {
            "emp_code": code,
            "leave_type": self.leave_type.text,
            "start_date": self.start_date.text.strip(),
            "end_date": self.end_date.text.strip(),
            "total_days": str(days),
            "reason": self.reason.text.strip(),
            "status": "Pending",
            "source": "Mobile",
            "synced": False,
            "created_at": {".sv": "timestamp"},
        }
        try:
            r = requests.post(FIREBASE_URL + ".json", json=payload, timeout=10)
            if r.ok:
                key = (r.json() or {}).get("name", "")
                self.reason.text = ""
                self.show_popup("Success", "Application Factory Office ko bhej di gayi hai.\n\nApplication ID: " + key)
            else:
                self.show_popup("Server Error", f"Application send nahi hui. HTTP {r.status_code}")
        except requests.RequestException:
            self.show_popup("Internet Error", "Internet connection check karke dobara try karein.")

    def check_status(self, _):
        code = self.emp_code.text.strip().upper()
        if not code:
            self.show_popup("Warning", "Employee Code darj karein.")
            return
        try:
            r = requests.get(FIREBASE_URL + ".json", timeout=10)
            if not r.ok:
                self.show_popup("Server Error", f"Status load nahi hua. HTTP {r.status_code}")
                return
            data = r.json() or {}
            apps = []
            for key, value in data.items():
                if isinstance(value, dict) and str(value.get("emp_code", "")).upper() == code:
                    apps.append((value.get("created_at", 0) or 0, key, value))
            if not apps:
                self.show_popup("Info", "Is Employee Code ke liye koi application nahi mili.")
                return
            _, key, latest = sorted(apps, key=lambda x: x[0] if isinstance(x[0], (int, float)) else 0)[-1]
            status = latest.get("status", "Pending")
            msg = (f"Application ID: {key}\n"
                   f"Leave: {latest.get('leave_type', '')}\n"
                   f"Date: {latest.get('start_date', '')} to {latest.get('end_date', '')}\n"
                   f"Status: {status}")
            self.show_popup("Leave Status", msg)
        except requests.RequestException:
            self.show_popup("Internet Error", "Server se connect nahi ho paya.")

if __name__ == "__main__":
    LeaveApp().run()
