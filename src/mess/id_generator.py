from __future__ import annotations

import hashlib
import logging
import subprocess
import sys
import shutil
import platform


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def get_motherboard_serial() -> str:
    """Fetch motherboard serial number on Linux using the absolute path."""
    try:
        dmidecode_path = shutil.which("dmidecode")
        if not dmidecode_path:
            logging.error(
                "dmidecode command not found. Ensure it is installed."
            )
            sys.exit(1)

        sudo_path = shutil.which("sudo")
        if not sudo_path:
            logging.error(
                "sudo command not found. Ensure it is installed."
            )
            sys.exit(1)

        result = subprocess.run(
            [sudo_path, dmidecode_path, "-s", "baseboard-serial-number"],
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(e.stderr.strip())
        sys.exit(1)


def get_cpu_id() -> str:
    """Fetch CPU serial ID on Linux using the absolute path."""
    try:
        result = subprocess.run(
            "cat /proc/cpuinfo | grep 'Serial' | awk '{print $3}'",
            check=True,
            capture_output=True,
            shell=True,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(e.stderr.strip())
        sys.exit(1)


def get_disk_serial() -> str:
    """Fetch Disk Drive Serial Number on Linux using the absolute path."""
    try:
        hdparm_path = shutil.which("hdparm")
        if not hdparm_path:
            logging.error("hdparm command not found. Ensure it is installed.")
            sys.exit(1)

        sudo_path = shutil.which("sudo")
        if not sudo_path:
            logging.error(
                "sudo command not found. Ensure it is installed."
            )
            sys.exit(1)

        result = subprocess.run(
            [sudo_path, hdparm_path, "-I", "/dev/sda"],
            check=True,
            capture_output=True,
            text=True
        )
        # Parse the serial number from the output
        serial_number = next(
            (
                line
                for line
                in result.stdout.splitlines()
                if "Serial Number" in line
            ),
            None
        )
        if serial_number:
            return serial_number.split(":")[-1].strip()
        else:
            logging.error("Serial Number not found in hdparm output.")
            sys.exit(1)
    except subprocess.CalledProcessError as e:
        logging.error(e.stderr.strip())
        sys.exit(1)


def generate_unique_machine_id() -> str:
    """Generate a unique machine ID by hashing multiple hardware attributes."""

    platform_name: str = platform.system()

    if platform_name != "Linux":
        error_message = f"OS not supported: {platform_name}"
        logging.error(error_message)
        sys.exit(1)

    try:
        with open("/etc/machine-id", "r") as file:
            machine_id = file.read().strip()
            logging.info("Using /etc/machine-id")
            return machine_id
    except FileNotFoundError:
        logging.warning(
            "/etc/machine-id not found. Falling back to hardware methods."
        )

    # Get hardware information using absolute paths
    motherboard_info = get_motherboard_serial()
    cpu_info = get_cpu_id()
    disk_info = get_disk_serial()

    # Combine the hardware information into a unique string
    unique_string: str = f"{motherboard_info} -- {cpu_info} -- {disk_info}"
    # Hash the string to create a unique machine ID
    machine_id: str = hashlib.sha256(unique_string.encode()).hexdigest()

    logging.warning(machine_id)

    return machine_id

