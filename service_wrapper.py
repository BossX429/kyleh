import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from monitor import SystemMonitor

class KyleHMonitorService(win32serviceutil.ServiceFramework):
    _svc_name_ = "KyleHMonitor"
    _svc_display_name_ = "KyleH System Monitor"
    _svc_description_ = "Real-time system monitoring with ML optimization and security scanning"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.monitor = None
        
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        
    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.main()
        
    def main(self):
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
            self.monitor = SystemMonitor(config_path)
            
            import threading
            monitor_thread = threading.Thread(target=self.monitor.monitor_loop)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
            
        except Exception as e:
            servicemanager.LogErrorMsg(f"Service error: {str(e)}")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(KyleHMonitorService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(KyleHMonitorService)
