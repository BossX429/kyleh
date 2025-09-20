"""Version information management for the system_monitor package."""

from __future__ import annotations

import importlib.metadata
import os
import re
import tomli
from pathlib import Path
from typing import Optional, Union

# Version format: major.minor.patch[-dev/alpha/beta.number]
VERSION_PATTERN = re.compile(
    r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"
    r"(?:-(?P<prerelease>dev|alpha|beta)\.(?P<prenumber>\d+))?$"
)

DEFAULT_VERSION = "0.1.0"

class Version:
    """Represents a semantic version with optional pre-release information."""
    
    def __init__(self, version_str: str) -> None:
        """Initialize version from string.
        
        Args:
            version_str: Version string in format major.minor.patch[-pre.number]
            
        Raises:
            ValueError: If version string is invalid
        """
        match = VERSION_PATTERN.match(version_str)
        if not match:
            raise ValueError(f"Invalid version format: {version_str}")
            
        self.major = int(match.group("major"))
        self.minor = int(match.group("minor"))
        self.patch = int(match.group("patch"))
        self.prerelease = match.group("prerelease")
        self.prenumber = int(match.group("prenumber")) if match.group("prenumber") else None
        
    def __str__(self) -> str:
        """Return string representation of version."""
        base = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease and self.prenumber is not None:
            return f"{base}-{self.prerelease}.{self.prenumber}"
        return base
        
    def __repr__(self) -> str:
        """Return detailed string representation of version."""
        return f"Version('{str(self)}')"

    def __lt__(self, other: Version) -> bool:
        """Compare if this version is less than another version."""
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        if self.patch != other.patch:
            return self.patch < other.patch
        if self.prerelease == other.prerelease:
            return False  # Same pre-release type, so they are equal
        if self.prerelease == "dev":
            return True  # dev is the lowest precedence
        if self.prerelease == "alpha":
            return other.prerelease != "dev"  # alpha is higher than dev
        if self.prerelease == "beta":
            return other.prerelease in ["dev", "alpha"]  # beta is higher than alpha and dev
        return False  # Fallback, should not reach here

def find_pyproject_toml() -> Optional[Path]:
    """Find pyproject.toml by searching parent directories.
    
    Returns:
        Optional[Path]: Path to pyproject.toml if found, None otherwise
    """
    current = Path(__file__).resolve().parent
    
    while current != current.parent:
        pyproject = current / "pyproject.toml"
        if pyproject.exists():
            return pyproject
        current = current.parent
    
    return None

def read_version_from_pyproject() -> Optional[str]:
    """Read version from pyproject.toml.
    
    Returns:
        Optional[str]: Version string if found, None otherwise
    """
    pyproject_path = find_pyproject_toml()
    if not pyproject_path:
        return None
        
    try:
        with open(pyproject_path, "rb") as f:
            data = tomli.load(f)
            return data.get("project", {}).get("version")
    except (IOError, tomli.TOMLDecodeError):
        return None

def get_version() -> Version:
    """Get package version from multiple sources.
    
    Tries sources in this order:
    1. importlib.metadata (for installed package)
    2. pyproject.toml
    3. Environment variable SYSTEM_MONITOR_VERSION
    4. Default version
    
    Returns:
        Version: Version object representing the package version
    """
    version_str = None
    
    # Try importlib.metadata first (most reliable when package is installed)
    try:
        version_str = importlib.metadata.version("system_monitor")
    except importlib.metadata.PackageNotFoundError:
        pass
    
    # Try pyproject.toml next (for development)
    if not version_str:
        version_str = read_version_from_pyproject()
    
    # Try environment variable (for testing/CI)
    if not version_str:
        version_str = os.environ.get("SYSTEM_MONITOR_VERSION")
    
    # Fall back to default version
    if not version_str:
        version_str = DEFAULT_VERSION
    
    try:
        return Version(version_str)
    except ValueError:
        # If we get an invalid version string, use default
        return Version(DEFAULT_VERSION)

def read_version() -> str:
    """Legacy function for backward compatibility.
    
    Returns:
        str: Version string
    """
    return str(get_version())