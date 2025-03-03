import click

from mess.id_generator import generate_unique_machine_id
from mess.manage_requirements import fulfill_requirements
from mess.security import decrypt_file, encrypt_file


@click.command()
@click.argument("file_path", required=True, type=str)
def main(file_path: str) -> None:
    fulfill_requirements()

    uid: str = generate_unique_machine_id()

    print(uid)

    if file_path.endswith(".mess"):
        decrypt_file(file_path=file_path, password=uid)
    else:
        encrypt_file(file_path=file_path, password=uid)
