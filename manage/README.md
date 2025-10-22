# 📁 Pasta Manage - Sistema de Gerenciamento MITSID Dash

Esta pasta contém os módulos de gerenciamento de dados do sistema MITSID Dash, permitindo operações CRUD (Create, Read, Update, Delete) em todas as entidades principais do sistema.

## 🗂️ Estrutura dos Arquivos

### 📋 Arquivos Principais

| Arquivo | Descrição | Funcionalidades |
|---------|-----------|-----------------|
| `gerenciador_principal.py` | **Menu central** do sistema | Acesso unificado a todos os gerenciadores |
| `gerenciar_materiais.py` | Gestão de materiais | Visualizar, adicionar, deletar materiais |
| `gerenciar_vidros.py` | Gestão de vidros | CRUD completo para tipos de vidro |
| `gerenciar_cores.py` | Gestão de cores | Paleta de cores com códigos hex/RGB |
| `gerenciar_projetos.py` | Gestão de projetos | Controle de projetos e status |
| `gerenciar_usuarios.py` | Gestão de usuários | Usuários, perfis e autenticação |

### 📄 Arquivos de Configuração

- `__init__.py` - Configuração do pacote Python
- `README.md` - Esta documentação

## 🚀 Como Usar

### Opção 1: Menu Principal Unificado
```bash
# Execute o gerenciador principal
python manage/gerenciador_principal.py
```

### Opção 2: Gerenciadores Individuais
```bash
# Execute gerenciadores específicos
python manage/gerenciar_materiais.py
python manage/gerenciar_usuarios.py
python manage/gerenciar_projetos.py
# ... etc
```

## 🛠️ Funcionalidades por Módulo

### 🧱 Gerenciar Materiais
- ✅ Visualizar status e contagem
- ✅ Listar todos os materiais
- ✅ Deletar todos os materiais
- ✅ Deletar material específico por nome
- 🔗 Integração com `db.db_local.LocalDatabase`

### 🪟 Gerenciar Vidros
- ✅ Status e estatísticas de vidros
- ✅ Listagem completa com detalhes
- ✅ Operações de exclusão
- ✅ Navegação por ID

### 🎨 Gerenciar Cores
- ✅ Gestão de paleta de cores
- ✅ Adição de cores com códigos hex/RGB
- ✅ Sistema de descrições
- ✅ CRUD completo

### 📋 Gerenciar Projetos  
- ✅ Controle de projetos
- ✅ Sistema de status (Planejamento, Em Andamento, Concluído, etc.)
- ✅ Gestão de clientes e datas
- ✅ Alteração dinâmica de status

### 👥 Gerenciar Usuários
- ✅ Sistema completo de usuários
- ✅ Perfis: admin, gerente, usuario, visualizador
- ✅ Hash de senhas com SHA-256
- ✅ Ativação/desativação de contas
- ✅ Reset de senhas
- ✅ Controle de acesso

## 🗄️ Banco de Dados

Todos os gerenciadores utilizam **SQLite local** através da classe `LocalDatabase`:

```
📂 db/
  ├── database.db (banco principal)
  └── db_local.py (classe LocalDatabase)
```

### Tabelas Gerenciadas
- `materiais` - Materiais de construção
- `vidros` - Tipos de vidro
- `cores` - Paleta de cores
- `projetos` - Projetos de engenharia  
- `usuarios` - Usuários do sistema

## 🔒 Segurança

### Usuários e Senhas
- Senhas são hasheadas com **SHA-256**
- Validação de senha mínima (6 caracteres)
- Verificação de emails únicos
- Sistema de perfis de acesso

### Operações Críticas
- Confirmação obrigatória para exclusões em massa
- Validação de dados de entrada
- Tratamento de erros com mensagens claras

## 📋 Dependências

```python
import sys
import os
import pandas as pd
import hashlib
from datetime import datetime
from db.db_local import LocalDatabase
```

## 🎯 Integração com o Sistema Principal

Os gerenciadores são **independentes** mas **integrados**:

1. **Podem ser executados individualmente** para manutenção específica
2. **Acessíveis via menu principal** para uso unificado
3. **Compartilham a mesma base de dados** (consistência)
4. **Seguem padrões visuais** uniformes (UX/UI)

## 🆘 Solução de Problemas

### Erro: "Tabela não encontrada"
```bash
💡 Algumas tabelas são criadas automaticamente ao adicionar o primeiro registro
   Tente adicionar um item primeiro, depois gerencie os dados
```

### Erro: "Módulo não encontrado"  
```bash
💡 Verifique se está executando a partir da pasta raiz do projeto:
   cd app-mitsid-dash
   python manage/gerenciador_principal.py
```

### Erro de Importação
```bash
💡 Certifique-se que a estrutura de pastas está correta:
   app-mitsid-dash/
   ├── db/db_local.py
   └── manage/gerenciador_*.py
```

## 🔄 Atualizações Futuras

- [ ] Interface gráfica (GUI) com tkinter
- [ ] Exportação de dados para CSV/Excel
- [ ] Backup automático do banco
- [ ] Logs de auditoria
- [ ] API REST para integração externa
- [ ] Relatórios automatizados

---

> 💡 **Dica**: Use o `gerenciador_principal.py` como ponto de entrada único para uma experiência de usuário mais fluida e integrada.