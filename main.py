import sys
import ctypes
import winreg
import json
import os
import urllib.parse
import tkinter as tk
from tkinter import ttk, messagebox
import datetime

# ==========================================
# 1. Hide the black console window immediately
# ==========================================
def hide_console():
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
        ctypes.windll.user32.ShowWindow(hwnd, 0)

hide_console()

# --- System settings and browser policies ---
HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
SETTINGS_FILE = "settings.json"

BROWSER_POLICIES = {
    "Google Chrome": {r"SOFTWARE\Policies\Google\Chrome": ("DnsOverHttpsMode", "off", winreg.REG_SZ)},
    "Microsoft Edge": {r"SOFTWARE\Policies\Microsoft\Edge": ("DnsOverHttpsMode", "off", winreg.REG_SZ)},
    "Brave Browser": {r"SOFTWARE\Policies\BraveSoftware\Brave": ("DnsOverHttpsMode", "off", winreg.REG_SZ)},
    "Vivaldi": {r"SOFTWARE\Policies\Vivaldi": ("DnsOverHttpsMode", "off", winreg.REG_SZ)},
    "Mozilla Firefox": {r"SOFTWARE\Policies\Mozilla\Firefox\DNSOverHTTPS": ("Enabled", 0, winreg.REG_DWORD)}
}

# --- Translated text ---
LANG_DATA = {
    'ar': {
        'title': "أداة التحكم في الوصول للمواقع",
        'tab_sites': "المواقع المحظورة",
        'tab_sched': "جدولة الحظر",
        'lbl_enter_site': "أدخل رابط الموقع المراد حظره:",
        'btn_block': "إضافة للحظر",
        'lbl_blocked_list': "المواقع المدرجة في القائمة:",
        'btn_unblock': "إزالة",
        'btn_toggle_lang': "English",
        'btn_full_exit': "إغلاق الأداة نهائياً",
        
        'mode_always': "حظر دائم (مستمر)",
        'mode_hourly': "مدة زمنية من كل ساعة",
        'mode_range': "فترة زمنية محددة",
        'mode_days': "أيام محددة في الأسبوع",
        'lbl_mins': "دقيقة",
        'lbl_from': "من الساعة (HH:MM):",
        'lbl_to': "إلى الساعة (HH:MM):",
        'btn_save_sched': "حفظ الإعدادات",
        
        'warn_title': "تنبيه هام",
        'warn_msg': "يرجى التأكد من إغلاق جميع المتصفحات قبل المتابعة لتطبيق التعديلات بشكل صحيح.\nهل تريد المتابعة؟",
        'err_empty': "يرجى كتابة اسم الموقع أولاً.",
        'err_exists': "هذا الموقع مدرج بالفعل!",
        'success_saved': "تم حفظ إعدادات الجدولة بنجاح.",
        
        'toast_start_title': "بدء الحظر",
        'toast_start_msg': "بدأت فترة حظر المواقع.",
        'toast_end_title': "انتهاء الحظر",
        'toast_end_msg': "انتهت فترة حظر المواقع.",
        'bg_notice': "البرنامج يعمل الآن في الخلفية. يمكنك إنهاءه من مدير المهام أو بفتحه مجدداً والضغط على 'إغلاق نهائياً'."
    },
    'en': {
        'title': "Website Access Control Tool",
        'tab_sites': "Blocked Sites",
        'tab_sched': "Scheduling",
        'lbl_enter_site': "Enter the website to block:",
        'btn_block': "Add to Blocklist",
        'lbl_blocked_list': "Listed Websites:",
        'btn_unblock': "Remove",
        'btn_toggle_lang': "العربية",
        'btn_full_exit': "Exit Tool Completely",
        
        'mode_always': "Always Blocked",
        'mode_hourly': "Duration per hour",
        'mode_range': "Specific Time Range",
        'mode_days': "Specific Days of the Week",
        'lbl_mins': "Minutes",
        'lbl_from': "From (HH:MM):",
        'lbl_to': "To (HH:MM):",
        'btn_save_sched': "Save Settings",
        
        'warn_title': "Important Warning",
        'warn_msg': "Please ensure all browsers are closed before continuing to apply changes correctly.\nDo you want to continue?",
        'err_empty': "Please enter a website name first.",
        'err_exists': "This website is already listed!",
        'success_saved': "Scheduling settings saved successfully.",
        
        'toast_start_title': "Block Started",
        'toast_start_msg': "Website blocking period has started.",
        'toast_end_title': "Block Ended",
        'toast_end_msg': "Website blocking period has ended.",
        'bg_notice': "Running in background. Kill via Task Manager or re-open and click 'Exit Completely'."
    }
}

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def manage_doh(disable=True):
    for browser, policies in BROWSER_POLICIES.items():
        for path, (key_name, val, val_type) in policies.items():
            try:
                if disable:
                    key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(key, key_name, 0, val_type, val)
                else:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_SET_VALUE)
                    winreg.DeleteValue(key, key_name)
                winreg.CloseKey(key)
            except:
                pass

