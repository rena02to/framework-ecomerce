import os
import sys
import shutil
import json
from pathlib import Path
import argparse

# Formas de pagamento disponíveis
PAYMENT_METHODS = ["Pix", "Boleto", "Cartão de Crédito", "Cartão de Débito"]

# Itens do framework a copiar
items_to_copy = [
    "carts_service",
    "users_service",
    "orders_service",
    "products_service",
    ".env",
    "nginx.conf",
    "docker-compose.yml",
]


def sanitize_name(name: str) -> str:
    sanitized = "".join(c if c.isalnum() or c == "_" else "_" for c in name)
    return f"svc_{sanitized}" if not sanitized.isidentifier() else sanitized


def create_project_folder(app_name: str):
    target_dir = Path("./") / app_name
    if target_dir.exists():
        print(f"⚠️ Pasta '{target_dir}' já existe. Remova-a ou use outro nome.")
        sys.exit(1)

    target_dir.mkdir()
    print(f"📂 Criada pasta do projeto: {target_dir.resolve()}")
    return target_dir


def copy_framework_items(target_dir: Path):
    framework_dir = Path(__file__).parent / "framework"

    for item in items_to_copy:
        src = framework_dir / item
        dst = target_dir / item
        if not src.exists():
            print(f"⚠️ O item '{item}' não existe no framework e será ignorado.")
            continue

        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        print(f"✅ Copiado '{item}' para '{dst}'")


def ask_payment_methods():
    active_methods = {}
    while True:
        for method in PAYMENT_METHODS:
            choice = (
                input(f"Ativar a forma de pagamento {method}? [s/N]: ").strip().lower()
            )
            active_methods[method] = choice == "s"

        if any(active_methods.values()):
            break
        else:
            print("⚠️ Você precisa ativar pelo menos uma forma de pagamento!")

    return active_methods


def save_payment_methods(target_dir: Path, active_methods: dict):
    config_file = target_dir / "payment_methods.json"
    with config_file.open("w") as f:
        json.dump(active_methods, f)
    print(f"💾 Formas de pagamento salvas em '{config_file}'")


def main():
    parser = argparse.ArgumentParser(description="Cria projeto com base no framework")
    parser.add_argument("--name", "-n", required=True, help="Nome do projeto")
    args = parser.parse_args()

    app_name = sanitize_name(args.name.strip())

    # 1️⃣ Cria a pasta do projeto
    target_dir = create_project_folder(app_name)

    # 2️⃣ Copia itens do framework
    copy_framework_items(target_dir)

    # 3️⃣ Pergunta ao usuário quais formas de pagamento ativar
    active_methods = ask_payment_methods()

    # 4️⃣ Salva essas escolhas para inicialização automática
    save_payment_methods(target_dir, active_methods)

    print("\n📦 Projeto criado com sucesso!")


if __name__ == "__main__":
    main()
