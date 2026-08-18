import sqlite3
import sys
import os
import webbrowser
import tempfile
import requests
import tkinter as tk
from tkinter import ttk, messagebox

FIREBASE_URL = "https://factoryleaveapp-default-rtdb.firebaseio.com/applications"

def connect_db():
    return sqlite3.connect('factory.db')

def get_employees():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT emp_code, name, department FROM employees")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception:
        return []

class FactoryLeaveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Factory Leave Management System")
        self.root.geometry("850x650")
        self.root.configure(bg="#f0f2f5")

        title_frame = tk.Frame(root, bg="#1e3d59", pady=12)
        title_frame.pack(fill="x")
        title_label = tk.Label(title_frame, text="FACTORY LEAVE MANAGEMENT SYSTEM", font=("Arial", 16, "bold"), fg="white", bg="#1e3d59")
        title_label.pack()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=15)

        self.tab_apply = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_apply, text=" 📝 Apply Leave ")
        self.setup_apply_tab()

        self.tab_history = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_history, text=" 📋 Leave History & Approvals ")
        self.setup_history_tab()

    def setup_apply_tab(self):
        frame = tk.LabelFrame(self.tab_apply, text=" Leave Application Form ", font=("Arial", 11, "bold"), padx=20, pady=15)
        frame.pack(fill="both", expand=True, padx=20, pady=15)

        tk.Label(frame, text="Select Employee:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=8)
        self.emp_list = get_employees()
        self.emp_options = [f"{e[0]} - {e[1]} ({e[2]})" for e in self.emp_list]
        self.emp_combobox = ttk.Combobox(frame, values=self.emp_options, width=45, state="readonly")
        self.emp_combobox.grid(row=0, column=1, pady=8, padx=10)
        if self.emp_options:
            self.emp_combobox.current(0)

        tk.Label(frame, text="Leave Type:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=8)
        self.type_combobox = ttk.Combobox(frame, values=["Casual Leave", "Sick Leave", "Earned Leave"], width=45, state="readonly")
        self.type_combobox.grid(row=1, column=1, pady=8, padx=10)
        self.type_combobox.current(0)

        tk.Label(frame, text="Start Date (YYYY-MM-DD):", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=8)
        self.start_date_entry = ttk.Entry(frame, width=48)
        self.start_date_entry.grid(row=2, column=1, pady=8, padx=10)
        self.start_date_entry.insert(0, "2026-08-17")

        tk.Label(frame, text="End Date (YYYY-MM-DD):", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="w", pady=8)
        self.end_date_entry = ttk.Entry(frame, width=48)
        self.end_date_entry.grid(row=3, column=1, pady=8, padx=10)
        self.end_date_entry.insert(0, "2026-08-17")

        tk.Label(frame, text="Total Days:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky="w", pady=8)
        self.days_entry = ttk.Entry(frame, width=48)
        self.days_entry.grid(row=4, column=1, pady=8, padx=10)
        self.days_entry.insert(0, "1")

        tk.Label(frame, text="Reason / Details:", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky="w", pady=8)
        self.reason_entry = ttk.Entry(frame, width=48)
        self.reason_entry.grid(row=5, column=1, pady=8, padx=10)

        btn_box = tk.Frame(frame)
        btn_box.grid(row=6, column=0, columnspan=2, pady=20)

        print_btn = tk.Button(btn_box, text=" 🖨️ Print / Download Form ", font=("Arial", 10, "bold"), bg="#28a745", fg="white", command=self.generate_print_form)
        print_btn.pack(side="left", padx=10)

        submit_btn = tk.Button(btn_box, text=" Submit Application ", font=("Arial", 10, "bold"), bg="#17a2b8", fg="white", command=self.submit_leave)
        submit_btn.pack(side="left", padx=10)

    def generate_print_form(self):
        emp_selection = self.emp_combobox.get()
        if not emp_selection:
            messagebox.showerror("Error", "Please select an employee")
            return

        try:
            emp_code = emp_selection.split(" - ")[0]
            rest = emp_selection[len(emp_code)+3:]
            emp_name = rest.split(" (")[0]
            dept = rest.split(" (")[1].replace(")", "") if "(" in rest else ""
        except Exception:
            emp_code = emp_selection
            emp_name = ""
            dept = ""

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Leave Application - {emp_code}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8f9fa; }}
        .container {{ max-width: 750px; margin: 0 auto; background: #ffffff; padding: 30px; border: 2px solid #1e3d59; border-radius: 8px; }}
        .header {{ text-align: center; border-bottom: 2px solid #1e3d59; padding-bottom: 12px; margin-bottom: 25px; }}
        .header h1 {{ margin: 0; color: #1e3d59; font-size: 24px; text-transform: uppercase; }}
        .header p {{ margin: 5px 0 0 0; font-size: 14px; font-weight: bold; color: #555; }}
        .section-title {{ background-color: #1e3d59; color: #ffffff; padding: 6px 12px; font-size: 14px; font-weight: bold; border-radius: 4px; margin-top: 20px; margin-bottom: 15px; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 15px; }}
        td {{ padding: 10px; font-size: 14px; vertical-align: middle; }}
        .label {{ font-weight: bold; width: 30%; color: #333; }}
        .line {{ border-bottom: 1px dashed #777; width: 70%; }}
        .checkbox-group {{ display: flex; gap: 20px; }}
        .checkbox-item {{ display: flex; align-items: center; gap: 5px; }}
        .box {{ width: 16px; height: 16px; border: 1.5px solid #333; display: inline-block; }}
        .footer-sig {{ margin-top: 40px; display: flex; justify-content: space-between; padding: 0 10px; }}
        .sig-box {{ text-align: center; width: 200px; border-top: 1px solid #333; padding-top: 5px; font-size: 13px; font-weight: bold; }}
        .no-print {{ text-align: center; margin-bottom: 20px; }}
        .btn-print {{ background-color: #28a745; color: white; border: none; padding: 10px 20px; font-size: 16px; font-weight: bold; border-radius: 5px; cursor: pointer; }}
        @media print {{ .no-print {{ display: none; }} body {{ background-color: #ffffff; margin: 0; }} .container {{ border: 2px solid #000; box-shadow: none; }} }}
    </style>
</head>
<body>
    <div class="no-print">
        <button class="btn-print" onclick="window.print()">🖨️ Print / Save as PDF</button>
    </div>
    <div class="container">
        <div class="header">
            <h1>SUBH PAPER COMPANY</h1>
            <p>EMPLOYEE LEAVE APPLICATION FORM / chutti aavedan patra</p>
        </div>
        <div class="section-title">1. EMPLOYEE DETAILS (Karmachari ki Jankari)</div>
        <table>
            <tr>
                <td class="label">Application Date:</td>
                <td class="line"></td>
                <td class="label" style="width:20%; text-align:right;">Emp Code:</td>
                <td style="font-weight:bold; font-size:15px; width:20%;">{emp_code}</td>
            </tr>
            <tr>
                <td class="label">Employee Name:</td>
                <td colspan="3" style="font-weight:bold; font-size:15px; border-bottom: 1px solid #ccc;">{emp_name}</td>
            </tr>
            <tr>
                <td class="label">Department / Machine:</td>
                <td colspan="3" style="font-weight:bold; font-size:15px; border-bottom: 1px solid #ccc;">{dept}</td>
            </tr>
        </table>
        <div class="section-title">2. LEAVE DETAILS (Chutti ki Jankari)</div>
        <table>
            <tr>
                <td class="label">Type of Leave:</td>
                <td colspan="3">
                    <div class="checkbox-group">
                        <div class="checkbox-item"><span class="box"></span> Casual Leave (CL)</div>
                        <div class="checkbox-item"><span class="box"></span> Sick Leave (SL)</div>
                        <div class="checkbox-item"><span class="box"></span> Earned Leave (EL)</div>
                    </div>
                </td>
            </tr>
            <tr>
                <td class="label">Leave Period:</td>
                <td colspan="3">From: ________________________ &nbsp;&nbsp;&nbsp;&nbsp; To: ________________________</td>
            </tr>
            <tr>
                <td class="label">Total Days:</td>
                <td colspan="3">________________________ Din</td>
            </tr>
            <tr>
                <td class="label">Reason for Leave:</td>
                <td colspan="3" class="line" style="height:40px;"></td>
            </tr>
        </table>
        <br>
        <div class="footer-sig">
            <div class="sig-box">Employee Signature</div>
            <div class="sig-box">Supervisor Signature</div>
        </div>
        <div class="section-title" style="margin-top:40px; background-color:#6c757d;">3. FOR OFFICE & SYSTEM USE ONLY</div>
        <table>
            <tr>
                <td class="label">Application Status:</td>
                <td><span class="box"></span> APPROVED &nbsp;&nbsp;&nbsp;&nbsp; <span class="box"></span> REJECTED</td>
            </tr>
            <tr>
                <td class="label">Entered in Software:</td>
                <td><span class="box"></span> YES &nbsp;&nbsp;&nbsp;&nbsp; <span class="box"></span> NO</td>
            </tr>
        </table>
        <div class="footer-sig" style="margin-top:30px;">
            <div></div>
            <div class="sig-box">Authorized Manager Signature</div>
        </div>
    </div>
</body>
</html>
"""
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, f"Leave_Form_{emp_code}.html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        webbrowser.open(f"file://{file_path}")

    def submit_leave(self):
        emp_selection = self.emp_combobox.get()
        if not emp_selection:
            messagebox.showerror("Error", "Please select an employee")
            return
        emp_code = emp_selection.split(" - ")[0]
        leave_type = self.type_combobox.get()
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()
        try:
            total_days = int(self.days_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Total Days must be a number!")
            return
        reason = self.reason_entry.get().strip()

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO leave_applications (emp_code, leave_type, start_date, end_date, total_days, reason)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (emp_code, leave_type, start_date, end_date, total_days, reason))
            conn.commit()
            conn.close()

            # Push to Firebase
            try:
                payload = {
                    "emp_code": emp_code,
                    "leave_type": leave_type,
                    "start_date": start_date,
                    "end_date": end_date,
                    "total_days": total_days,
                    "reason": reason,
                    "status": "Pending",
                    "source": "Desktop"
                }
                requests.post(f"{FIREBASE_URL}.json", json=payload, timeout=5)
            except Exception:
                pass

            messagebox.showinfo("Success", "✅ Leave Application Submitted Successfully!")
            self.reason_entry.delete(0, tk.END)
            self.refresh_history()
        except Exception as e:
            messagebox.showerror("Database Error", f"Error saving data: {str(e)}")

    def setup_history_tab(self):
        btn_frame = tk.Frame(self.tab_history)
        btn_frame.pack(fill="x", padx=10, pady=5)

        approve_btn = tk.Button(btn_frame, text=" Approve Selected ", bg="#28a745", fg="white", font=("Arial", 10, "bold"), command=lambda: self.update_status("Approved"))
        approve_btn.pack(side="left", padx=5)

        reject_btn = tk.Button(btn_frame, text=" Reject Selected ", bg="#dc3545", fg="white", font=("Arial", 10, "bold"), command=lambda: self.update_status("Rejected"))
        reject_btn.pack(side="left", padx=5)

        refresh_btn = tk.Button(btn_frame, text=" 🔄 Sync Online Requests ", bg="#007bff", fg="white", font=("Arial", 10, "bold"), command=self.sync_and_refresh)
        refresh_btn.pack(side="right", padx=5)

        columns = ("ID", "Code", "Name", "Department", "Type", "Start", "End", "Days", "Reason", "Status")
        self.tree = ttk.Treeview(self.tab_history, columns=columns, show="headings", height=18)
        
        widths = [40, 60, 130, 110, 90, 85, 85, 45, 120, 80]
        for col, w in zip(columns, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")

        scrollbar = ttk.Scrollbar(self.tab_history, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        self.refresh_history()

    def sync_and_refresh(self):
        # Fetch Mobile Requests from Firebase
        try:
            res = requests.get(f"{FIREBASE_URL}.json", timeout=5)
            if res.status_code == 200 and res.json():
                fb_data = res.json()
                conn = connect_db()
                cursor = conn.cursor()
                for key, val in fb_data.items():
                    if val.get("source") == "Mobile" and not val.get("synced"):
                        cursor.execute('''
                            INSERT INTO leave_applications (emp_code, leave_type, start_date, end_date, total_days, reason, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (val.get("emp_code"), val.get("leave_type"), val.get("start_date"), val.get("end_date"), val.get("total_days"), val.get("reason"), "Pending"))
                        requests.patch(f"{FIREBASE_URL}/{key}.json", json={"synced": True})
                conn.commit()
                conn.close()
        except Exception:
            pass
        self.refresh_history()

    def refresh_history(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT la.app_id, e.emp_code, e.name, e.department, la.leave_type, la.start_date, la.end_date, la.total_days, la.reason, la.status
                FROM leave_applications la
                JOIN employees e ON la.emp_code = e.emp_code
                ORDER BY la.app_id DESC
            ''')
            records = cursor.fetchall()
            conn.close()

            for r in records:
                self.tree.insert("", "end", values=r)
        except Exception:
            pass

    def update_status(self, new_status):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Kripya list me se koi ek application select karein!")
            return
        
        values = self.tree.item(selected_item)['values']
        app_id = values[0]
        emp_code = values[1]
        
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE leave_applications SET status = ? WHERE app_id = ?", (new_status, app_id))
            conn.commit()
            conn.close()

            # Online Firebase Status Updates
            try:
                res = requests.get(f"{FIREBASE_URL}.json", timeout=5)
                if res.status_code == 200 and res.json():
                    for key, val in res.json().items():
                        if str(val.get("emp_code")) == str(emp_code):
                            requests.patch(f"{FIREBASE_URL}/{key}.json", json={"status": new_status})
            except Exception as e:
                print("Firebase update error:", e)

            messagebox.showinfo("Updated", f"Application ID {app_id} ko '{new_status}' kar diya gaya hai.")
            self.refresh_history()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FactoryLeaveApp(root)
    root.mainloop()