def clean_domain(url):
    url = url.strip().lower()
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    netloc = urllib.parse.urlparse(url).netloc
    base = netloc[4:] if netloc.startswith('www.') else netloc
    return base, f"www.{base}"

def handle_arabic_shortcuts(event):
    if event.keycode == 86:
        event.widget.event_generate("<<Paste>>")
        return "break"
    elif event.keycode == 67:
        event.widget.event_generate("<<Copy>>")
        return "break"
    elif event.keycode == 88:
        event.widget.event_generate("<<Cut>>")
        return "break"
    elif event.keycode == 65:
        event.widget.event_generate("<<SelectAll>>")
        return "break"

class BlockApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.lang = 'ar'
        
        self.settings = {
            'sites': [],
            'schedule': {
                'mode': 'always',
                'hourly_mins': 25,
                'range_start': '14:00',
                'range_end': '18:00',
                'days': [0, 1, 2, 3, 4, 5, 6] 
            }
        }
        self.load_settings()
        self.is_currently_blocking = False
        
        self.geometry("520x600")
        self.resizable(False, False)
        self.configure(bg="#f0f0f0")
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.protocol("WM_DELETE_WINDOW", self.hide_to_background)
        
        self.setup_ui()
        self.update_texts()
        self.refresh_list()
        self.check_schedule()

    def hide_to_background(self):
        messagebox.showinfo("Background", LANG_DATA[self.lang]['bg_notice'])
        self.withdraw()

    def full_exit(self):
        self.destroy()
        sys.exit()

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    data = json.load(f)
                    self.settings.update(data)
            except:
                pass

    def save_settings(self):
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(self.settings, f)

    def setup_ui(self):
        top_frame = tk.Frame(self, bg="#f0f0f0")
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        self.btn_lang = ttk.Button(top_frame, command=self.toggle_lang, cursor="hand2")
        self.btn_lang.pack(side=tk.RIGHT)
        
        self.btn_exit = tk.Button(top_frame, bg="#333", fg="white", relief=tk.FLAT, cursor="hand2", command=self.full_exit)
        self.btn_exit.pack(side=tk.LEFT, padx=5)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=15, pady=5)
        
        self.tab_sites = tk.Frame(self.notebook, bg="#ffffff")
        self.tab_sched = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(self.tab_sites, text="المواقع")
        self.notebook.add(self.tab_sched, text="الجدولة")
        
        self.setup_sites_tab()
        self.setup_sched_tab()

    def setup_sites_tab(self):
        input_frame = tk.Frame(self.tab_sites, bg="#ffffff")
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.lbl_enter = tk.Label(input_frame, bg="#ffffff", font=("Arial", 11, "bold"))
        self.lbl_enter.pack(pady=(10, 5))
        
        self.entry_site = ttk.Entry(input_frame, font=("Arial", 12), width=35)
        self.entry_site.pack(pady=5)
        self.entry_site.bind("<Control-KeyPress>", handle_arabic_shortcuts)
        
        self.btn_add = tk.Button(input_frame, bg="#d9534f", fg="white", font=("Arial", 11, "bold"), 
                                 relief=tk.FLAT, cursor="hand2", command=self.add_site)
        self.btn_add.pack(pady=(5, 10), ipadx=20, ipady=3)

        self.lbl_list = tk.Label(self.tab_sites, bg="#ffffff", font=("Arial", 11, "bold"))
        self.lbl_list.pack(pady=(5, 5))
        
        list_container = tk.Frame(self.tab_sites)
        list_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        self.canvas = tk.Canvas(list_container, bg="#f9f9f9", bd=1, relief=tk.SOLID, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f9f9f9")
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_sched_tab(self):
        self.sched_mode_var = tk.StringVar(value=self.settings['schedule']['mode'])
        
        self.rb_always = tk.Radiobutton(self.tab_sched, value="always", variable=self.sched_mode_var, bg="#ffffff", font=("Arial", 11, "bold"))
        self.rb_always.pack(anchor="w", padx=20, pady=10)
        
        frame_hourly = tk.Frame(self.tab_sched, bg="#ffffff")
        frame_hourly.pack(fill=tk.X, padx=20, pady=5)
        self.rb_hourly = tk.Radiobutton(frame_hourly, value="hourly", variable=self.sched_mode_var, bg="#ffffff", font=("Arial", 11, "bold"))
        self.rb_hourly.pack(side=tk.LEFT)
        self.spin_hourly = ttk.Spinbox(frame_hourly, from_=1, to=59, width=5)
        self.spin_hourly.set(self.settings['schedule']['hourly_mins'])
        self.spin_hourly.pack(side=tk.LEFT, padx=10)
        self.lbl_mins = tk.Label(frame_hourly, bg="#ffffff")
        self.lbl_mins.pack(side=tk.LEFT)
        
        frame_range = tk.Frame(self.tab_sched, bg="#ffffff")
        frame_range.pack(fill=tk.X, padx=20, pady=5)
        self.rb_range = tk.Radiobutton(frame_range, value="range", variable=self.sched_mode_var, bg="#ffffff", font=("Arial", 11, "bold"))
        self.rb_range.pack(anchor="w")
        
        r_inputs = tk.Frame(frame_range, bg="#ffffff")
        r_inputs.pack(fill=tk.X, padx=30, pady=5)
        self.lbl_from = tk.Label(r_inputs, bg="#ffffff")
        self.lbl_from.grid(row=0, column=0, padx=5)
        self.ent_start = ttk.Entry(r_inputs, width=8)
        self.ent_start.insert(0, self.settings['schedule']['range_start'])
        self.ent_start.grid(row=0, column=1)
        self.lbl_to = tk.Label(r_inputs, bg="#ffffff")
        self.lbl_to.grid(row=0, column=2, padx=5)
        self.ent_end = ttk.Entry(r_inputs, width=8)
        self.ent_end.insert(0, self.settings['schedule']['range_end'])
        self.ent_end.grid(row=0, column=3)
        
        frame_days = tk.Frame(self.tab_sched, bg="#ffffff")
        frame_days.pack(fill=tk.X, padx=20, pady=5)
        self.rb_days = tk.Radiobutton(frame_days, value="days", variable=self.sched_mode_var, bg="#ffffff", font=("Arial", 11, "bold"))
        self.rb_days.pack(anchor="w")
        
        self.day_vars = []
        days_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        d_grid = tk.Frame(frame_days, bg="#ffffff")
        d_grid.pack(padx=30, pady=5, anchor="w")
        for i, d_name in enumerate(days_names):
            var = tk.IntVar(value=1 if i in self.settings['schedule']['days'] else 0)
            self.day_vars.append(var)
            chk = tk.Checkbutton(d_grid, text=d_name, variable=var, bg="#ffffff")
            chk.grid(row=0, column=i, padx=2)

        self.btn_save_sched = tk.Button(self.tab_sched, bg="#5cb85c", fg="white", font=("Arial", 11, "bold"), 
                                        relief=tk.FLAT, cursor="hand2", command=self.save_schedule_ui)
        self.btn_save_sched.pack(pady=20, ipadx=20, ipady=3)

    def update_texts(self):
        t = LANG_DATA[self.lang]
        self.title(t['title'])
        self.btn_lang.config(text=t['btn_toggle_lang'])
        self.btn_exit.config(text=t['btn_full_exit'])
        self.notebook.tab(self.tab_sites, text=t['tab_sites'])
        self.notebook.tab(self.tab_sched, text=t['tab_sched'])
        
        self.lbl_enter.config(text=t['lbl_enter_site'])
        self.btn_add.config(text=t['btn_block'])
        self.lbl_list.config(text=t['lbl_blocked_list'])
        
        self.rb_always.config(text=t['mode_always'])
        self.rb_hourly.config(text=t['mode_hourly'])
        self.lbl_mins.config(text=t['lbl_mins'])
        self.rb_range.config(text=t['mode_range'])
        self.lbl_from.config(text=t['lbl_from'])
        self.lbl_to.config(text=t['lbl_to'])
        self.rb_days.config(text=t['mode_days'])
        self.btn_save_sched.config(text=t['btn_save_sched'])
        
        self.refresh_list()

    def toggle_lang(self):
        self.lang = 'en' if self.lang == 'ar' else 'ar'
        self.update_texts()

    def save_schedule_ui(self):
        self.settings['schedule']['mode'] = self.sched_mode_var.get()
        self.settings['schedule']['hourly_mins'] = int(self.spin_hourly.get())
        self.settings['schedule']['range_start'] = self.ent_start.get()
        self.settings['schedule']['range_end'] = self.ent_end.get()
        self.settings['schedule']['days'] = [i for i, var in enumerate(self.day_vars) if var.get() == 1]
        self.save_settings()
        
        t = LANG_DATA[self.lang]
        messagebox.showinfo(t['title'], t['success_saved'])
        self.evaluate_schedule(force_refresh=True)

    def add_site(self):
        t = LANG_DATA[self.lang]
        raw_url = self.entry_site.get()
        if not raw_url:
            messagebox.showwarning(t['warn_title'], t['err_empty'])
            return
            
        base, www_base = clean_domain(raw_url)
        if base in self.settings['sites']:
            messagebox.showinfo(t['warn_title'], t['err_exists'])
            return
            
        confirm = messagebox.askokcancel(t['warn_title'], t['warn_msg'])
        if not confirm: return

        self.settings['sites'].append(base)
        self.save_settings()
        self.entry_site.delete(0, tk.END)
        self.refresh_list()
        self.evaluate_schedule(force_refresh=True)

    def remove_site(self, site):
        t = LANG_DATA[self.lang]
        
        # Confirm with the user before closing the browser to ensure the unblocking takes effect properly
        confirm = messagebox.askokcancel(t['warn_title'], t['warn_msg'])
        if not confirm: return

        base, www_base = clean_domain(site)
        
        # 1. Remove entries from the hosts file using split() to avoid errors
        try:
            with open(HOSTS_PATH, 'r') as file:
                lines = file.readlines()
            
            with open(HOSTS_PATH, 'w') as file:
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) >= 2 and parts[0] == '127.0.0.1' and parts[1] in [base, www_base]:
                        continue  # Skip the selected site line
                    file.write(line)
        except:
            pass

        # 2. Update the internal settings list
        if base in self.settings['sites']:
            self.settings['sites'].remove(base)
            self.save_settings()
            self.refresh_list()
            
            # 3. Clear the system DNS cache
            os.system("ipconfig /flushdns")

            # 4. Refresh the network state
            self.evaluate_schedule(force_refresh=True)

    def refresh_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        t = LANG_DATA[self.lang]
        for site in self.settings['sites']:
            row = tk.Frame(self.scrollable_frame, bg="#f9f9f9")
            row.pack(fill=tk.X, padx=5, pady=5)
            
            lbl = tk.Label(row, text=site, bg="#f9f9f9", font=("Arial", 11))
            lbl.pack(side=tk.LEFT if self.lang == 'en' else tk.RIGHT, padx=10)
            
            btn = tk.Button(row, text=t['btn_unblock'], bg="#d9534f", fg="white", 
                            relief=tk.FLAT, cursor="hand2", command=lambda s=site: self.remove_site(s))
            btn.pack(side=tk.RIGHT if self.lang == 'en' else tk.LEFT, padx=10)

    # ==========================================
    # Scheduling and background task functions
    # ==========================================
    def show_toast(self, title, msg):
        toast = tk.Toplevel(self)
        toast.overrideredirect(True)
        toast.attributes('-topmost', True)
        
        sw = toast.winfo_screenwidth()
        sh = toast.winfo_screenheight()
        toast.geometry(f"300x80+{sw-320}+{sh-140}")
        toast.configure(bg='#333333')
        
        tk.Label(toast, text=title, fg='white', bg='#333333', font=('Arial', 10, 'bold')).pack(pady=(10, 2))
        tk.Label(toast, text=msg, fg='white', bg='#333333', font=('Arial', 9)).pack()
        
        toast.after(5000, toast.destroy)

    def apply_blocks(self):
        try:
            with open(HOSTS_PATH, 'r') as file:
                lines = file.readlines()
            
            targets = []
            for s in self.settings['sites']:
                b, w = clean_domain(s)
                targets.extend([b, w])
                
            clean_lines = []
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 2 and parts[0] == '127.0.0.1' and parts[1] in targets:
                    continue
                clean_lines.append(line)
            
            if self.settings['sites']:
                with open(HOSTS_PATH, 'w') as file:
                    file.writelines(clean_lines)
                    # Handle the issue of overlapping lines
                    if clean_lines and not clean_lines[-1].endswith('\n'):
                        file.write('\n')
                    for site in self.settings['sites']:
                        file.write(f"127.0.0.1 {site}\n127.0.0.1 www.{site}\n")
                manage_doh(disable=True)
                os.system("ipconfig /flushdns")
            else:
                manage_doh(disable=False)
        except:
            pass

    def remove_all_blocks(self):
        try:
            with open(HOSTS_PATH, 'r') as file:
                lines = file.readlines()
                
            targets = []
            for s in self.settings['sites']:
                b, w = clean_domain(s)
                targets.extend([b, w])
                
            with open(HOSTS_PATH, 'w') as file:
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) >= 2 and parts[0] == '127.0.0.1' and parts[1] in targets:
                        continue
                    file.write(line)
            manage_doh(disable=False)
            os.system("ipconfig /flushdns")
        except:
            pass

    def evaluate_schedule(self, force_refresh=False):
        now = datetime.datetime.now()
        sched = self.settings['schedule']
        should_block = False

        if not self.settings['sites']:
            should_block = False
        elif sched['mode'] == 'always':
            should_block = True
        elif sched['mode'] == 'hourly':
            if now.minute < sched['hourly_mins']:
                should_block = True
        elif sched['mode'] == 'range':
            try:
                s_h, s_m = map(int, sched['range_start'].split(':'))
                e_h, e_m = map(int, sched['range_end'].split(':'))
                start_time = datetime.time(s_h, s_m)
                end_time = datetime.time(e_h, e_m)
                if start_time <= now.time() <= end_time:
                    should_block = True
            except:
                pass
        elif sched['mode'] == 'days':
            if now.weekday() in sched['days']:
                should_block = True

        if should_block != self.is_currently_blocking or force_refresh:
            if should_block:
                self.apply_blocks()
                if should_block != self.is_currently_blocking:
                    self.show_toast(LANG_DATA[self.lang]['toast_start_title'], LANG_DATA[self.lang]['toast_start_msg'])
            else:
                self.remove_all_blocks()
                if should_block != self.is_currently_blocking:
                    self.show_toast(LANG_DATA[self.lang]['toast_end_title'], LANG_DATA[self.lang]['toast_end_msg'])
            
            self.is_currently_blocking = should_block

    def check_schedule(self):
        self.evaluate_schedule()
        self.after(10000, self.check_schedule)

if __name__ == "__main__":
    if is_admin():
        app = BlockApp()
        app.mainloop()
    else:
        hide_console() 
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 0)