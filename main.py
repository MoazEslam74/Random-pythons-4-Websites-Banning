import sys
import ctypes
import winreg

# Dictionary of texts to support both Arabic and English
messages = {
    'ar': {
        'menu_title': "\n=== أداة التحكم في الوصول ليوتيوب ===",
        'opt_block': "[1] تفعيل الحظر (قفل يوتيوب)",
        'opt_unblock': "[2] إيقاف الحظر (فتح يوتيوب)",
        'opt_toggle': "[3] Switch to English (التبديل للإنجليزية)",
        'opt_exit': "[4] خروج",
        'prompt': "اختر الإجراء المطلوب: ",
        'hosts_blocked': "[+] تم حظر يوتيوب في ملف hosts بنجاح.",
        'doh_disabled': "[+] تم تعطيل DoH بنجاح في متصفح",
        'hosts_unblocked': "[-] تم فك حظر يوتيوب من ملف hosts بنجاح.",
        'doh_enabled': "[-] تم إلغاء قيود DoH بنجاح من متصفح",
        'error_hosts': "[!] حدث خطأ أثناء تعديل hosts",
        'error_registry': "[!] حدث خطأ أثناء تعديل السجل",
        'restart_note': "\n* ملاحظة: يرجى إعادة تشغيل المتصفح لتطبيق التغييرات.",
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
        'doh_disabled': "[+] DoH policy successfully disabled for",
        'hosts_unblocked': "[-] YouTube was successfully unblocked in the hosts file.",
        'doh_enabled': "[-] DoH policy successfully removed for",
        'error_hosts': "[!] Error modifying hosts",
        'error_registry': "[!] Error modifying registry",
        'restart_note': "\n* Note: Please restart your browser to apply changes.",
        'exit_msg': "Closing tool...",
        'invalid_choice': "Invalid choice, please try again."
    }
}

def is_admin():
    """Check whether the script is running with administrator privileges"""
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
    """Remove YouTube domains from the hosts file"""
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
    policies = {
        r"SOFTWARE\Policies\Google\Chrome": ("DnsOverHttpsMode", "off", winreg.REG_SZ),
        r"SOFTWARE\Policies\Microsoft\Edge": ("DnsOverHttpsMode", "off", winreg.REG_SZ)
    }
    for registry_path, (val_name, val_data, val_type) in policies.items():
        try:
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, registry_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, val_name, 0, val_type, val_data)
            winreg.CloseKey(key)
            browser_name = registry_path.split("\\")[-1]
            print(f"{messages[lang]['doh_disabled']} {browser_name}")
        except Exception as e:
            print(f"{messages[lang]['error_registry']} ({registry_path}): {e}")

def enable_browser_doh(lang):
    """Remove the policy from the registry so the browser can return to its default state"""
    policies = [
        r"SOFTWARE\Policies\Google\Chrome",
        r"SOFTWARE\Policies\Microsoft\Edge"
    ]
    for registry_path in policies:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path, 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, "DnsOverHttpsMode")
            winreg.CloseKey(key)
            browser_name = registry_path.split("\\")[-1]
            print(f"{messages[lang]['doh_enabled']} {browser_name}")
        except FileNotFoundError:
            # If the policy does not exist in the first place (which is the desired state), skip it quietly
            pass
        except Exception as e:
            print(f"{messages[lang]['error_registry']} ({registry_path}): {e}")

def main_menu():
    lang = 'ar'  # Default language
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
        # Re-request administrator execution if privileges are not available
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)