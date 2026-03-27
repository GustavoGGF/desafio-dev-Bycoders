## Sistema de Importação de Arquivos CNAB
Este projeto é uma solução Fullstack para o processamento, persistência e visualização de dados provenientes de arquivos CNAB (largura fixa). A aplicação utiliza uma arquitetura moderna focada em performance e experiência do usuário (UX).

## Tecnologias Utilizadas
- **Backend**: Python 3.11+ com FastAPI.

- **Banco de Dados**: PostgreSQL 15 (executando em container).

- **Frontend**: HTML5, CSS3, HTMX (para reatividade sem SPAs pesadas).

- **ORM**: SQLAlchemy com suporte a sessões e transações.

- **Containerização**: Docker e Docker Compose.

- **Segurança**: Autenticação com JWT (JSON Web Tokens).

## Funcionalidades
Segurança: Proteção de rotas e autenticação via JWT.

Upload Eficiente: Parse de arquivos de largura fixa linha a linha (Memory Efficient) usando Generators.

Persistência Atômica: Inserção de dados em lote (Batch) com Rollback automático em caso de falha de integridade.

Dashboard Dinâmica: Visualização de transações com atualização em tempo real via HTMX.

Documentação Automática: Swagger UI disponível nativamente pelo FastAPI.

## Como Executar o Projeto
Pré-requisitos
Docker e Docker Compose instalados.

Passo a Passo
Clonar o repositório:

git clone [https://github.com/GustavoGGF/desafio-dev-Bycoders]
cd desafio-dev-Bycoders

docker-compose -f docker-compose-desafio.yml up --build

Acessar a Aplicação:

**Interface**: http://localhost:8000

**Documentação API**: http://localhost:8000/docs

Auditoria e Manutenção (PSQL)
Caso precise validar os dados diretamente no banco de dados:

Acessar o Banco:

Bash
docker exec -it cnab_db_container psql -U postgres -d cnab_db

Consultar Dados:
SELECT * FROM transacoes LIMIT 10;

## Arquitetura de Software
O projeto foi desenhado para ser resiliente:

Frontend Reativo: O uso do HTMX permite que o formulário de upload limpe os campos automaticamente e atualize a tabela de resultados via disparos de eventos (htmx:afterRequest), sem necessidade de recarregar a página.

Integridade de Dados: A função post_all_transactions garante que, se houver um erro no meio do processamento de um lote, o banco realize um rollback completo, evitando dados parciais ou "sujos".

Rede Isolada: O Docker Compose gerencia uma rede interna (cnab_network) onde o FastAPI e o Postgres se comunicam com segurança, expondo apenas as portas necessárias para o host.