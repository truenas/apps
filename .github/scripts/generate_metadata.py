#!/usr/bin/env python3
"""
This script analyzes Docker Compose for apps and updates their metadata
by rendering app templates and extracting "real" data from docker-compose files.
"""

import os
import sys
import yaml
import logging
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass


args: argparse.Namespace | None = None


# Configuration
CONTAINER_IMAGE = "ghcr.io/truenas/apps_validation:latest"
PLATFORM = "linux/amd64"
IX_DEV_DIR = "ix-dev"
TEST_VALUES_DIR = "templates/test_values"
RENDERED_COMPOSE_PATH = "templates/rendered/docker-compose.yaml"
APP_YAML = "app.yaml"
IX_VALUES_YAML = "ix_values.yaml"
QUESTIONS_YAML = "questions.yaml"

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class Capability:
    """Represents a Docker capability with its description."""

    name: str
    description: str

    def to_dict(self) -> Dict[str, str]:
        return {"name": self.name, "description": self.description}


class CapabilityDescriptor:
    """Manages capability descriptions and formatting."""

    CAPABILITY_DESCRIPTIONS = {
        "AUDIT_CONTROL": "able to control audit subsystem configuration",
        "AUDIT_READ": "able to read audit log entries",
        "AUDIT_WRITE": "able to write records to audit log",
        "BLOCK_SUSPEND": "able to block system suspend operations",
        "BPF": "able to use Berkeley Packet Filter programs",
        "CHECKPOINT_RESTORE": "able to use checkpoint/restore functionality",
        "CHOWN": "able to change file ownership arbitrarily",
        "DAC_OVERRIDE": "able to bypass file permission checks",
        "DAC_READ_SEARCH": "able to bypass read/execute permission checks",
        "FOWNER": "able to bypass permission checks for file operations",
        "FSETID": "able to preserve set-user-ID and set-group-ID bits",
        "IPC_LOCK": "able to lock memory segments in RAM",
        "IPC_OWNER": "able to bypass permission checks for IPC operations",
        "KILL": "able to send signals to any process",
        "LEASE": "able to establish file leases",
        "LINUX_IMMUTABLE": "able to set immutable and append-only file attributes",
        "MAC_ADMIN": "able to configure Mandatory Access Control",
        "MAC_OVERRIDE": "able to override Mandatory Access Control restrictions",
        "MKNOD": "able to create special files using mknod()",
        "NET_ADMIN": "able to perform network administration tasks",
        "NET_BIND_SERVICE": "able to bind to privileged ports (< 1024)",
        "NET_BROADCAST": "able to make socket broadcasts",
        "NET_RAW": "able to use raw and packet sockets",
        "PERFMON": "able to access performance monitoring interfaces",
        "SETFCAP": "able to set file capabilities on other files",
        "SETGID": "able to change group ID of processes",
        "SETPCAP": "able to transfer capabilities between processes",
        "SETUID": "able to change user ID of processes",
        "SYS_ADMIN": "able to perform system administration operations",
        "SYS_BOOT": "able to reboot and load/unload kernel modules",
        "SYS_CHROOT": "able to use chroot() system call",
        "SYS_MODULE": "able to load and unload kernel modules",
        "SYS_NICE": "able to modify process scheduling priority",
        "SYS_PACCT": "able to configure process accounting",
        "SYS_PTRACE": "able to trace and control other processes",
        "SYS_RAWIO": "able to perform raw I/O operations",
        "SYS_RESOURCE": "able to override resource limits",
        "SYS_TIME": "able to set system clock and real-time clock",
        "SYS_TTY_CONFIG": "able to configure TTY devices",
        "SYSLOG": "able to perform privileged syslog operations",
        "WAKE_ALARM": "able to trigger system wake alarms",
    }

    @classmethod
    def create_description(cls, capability: str, services: List[str]) -> str:
        """Create a human-readable description for a capability."""
        if capability not in cls.CAPABILITY_DESCRIPTIONS:
            raise ValueError(f"Unknown capability: {capability}")

        if not services:
            raise ValueError(f"No services provided for capability: {capability}")

        # Format service names (replace hyphens with spaces and title case)
        formatted_services = [service.replace("-", " ").title() for service in services]

        base_description = cls.CAPABILITY_DESCRIPTIONS[capability]

        if len(formatted_services) == 1:
            return f"{formatted_services[0]} is {base_description}"
        else:
            return f"{', '.join(formatted_services)} are {base_description}"


