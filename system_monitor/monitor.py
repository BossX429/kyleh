"""System monitoring functionality for security analysis."""

from __future__ import annotations

import logging
import signal
import sys
import time
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Set, Union

try:
    import psutil  # type: ignore
except ImportError:
    print("Error: The 'psutil' module is not installed. Please install it using 'pip install psutil'.")
    sys.exit(1)

# Configure logging
DEFAULT_LOG_PATH = Path("security_monitor.log").absolute()

class SecurityMonitor:
    """Monitor system resources and activities for security analysis."""

    def __init__(self, log_path: Optional[Union[str, Path]] = None, 
                 monitor_interval: float = 5.0, cpu_threshold: float = 90.0):
        """Initialize the security monitor.

        Args:
            log_path: Optional path to the log file. Defaults to security_monitor.log
                     in the current directory.
            monitor_interval: Time between monitoring checks in seconds
            cpu_threshold: CPU usage percentage threshold for warnings
        """
        self.previous_processes: Set[int] = set()
        self.running: bool = True
        self.monitor_interval = monitor_interval
        self.cpu_threshold = cpu_threshold
        self._setup_logging(log_path if log_path else DEFAULT_LOG_PATH)
        self._setup_signal_handlers()
        self._initialize_process_list()

        # Initialize WMI only on Windows
        self.wmi = None
        if sys.platform.startswith('win'):
            try:
                import wmi  # type: ignore[import]
                self.wmi = wmi.WMI()
            except ImportError:
                logging.warning("WMI features will be disabled - wmi package not available")
            except Exception as e:
                logging.warning(f"Failed to initialize WMI: {e}")

    def _setup_logging(self, log_path: Union[str, Path]) -> None:
        """Configure logging for the monitor.

        Args:
            log_path: Path to the log file
        """
        if isinstance(log_path, str):
            log_path = Path(log_path)

        log_path.parent.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        self.log_path = log_path
        logging.info(f"Logging to: {self.log_path}")

    def _setup_signal_handlers(self) -> None:
        """Set up handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum: int, frame: Optional[object]) -> None:
        """Handle shutdown signals.

        Args:
            signum: Signal number
            frame: Current stack frame (unused)
        """
        logging.info(f"Received signal {signum}, shutting down...")
        self.running = False

    def _initialize_process_list(self) -> None:
        """Initialize the list of running processes."""
        try:
            self.previous_processes = set(p.pid for p in psutil.process_iter(['pid']))
        except psutil.Error as e:
            logging.error(f"Failed to initialize process list: {e}")
            self.previous_processes = set()

    def monitor_system(self) -> None:
        """Main monitoring loop with proper error handling."""
        logging.info("Starting system monitoring")

        try:
            while self.running:
                self._monitor_iteration()
                time.sleep(self.monitor_interval)
        except KeyboardInterrupt:
            logging.info("Monitoring stopped by user")
            self.running = False
        except Exception as e:
            logging.error(f"Fatal error in monitoring: {e}")
            raise
        finally:
            logging.info("Monitoring stopped")

    def _monitor_iteration(self) -> None:
        """Run one iteration of system monitoring."""
        try:
            self._check_cpu_usage()
            self._check_new_processes()
            self._check_network_connections()
        except Exception as e:
            logging.error(f"Error in monitoring iteration: {e}")

    def _check_cpu_usage(self) -> None:
        """Monitor CPU usage."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > self.cpu_threshold:
                logging.warning(f"High CPU usage detected: {cpu_percent:.1f}% (threshold: {self.cpu_threshold:.1f}%)")
        except Exception as e:
            logging.error(f"Error monitoring CPU: {e}")

    def _check_new_processes(self) -> None:
        """Monitor for new processes with improved logging."""
        try:
            current_processes = set(p.pid for p in psutil.process_iter(['pid']))
            new_processes = current_processes - self.previous_processes

            for pid in new_processes:
                try:
                    process = psutil.Process(pid)
                    with process.oneshot():  # More efficient process info gathering
                        # Safely get process information with fallbacks
                        try:
                            name = process.name() or "unknown"
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            name = "unknown"
                        
                        try:
                            exe = process.exe() or "N/A"
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            exe = "N/A"
                        
                        try:
                            username = process.username() or "N/A"
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            username = "N/A"
                        
                        try:
                            cmdline = ' '.join(process.cmdline()) if process.cmdline() else "N/A"
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            cmdline = "N/A"
                        
                        # Log concise process information
                        logging.info(
                            f"New process: PID={pid}, Name='{name}', User='{username}'"
                        )
                        
                        # Log detailed info at debug level
                        if exe != "N/A" or cmdline != "N/A":
                            logging.debug(f"Process details: PID={pid}, Exe='{exe}', Cmd='{cmdline}'")
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    logging.debug(f"Could not access process {pid}: {e}")
                except Exception as e:
                    logging.error(f"Error checking process {pid}: {e}")

            self.previous_processes = current_processes
        except Exception as e:
            logging.error(f"Error monitoring processes: {e}")

    def _check_network_connections(self) -> None:
        """Monitor network connections with intelligent filtering."""
        try:
            connections = psutil.net_connections(kind='inet')
            suspicious_ports = {22, 23, 135, 139, 445, 1433, 3389, 5432, 5900}  # Common attack targets
            external_connections = []
            suspicious_activity = []
            
            for conn in connections:
                if conn.status == 'ESTABLISHED' and conn.raddr:
                    # Check for external connections (not localhost/private networks)
                    is_external = not (
                        conn.raddr.ip.startswith('127.') or
                        conn.raddr.ip.startswith('::1') or
                        conn.raddr.ip.startswith('192.168.') or
                        conn.raddr.ip.startswith('10.') or
                        conn.raddr.ip.startswith('172.')
                    )
                    
                    if is_external:
                        external_connections.append(conn)
                    
                    # Check for suspicious port activity
                    if (conn.laddr.port in suspicious_ports or 
                        conn.raddr.port in suspicious_ports):
                        suspicious_activity.append(conn)
            
            # Log summary of external connections
            if external_connections:
                logging.info(f"Active external connections: {len(external_connections)}")
                # Log details for first few connections
                for conn in external_connections[:3]:
                    logging.debug(
                        f"External: {conn.laddr.ip}:{conn.laddr.port} -> "
                        f"{conn.raddr.ip}:{conn.raddr.port} (PID: {conn.pid})"
                    )
                if len(external_connections) > 3:
                    logging.debug(f"... and {len(external_connections) - 3} more external connections")
            
            # Log suspicious activity
            for conn in suspicious_activity:
                logging.warning(
                    f"Suspicious port activity: {conn.laddr.ip}:{conn.laddr.port} -> "
                    f"{conn.raddr.ip}:{conn.raddr.port} (PID: {conn.pid})"
                )
                    
        except psutil.AccessDenied:
            logging.warning("Access denied when checking network connections")
        except Exception as e:
            logging.error(f"Error monitoring network: {e}")

def main() -> None:
    """Entry point for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="System security monitoring tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Run with default settings
  %(prog)s --log-file /var/log/security.log   # Custom log file
  %(prog)s --interval 10 --verbose           # 10s interval, verbose logging
  %(prog)s --cpu-threshold 80                # Custom CPU threshold
        """
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        help="Path to log file (default: security_monitor.log)",
        default=str(DEFAULT_LOG_PATH)
    )
    
    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="Monitoring interval in seconds (default: 5.0)"
    )
    
    parser.add_argument(
        "--cpu-threshold",
        type=float,
        default=90.0,
        help="CPU usage threshold for warnings (default: 90.0%%)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging (INFO level)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging (DEBUG level)"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress console output (only log to file)"
    )

    args = parser.parse_args()
    
    # Configure logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.verbose:
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(logging.WARNING)
    
    if not args.quiet:
        print(f"Security monitoring started. Check {args.log_file} for details.")
        print("Press Ctrl+C to stop monitoring.")
    
    # Create monitor with custom settings
    monitor = SecurityMonitor(
        log_path=args.log_file,
        monitor_interval=args.interval,
        cpu_threshold=args.cpu_threshold
    )
    
    monitor.monitor_system()

if __name__ == "__main__":
    main()