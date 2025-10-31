import os
import sys
import shutil
import json
from pathlib import Path
import argparse
import re

# Formas de pagamento disponíveis
PAYMENT_METHODS = ["Pix", "Boleto", "Cartão de Crédito", "Cartão de Débito"]

# Itens do framework a copiar
items_to_copy = [
    "carts_service",
    "users_service",
    "orders_service",
    "products_service",
    "recommendations_service",
    ".env",
    "nginx.conf",
    "docker-compose.yml",
]


def configure_product_view_filters(target_dir, filter_title, filter_description):
    views_file = target_dir / "products_service" / "products" / "views.py"
    views_file.parent.mkdir(parents=True, exist_ok=True)

    with open(views_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Captura o bloco original e a indentação antes do "if query"
    pattern = r"""
        (?P<indent>\s*)if\ query:\s*\n
        (?:\s*filters\s*&=\s*Q\(categories__value__icontains=query\)\s*\n)?
        (?:\s*filters\s*&=\s*Q\(name__icontains=query\)\s*\n)?
        (?:\s*filters\s*&=\s*Q\(description__icontains=query\)\s*\n)?
    """

    # Constrói o novo bloco mantendo a indentação capturada
    def replace_block(match):
        indent = match.group("indent")
        new = f"{indent}if query:\n"
        new += f"{indent}    filters &= Q(categories__value__icontains=query)\n"

        if filter_title:
            new += f"{indent}    filters &= Q(name__icontains=query)\n"
        if filter_description:
            new += f"{indent}    filters &= Q(description__icontains=query)\n"

        return new

    content = re.sub(pattern, replace_block, content, flags=re.VERBOSE)

    with open(views_file, "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Filtros configurados com sucesso!")


def save_recommendation_views(target_dir, active_urls):
    """
    Gera o arquivo views.py com apenas as classes de recomendação selecionadas.
    """
    views_file = target_dir / "recommendations_service" / "recomendations" / "views.py"
    views_file.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "from rest_framework.views import APIView\n",
        "from rest_framework.response import Response\n",
        "from rest_framework import status\n",
        "from .simple import recommend_by_category\n",
        "from recommendations_service.utils.requests import call_service\n",
        "import random\n\n",
    ]

    # Última compra
    if active_urls.get("last_purchase"):
        lines.append(
            """class RecomendationLastPurchaseView(APIView):
    def get(self, request):
        access_token = request.COOKIES.get("access_token")
        last_product = None
        if access_token:
            last_product_data = call_service(
                "http://nginx_gateway:8000/api/orders/last/", access_token
            )
            if last_product_data["status_code"] == 200:
                last_product = last_product_data.get("data").get("data")
        if not access_token or not last_product:
            avaliable_products = call_service(
                "http://nginx_gateway:8000/api/products/avaliable_products/", None
            )
            if avaliable_products["status_code"] == 200:
                last_product = random.choice(avaliable_products.get("data").get("data"))
        return recommend_by_category(self, request, last_product)\n\n"""
        )

    # Último item do carrinho
    if active_urls.get("last_add_cart"):
        lines.append(
            """class RecomendationLastAddCartView(APIView):
    def get(self, request):
        access_token = request.COOKIES.get("access_token")
        last_product = None
        if access_token:
            last_product_data = call_service(
                "http://nginx_gateway:8000/api/carts/last/", access_token
            )
            if last_product_data["status_code"] == 200:
                last_product = last_product_data.get("data").get("data")
        if not access_token or not last_product:
            avaliable_products = call_service(
                "http://nginx_gateway:8000/api/products/avaliable_products/", None
            )
            if avaliable_products["status_code"] == 200:
                last_product = random.choice(avaliable_products.get("data").get("data"))
        return recommend_by_category(self, request, last_product)\n"""
        )

    with views_file.open("w") as f:
        f.writelines(lines)

    print(f"💾 Views de recomendação salvas em '{views_file}'")