class AppDiscovery:
    """Handles discovery and validation of TrueNAS apps."""

    EXCLUDED_TEST_APPS = {"other-nginx", "nginx"}  # Excluded from test train

    @classmethod
    def discover_single_app(cls, app_path: Path, train_name: str) -> Optional[Dict[str, List[str]]]:
        """Discover a single app and return its test values."""
        app_name = app_path.name

        # Skip excluded apps in test train
        if train_name == "test" and app_name in cls.EXCLUDED_TEST_APPS:
            logger.debug(f"Skipping excluded app: {app_name}")
            return None

        # Validate app structure
        app_yaml_path = app_path / APP_YAML
        if not app_yaml_path.exists():
            logger.warning(f"Skipping {app_path}: missing {APP_YAML}")
            return None

        # Find test values
        test_values_path = app_path / TEST_VALUES_DIR
        test_values = []

        if test_values_path.exists():
            test_values = [f.name for f in test_values_path.iterdir() if f.is_file() and f.suffix == ".yaml"]

        if not test_values:
            logger.warning(f"No test values found for {app_path}")

        logger.debug(f"Found app: {app_path} with {len(test_values)} test values")
        return {"test_values": test_values}

    @classmethod
    def discover_apps(cls, base_dir: str = IX_DEV_DIR) -> Dict[str, Dict[str, List[str]]]:
        """Discover all valid apps and their test values."""
        apps = {}
        base_path = Path(base_dir)

        if not base_path.exists():
            logger.error(f"Base directory {base_dir} does not exist")
            return apps

        for train_path in base_path.iterdir():
            if not train_path.is_dir():
                continue

            train_name = train_path.name
            logger.info(f"Processing train: {train_name}")

            for app_path in train_path.iterdir():
                if not app_path.is_dir():
                    continue

                app_info = cls.discover_single_app(app_path, train_name)
                if app_info is not None:
                    apps[str(app_path)] = app_info

        logger.info(f"Discovered {len(apps)} apps")
        return apps


class QuestionsAnalyzer:
    @staticmethod
    def analyze_containers_in_labels_section(app_path: str, service_names: List[str]) -> None:
        """Update containers in labels section of app.yaml."""
        app_yaml_path = Path(app_path) / QUESTIONS_YAML
        if not app_yaml_path.exists():
            raise FileNotFoundError(f"App {app_path} does not have {QUESTIONS_YAML}")
        try:
            with open(app_yaml_path, "r") as f:
                app_config = yaml.safe_load(f)
        except (IOError, yaml.YAMLError) as e:
            raise RuntimeError(f"Failed to read {app_yaml_path}") from e

        if not isinstance(app_config, dict):
            raise ValueError(f"Invalid app config in {app_yaml_path}")

        for question in app_config.get("questions", []):
            if question["variable"] != "labels":
                continue
            for item in question["schema"]["items"][0]["schema"]["attrs"]:
                if item["variable"] != "containers":
                    continue
                old_enum = item["schema"]["items"][0]["schema"]["enum"]
                new_enum = [{"value": service_name, "description": service_name} for service_name in service_names]
                if sorted(old_enum, key=lambda x: x["value"]) != sorted(new_enum, key=lambda x: x["value"]):
                    difference = set([e["value"] for e in new_enum]) ^ (set([e["value"] for e in old_enum]))
                    raise ValueError(
                        f"Containers in labels section and service names of {app_path} have a mismatch"
                        f" the difference is ({len(difference)}) {difference}"
                    )
            break


