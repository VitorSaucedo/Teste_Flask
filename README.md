# Lista de Tarefas (Todo List)

Uma aplicação completa de lista de tarefas desenvolvida com Flask, proporcionando diversas funcionalidades para gerenciar suas tarefas de forma eficiente.

## Funcionalidades

- **Tarefas**: Adicionar, editar, concluir e excluir tarefas
- **Categorias**: Organizar tarefas por categorias personalizáveis
- **Prioridades**: Definir prioridades (Alta, Média, Baixa) para tarefas
- **Datas de Vencimento**: Estabelecer prazos para conclusão
- **Tags**: Adicionar etiquetas para facilitar a busca e organização
- **Descrições**: Incluir detalhes adicionais para cada tarefa
- **Filtragem**: Filtrar tarefas por categoria e prioridade
- **Pesquisa**: Buscar tarefas específicas por conteúdo, descrição ou tags
- **Estatísticas**: Visualizar dados sobre suas tarefas e taxa de conclusão
- **Tema Escuro/Claro**: Alternar entre os temas conforme preferência
- **Indicadores Visuais**: Destaque para tarefas de alta prioridade e atrasadas
- **Interface Responsiva**: Compatível com dispositivos móveis e desktop

## Tecnologias Utilizadas

- Python 3
- Flask
- SQLAlchemy
- SQLite
- Bootstrap 5
- Chart.js
- Font Awesome
- HTML/CSS/JavaScript

## Requisitos

- Python 3.8 ou superior
- Pacotes listados em requirements.txt

## Instalação

1. Clone este repositório
2. Crie e ative um ambiente virtual (opcional):
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

- `app.py`: Arquivo principal da aplicação Flask com rotas e modelo de dados
- `templates/`: Diretório contendo os templates HTML
  - `base.html`: Template base com layout comum
  - `index.html`: Página principal com a lista de tarefas
  - `update.html`: Página para editar tarefas
  - `statistics.html`: Página de estatísticas e gráficos
- `static/`: Diretório contendo arquivos estáticos
  - `style.css`: Estilos CSS da aplicação
  - `theme.js`: JavaScript para alternar entre temas claro/escuro
- `todo.db`: Banco de dados SQLite para armazenamento das tarefas

## Futuras Melhorias

- Sistema de autenticação de usuários
- Subtarefas
- Sincronização com calendário
- Notificações e lembretes
- Aplicativo móvel

## Licença

Este projeto está licenciado sob a licença MIT. 