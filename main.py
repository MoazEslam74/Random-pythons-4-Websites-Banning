import sys
import ctypes
import winreg

# Interface messages for both languages
messages = {
    'ar': {
        'menu_title': "\n=== أداة التحكم في الوصول ليوتيوب ===",
        'opt_block': "[1] تفعيل الحظر (قفل يوتيوب)",
        'opt_unblock': "[2] إيقاف الحظر (فتح يوتيوب)",
        'opt_toggle': "[3] Switch to English (التبديل للإنجليزية)",
        'opt_exit': "[4] خروج",
        'prompt': "اختر الإجراء المطلوب: ",
        'hosts_blocked': "[+] تم حظر يوتيوب في ملف hosts بنجاح.",
        'doh_disabled': "[+] تم تعطيل DoH بنجاح في متصفح:",
        'hosts_unblocked': "[-] تم فك حظر يوتيوب من ملف hosts بنجاح.",
        'doh_enabled': "[-] تم إلغاء قيود DoH بنجاح من متصفح:",
        'error_hosts': "[!] حدث خطأ أثناء تعديل hosts",
        'error_registry': "[!] حدث خطأ أثناء تعديل السجل",
        'restart_note': "\n* ملاحظة: يرجى إعادة تشغيل المتصفحات لتطبيق التغييرات.",
        'exit_msg': "جاري إغلاق الأداة...",
        'invalid_choice': "خيار غير صحيح، الرجاء المحاولة مرة أخرى."
    },
    'en': {
        'menu_title': "\n=== YouTube Access Control Tool ===",
        'opt_block': "[1] Enable Block (Lock YouTube)",
        'opt_unblock': "[2] Disable Block (Unlock YouTube)",
        'opt_toggle': "[3] التبديل للعربية (Switch to Arabic)",
        'opt_exit': "[4] Exit",
        'prompt': "Select an action: ",
        'hosts_blocked': "[+] YouTube was successfully blocked in the hosts file.",
        'doh_disabled': "[+] DoH policy successfully disabled for:",
        'hosts_unblocked': "[-] YouTube was successfully unblocked in the hosts file.",
        'doh_enabled': "[-] DoH policy successfully removed for:",
        'error_hosts': "[!] Error modifying hosts",
        'error_registry': "[!] Error modifying registry",
        'restart_note': "\n* Note: Please restart your browsers to apply changes.",
        'exit_msg': "Closing tool...",
        'invalid_choice': "Invalid choice, please try again."
    }
}

# Browser template (you can easily add any new browser here)
BROWSER_POLICIES = {
    "Google Chrome": {
        "path": r"SOFTWARE\Policies\Google\Chrome",
        "key": "DnsOverHttpsMode",
        "value": "off",
        "type": winreg.REG_SZ
    },
    "Microsoft Edge": {
        "path": r"SOFTWARE\Policies\Microsoft\Edge",
        "key": "DnsOverHttpsMode",
        "value": "off",
        "type": winreg.REG_SZ
    },
    "Brave Browser": {
        "path": r"SOFTWARE\Policies\BraveSoftware\Brave",
        "key": "DnsOverHttpsMode",
        "value": "off",
        "type": winreg.REG_SZ
    },
    "Vivaldi": {
        "path": r"SOFTWARE\Policies\Vivaldi",
        "key": "DnsOverHttpsMode",
        "value": "off",
        "type": winreg.REG_SZ
    },
    "Mozilla Firefox": {
        # Firefox uses different data types and values (DWORD instead of String)
        "path": r"SOFTWARE\Policies\Mozilla\Firefox\DNSOverHTTPS",
        "key": "Enabled",
        "value": 0, 
        "type": winreg.REG_DWORD
    }
}

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def block_youtube(lang):
    hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    websites_to_block = ["youtube.com", "www.youtube.com"]
    try:
        with open(hosts_path, 'r+') as file:
            content = file.read()
            for site in websites_to_block:
                if site not in content:
                    file.write(f"\n127.0.0.1 {site}")
        print(messages[lang]['hosts_blocked'])
    except Exception as e:
        print(f"{messages[lang]['error_hosts']}: {e}")

def unblock_youtube(lang):
    hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    websites_to_block = ["youtube.com", "www.youtube.com"]
    try:
        with open(hosts_path, 'r') as file:
            lines = file.readlines()
        with open(hosts_path, 'w') as file:
            for line in lines:
                if not any(site in line for site in websites_to_block):
                    file.write(line)
        print(messages[lang]['hosts_unblocked'])
    except Exception as e:
        print(f"{messages[lang]['error_hosts']}: {e}")

def disable_browser_doh(lang):
    for browser_name, config in BROWSER_POLICIES.items():
        try:
            # CreateKeyEx creates the path automatically if it does not already exist
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, config['path'], 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, config['key'], 0, config['type'], config['value'])
            winreg.CloseKey(key)
            print(f"{messages[lang]['doh_disabled']} {browser_name}")
        except Exception as e:
            print(f"{messages[lang]['error_registry']} ({browser_name}): {e}")

def enable_browser_doh(lang):
    for browser_name, config in BROWSER_POLICIES.items():
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, config['path'], 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, config['key'])
            winreg.CloseKey(key)
            print(f"{messages[lang]['doh_enabled']} {browser_name}")
        except FileNotFoundError:
            # If the policy does not exist, ignore it quietly
            pass
        except Exception as e:
            print(f"{messages[lang]['error_registry']} ({browser_name}): {e}")

def main_menu():
    lang = 'ar' 
    while True:
        print(messages[lang]['menu_title'])
        print(messages[lang]['opt_block'])
        print(messages[lang]['opt_unblock'])
        print(messages[lang]['opt_toggle'])
        print(messages[lang]['opt_exit'])
        
        choice = input(messages[lang]['prompt']).strip()

        if choice == '1':
            block_youtube(lang)
            disable_browser_doh(lang)
            print(messages[lang]['restart_note'])
        elif choice == '2':
            unblock_youtube(lang)
            enable_browser_doh(lang)
            print(messages[lang]['restart_note'])
        elif choice == '3':
            lang = 'en' if lang == 'ar' else 'ar'
        elif choice == '4':
            print(messages[lang]['exit_msg'])
            break
        else:
            print(messages[lang]['invalid_choice'])

if __name__ == "__main__":
    if is_admin():
        main_menu()
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)