class DockerComposeAnalyzer:
    """Analyzes Docker Compose files for capability requirements."""

    @staticmethod
    def extract_service_names(compose_data: Dict, include_short_lived: bool = False) -> List[str]:
        """Extract service names from docker-compose data."""
        if "services" not in compose_data:
            raise ValueError("No services found in compose data")

        service_names = []
        for service_name, service_config in compose_data["services"].items():
            if not include_short_lived:
                # Skip services without restart policies (short-lived containers)
                restart_policy = service_config.get("restart", "")
                if restart_policy.startswith("on-failure"):
                    logger.debug(f"Skipping short-lived service: {service_name}")
                    continue
            service_names.append(service_name)

        return service_names

    @staticmethod
    def extract_capabilities(compose_data: Dict) -> Dict[str, Set[str]]:
        """Extract capabilities from docker-compose data."""
        service_capabilities = {}

        if "services" not in compose_data:
            raise ValueError("No services found in compose data")

        for service_name, service_config in compose_data["services"].items():
            # Skip services without restart policies (short-lived containers)
            restart_policy = service_config.get("restart", "")
            if not restart_policy:
                logger.warning(f"No restart policy for service: {service_name}")
                continue

            # Skip services that restart only on failure
            if restart_policy.startswith("on-failure"):
                logger.debug(f"Skipping short-lived service: {service_name}")
                continue

            if "cap_drop" not in service_config:
                logger.warning(f"No cap_drop for service: {service_name}")
            else:
                if service_config["cap_drop"] != ["ALL"]:
                    logger.warning(f"Non-default cap_drop for service: {service_name}")

            # Extract capabilities
            if "cap_add" in service_config:
                capabilities = set(service_config["cap_add"])
                if capabilities:
                    service_capabilities[service_name] = capabilities
                    logger.debug(f"Service {service_name} has capabilities: {capabilities}")

        return service_capabilities


