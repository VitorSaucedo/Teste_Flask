# Lista de Tarefas (Todo List)

Uma aplicação web completa para gerenciamento de tarefas desenvolvida com Flask. Este sistema oferece uma interface intuitiva e funcionalidades avançadas para organizar suas atividades diárias de forma eficiente.

## Funcionalidades

- **Autenticação de Usuários**: Sistema completo de registro, login e gerenciamento de perfil
- **Tarefas**: Adicionar, editar, concluir e excluir tarefas
- **Subtarefas**: Criar e gerenciar itens subordinados a uma tarefa principal
- **Categorias**: Organizar tarefas por categorias personalizáveis 
- **Prioridades**: Definir níveis de prioridade (Alta, Média, Baixa)
- **Datas de Vencimento**: Estabelecer prazos para conclusão das tarefas
- **Tags**: Adicionar etiquetas para facilitar a busca e organização
- **Descrições**: Incluir detalhes adicionais para cada tarefa
- **Filtragem**: Filtrar tarefas por categoria, prioridade e status
- **Pesquisa**: Buscar tarefas específicas por conteúdo, descrição ou tags
- **Estatísticas**: Visualizar dados sobre suas tarefas e taxa de conclusão
- **Tema Escuro/Claro**: Alternar entre os temas conforme preferência
- **Indicadores Visuais**: Destaque para tarefas de alta prioridade e atrasadas
- **Interface Responsiva**: Compatível com dispositivos móveis e desktop

## Tecnologias Utilizadas

- **Backend**:
  - Python 3
  - Flask
  - SQLAlchemy (ORM)
  - Flask-Login (Autenticação)
  - Werkzeug (Segurança e utilitários)
- **Banco de Dados**:
  - SQLite
- **Frontend**:
  - Bootstrap 5
  - Chart.js (Visualização de dados)
  - Font Awesome (Ícones)
  - HTML/CSS/JavaScript

## Requisitos

- Python 3.8 ou superior
- Pacotes Python listados em `requirements.txt`

## Instalação

1. Clone este repositório
2. Crie e ative um ambiente virtual (recomendado):
   ```
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```
3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
4. Execute a aplicação:
   ```
   python app.py
   ```
5. Acesse http://localhost:5000 no seu navegador

## Estrutura do Projeto

- `app.py`: Aplicação principal Flask (rotas, modelos e lógica de negócio)
- `create_db.py`: Script para criação inicial do banco de dados
- `requirements.txt`: Lista de dependências do projeto
- `templates/`: Diretório contendo os templates HTML
  - `base.html`: Template base com layout comum
  - `index.html`: Página principal com a lista de tarefas
  - `update.html`: Página para editar tarefas
  - `login.html`: Página de login
  - `register.html`: Página de registro de usuários
  - `profile.html`: Página de perfil do usuário
  - `statistics.html`: Página de estatísticas e gráficos
  - `_task_item.html`: Componente de item de tarefa
  - `_task_list.html`: Componente de lista de tarefas
- `static/`: Diretório contendo arquivos estáticos (CSS, JS, imagens)
- `instance/`: Diretório contendo arquivos de instância da aplicação
- `todo.db`: Banco de dados SQLite para armazenamento dos dados

## Modelos de Dados

- **User**: Usuários do sistema com autenticação
- **Todo**: Tarefas principais com propriedades como título, descrição, categoria, etc.
- **Subtask**: Subtarefas vinculadas às tarefas principais

## Futuras Melhorias

- Integração com calendário para visualização de tarefas
- Notificações e lembretes de tarefas próximas do vencimento
- Compartilhamento de tarefas entre usuários
- Sincronização com dispositivos móveis
- API completa para integração com outros sistemas

## Licença

Este projeto está licenciado sob a licença MIT. 