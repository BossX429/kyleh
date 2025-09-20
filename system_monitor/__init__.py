"""System monitoring package for security analysis."""

from typing import List

try:
    from importlib.metadata import version
    __version__ = version("system_monitor")
except ImportError:
    from system_monitor.version import read_version
    __version__ = read_version()

# Only expose what's necessary
from system_monitor.monitor import SecurityMonitor

__author__ = "Kyle H"
__all__: List[str] = ["SecurityMonitor", "__version__"]