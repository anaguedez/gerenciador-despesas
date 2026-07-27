# gerenciador-despesas

O Gerenciador de Despesas é uma aplicação web desenvolvida para auxiliar no controle de gastos pessoais. O objetivo é permitir que o usuário cadastre, visualize, edite e exclua despesas de forma simples, além de acompanhar informações financeiras por meio de um painel com indicadores.

O projeto foi desenvolvido utilizando Python no backend, Flask como framework web, SQLite para armazenamento dos dados e HTML, CSS e Bootstrap para construção da interface.

## Tecnologias utilizadas

- **Python**: linguagem principal do projeto.
- **Flask**: framework responsável pelas rotas, processamento das requisições e comunicação entre a interface e o banco de dados.
- **SQLite**: banco de dados utilizado para armazenar as despesas.
- **HTML**: estrutura das páginas.
- **CSS**: personalização do layout.
- **Bootstrap 5**: componentes e responsividade.
- **Jinja2**: mecanismo de templates do Flask para exibir os dados do banco nas páginas HTML.

## Estrutura do projeto
├── app.py
├── banco.py
├── despesas.db
│
├── templates/
│   ├── index.html
│   └── editar.html
│
├── static/
│   ├── style.css
│   └── script.js