class AppRenderer:
    """Handles rendering of TrueNAS apps using Docker container."""

    def __init__(self, container_image: str = CONTAINER_IMAGE, platform: str = PLATFORM):
        self.container_image = container_image
        self.platform = platform

    def render_app(self, app_path: str, test_values_file: str) -> Dict:
        """Render an app with specific test values and return compose data."""
        workspace_path = os.getcwd()

        cmd = [
            "docker",
            "run",
            f"--platform={self.platform}",
            "--quiet",
            "--rm",
            f"-v={workspace_path}:/workspace",
            self.container_image,
            "apps_render_app",
            "render",
            f"--path=/workspace/{app_path}",
            f"--values=/workspace/{app_path}/{TEST_VALUES_DIR}/{test_values_file}",
        ]

        logger.debug(f"Rendering command: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.debug(f"Render completed successfully for {app_path}/{test_values_file}")
            if result.stdout:
                logger.debug(f"Render output: {result.stdout}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to render {app_path}/{test_values_file}")
            logger.error(f"Error output: {e.stderr}")
            raise RuntimeError(f"Rendering failed for {app_path}/{test_values_file}") from e

        # Read the rendered compose file
        compose_path = Path(app_path) / RENDERED_COMPOSE_PATH
        if not compose_path.exists():
            raise FileNotFoundError(f"Rendered compose file not found: {compose_path}")

        try:
            fix_permissions(compose_path)
            with open(compose_path, "r") as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise RuntimeError(f"Failed to parse rendered compose file: {compose_path}") from e


class AppUpdater:
    """Handles updating app metadata with capability information."""

    @staticmethod
    def bump_version(version: str) -> str:
        """Increment the patch version number."""

        if args is not None and args.no_bump:
            return version

        try:
            parts = version.split(".")
            if len(parts) != 3:
                raise ValueError("Version must be in format x.y.z")

            parts[2] = str(int(parts[2]) + 1)
            return ".".join(parts)
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid version format: {version}") from e

    @staticmethod
    def get_app_version(app_path: str) -> str:
        """Get the app version from app.yaml."""
        if app_path == f"{IX_DEV_DIR}/stable/ix-app":
            with open(Path(app_path) / APP_YAML, "r") as f:
                app_config = yaml.safe_load(f)
            return app_config["version"]
        yaml_path = Path(app_path) / IX_VALUES_YAML
        if not yaml_path.exists():
            raise FileNotFoundError(f"App {app_path} does not have {IX_VALUES_YAML}")
        try:
            with open(yaml_path, "r") as f:
                values = yaml.safe_load(f)
                return values["images"]["image"]["tag"]
        except (IOError, yaml.YAMLError) as e:
            raise RuntimeError(f"Failed to read {yaml_path}") from e

    @staticmethod
    def update_app_metadata(app_path: str, capabilities: List[Capability]) -> None:
        """Update app.yaml with new capabilities."""
        app_yaml_path = Path(app_path) / APP_YAML

        try:
            with open(app_yaml_path, "r") as f:
                app_config = yaml.safe_load(f)
        except (IOError, yaml.YAMLError) as e:
            raise RuntimeError(f"Failed to read {app_yaml_path}") from e

        # Validate app config
        if not isinstance(app_config, dict):
            raise ValueError(f"Invalid app config in {app_yaml_path}")

        # Check for multiple categories (warning only)
        categories = app_config.get("categories", [])
        if len(categories) > 1:
            logger.warning(f"App {app_path} has multiple categories: {categories}")
        if "date_added" not in app_config:
            logger.warning(f"App {app_path} has no date added")
        if "changelog_url" not in app_config:
            logger.warning(f"App {app_path} has no changelog URL")

        should_bump = False

        # Make sure app version is up to date
        new_version = AppUpdater.get_app_version(app_path)
        old_version = app_config["app_version"]

        if new_version != old_version:
            should_bump = True
        app_config["app_version"] = new_version

        # Convert capabilities to dict format
        new_capabilities = [cap.to_dict() for cap in capabilities]
        old_capabilities = app_config.get("capabilities", [])

        # Update version if capabilities changed
        if old_capabilities != new_capabilities:
            should_bump = True
        app_config["capabilities"] = new_capabilities

        if should_bump:
            current_version = app_config["version"]
            app_config["version"] = AppUpdater.bump_version(current_version)
            logger.info(f"Updated version from {current_version} to {app_config['version']}")

        try:
            with open(app_yaml_path, "w") as f:
                yaml.dump(app_config, f, default_flow_style=False, sort_keys=False)
        except IOError as e:
            raise RuntimeError(f"Failed to write {app_yaml_path}") from e


@dataclass
class AnalyzedApp:
    capabilities: List[Capability]
    service_names: List[str]


class MetadataManager:
    """Main class for managing TrueNAS app metadata."""

    def __init__(self):
        self.renderer = AppRenderer()
        self.analyzer = DockerComposeAnalyzer()
        self.descriptor = CapabilityDescriptor()

    def analyze_app(self, app_path: str, app_info: Dict[str, List[str]]) -> AnalyzedApp:
        """Analyzes app across all test configurations."""
        # CHOWN: [service1, service2]
        all_capabilities: Dict[str, Set[str]] = {}
        service_names = set()

        test_files = app_info["test_values"]
        if not test_files:
            logger.warning(f"No test values found for {app_path}")
            return AnalyzedApp([], [])

        for test_file in test_files:
            logger.debug(f"Processing test file: {test_file}")

            try:
                # Render the app with this test configuration
                compose_data = self.renderer.render_app(app_path, test_file)

                service_names.update(set(self.analyzer.extract_service_names(compose_data)))

                # Extract capabilities from the rendered compose
                service_caps = self.analyzer.extract_capabilities(compose_data)

                # Aggregate capabilities across services
                for service, caps in service_caps.items():
                    for cap in caps:
                        if cap not in all_capabilities:
                            all_capabilities[cap] = set()
                        all_capabilities[cap].add(service)

            except Exception as e:
                logger.error(f"Failed to process {app_path}/{test_file}: {e}")
                raise

        # Convert to Capability objects
        capabilities = []
        for cap_name, services in all_capabilities.items():
            try:
                description = self.descriptor.create_description(cap_name, list(services))
                capabilities.append(Capability(cap_name, description))
            except ValueError as e:
                logger.error(f"Failed to create capability description: {e}")
                continue

        # Sort by capability name for consistency
        capabilities.sort(key=lambda c: c.name)
        return AnalyzedApp(capabilities, sorted(service_names))

    def update_single_app(self, app_path: str, app_info: Dict[str, List[str]]) -> None:
        """Update capabilities for a single app."""
        logger.debug(f"Updating capabilities for {app_path}")

        try:
            data = self.analyze_app(app_path, app_info)
            capabilities = data.capabilities
            service_names = data.service_names
            QuestionsAnalyzer.analyze_containers_in_labels_section(app_path, service_names)
            AppUpdater.update_app_metadata(app_path, capabilities)
            logger.info(f"Successfully updated {app_path} with {len(capabilities)} capabilities")
        except Exception as e:
            logger.error(f"Failed to update {app_path}: {e}")
            raise

    def update_all_apps(self) -> None:
        """Update capabilities for all discovered apps."""
        apps = AppDiscovery.discover_apps()

        if not apps:
            logger.warning("No apps found to process")
            return

        success_count = 0
        failed_count = 0
        for app_path, app_info in apps.items():
            try:
                self.update_single_app(app_path, app_info)
                success_count += 1
            except Exception as e:
                logger.error(f"Skipping {app_path} due to error: {e}")
                failed_count += 1
                continue

        logger.info(f"Successfully processed {success_count}/{len(apps)} apps")
        if failed_count:
            logger.error(f"Failed to process {failed_count}/{len(apps)} apps")
            sys.exit(1)


def fix_permissions(file_path):
    logger.debug(f"Fixing permissions for file [{file_path}]")
    cmd = " ".join(
        [
            f"docker run --platform {PLATFORM} --quiet --rm -v {os.getcwd()}:/workspace",
            f"--entrypoint /bin/bash {CONTAINER_IMAGE} -c 'chmod 777 /workspace/{file_path}'",
        ]
    )
    res = subprocess.run(cmd, shell=True, capture_output=True)
    if res.returncode != 0:
        logger.error(f"Failed to fix permissions for file [{file_path}]")
        logger.error(res.stderr.decode("utf-8"))
        sys.exit(1)
    logger.debug(f"Done fixing permissions for file [{file_path}]")


def main():
    """Main entry point."""
    global args

    try:
        manager = MetadataManager()
        parser = argparse.ArgumentParser(description="TrueNAS Apps Capability Manager")
        parser.add_argument("--train", help="train name", required=False)
        parser.add_argument("--app", help="app name", required=False)
        parser.add_argument("--no-bump", help="do not bump version", action="store_true", default=False, required=False)
        args = parser.parse_args()

        if args.train and args.app:
            app_path = f"{IX_DEV_DIR}/{args.train}/{args.app}"
            app = AppDiscovery.discover_single_app(Path(app_path), args.train)
            if app is None:
                logger.error(f"App {app_path} not found")
                sys.exit(1)
            manager.update_single_app(app_path, app)
        elif args.train or args.app:
            logger.error("Both train and app must be provided together, or neither")
            parser.print_help()
            sys.exit(1)
        else:
            manager.update_all_apps()

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
