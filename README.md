# Nome do Projeto

Este projeto utiliza uma arquitetura de microsserviços baseada em Linha de Produto de Software (LPS) para gerar uma aplicação de backend customizada.

Este guia fornece as instruções diretas para gerar e executar o backend.

## Pré-requisitos

Para executar este projeto, você precisará ter os seguintes softwares instalados:

* Git
* Python (3.10 ou superior)
* Docker
* Docker Compose

## Como Rodar

Siga este passo a passo para configurar e iniciar os serviços.

### 1. Clonar o Repositório

Primeiro, clone este repositório para sua máquina local.

```bash
git clone <url-do-seu-repositorio>
```

### 2. Acessar a Pasta do Gerador
Entre na pasta do repositório que você acabou de clonar.

```bash
cd <nome-da-pasta-do-repositorio>
```

### 3. Executar o Script de Geração
Use o script create_app.py para gerar a estrutura base do seu projeto. Substitua <nome-do-projeto> pelo nome que você deseja usar.

```bash
python create_app.py --name <nome-do-projeto>
```

### 4. Responder aos Prompts
O script fará uma série de perguntas na linha de comando para definir quais microsserviços e funcionalidades serão incluídos na sua aplicação. Responda s (sim) ou n (não) para cada funcionalidade.

### 5. Acessar o Projeto Gerado
Após o script finalizar, acesse a nova pasta do projeto que foi criada.

```bash
cd <nome-do-projeto>
```

### 6. Configurar o Ambiente
Antes de iniciar, pode ser necessário realizar configurações específicas (ex: definir chaves de API, ajustar portas ou configurar bancos de dados).

Verifique os arquivos .env dentro das pastas de cada microsserviço (ex: users_service/.env, products_service/.env, etc.) e substitua as variáveis de ambiente necessárias.

### 7. Subir os Contêineres
Com o Docker em execução na sua máquina, utilize o Docker Compose para construir as imagens e iniciar todos os microsserviços.

Não podem haver serviços rodando nas portas 8000 à 8006

```bash
docker-compose up --build -d
```

Após os contêineres iniciarem, o Nginx (gateway) estará disponível em http://localhost:8000, roteando as requisições para os microsserviços apropriados (ex: http://localhost:8000/api/users/, http://localhost:8000/api/products/, etc.).

### 8. Criar Superusuários (Opcional)
Para acessar a interface do Django Admin de cada microsserviço (para depuração ou gerenciamento manual), você precisa criar um superusuário para cada um.

Com os contêineres em execução, abra novos terminais e execute os seguintes comandos para cada serviço que necessitar de um admin.

Exemplo com o serviço de Usuários:
```bash
docker-compose exec users_service python manage.py createsuperuser
```

Exemplo com o serviço de Produtos:
```bash
docker-compose exec products_service python manage.py createsuperuser
```

### Sobre o Front-end
Este projeto não inclui um front-end. Ele gera apenas a API de backend. O desenvolvimento da aplicação de interface (seja web ou mobile) é de responsabilidade do implementador e deve consumir a API que agora está em execução.

