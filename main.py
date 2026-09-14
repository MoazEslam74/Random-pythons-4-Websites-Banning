import sys
import ctypes
import winreg
import json
import os
import urllib.parse
import tkinter as tk
from tkinter import ttk, messagebox

# --- System settings and browser policies ---
HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
SAVE_FILE = "blocked_sites.json"

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
        'lbl_enter_site': "أدخل رابط الموقع المراد حظره:",
        'btn_block': "تفعيل الحظر",
        'lbl_blocked_list': "المواقع المحظورة حالياً:",
        'btn_unblock': "فك الحظر",
        'btn_toggle_lang': "English",
        'warn_title': "تنبيه هام",
        'warn_msg': "يرجى التأكد من إغلاق جميع المتصفحات قبل المتابعة لتطبيق التعديلات بشكل صحيح.\nهل تريد المتابعة؟",
        'err_empty': "يرجى كتابة اسم الموقع أولاً.",
        'err_exists': "هذا الموقع محظور بالفعل!",
        'success_block': "تم حظر الموقع وتطبيق سياسات DoH بنجاح.",
        'success_unblock': "تم فك الحظر عن الموقع."
    },
    'en': {
        'title': "Website Access Control Tool",
        'lbl_enter_site': "Enter the website to block:",
        'btn_block': "Enable Block",
        'lbl_blocked_list': "Currently Blocked Websites:",
        'btn_unblock': "Unblock",
        'btn_toggle_lang': "العربية",
        'warn_title': "Important Warning",
        'warn_msg': "Please ensure all browsers are closed before continuing to apply changes correctly.\nDo you want to continue?",
        'err_empty': "Please enter a website name first.",
        'err_exists': "This website is already blocked!",
        'success_block': "Website blocked and DoH policies applied successfully.",
        'success_unblock': "Website successfully unblocked."
    }
}

# --- Core system functions ---
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
    """Extract the base domain and www version from the input"""
    url = url.strip().lower()
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    netloc = urllib.parse.urlparse(url).netloc
    base = netloc[4:] if netloc.startswith('www.') else netloc
    return base, f"www.{base}"

def load_saved_sites():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_sites(sites):
    with open(SAVE_FILE, 'w') as f:
        json.dump(sites, f)

# --- GUI user interface ---
class BlockApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.lang = 'ar'
        self.blocked_sites = load_saved_sites()
        
        self.geometry("500x550")
        self.resizable(False, False)
        
        # Color styling
        self.configure(bg="#f0f0f0")
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.setup_ui()
        self.update_texts()
        self.refresh_list()

    def setup_ui(self):
        # Top language bar
        top_frame = tk.Frame(self, bg="#f0f0f0")
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        self.btn_lang = ttk.Button(top_frame, command=self.toggle_lang, cursor="hand2")
        self.btn_lang.pack(side=tk.RIGHT)

        # Input section
        input_frame = tk.Frame(self, bg="#ffffff", bd=1, relief=tk.SOLID)
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.lbl_enter = tk.Label(input_frame, bg="#ffffff", font=("Arial", 11, "bold"))
        self.lbl_enter.pack(pady=(10, 5))
        
        self.entry_site = ttk.Entry(input_frame, font=("Arial", 12), width=35)
        self.entry_site.pack(pady=5)
        
        self.btn_add = tk.Button(input_frame, bg="#d9534f", fg="white", font=("Arial", 11, "bold"), 
                                 relief=tk.FLAT, cursor="hand2", command=self.add_site)
        self.btn_add.pack(pady=(5, 15), ipadx=20, ipady=3)

        # List section
        self.lbl_list = tk.Label(self, bg="#f0f0f0", font=("Arial", 11, "bold"))
        self.lbl_list.pack(pady=(15, 5))
        
        # Scrollable list container
        list_container = tk.Frame(self)
        list_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        self.canvas = tk.Canvas(list_container, bg="#ffffff", bd=1, relief=tk.SOLID, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg="#ffffff")
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def update_texts(self):
        t = LANG_DATA[self.lang]
        self.title(t['title'])
        self.btn_lang.config(text=t['btn_toggle_lang'])
        self.lbl_enter.config(text=t['lbl_enter_site'])
        self.btn_add.config(text=t['btn_block'])
        self.lbl_list.config(text=t['lbl_blocked_list'])
        self.refresh_list()  # Redraw buttons with the new text

    def toggle_lang(self):
        self.lang = 'en' if self.lang == 'ar' else 'ar'
        self.update_texts()

    def add_site(self):
        t = LANG_DATA[self.lang]
        raw_url = self.entry_site.get()
        
        if not raw_url:
            messagebox.showwarning(t['warn_title'], t['err_empty'])
            return
            
        base, www_base = clean_domain(raw_url)
        
        if base in self.blocked_sites:
            messagebox.showinfo(t['warn_title'], t['err_exists'])
            return
            
        # Confirmation prompt to close browsers before continuing (Continue / Cancel)
        confirm = messagebox.askokcancel(t['warn_title'], t['warn_msg'])
        if not confirm:
            return

        try:
            # Add entries to the hosts file
            with open(HOSTS_PATH, 'r+') as file:
                content = file.read()
                if base not in content:
                    file.write(f"\n127.0.0.1 {base}")
                if www_base not in content:
                    file.write(f"\n127.0.0.1 {www_base}")
            
            # Apply DoH policies
            manage_doh(disable=True)
            
            # Update the saved list and UI
            self.blocked_sites.append(base)
            save_sites(self.blocked_sites)
            self.entry_site.delete(0, tk.END)
            self.refresh_list()
            messagebox.showinfo(t['title'], t['success_block'])
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def remove_site(self, site):
        t = LANG_DATA[self.lang]
        base, www_base = clean_domain(site)
        
        try:
            # Read hosts and filter out the site
            with open(HOSTS_PATH, 'r') as file:
                lines = file.readlines()
            
            with open(HOSTS_PATH, 'w') as file:
                for line in lines:
                    if base not in line and www_base not in line:
                        file.write(line)
            
            # Update the saved file
            self.blocked_sites.remove(base)
            save_sites(self.blocked_sites)
            
            # If the list is empty, remove DoH policies
            if not self.blocked_sites:
                manage_doh(disable=False)
                
            self.refresh_list()
            messagebox.showinfo(t['title'], t['success_unblock'])
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_list(self):
        # Clear the current list
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        t = LANG_DATA[self.lang]
        
        for site in self.blocked_sites:
            row = tk.Frame(self.scrollable_frame, bg="#ffffff")
            row.pack(fill=tk.X, padx=5, pady=5)
            
            lbl = tk.Label(row, text=site, bg="#ffffff", font=("Arial", 11))
            lbl.pack(side=tk.LEFT if self.lang == 'en' else tk.RIGHT, padx=10)
            
            btn = tk.Button(row, text=t['btn_unblock'], bg="#5cb85c", fg="white", 
                            relief=tk.FLAT, cursor="hand2", command=lambda s=site: self.remove_site(s))
            btn.pack(side=tk.RIGHT if self.lang == 'en' else tk.LEFT, padx=10, ipady=1)

if __name__ == "__main__":
    if is_admin():
        app = BlockApp()
        app.mainloop()
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)