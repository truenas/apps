#!/usr/bin/env python3
"""
TrueNAS Apps Capability Manager

This script analyzes Docker Compose configurations for TrueNAS apps and updates
their metadata with capability requirements extracted from rendered templates.
"""

# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml",
# ]
# ///

import os
import re
import sys
import yaml
import logging
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass


# Global configuration
class Config:
    CONTAINER_IMAGE = "ghcr.io/truenas/apps_validation:latest"
    PLATFORM = "linux/amd64"

    RE_VAR_NAME = r"^[a-z0-9_]+$"

    # Directory structure
    APPS_ROOT_DIR = "ix-dev"
    TEST_VALUES_DIR = "templates/test_values"
    RENDERED_COMPOSE_PATH = "templates/rendered/docker-compose.yaml"

    # File names
    APP_METADATA_FILE = "app.yaml"
    APP_VALUES_FILE = "ix_values.yaml"
    QUESTIONS_FILE = "questions.yaml"

    # Special apps excluded from test train
    EXCLUDED_TEST_APPS = {"other-nginx", "nginx"}


# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DockerCapability:
    """Represents a Docker capability with its human-readable description."""

    name: str
    description: str

    def to_dict(self) -> Dict[str, str]:
        return {"description": self.description, "name": self.name}


@dataclass
class AppAnalysisResult:
    """Results from analyzing an app's Docker compose configurations."""

    capabilities: List[DockerCapability]
    service_names: List[str]
    app_version: str


@dataclass
class AppManifest:
    """Represents an app's basic information and test configurations."""

    path: Path
    name: str
    train: str
    test_value_files: List[str]


class DockerCapabilityRegistry:
    """Registry of Docker capabilities with their descriptions."""

    _CAPABILITY_DESCRIPTIONS = {
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

    _RENAME_MAPPINGS = {
        "dssystem": "DS System",
        "npm": "Nginx Proxy Manager",
        "omada": "Omada Controller",
        "lms": "Lyrion Media Server",
    }

    @staticmethod
    def service_name_to_title(service_name: str) -> str:
        """Convert a service name to a human-readable title."""
        return service_name.replace("-", " ").replace("_", " ").title()

    @staticmethod
    def hash_service_name(service_name: str) -> str:
        """Hash a service name to a short, unique identifier."""
        return service_name.lower().replace("_", "").replace("-", "").replace(" ", "")

    @classmethod
    def create_capability_description(cls, capability_name: str, service_names: List[str], title: str) -> str:
        """Create a human-readable description for a capability and its services."""
        if capability_name not in cls._CAPABILITY_DESCRIPTIONS:
            raise ValueError(f"Unknown capability: {capability_name}")

        if not service_names:
            raise ValueError(f"No services provided for capability: {capability_name}")
        clean_service_names = set()
        for name in service_names:
            parts = name.split("-")
            if parts[-1].isnumeric():
                name = "-".join(parts[:-1])
            clean_service_names.add(name)

        formatted_services = []
        for name in clean_service_names:
            if cls.hash_service_name(name) == cls.hash_service_name(title):
                formatted_services.append(title)
            elif name.lower() in cls._RENAME_MAPPINGS:
                formatted_services.append(cls._RENAME_MAPPINGS[name.lower()])
            else:
                formatted_services.append(cls.service_name_to_title(name))

        base_description = cls._CAPABILITY_DESCRIPTIONS[capability_name]

        if len(formatted_services) == 1:
            return f"{formatted_services[0]} is {base_description}"
        else:
            return f"{', '.join(sorted(formatted_services))} are {base_description}"


class FileSystemCache:
    """Simple file system cache to avoid repeated file reads."""

    def __init__(self):
        self._yaml_cache = {}

    def read_yaml_file(self, file_path: Path) -> Dict:
        """Read and cache YAML file contents."""
        # Convert to string for hashing
        file_key = str(file_path)

        # Check if file is cached and still valid
        if file_key in self._yaml_cache:
            cached_data, cached_mtime = self._yaml_cache[file_key]
            try:
                current_mtime = file_path.stat().st_mtime
                if current_mtime == cached_mtime:
                    return cached_data
            except OSError:
                # File might have been deleted, remove from cache
                del self._yaml_cache[file_key]

        # Read and cache the file
        try:
            with open(file_path, "r") as f:
                data = yaml.safe_load(f)

            # Ensure we have a dict
            if not isinstance(data, dict):
                raise ValueError(f"YAML file {file_path} must contain a dictionary at root level, got {type(data)}")

            # Cache with modification time
            mtime = file_path.stat().st_mtime
            self._yaml_cache[file_key] = (data, mtime)
            return data

        except (IOError, yaml.YAMLError) as e:
            raise RuntimeError(f"Failed to read YAML file {file_path}") from e

    def write_yaml_file(self, file_path: Path, data: Dict) -> None:
        """Write YAML data to file and invalidate cache."""
        try:
            with open(file_path, "w") as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)

            # Remove from cache since file was modified
            file_key = str(file_path)
            if file_key in self._yaml_cache:
                del self._yaml_cache[file_key]

        except IOError as e:
            raise RuntimeError(f"Failed to write YAML file {file_path}") from e

    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._yaml_cache.clear()


