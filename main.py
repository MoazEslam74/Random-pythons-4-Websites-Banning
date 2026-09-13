import sys
import ctypes

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
        # Open the file with read/write permissions
        with open(hosts_path, 'r+') as file:
            content = file.read()
            for site in websites_to_block:
                # Check whether the site is already present to avoid duplication
                if site not in content:
                    file.write(f"\n{redirect_ip} {site}")
        print("YouTube has been blocked successfully.")
    except Exception as e:
        print(f"An error occurred while modifying the file: {e}")

if __name__ == "__main__":
    if is_admin():
        # If the required permissions are available, perform the block
        block_youtube()
        input("\nPress Enter to exit...")
    else:
        # If the required permissions are not available, relaunch the script as an administrator
        print("Requesting administrator privileges...")
        ctypes.windll.shell32.ShellExecuteW(
            None, 
            "runas", 
            sys.executable, 
            " ".join(sys.argv), 
            None, 
            1
        )