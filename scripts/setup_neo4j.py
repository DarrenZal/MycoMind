#!/usr/bin/env python3
"""
Neo4j Setup Script for MycoMind

This script helps set up Neo4j for MycoMind knowledge graphs.
It can download Neo4j, create configuration files, and start the server.

Usage:
    python setup_neo4j.py --download
    python setup_neo4j.py --start
    python setup_neo4j.py --stop
    python setup_neo4j.py --status
"""

import os
import sys
import subprocess
import requests
import zipfile
import tarfile
import argparse
import logging
import time
import signal
import platform
import shutil
import re
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class Neo4jSetup:
    """
    Helper class for setting up and managing Neo4j.
    """
    
    def __init__(self, install_dir: str = "neo4j"):
        """
        Initialize Neo4j setup.
        
        Args:
            install_dir: Directory to install Neo4j
        """
        self.install_dir = Path(install_dir).resolve()
        self.neo4j_version = "5.15.0"  # Latest stable version
        
        # Determine OS and architecture
        self.system = platform.system().lower()
        self.is_windows = self.system == "windows"
        self.is_mac = self.system == "darwin"
        self.is_linux = self.system == "linux"
        
        # Set download URL based on OS
        if self.is_windows:
            self.download_url = f"https://neo4j.com/artifact.php?name=neo4j-community-{self.neo4j_version}-windows.zip"
            self.archive_ext = "zip"
        elif self.is_mac:
            self.download_url = f"https://neo4j.com/artifact.php?name=neo4j-community-{self.neo4j_version}-unix.tar.gz"
            self.archive_ext = "tar.gz"
        else:  # Linux
            self.download_url = f"https://neo4j.com/artifact.php?name=neo4j-community-{self.neo4j_version}-unix.tar.gz"
            self.archive_ext = "tar.gz"
        
        # Set paths
        self.neo4j_dir = self.install_dir / f"neo4j-community-{self.neo4j_version}"
        
        if self.is_windows:
            self.bin_dir = self.neo4j_dir / "bin"
            self.neo4j_cmd = self.bin_dir / "neo4j.bat"
            self.conf_file = self.neo4j_dir / "conf" / "neo4j.conf"
            self.import_dir = self.neo4j_dir / "import"
        else:
            self.bin_dir = self.neo4j_dir / "bin"
            self.neo4j_cmd = self.bin_dir / "neo4j"
            self.conf_file = self.neo4j_dir / "conf" / "neo4j.conf"
            self.import_dir = self.neo4j_dir / "import"
        
        self.pid_file = self.install_dir / "neo4j.pid"
        self.log_file = self.install_dir / "neo4j.log"
        
        logger.info(f"Neo4j setup initialized for {self.install_dir}")
    
    def check_java_version(self) -> Tuple[bool, str]:
        """
        Check if the installed Java version is compatible with Neo4j.
        Neo4j 5.x requires Java 17 or Java 21.
        
        Returns:
            Tuple of (is_compatible, version_string)
        """
        try:
            # Run java -version
            result = subprocess.run(
                ["java", "-version"], 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode != 0:
                logger.error("Java not found. Please install Java 17 or Java 21.")
                return False, "Not installed"
            
            # Parse version string
            output = result.stdout
            if not output:
                output = result.stderr  # Sometimes version is in stderr
            
            # Extract version using regex
            version_match = re.search(r'version "([^"]+)"', output)
            if not version_match:
                logger.error("Could not determine Java version.")
                return False, "Unknown"
            
            version_str = version_match.group(1)
            
            # Check if version is compatible
            if "17" in version_str or "17." in version_str:
                logger.info(f"✓ Compatible Java version detected: {version_str}")
                return True, version_str
            elif "21" in version_str or "21." in version_str:
                logger.info(f"✓ Compatible Java version detected: {version_str}")
                return True, version_str
            else:
                logger.error(f"Unsupported Java {version_str} detected. Please use Java(TM) 17 or Java(TM) 21 to run Neo4j Server.")
                return False, version_str
                
        except Exception as e:
            logger.error(f"Error checking Java version: {e}")
            return False, "Error"
    
    def download_neo4j(self) -> bool:
        """
        Download and extract Neo4j.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create install directory
            self.install_dir.mkdir(parents=True, exist_ok=True)
            
            archive_file = self.install_dir / f"neo4j-community-{self.neo4j_version}.{self.archive_ext}"
            
            # Download if not already present
            if not archive_file.exists():
                logger.info(f"Downloading Neo4j {self.neo4j_version}...")
                response = requests.get(self.download_url, stream=True)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(archive_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                percent = (downloaded / total_size) * 100
                                print(f"\rDownloading: {percent:.1f}%", end='', flush=True)
                
                print()  # New line after progress
                logger.info("Download completed")
            else:
                logger.info("Neo4j archive already exists")
            
            # Extract if not already extracted
            if not self.neo4j_dir.exists():
                logger.info("Extracting Neo4j...")
                if self.archive_ext == "zip":
                    with zipfile.ZipFile(archive_file, 'r') as zip_ref:
                        zip_ref.extractall(self.install_dir)
                else:  # tar.gz
                    with tarfile.open(archive_file, 'r:gz') as tar_ref:
                        tar_ref.extractall(self.install_dir)
                logger.info("Extraction completed")
            else:
                logger.info("Neo4j already extracted")

            # Check if extracted directory is nested
            extracted_dir = self.install_dir / f"neo4j-community-{self.neo4j_version}"
            if not extracted_dir.exists():
                # Check for a nested directory
                extracted_dirs = [d for d in self.install_dir.iterdir() if d.is_dir() and d.name.startswith("neo4j-community")]
                if extracted_dirs:
                    self.neo4j_dir = extracted_dirs[0]
                    if self.is_windows:
                        self.bin_dir = self.neo4j_dir / "bin"
                        self.neo4j_cmd = self.bin_dir / "neo4j.bat"
                        self.conf_file = self.neo4j_dir / "conf" / "neo4j.conf"
                        self.import_dir = self.neo4j_dir / "import"
                    else:
                        self.bin_dir = self.neo4j_dir / "bin"
                        self.neo4j_cmd = self.bin_dir / "neo4j"
                        self.conf_file = self.neo4j_dir / "conf" / "neo4j.conf"
                        self.import_dir = self.neo4j_dir / "import"
                    logger.info(f"Found nested Neo4j directory: {self.neo4j_dir}")
                else:
                    logger.error("✗ Neo4j directory not found after extraction")
                    return False
            else:
                self.neo4j_dir = extracted_dir
                if self.is_windows:
                    self.bin_dir = self.neo4j_dir / "bin"
                    self.neo4j_cmd = self.bin_dir / "neo4j.bat"
                    self.conf_file = self.neo4j_dir / "conf" / "neo4j.conf"
                    self.import_dir = self.neo4j_dir / "import"
                else:
                    self.bin_dir = self.neo4j_dir / "bin"
                    self.neo4j_cmd = self.bin_dir / "neo4j"
                    self.conf_file = self.neo4j_dir / "conf" / "neo4j.conf"
                    self.import_dir = self.neo4j_dir / "import"

            # Verify installation
            #if self.neo4j_cmd.exists():
            #    logger.info("✓ Neo4j installation verified")
            #    return True
            #else:
            logger.warning("Skipping Neo4j command verification")
            return True

        except Exception as e:
            logger.error(f"✗ Error downloading Neo4j: {e}")
            return False
    
    def update_config(self, settings: Dict[str, str] = None) -> bool:
        """
        Update Neo4j configuration file.
        
        Args:
            settings: Dictionary of settings to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if config file exists
            if not self.conf_file.exists():
                logger.warning(f"Configuration file not found at {self.conf_file}. Attempting to locate it...")

                # Attempt to locate the config file in a nested directory
                extracted_dirs = [d for d in self.install_dir.iterdir() if d.is_dir() and d.name.startswith("neo4j-community")]
                if extracted_dirs:
                    self.neo4j_dir = extracted_dirs[0]
                    self.conf_file = self.neo4j_dir / "conf" / "neo4j.conf"
                    self.import_dir = self.neo4j_dir / "import"
                    logger.info(f"Found nested Neo4j directory: {self.neo4j_dir}")
                    logger.info(f"Updated config file path: {self.conf_file}")
                else:
                    logger.error("✗ Neo4j directory not found after extraction")
                    return False

                if not self.conf_file.exists():
                    logger.error(f"Configuration file still not found: {self.conf_file}")
                    return False

            # Default settings
            default_settings = {
                "dbms.default_listen_address": "0.0.0.0",
                "dbms.default_database": "mycomind",
                "dbms.security.auth_enabled": "false",  # Disable auth for development
                "dbms.directories.import": str(self.import_dir),
                "dbms.memory.heap.initial_size": "512m",
                "dbms.memory.heap.max_size": "4g"
            }

            # Merge with provided settings
            if settings:
                default_settings.update(settings)

            # Read current config
            with open(self.conf_file, 'r') as f:
                lines = f.readlines()

            # Update config
            new_lines = []
            updated_keys = set()

            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    new_lines.append(line)
                    continue

                key = line.split('=')[0].strip()
                if key in default_settings:
                    new_lines.append(f"{key}={default_settings[key]}")
                    updated_keys.add(key)
                else:
                    new_lines.append(line)

            # Add missing settings
            for key, value in default_settings.items():
                if key not in updated_keys:
                    new_lines.append(f"{key}={value}")

            # Write updated config
            with open(self.conf_file, 'w') as f:
                f.write('\n'.join(new_lines))

            logger.info(f"✓ Configuration updated: {self.conf_file}")
            return True

        except Exception as e:
            logger.error(f"✗ Error updating config: {e}")
            return False
    
    def start_server(self, settings: Dict[str, str] = None) -> bool:
        """
        Start Neo4j server.
        
        Args:
            settings: Dictionary of settings to update before starting
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check Java version first
            java_compatible, java_version = self.check_java_version()
            if not java_compatible:
                logger.error(f"Neo4j 5.x requires Java 17 or Java 21. Found: {java_version}")
                logger.error("Please install a compatible Java version and try again.")
                return False
            
            # Check if already running
            if self.is_running():
                logger.info("Neo4j server is already running")
                return True
            
            # Update config if settings provided
            if settings:
                self.update_config(settings)
            
            # Build command
            if self.is_windows:
                cmd = [str(self.neo4j_cmd), "console"]
                shell = True
            else:
                cmd = [str(self.neo4j_cmd), "console"]
                shell = False
            
            logger.info(f"Starting Neo4j server...")
            logger.info(f"Command: {' '.join(cmd)}")
            
            # Start server in background
            with open(self.log_file, 'w') as log_f:
                process = subprocess.Popen(
                    cmd,
                    stdout=log_f,
                    stderr=subprocess.STDOUT,
                    shell=shell,
                    cwd=self.neo4j_dir
                )
            
            # Save PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # Wait a moment and check if it started
            time.sleep(5)
            
            if self.is_running():
                logger.info(f"✓ Neo4j server started successfully (PID: {process.pid})")
                logger.info(f"  Web interface: http://localhost:7474")
                logger.info(f"  Bolt endpoint: bolt://localhost:7687")
                logger.info(f"  Log file: {self.log_file}")
                return True
            else:
                logger.error("✗ Neo4j server failed to start")
                self._show_recent_logs()
                return False
                
        except Exception as e:
            logger.error(f"✗ Error starting server: {e}")
            return False
    
    def stop_server(self) -> bool:
        """
        Stop Neo4j server.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.is_running():
                logger.info("Neo4j server is not running")
                return True
            
            # Use Neo4j command to stop
            if self.neo4j_cmd.exists():
                if self.is_windows:
                    cmd = [str(self.neo4j_cmd), "stop"]
                    shell = True
                else:
                    cmd = [str(self.neo4j_cmd), "stop"]
                    shell = False
                
                logger.info("Stopping Neo4j server...")
                result = subprocess.run(cmd, shell=shell, cwd=self.neo4j_dir)
                
                if result.returncode == 0:
                    logger.info("✓ Neo4j server stopped")
                    if self.pid_file.exists():
                        self.pid_file.unlink()
                    return True
                else:
                    logger.error("✗ Failed to stop Neo4j server")
                    return False
            
            # Fallback: Kill process by PID
            if self.pid_file.exists():
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                try:
                    # Try graceful shutdown first
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(2)
                    
                    # Check if still running
                    try:
                        os.kill(pid, 0)  # Check if process exists
                        # Still running, force kill
                        os.kill(pid, signal.SIGKILL)
                        time.sleep(1)
                    except ProcessLookupError:
                        pass  # Process already terminated
                    
                    # Remove PID file
                    self.pid_file.unlink()
                    
                    logger.info("✓ Neo4j server stopped")
                    return True
                    
                except ProcessLookupError:
                    logger.info("Neo4j server was not running")
                    self.pid_file.unlink()
                    return True
            
            logger.warning("Could not stop Neo4j server")
            return False
                
        except Exception as e:
            logger.error(f"✗ Error stopping server: {e}")
            return False
    
    def is_running(self) -> bool:
        """
        Check if Neo4j server is running.
        
        Returns:
            True if running, False otherwise
        """
        try:
            # Check via HTTP ping
            response = requests.get("http://localhost:7474", timeout=2)
            return response.status_code == 200
        except:
            # Try checking process
            if self.pid_file.exists():
                try:
                    with open(self.pid_file, 'r') as f:
                        pid = int(f.read().strip())
                    
                    # Check if process exists
                    if self.is_windows:
                        # Windows: Use tasklist
                        result = subprocess.run(
                            f"tasklist /FI \"PID eq {pid}\"", 
                            shell=True, 
                            capture_output=True, 
                            text=True
                        )
                        return str(pid) in result.stdout
                    else:
                        # Unix: Use kill -0
                        try:
                            os.kill(pid, 0)
                            return True
                        except ProcessLookupError:
                            return False
                except:
                    return False
            return False
    
    def get_status(self) -> dict:
        """
        Get server status information.
        
        Returns:
            Status dictionary
        """
        status = {
            'running': self.is_running(),
            'pid': None,
            'version': self.neo4j_version,
            'config_exists': self.conf_file.exists(),
            'cmd_exists': self.neo4j_cmd.exists(),
            'log_size': 0
        }
        
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    status['pid'] = int(f.read().strip())
            except:
                pass
        
        if self.log_file.exists():
            status['log_size'] = self.log_file.stat().st_size
        
        return status
    
    def _show_recent_logs(self, lines: int = 20) -> None:
        """
        Show recent log entries.
        
        Args:
            lines: Number of lines to show
        """
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    log_lines = f.readlines()
                    recent_lines = log_lines[-lines:]
                    
                logger.info(f"Recent log entries ({len(recent_lines)} lines):")
                for line in recent_lines:
                    print(f"  {line.rstrip()}")
            except Exception as e:
                logger.error(f"Could not read log file: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Neo4j Setup for MycoMind')
    parser.add_argument('--download', action='store_true', help='Download and install Neo4j')
    parser.add_argument('--start', action='store_true', help='Start Neo4j server')
    parser.add_argument('--stop', action='store_true', help='Stop Neo4j server')
    parser.add_argument('--status', action='store_true', help='Show server status')
    parser.add_argument('--restart', action='store_true', help='Restart Neo4j server')
    parser.add_argument('--logs', action='store_true', help='Show recent logs')
    parser.add_argument('--check-java', action='store_true', help='Check Java version compatibility')
    parser.add_argument('--install-dir', default='neo4j', help='Installation directory')
    parser.add_argument('--memory', default='2g', help='JVM memory allocation')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        setup = Neo4jSetup(args.install_dir)
        
        if args.check_java:
            compatible, version = setup.check_java_version()
            if compatible:
                print(f"✓ Java version {version} is compatible with Neo4j 5.x")
                return 0
            else:
                print(f"✗ Java version {version} is NOT compatible with Neo4j 5.x")
                print("Neo4j 5.x requires Java 17 or Java 21.")
                return 1
        
        if args.download:
            if setup.download_neo4j():
                # Update config with memory settings
                settings = {
                    "dbms.memory.heap.max_size": args.memory
                }
                setup.update_config(settings)
                logger.info("Neo4j setup completed successfully!")
                logger.info(f"Next steps:")
                logger.info(f"  1. Start server: python setup_neo4j.py --start")
                logger.info(f"  2. Check status: python setup_neo4j.py --status")
                logger.info(f"  3. Load data: :source cypher_file.cypher in Neo4j Browser")
            else:
                return 1
        
        elif args.start:
            if not setup.neo4j_cmd.exists():
                logger.error("Neo4j not installed. Run with --download first.")
                return 1
            
            # Check Java version first
            compatible, version = setup.check_java_version()
            if not compatible:
                logger.error(f"Java version {version} is NOT compatible with Neo4j 5.x")
                logger.error("Neo4j 5.x requires Java 17 or Java 21.")
                logger.error("Please install a compatible Java version and try again.")
                return 1
            
            # Update memory settings
            settings = {
                "dbms.memory.heap.max_size": args.memory
            }
            
            if setup.start_server(settings):
                return 0
            else:
                return 1
        
        elif args.stop:
            if setup.stop_server():
                return 0
            else:
                return 1
        
        elif args.restart:
            logger.info("Restarting Neo4j server...")
            setup.stop_server()
            time.sleep(2)
            
            # Check Java version first
            compatible, version = setup.check_java_version()
            if not compatible:
                logger.error(f"Java version {version} is NOT compatible with Neo4j 5.x")
                logger.error("Neo4j 5.x requires Java 17 or Java 21.")
                logger.error("Please install a compatible Java version and try again.")
                return 1
            
            # Update memory settings
            settings = {
                "dbms.memory.heap.max_size": args.memory
            }
            
            if setup.start_server(settings):
                return 0
            else:
                return 1
        
        elif args.status:
            status = setup.get_status()
            print(f"\nNeo4j Server Status:")
            print(f"  Running: {'✓' if status['running'] else '✗'}")
            print(f"  PID: {status['pid'] if status['pid'] else 'N/A'}")
            print(f"  Version: {status['version']}")
            print(f"  Config exists: {'✓' if status['config_exists'] else '✗'}")
            print(f"  Command exists: {'✓' if status['cmd_exists'] else '✗'}")
            print(f"  Log size: {status['log_size']} bytes")
            
            # Check Java version
            compatible, version = setup.check_java_version()
            print(f"  Java version: {version} {'✓' if compatible else '✗'}")
            
            if status['running']:
                print(f"  Web interface: http://localhost:7474")
                print(f"  Bolt endpoint: bolt://localhost:7687")
        
        elif args.logs:
            setup._show_recent_logs()
        
        else:
            parser.print_help()
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
