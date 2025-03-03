import logging
import shutil
import subprocess
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def is_installed(package_name: str) -> bool:
    """Check if a package is installed."""
    dpkg_path = shutil.which("dpkg")

    if not dpkg_path:
        logging.error("dpkg command not found. Ensure it is installed.")
        sys.exit(1)

    try:
        subprocess.run(
            [dpkg_path, "-s", package_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    except subprocess.CalledProcessError:
        return False
    else:
        return True


def install_package(package_name: str) -> bool:
    """Install a package using apt."""
    logging.info("Installing %s...", package_name)

    apt_path = shutil.which("apt")  # Get full path of apt
    sudo_path = shutil.which("sudo")  # Get full path of sudo

    if not apt_path:
        logging.error("apt command not found. Ensure it is installed.")
        sys.exit(1)

    if not sudo_path:
        logging.error("sudo command not found. Ensure it is installed.")
        sys.exit(1)

    try:
        subprocess.run(
            [sudo_path, apt_path, "install", "-y", package_name],
            check=True
        )
        logging.info("%s installed successfully!", package_name)
    except subprocess.CalledProcessError:
        logging.info("Failed to install %s.", package_name)
        return False
    else:
        return True


def fulfill_requirements() -> None:
    required_packages: list[str] = ["dmidecode", "hdparm", "util-linux"]

    missing_packages: list[str] = [
        pkg
        for pkg
        in required_packages
        if not is_installed(pkg)
    ]

    if missing_packages:
        logging.info(
            "Missing packages detected: %s",
            ", ".join(missing_packages)
        )
        logging.info("Installing missing packages...")
        for pkg in missing_packages:
            install_package(pkg)

    logging.warning("All Packages aquired.")
