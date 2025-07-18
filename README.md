
# Corteus - Gestor de Cortes para Manufatura

Sistema web para otimização de cortes de materiais, com backend em FastAPI.

## Funcionalidades

- **API RESTful**: Backend robusto em FastAPI para gerenciamento de cortes, projetos e relatórios
- **Autenticação**: Sistema de autenticação de usuários
- **Geração de Relatórios**: Exportação de resultados em PDF
- **Dashboard Analítico**: Visualização de dados e relatórios
- **Serviços Modulares**: Organização em módulos para cortes, relatórios, autenticação e integrações
- **Interface Web**: Templates HTML responsivos e tema escuro

## Estrutura do Projeto

- `corteus-fastapi/app/` - Código principal do backend (rotas, modelos, serviços, templates)
- `corteus-fastapi/Modulação/` - Lógica de cortes, utilitários e geração de PDFs
- `corteus-fastapi/static/` - Arquivos estáticos (CSS, JS, imagens)
- `corteus-fastapi/templates/` - Templates HTML

## Deploy

Projeto pronto para deploy no Render.

### Requisitos

- Python 3.9+
- FastAPI
- Uvicorn
- Jinja2
- ReportLab
- Pillow

Instale as dependências:

```bash
pip install -r corteus-fastapi/requirements.txt
```

## Desenvolvimento Local

Execute o backend localmente:

```bash
cd corteus-fastapi
uvicorn app.main:app --reload
```

Acesse a documentação interativa em: [http://localhost:8000/docs](http://localhost:8000/docs)

## Autor

Desenvolvido por MatheusANBS