def save_recommendation_urls(target_dir, active_urls):
    urls_file = target_dir / "urls.py"

    lines = ["from django.urls import path\n"]

    # Condicionalmente adiciona o import das views
    imports = []
    if active_urls.get("last_purchase"):
        imports.append("RecomendationLastPurchaseView")
    if active_urls.get("last_add_cart"):
        imports.append("RecomendationLastAddCartView")

    if imports:
        lines.append("from .views import (\n")
        for view in imports:
            lines.append(f"    {view},\n")
        lines.append(")\n\n")

    # Cria a lista de urlpatterns
    lines.append("urlpatterns = [\n")
    if active_urls.get("last_purchase"):
        lines.append(
            '    path("last_purchase/", RecomendationLastPurchaseView.as_view()),\n'
        )
    if active_urls.get("last_add_cart"):
        lines.append(
            '    path("last_add_cart/", RecomendationLastAddCartView.as_view()),\n'
        )
    lines.append("]\n")

    with urls_file.open("w") as f:
        f.writelines(lines)

    print(f"💾 URLs de recomendação salvas em '{urls_file}'")


def sanitize_name(name):
    sanitized = "".join(c if c.isalnum() or c == "_" else "_" for c in name)
    return f"svc_{sanitized}" if not sanitized.isidentifier() else sanitized


def create_project_folder(app_name):
    target_dir = Path("./") / app_name
    if target_dir.exists():
        print(f"⚠️ Pasta '{target_dir}' já existe. Remova-a ou use outro nome.")
        sys.exit(1)

    target_dir.mkdir()
    print(f"📂 Criada pasta do projeto: {target_dir.resolve()}")
    return target_dir


def copy_framework_items(target_dir):
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


def ask_recommendations_urls():
    active_urls = {}
    print("\n🛒 Configuração de recomendações:")
    active_urls["last_purchase"] = (
        input("Ativar recomendação de Última Compra? [s/N] (padrão N): ")
        .strip()
        .lower()
        == "s"
    )
    active_urls["last_add_cart"] = (
        input("Ativar recomendação de Último Item do Carrinho? [s/N] (padrão N): ")
        .strip()
        .lower()
        == "s"
    )

    return active_urls


def ask_payment_methods():
    active_methods = {}
    while True:
        for method in PAYMENT_METHODS:
            choice = (
                input(f"Ativar a forma de pagamento {method}? [S/N] (padrão N): ")
                .strip()
                .lower()
            )
            active_methods[method] = choice.lower() == "s"

        if any(active_methods.values()):
            break
        else:
            print("⚠️ Você precisa ativar pelo menos uma forma de pagamento!")

    return active_methods


def ask_product_filters():
    print("\n🔍 Configuração de filtros da ProductView:")
    filter_title = (
        input("Filtrar por título? [s/N] (padrão N): ").strip().lower() == "s"
    )
    filter_description = (
        input("Filtrar por descrição? [s/N] (padrão N): ").strip().lower() == "s"
    )
    return filter_title, filter_description


def save_payment_methods(target_dir, active_methods):
    config_file = target_dir / "payment_methods.json"
    with config_file.open("w") as f:
        json.dump(active_methods, f)
    print(f"💾 Formas de pagamento salvas em '{config_file}'")


def main():
    parser = argparse.ArgumentParser(description="Cria projeto com base no framework")
    parser.add_argument("--name", "-n", required=True, help="Nome do projeto")
    args = parser.parse_args()

    app_name = sanitize_name(args.name.strip())

    # Cria a pasta do projeto
    target_dir = create_project_folder(app_name)

    # Copia itens do framework
    copy_framework_items(target_dir)

    # Pergunta ao usuário quais formas de pagamento ativar
    active_methods = ask_payment_methods()

    # Salva essas escolhas para inicialização automática
    save_payment_methods(target_dir, active_methods)

    #  Pergunta ao usuário quais URLs de recomendação ativar
    active_urls = ask_recommendations_urls()

    # Configura URLs de recomendação
    save_recommendation_urls(
        target_dir,
        active_urls,
    )

    # Configura Views de recomendação
    save_recommendation_views(
        target_dir,
        active_urls,
    )

    # Pergunta ao usuário quais filtros da ProductView ativar
    filter_title, filter_description = ask_product_filters()

    # Configura a ProductView com os filtros escolhidos
    configure_product_view_filters(target_dir, filter_title, filter_description)

    print("\n📦 Projeto criado com sucesso!")


if __name__ == "__main__":
    main()