class AppDiscoveryService:
    """Service for discovering and validating TrueNAS apps."""

    def __init__(self, apps_root_dir: str = Config.APPS_ROOT_DIR):
        self.apps_root_path = Path(apps_root_dir)

    def discover_all_apps(self) -> List[AppManifest]:
        """Discover all valid apps across all trains."""
        if not self.apps_root_path.exists():
            logger.error(f"Apps root directory {self.apps_root_path} does not exist")
            return []

        all_apps = []
        for train_path in self.apps_root_path.iterdir():
            if not train_path.is_dir():
                continue

            train_name = train_path.name
            logger.info(f"Scanning train: {train_name}")

            train_apps = self._discover_apps_in_train(train_path, train_name)
            all_apps.extend(train_apps)

        logger.info(f"Discovered {len(all_apps)} apps total")
        return all_apps

    def discover_single_app(self, train_name: str, app_name: str) -> Optional[AppManifest]:
        """Discover a specific app by train and name."""
        app_path = self.apps_root_path / train_name / app_name
        return self._create_app_manifest(app_path, train_name)

    def _discover_apps_in_train(self, train_path: Path, train_name: str) -> List[AppManifest]:
        """Discover all apps within a specific train."""
        apps = []
        for app_path in train_path.iterdir():
            if not app_path.is_dir():
                continue

            app_manifest = self._create_app_manifest(app_path, train_name)
            if app_manifest:
                apps.append(app_manifest)

        return apps

    def _create_app_manifest(self, app_path: Path, train_name: str) -> Optional[AppManifest]:
        """Create an AppManifest for a single app directory."""
        app_name = app_path.name

        # Skip excluded apps in test train
        if train_name == "test" and app_name in Config.EXCLUDED_TEST_APPS:
            logger.debug(f"Skipping excluded test app: {app_name}")
            return None

        # Validate required files exist
        if not (app_path / Config.APP_METADATA_FILE).exists():
            logger.warning(f"Skipping {app_path}: missing {Config.APP_METADATA_FILE}")
            return None

        # Find test value files
        test_values_path = app_path / Config.TEST_VALUES_DIR
        test_value_files = []

        if test_values_path.exists():
            test_value_files = [f.name for f in test_values_path.iterdir() if f.is_file() and f.suffix == ".yaml"]

        if not test_value_files:
            logger.warning(f"No test values found for {app_path}")

        logger.debug(f"Found app: {app_path} with {len(test_value_files)} test configurations")
        return AppManifest(path=app_path, name=app_name, train=train_name, test_value_files=test_value_files)


