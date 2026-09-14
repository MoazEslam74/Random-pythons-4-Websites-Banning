import sys
import ctypes
import winreg

def is_admin():
    """Check whether the script is running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def block_youtube():
    """Add YouTube domains to the hosts file"""
    hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    redirect_ip = "127.0.0.1"
    websites_to_block = ["youtube.com", "www.youtube.com"]

    try:
        with open(hosts_path, 'r+') as file:
            content = file.read()
            for site in websites_to_block:
                if site not in content:
                    file.write(f"\n{redirect_ip} {site}")
        print("YouTube was blocked successfully in the hosts file.")
    except Exception as e:
        print(f"An error occurred while modifying hosts: {e}")

def disable_browser_doh():
    """Disable encrypted DNS (DoH) in Chrome and Edge via the system registry"""
    # Browser registry paths and the required setting
    policies = {
        r"SOFTWARE\Policies\Google\Chrome": ("DnsOverHttpsMode", "off", winreg.REG_SZ),
        r"SOFTWARE\Policies\Microsoft\Edge": ("DnsOverHttpsMode", "off", winreg.REG_SZ)
    }
    
    for registry_path, (val_name, val_data, val_type) in policies.items():
        try:
            # Open or create the policy path in the local machine registry
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, registry_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, val_name, 0, val_type, val_data)
            winreg.CloseKey(key)
            print(f"DoH was disabled successfully at path: {registry_path}")
        except Exception as e:
            print(f"An error occurred while modifying the registry ({registry_path}): {e}")

if __name__ == "__main__":
    if is_admin():
        block_youtube()
        disable_browser_doh()
        print("\nNote: the browser may need to be restarted for the registry policy changes to take effect.")
        input("Press Enter to exit...")
    else:
        print("Requesting administrator privileges...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)