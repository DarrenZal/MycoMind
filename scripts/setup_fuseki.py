#!/usr/bin/env python3
"""
Fuseki Setup Script for MycoMind

This script helps set up Apache Jena Fuseki for MycoMind knowledge graphs.
It can download Fuseki, create configuration files, and start the server.

Usage:
    python setup_fuseki.py --download
    python setup_fuseki.py --start
    python setup_fuseki.py --stop
    python setup_fuseki.py --status
"""

import os
import sys
import subprocess
import requests
import zipfile
import argparse
import logging
import time
import signal
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class FusekiSetup:
    """
    Helper class for setting up and managing Apache Jena Fuseki.
    """
    
    def __init__(self, install_dir: str = "fuseki"):
        """
        Initialize Fuseki setup.
        
        Args:
            install_dir: Directory to install Fuseki
        """
        self.install_dir = Path(install_dir).resolve()
        self.fuseki_version = "4.10.0"  # Latest stable version
        self.download_url = f"https://archive.apache.org/dist/jena/binaries/apache-jena-fuseki-{self.fuseki_version}.zip"
        self.fuseki_jar = self.install_dir / f"apache-jena-fuseki-{self.fuseki_version}" / "fuseki-server.jar"
        self.config_file = self.install_dir / "mycomind-config.ttl"
        self.pid_file = self.install_dir / "fuseki.pid"
        self.log_file = self.install_dir / "fuseki.log"
        
        logger.info(f"Fuseki setup initialized for {self.install_dir}")
    
    def download_fuseki(self) -> bool:
        """
        Download and extract Apache Jena Fuseki.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create install directory
            self.install_dir.mkdir(parents=True, exist_ok=True)
            
            zip_file = self.install_dir / f"apache-jena-fuseki-{self.fuseki_version}.zip"
            
            # Download if not already present
            if not zip_file.exists():
                logger.info(f"Downloading Fuseki {self.fuseki_version}...")
                response = requests.get(self.download_url, stream=True)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(zip_file, 'wb') as f:
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
                logger.info("Fuseki archive already exists")
            
            # Extract if not already extracted
            fuseki_dir = self.install_dir / f"apache-jena-fuseki-{self.fuseki_version}"
            if not fuseki_dir.exists():
                logger.info("Extracting Fuseki...")
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(self.install_dir)
                logger.info("Extraction completed")
            else:
                logger.info("Fuseki already extracted")
            
            # Verify installation
            if self.fuseki_jar.exists():
                logger.info("✓ Fuseki installation verified")
                return True
            else:
                logger.error("✗ Fuseki jar not found after extraction")
                return False
                
        except Exception as e:
            logger.error(f"✗ Error downloading Fuseki: {e}")
            return False
    
    def create_config(self) -> bool:
        """
        Create Fuseki configuration file for MycoMind.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            config_content = f"""
@prefix fuseki: <http://jena.apache.org/fuseki#> .
@prefix rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:   <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ja:     <http://jena.hpl.hp.com/2005/11/Assembler#> .
@prefix :       <#> .

# MycoMind Knowledge Graph Service
:service rdf:type fuseki:Service ;
    fuseki:name "mycomind" ;
    fuseki:serviceQuery "query" ;
    fuseki:serviceQuery "sparql" ;
    fuseki:serviceUpdate "update" ;
    fuseki:serviceUpload "upload" ;
    fuseki:serviceReadWriteGraphStore "data" ;
    fuseki:dataset :dataset .

# Dataset configuration
:dataset rdf:type ja:RDFDataset ;
    ja:defaultGraph :graph .

# Graph configuration (in-memory for now)
:graph rdf:type ja:MemoryModel .

# Alternative: Persistent TDB2 storage
# Uncomment the following lines for persistent storage:
# :graph rdf:type ja:GraphTDB2 ;
#     ja:location "{self.install_dir}/databases/mycomind" .
"""
            
            with open(self.config_file, 'w') as f:
                f.write(config_content.strip())
            
            logger.info(f"✓ Configuration file created: {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Error creating config: {e}")
            return False
    
    def start_server(self, port: int = 3030, memory: str = "2g") -> bool:
        """
        Start Fuseki server.
        
        Args:
            port: Port to run server on
            memory: JVM memory allocation
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if already running
            if self.is_running():
                logger.info("Fuseki server is already running")
                return True
            
            # Ensure Java is available
            try:
                result = subprocess.run(['java', '-version'], 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error("Java is not installed or not in PATH")
                    return False
            except FileNotFoundError:
                logger.error("Java is not installed or not in PATH")
                return False
            
            # Create databases directory for persistent storage
            db_dir = self.install_dir / "databases"
            db_dir.mkdir(exist_ok=True)
            
            # Build command
            fuseki_home = str(self.install_dir / f"apache-jena-fuseki-{self.fuseki_version}")
            cmd = [
                'java',
                f'-Xmx{memory}',
                '-jar', str(self.fuseki_jar),
                '--config', str(self.config_file),
                '--port', str(port)
            ]
            
            logger.info(f"Starting Fuseki server on port {port} with FUSEKI_HOME {fuseki_home}...")
            logger.info(f"Command: {' '.join(cmd)}")
            
            # Set environment variable
            env = os.environ.copy()
            env["FUSEKI_HOME"] = fuseki_home
            env["JAVA_HOME"] = "/Users/darrenzal/.sdkman/candidates/java/current"
            
            # Log environment variables
            logger.debug(f"FUSEKI_HOME: {env.get('FUSEKI_HOME')}")
            logger.debug(f"JAVA_HOME: {env.get('JAVA_HOME')}")
            logger.debug(f"Environment: {env}")
            
            # Start server in background
            try:
                with open(self.log_file, 'w') as log_f:
                    process = subprocess.Popen(
                        cmd,
                        stdout=log_f,
                        stderr=subprocess.STDOUT,
                        cwd=self.install_dir,
                        env=env
                    )
            except Exception as e:
                logger.error(f"✗ Error starting server: {e}")
                logger.error(traceback.format_exc())
                return False
            
            # Save PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # Wait a moment and check if it started
            time.sleep(3)
            
            if self.is_running():
                logger.info(f"✓ Fuseki server started successfully (PID: {process.pid})")
                logger.info(f"  Web interface: http://localhost:{port}")
                logger.info(f"  SPARQL endpoint: http://localhost:{port}/mycomind/sparql")
                logger.info(f"  Log file: {self.log_file}")
                return True
            else:
                logger.error("✗ Fuseki server failed to start")
                self._show_recent_logs()
                return False
                
        except Exception as e:
            logger.error(f"✗ Error starting server: {e}")
            return False
    
    def stop_server(self) -> bool:
        """
        Stop Fuseki server.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.is_running():
                logger.info("Fuseki server is not running")
                return True
            
            # Read PID
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
                    
                    logger.info("✓ Fuseki server stopped")
                    return True
                    
                except ProcessLookupError:
                    logger.info("Fuseki server was not running")
                    self.pid_file.unlink()
                    return True
                    
            else:
                logger.warning("PID file not found, trying to find and kill Fuseki processes")
                # Try to find and kill any Fuseki processes
                try:
                    subprocess.run(['pkill', '-f', 'fuseki-server'], check=False)
                    logger.info("✓ Killed any running Fuseki processes")
                    return True
                except:
                    logger.error("Could not kill Fuseki processes")
                    return False
                    
        except Exception as e:
            logger.error(f"✗ Error stopping server: {e}")
            return False
    
    def is_running(self) -> bool:
        """
        Check if Fuseki server is running.
        
        Returns:
            True if running, False otherwise
        """
        try:
            # Check via HTTP ping
            response = requests.get(f"http://localhost:3031/$/ping", timeout=2)
            return response.status_code == 200
        except:
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
            'config_exists': self.config_file.exists(),
            'jar_exists': self.fuseki_jar.exists(),
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
    parser = argparse.ArgumentParser(description='Fuseki Setup for MycoMind')
    parser.add_argument('--download', action='store_true', help='Download and install Fuseki')
    parser.add_argument('--start', action='store_true', help='Start Fuseki server')
    parser.add_argument('--stop', action='store_true', help='Stop Fuseki server')
    parser.add_argument('--status', action='store_true', help='Show server status')
    parser.add_argument('--restart', action='store_true', help='Restart Fuseki server')
    parser.add_argument('--logs', action='store_true', help='Show recent logs')
    parser.add_argument('--install-dir', default='fuseki', help='Installation directory')
    parser.add_argument('--port', type=int, default=3030, help='Server port')
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
        setup = FusekiSetup(args.install_dir)
        
        if args.download:
            if setup.download_fuseki():
                setup.create_config()
                logger.info("Fuseki setup completed successfully!")
                logger.info(f"Next steps:")
                logger.info(f"  1. Start server: python setup_fuseki.py --start")
                logger.info(f"  2. Check status: python setup_fuseki.py --status")
                logger.info(f"  3. Load data: python graph_db_client.py --load data.jsonld")
            else:
                return 1
        
        elif args.start:
            if not setup.fuseki_jar.exists():
                logger.error("Fuseki not installed. Run with --download first.")
                return 1
            
            if not setup.config_file.exists():
                setup.create_config()
            
            if setup.start_server(args.port, args.memory):
                logger.info(f"Fuseki started on port {args.port}")
                return 0
            else:
                logger.error(f"Fuseki failed to start on port {args.port}")
                return 1
        
        elif args.stop:
            if setup.stop_server():
                return 0
            else:
                return 1
        
        elif args.restart:
            logger.info("Restarting Fuseki server...")
            setup.stop_server()
            time.sleep(2)
            if setup.start_server(args.port, args.memory):
                return 0
            else:
                return 1
        
        elif args.status:
            status = setup.get_status()
            print(f"\nFuseki Server Status:")
            print(f"  Running: {'✓' if status['running'] else '✗'}")
            print(f"  PID: {status['pid'] if status['pid'] else 'N/A'}")
            print(f"  Config exists: {'✓' if status['config_exists'] else '✗'}")
            print(f"  Jar exists: {'✓' if status['jar_exists'] else '✗'}")
            print(f"  Log size: {status['log_size']} bytes")
            
            if status['running']:
                print(f"  Web interface: http://localhost:{args.port}")
                print(f"  SPARQL endpoint: http://localhost:{args.port}/mycomind/sparql")
        
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