class DockerComposeRenderer:
    """Handles rendering TrueNAS apps using Docker container."""

    def __init__(self, container_image: str = Config.CONTAINER_IMAGE, platform: str = Config.PLATFORM):
        self.container_image = container_image
        self.platform = platform

    def render_app_with_values(self, app_manifest: AppManifest, test_values_filename: str) -> Dict:
        """Render an app with specific test values and return compose data."""
        workspace_path = os.getcwd()
        values_path = app_manifest.path / Config.TEST_VALUES_DIR / test_values_filename

        docker_cmd = [
            "docker",
            "run",
            f"--platform={self.platform}",
            "--quiet",
            "--rm",
            f"-v={workspace_path}:/workspace",
            self.container_image,
            "apps_render_app",
            "render",
            f"--path=/workspace/{app_manifest.path}",
            f"--values=/workspace/{values_path}",
        ]

        logger.debug(f"Rendering: {' '.join(docker_cmd)}")

        try:
            result = subprocess.run(docker_cmd, capture_output=True, text=True, check=True)
            logger.debug(f"Successfully rendered {app_manifest.name} with {test_values_filename}")

            if result.stdout:
                logger.debug(f"Render output: {result.stdout}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to render {app_manifest.name}/{test_values_filename}")
            logger.error(f"Docker error: {e.stderr}")
            raise RuntimeError(f"Rendering failed for {app_manifest.name}") from e

        # Read rendered compose file
        compose_path = app_manifest.path / Config.RENDERED_COMPOSE_PATH
        if not compose_path.exists():
            raise FileNotFoundError(f"Rendered compose file not found: {compose_path}")

        try:
            self._fix_file_permissions(compose_path)
            with open(compose_path, "r") as f:
                data = yaml.safe_load(f)

            # Ensure we have a dict
            if not isinstance(data, dict):
                raise ValueError(f"YAML file {compose_path} must contain a dictionary at root level, got {type(data)}")
            return data

        except yaml.YAMLError as e:
            raise RuntimeError(f"Failed to parse rendered compose: {compose_path}") from e

    def _fix_file_permissions(self, file_path: Path) -> None:
        """Fix file permissions using Docker container."""
        logger.debug(f"Fixing permissions for {file_path}")

        docker_cmd = [
            "docker",
            "run",
            f"--platform={self.platform}",
            "--quiet",
            "--rm",
            f"-v={os.getcwd()}:/workspace",
            "--entrypoint=/bin/bash",
            self.container_image,
            "-c",
            f"chmod 777 /workspace/{file_path}",
        ]

        result = subprocess.run(docker_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Failed to fix permissions for {file_path}")
            logger.error(result.stderr)
            raise RuntimeError(f"Permission fix failed for {file_path}")


class DockerComposeAnalyzer:
    """Analyzes Docker Compose configurations for service capabilities."""

    @staticmethod
    def extract_service_names(compose_data: Dict, include_short_lived: bool = False) -> List[str]:
        """Extract service names from compose data, optionally including short-lived services."""
        services = compose_data.get("services", {})
        if not services:
            raise ValueError("No services found in compose data")

        service_names = []
        for service_name, service_config in services.items():
            if not include_short_lived:
                restart_policy = service_config.get("restart", "")
                if restart_policy.startswith("on-failure"):
                    logger.debug(f"Skipping short-lived service: {service_name}")
                    continue

            service_names.append(service_name)

        return service_names

    @staticmethod
    def extract_capabilities_by_service(compose_data: Dict) -> Dict[str, Set[str]]:
        """Extract capabilities grouped by service from compose data."""
        services = compose_data.get("services", {})
        if not services:
            raise ValueError("No services found in compose data")

        service_capabilities = {}

        for service_name, service_config in services.items():
            restart_policy = service_config.get("restart", "")

            # Skip services without restart policy
            if not restart_policy:
                logger.warning(f"No restart policy for service: {service_name}")
                continue

            # Skip short-lived services
            if restart_policy.startswith("on-failure"):
                logger.debug(f"Skipping short-lived service: {service_name}")
                continue

            # Validate cap_drop configuration
            if "cap_drop" not in service_config:
                logger.error(
                    f"No cap_drop for service: {service_name}. Consider explicitly setting the defaults via cap_add "
                    "https://github.com/moby/moby/blob/7a0bf747f5c25da0794e42d5f9e5a40db5a7786e/oci/caps/defaults.go#L4"
                )
            elif service_config["cap_drop"] != ["ALL"]:
                logger.error(f"Non-standard cap_drop for service: {service_name}")

            # Extract capabilities
            if "cap_add" in service_config:
                capabilities = set(service_config["cap_add"])
                if capabilities:
                    service_capabilities[service_name] = capabilities
                    logger.debug(f"Service {service_name} capabilities: {capabilities}")

        return service_capabilities


class AppQuestionsValidator:
    """Validates app questions configuration against actual services."""

    def __init__(self, file_cache: FileSystemCache):
        self.file_cache = file_cache

    def validate_question(self, question: Dict) -> None:
        """Validate a single question configuration."""
        if "variable" not in question:
            raise ValueError("Question missing variable field")

        variable_name = question["variable"]
        if variable_name == "TZ":
            return

        if variable_name not in [
            "storageEntry",
            "publicIpDnsProviderEntry",
            "jenkinsJavaOpt",
            "jenkinsOption",
            "aspellDict",
            "trustedProxy",
            "extraParam",
        ]:
            if not re.match(Config.RE_VAR_NAME, variable_name):
                raise ValueError(f"Invalid variable name: {variable_name}")

        schema = question["schema"]
        schema_type = schema["type"]
        if schema_type == "dict":
            for attr in schema["attrs"]:
                self.validate_question(attr)
        elif schema_type == "list":
            for item in schema["items"]:
                self.validate_question(item)

    def validate_variable_names(self, app_manifest: AppManifest) -> None:
        """Validate that variable names in questions match service names."""
        questions_path = app_manifest.path / Config.QUESTIONS_FILE
        if not questions_path.exists():
            raise FileNotFoundError(f"Questions file not found: {questions_path}")

        questions_config = self.file_cache.read_yaml_file(questions_path)
        if not isinstance(questions_config, dict):
            raise ValueError(f"Invalid questions config in {questions_path}")

        for question in questions_config.get("questions", []):
            self.validate_question(question)

    def validate_container_labels_section(self, app_manifest: AppManifest, service_names: List[str]) -> None:
        """Validate that container labels section matches actual service names."""
        questions_path = app_manifest.path / Config.QUESTIONS_FILE
        if not questions_path.exists():
            raise FileNotFoundError(f"Questions file not found: {questions_path}")

        questions_config = self.file_cache.read_yaml_file(questions_path)
        if not isinstance(questions_config, dict):
            raise ValueError(f"Invalid questions config in {questions_path}")

        # Find the labels question and validate containers enum
        for question in questions_config.get("questions", []):
            if question.get("variable") != "labels":
                continue

            for item in question["schema"]["items"][0]["schema"]["attrs"]:
                if item.get("variable") != "containers":
                    continue

                old_enum = item["schema"]["items"][0]["schema"]["enum"]
                new_enum = [{"value": name, "description": name} for name in service_names]

                old_values = {item["value"] for item in old_enum}
                new_values = {item["value"] for item in new_enum}

                if old_values != new_values:
                    raise ValueError(
                        f"Container labels section should have {sorted(new_values)} " f"but has {sorted(old_values)}"
                    )
            break


class AppVersionManager:
    """Manages app version information and updates."""

    def __init__(self, file_cache: FileSystemCache, should_bump_versions: bool = True):
        self.file_cache = file_cache
        self.should_bump_versions = should_bump_versions

    def get_current_app_version(self, app_manifest: AppManifest) -> str:
        """Get the current app version from appropriate source."""
        # Special case for ix-app
        if str(app_manifest.path) == f"{Config.APPS_ROOT_DIR}/stable/ix-app":
            app_config = self.file_cache.read_yaml_file(app_manifest.path / Config.APP_METADATA_FILE)
            return app_config["version"]

        # Regular apps use ix_values.yaml
        values_path = app_manifest.path / Config.APP_VALUES_FILE
        if not values_path.exists():
            raise FileNotFoundError(f"App values file not found: {values_path}")

        values_config = self.file_cache.read_yaml_file(values_path)
        return values_config["images"]["image"]["tag"]

    def increment_patch_version(self, version: str) -> str:
        """Increment the patch version number."""
        if not self.should_bump_versions:
            return version

        try:
            parts = version.split(".")
            if len(parts) != 3:
                raise ValueError("Version must be in format x.y.z")

            parts[2] = str(int(parts[2]) + 1)
            return ".".join(parts)
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid version format: {version}") from e


class AppMetadataUpdater:
    """Updates app metadata files with capability information."""

    def __init__(self, file_cache: FileSystemCache, version_manager: AppVersionManager):
        self.file_cache = file_cache
        self.version_manager = version_manager

    def update_app_metadata(
        self,
        app_manifest: AppManifest,
        capabilities: List[DockerCapability],
        current_app_version: str,
        should_bump_version: bool = True,
    ) -> None:
        """Update app.yaml with new capabilities and version information."""
        app_metadata_path = app_manifest.path / Config.APP_METADATA_FILE
        app_config = self.file_cache.read_yaml_file(app_metadata_path)

        if not isinstance(app_config, dict):
            raise ValueError(f"Invalid app config in {app_metadata_path}")

        # Validate app configuration (warnings only)
        self._validate_app_configuration(app_manifest, app_config)

        # Check if update is needed
        needs_version_bump = False

        # Update app version if changed
        old_app_version = app_config.get("app_version", "")
        # If the old app version is a substring of the current version, keep it
        # Example new version is 1.2.3-debian and app_version is 1.2.3. This is fine.
        if old_app_version in current_app_version:
            current_app_version = old_app_version
        if current_app_version != old_app_version:
            needs_version_bump = True
        app_config["app_version"] = current_app_version

        # Update capabilities if changed
        new_capabilities_data = sorted([cap.to_dict() for cap in capabilities], key=lambda c: c["name"])
        old_capabilities_data = sorted(app_config.get("capabilities", []), key=lambda c: c["name"])

        if old_capabilities_data != new_capabilities_data:
            needs_version_bump = True
        app_config["capabilities"] = new_capabilities_data

        # Bump version if needed
        if needs_version_bump and should_bump_version:
            old_version = app_config["version"]
            new_version = self.version_manager.increment_patch_version(old_version)
            app_config["version"] = new_version
            logger.info(f"Updated {app_manifest.name} version: {old_version} → {new_version}")

        # Write updated configuration
        self.file_cache.write_yaml_file(app_metadata_path, app_config)

    def _validate_app_configuration(self, app_manifest: AppManifest, app_config: Dict) -> None:
        """Validate app configuration and log warnings for issues."""
        app_name = app_config.get("name", app_manifest.name)

        # Check for multiple categories
        categories = app_config.get("categories", [])
        if len(categories) > 1:
            logger.warning(f"{app_manifest.name}: multiple categories: {categories}")

        # Check for missing fields
        if "date_added" not in app_config:
            logger.warning(f"{app_manifest.name}: missing date_added")
        if "changelog_url" not in app_config:
            logger.warning(f"{app_manifest.name}: missing changelog_url")

        # Validate media URLs
        expected_base_url = f"https://media.sys.truenas.net/apps/{app_name}"

        icon_url = app_config.get("icon", "")
        if not icon_url.startswith(f"{expected_base_url}/icons/"):
            logger.warning(f"{app_manifest.name}: invalid icon URL: {icon_url}")

        for screenshot_url in app_config.get("screenshots", []):
            if not screenshot_url.startswith(f"{expected_base_url}/screenshots/"):
                logger.warning(f"{app_manifest.name}: invalid screenshot URL: {screenshot_url}")


class TrueNASAppCapabilityManager:
    """Main orchestrator for TrueNAS app capability management."""

    def __init__(self, should_bump_versions: bool = True):
        self.should_bump_versions = should_bump_versions
        self.file_cache = FileSystemCache()
        self.discovery_service = AppDiscoveryService()
        self.compose_renderer = DockerComposeRenderer()
        self.compose_analyzer = DockerComposeAnalyzer()
        self.questions_validator = AppQuestionsValidator(self.file_cache)
        self.version_manager = AppVersionManager(self.file_cache, should_bump_versions)
        self.metadata_updater = AppMetadataUpdater(self.file_cache, self.version_manager)
        self.capability_registry = DockerCapabilityRegistry()

    def analyze_single_app(self, app_manifest: AppManifest) -> AppAnalysisResult:
        """Analyze a single app across all its test configurations."""
        if not app_manifest.test_value_files:
            logger.warning(f"No test configurations for {app_manifest.name}")
            return AppAnalysisResult([], [], "")

        # Extract app title from app.yaml
        app_metadata_path = app_manifest.path / Config.APP_METADATA_FILE
        app_config = self.file_cache.read_yaml_file(app_metadata_path)
        if not isinstance(app_config, dict):
            raise ValueError(f"Invalid app config in {app_metadata_path}")
        app_title = app_config.get("title", app_manifest.name)

        # Track capabilities across all test configurations
        capability_to_services: Dict[str, Set[str]] = {}
        all_service_names = set()

        for test_values_file in app_manifest.test_value_files:
            logger.debug(f"Processing {app_manifest.name} with {test_values_file}")

            try:
                # Render app with test configuration
                compose_data = self.compose_renderer.render_app_with_values(app_manifest, test_values_file)

                # Extract service information
                service_names = self.compose_analyzer.extract_service_names(compose_data)
                all_service_names.update(service_names)

                # Extract capabilities by service
                service_capabilities = self.compose_analyzer.extract_capabilities_by_service(compose_data)

                # Aggregate capabilities
                for service_name, capabilities in service_capabilities.items():
                    for capability in capabilities:
                        if capability not in capability_to_services:
                            capability_to_services[capability] = set()
                        capability_to_services[capability].add(service_name)

            except Exception as e:
                logger.error(f"Failed to process {app_manifest.name}/{test_values_file}: {e}")
                raise

        # Convert to DockerCapability objects
        capabilities = []
        for capability_name, services in capability_to_services.items():
            try:
                description = self.capability_registry.create_capability_description(
                    capability_name, sorted(services), app_title
                )
                capabilities.append(DockerCapability(capability_name, description))
            except ValueError as e:
                logger.error(f"Failed to create capability description: {e}")
                continue

        # Get current app version
        current_version = self.version_manager.get_current_app_version(app_manifest)

        return AppAnalysisResult(
            capabilities=sorted(capabilities, key=lambda c: c.name),
            service_names=sorted(all_service_names),
            app_version=str(current_version),
        )

    def update_single_app(self, app_manifest: AppManifest) -> None:
        """Update capabilities and metadata for a single app."""
        logger.debug(f"Updating capabilities for {app_manifest.name}")

        try:
            # Analyze the app
            analysis_result = self.analyze_single_app(app_manifest)

            # Validate variable names in questions
            self.questions_validator.validate_variable_names(app_manifest)

            # Validate questions configuration
            self.questions_validator.validate_container_labels_section(app_manifest, analysis_result.service_names)

            # Update metadata
            self.metadata_updater.update_app_metadata(
                app_manifest, analysis_result.capabilities, analysis_result.app_version, self.should_bump_versions
            )

            logger.info(
                f"Successfully updated {app_manifest.name} with " f"{len(analysis_result.capabilities)} capabilities"
            )

        except Exception as e:
            logger.error(f"Failed to update {app_manifest.name}: {e}")
            raise

    def update_all_apps(self) -> None:
        """Update capabilities for all discovered apps."""
        app_manifests = self.discovery_service.discover_all_apps()

        if not app_manifests:
            logger.warning("No apps found to process")
            return

        success_count = 0
        failed_count = 0

        for app_manifest in app_manifests:
            try:
                self.update_single_app(app_manifest)
                success_count += 1
            except Exception as e:
                logger.error(f"Skipping {app_manifest.name}: {e}")
                failed_count += 1
                continue

        logger.info(f"Successfully processed {success_count}/{len(app_manifests)} apps")
        if failed_count > 0:
            logger.error(f"Failed to process {failed_count} apps")
            sys.exit(1)

    def update_specific_app(self, train_name: str, app_name: str) -> None:
        """Update capabilities for a specific app."""
        app_manifest = self.discovery_service.discover_single_app(train_name, app_name)
        if not app_manifest:
            logger.error(f"App {train_name}/{app_name} not found")
            sys.exit(1)

        self.update_single_app(app_manifest)


def parse_command_line_arguments() -> argparse.Namespace:
    """Parse and return command line arguments."""
    parser = argparse.ArgumentParser(
        description="TrueNAS Apps Capability Manager - Analyze and update app capabilities"
    )
    parser.add_argument("--train", help="Specific train name to process")
    parser.add_argument("--app", help="Specific app name to process (requires --train)")
    parser.add_argument("--no-bump", action="store_true", help="Skip version bumping when updating metadata")

    return parser.parse_args()


def main():
    """Main application entry point."""
    try:
        args = parse_command_line_arguments()

        # Initialize the capability manager
        capability_manager = TrueNASAppCapabilityManager(should_bump_versions=not args.no_bump)

        # Determine operation mode
        if args.train and args.app:
            # Update specific app
            capability_manager.update_specific_app(args.train, args.app)
        elif args.train or args.app:
            # Invalid: both train and app must be provided together
            logger.error("Both --train and --app must be provided together, or neither")
            sys.exit(1)
        else:
            # Update all apps
            capability_manager.update_all_apps()

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
