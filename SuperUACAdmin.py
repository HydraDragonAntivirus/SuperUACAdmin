import sys
import ctypes
import os
import winsound
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import Slot
import winreg
import win32security
from win32security import *
from ntsecuritycon import *

class SuperUACAdmin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Super UAC Admin")
        self.setGeometry(300, 300, 400, 200)
        self.setWindowIcon(QIcon("assets/shield.png"))

        self.update_button = QPushButton("Enable SUPER UAC", self)
        self.update_button.setGeometry(100, 40, 200, 40)
        self.update_button.clicked.connect(self.update_registry_settings)

        # Add a button to disable Super UAC functionality (unlock registry key)
        self.disable_button = QPushButton("Disable SUPER UAC", self)
        self.disable_button.setGeometry(100, 100, 200, 40)
        self.disable_button.clicked.connect(self.disable_registry_lock)

    @Slot()
    def update_registry_settings(self):
        try:
            reg_key_path = r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System"
            
            # Open registry key and set EnableLUA
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(reg_key, "EnableLUA", 0, winreg.REG_DWORD, 1)
            
            # Lock the registry key (this happens only if "Enable SUPER UAC" is clicked)
            self.lock_registry_key(reg_key_path)

            QMessageBox.information(self, "Success", "UAC updated and registry key locked successfully!", QMessageBox.Ok)
        except Exception as ex:
            QMessageBox.critical(self, "Error", f"An error occurred: {ex}", QMessageBox.Ok)

    @Slot()
    def disable_registry_lock(self):
        try:
            reg_key_path = r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System"
            
            # Open registry key and set EnableLUA to 0 to disable Super UAC
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(reg_key, "EnableLUA", 0, winreg.REG_DWORD, 0)

            # Skip locking the registry key here to disable Super UAC
            QMessageBox.information(self, "Success", "UAC disabled successfully!", QMessageBox.Ok)
        except Exception as ex:
            QMessageBox.critical(self, "Error", f"An error occurred while disabling UAC: {ex}", QMessageBox.Ok)

    def lock_registry_key(self, key_path):
        try:
            # Open the registry key with permissions to change security
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ | winreg.KEY_WRITE)
            key_security = win32security.GetNamedSecurityInfo(
                key_path, SE_REGISTRY_KEY, DACL_SECURITY_INFORMATION
            )

            # Modify access control settings
            dacl = key_security.GetSecurityDescriptorDacl()
            dacl.RemoveAccessAllowedAceByIndex(0)  # Remove any existing ACE

            everyone_sid = win32security.SID(WELL_KNOWN_SID_TYPE.WORLD_SID_AUTHORITY)
            dacl.AddAccessDeniedAce(win32security.ACL_REVISION, GENERIC_ALL, everyone_sid)

            win32security.SetNamedSecurityInfo(
                key_path,
                SE_REGISTRY_KEY,
                DACL_SECURITY_INFORMATION,
                None,
                None,
                dacl,
                None,
            )
        except Exception as ex:
            QMessageBox.critical(self, "Error", f"Failed to lock registry key: {ex}", QMessageBox.Ok)


# Apply the custom style globally
style = """
QWidget {
    background-color: #2b2b2b;
    color: #e0e0e0;
    font-family: Arial, sans-serif;
    font-size: 14px;
}

QPushButton {
    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
                                stop:0.2 #007bff, stop:0.8 #0056b3);
    color: white;
    border: 2px solid #007bff;
    padding: 4px 10px;
    border-radius: 8px;
    min-width: 250px;
    font-weight: bold;
    text-align: center;
}

QPushButton:hover {
    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
                                stop:0.2 #0056b3, stop:0.8 #004380);
    border-color: #0056b3;
}

QPushButton:pressed {
    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
                                stop:0.2 #004380, stop:0.8 #003d75);
    border-color: #004380;
}

QFileDialog {
    background-color: #2b2b2b;
    color: #e0e0e0;
}

QMessageBox {
    background-color: #2b2b2b;
    color: #e0e0e0;
}
"""

# Create the QApplication instance first, before anything else
app = QApplication(sys.argv)
app.setStyleSheet(style)  # Apply the global style

# Create the window object before checking for admin privileges
window = SuperUACAdmin()

# Check for admin privileges
if not ctypes.windll.shell32.IsUserAnAdmin():
    icon_path = os.path.join(os.path.dirname(__file__), "assets", "shield.png")
    icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()  # Set the icon or fallback to empty
    msg_box = QMessageBox(window)  # Create the message box
    msg_box.setIcon(QMessageBox.Critical)  # Set the icon as Critical
    msg_box.setText("This application requires administrative privileges.")
    msg_box.setWindowTitle("Error")
    msg_box.setStandardButtons(QMessageBox.Ok)  # Set standard buttons
    msg_box.setIconPixmap(icon.pixmap(32, 32))  # Set the icon pixmap (resize if needed)
    
    # Apply the style to the message box itself
    msg_box.setStyleSheet(style)  # Apply the same style to the message box
    
    # Play the Windows error sound
    winsound.Beep(1000, 500)  # Frequency (1000 Hz) and duration (500 ms)
    
    msg_box.exec()  # Show the message box
    sys.exit(1)

# Start the application if admin privileges are granted
window.show()
sys.exit(app.exec())
