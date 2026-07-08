from pathlib import Path
import secrets


# ==================================================
# NovaPOS Secret Key Generator
# ==================================================


def generate_secret_key(length: int = 64) -> str:
    """
    Generate a secure random secret key.
    """
    return secrets.token_urlsafe(length)


def update_env(secret_key: str):
    """
    Update SECRET_KEY value inside backend/.env
    """

    project_root = Path(__file__).resolve().parent.parent

    env_path = project_root / "backend" / ".env"

    if not env_path.exists():
        raise FileNotFoundError(
            f"No existe archivo .env en: {env_path}"
        )

    lines = env_path.read_text(
        encoding="utf-8"
    ).splitlines()

    updated = False
    new_lines = []

    for line in lines:

        if line.startswith("SECRET_KEY="):
            new_lines.append(
                f"SECRET_KEY={secret_key}"
            )
            updated = True
        else:
            new_lines.append(line)

    if not updated:
        new_lines.append(
            f"SECRET_KEY={secret_key}"
        )

    env_path.write_text(
        "\n".join(new_lines) + "\n",
        encoding="utf-8"
    )

    return env_path


if __name__ == "__main__":

    secret = generate_secret_key()

    path = update_env(secret)

    print()
    print("NovaPOS SECRET_KEY generada correctamente")
    print("-----------------------------------------")
    print(f"Archivo actualizado: {path}")
    print()
    print("Nueva SECRET_KEY:")
    print(secret)
    print()