Financial Data Integration System
📋 Descrição
Sistema acadêmico de integração de dados financeiros que demonstra um pipeline completo de ETL (Extract, Transform, Load). O projeto implementa boas práticas de engenharia de dados para extração eficiente de uma API externa, processamento inteligente e armazenamento otimizado em SQL Server.
🎯 Objetivo Acadêmico
Este projeto foi desenvolvido para demonstrar conhecimentos em:

Integração de APIs com tratamento de paginação
Otimização de consultas com cargas incrementais
Gestão inteligente de dados evitando redundâncias
Arquitetura de software com separação de responsabilidades
Boas práticas de desenvolvimento Python

🚀 Funcionalidades e Boas Práticas Implementadas
🔄 Carga Incremental Inteligente

Detecção automática: Sistema identifica se é primeira execução ou atualização
Janela de atualização: Busca apenas últimos 2 dias em atualizações
Economia de recursos: Evita reprocessar dados já existentes

📡 Otimização de API

Paginação eficiente: Processa dados em lotes de 100 registros
Rate limiting: Implementa delay entre requisições (1 segundo)
Filtros inteligentes: Usa constraints para buscar apenas dados necessários
Tratamento de erros: Controla falhas de conectividade

🗃️ Gestão Inteligente do Banco

Verificação de existência: Checa se tabela existe antes de decidir tipo de carga
Prevenção de duplicatas: Ignora registros já existentes usando chave primária
Tipos de dados otimizados: Define precisão adequada para campos monetários
Conexão segura: Usa pool de conexões SQLAlchemy

🛡️ Robustez e Confiabilidade

Tratamento de integridade: Captura e ignora violações de chave primária
Validação de dados: Converte datas com tratamento de erros
Limpeza de recursos: Fecha conexões adequadamente
Feedback em tempo real: Informa progresso e resultados

🛠️ Tecnologias Utilizadas

Python 3.8+
SQLAlchemy - ORM para banco de dados
Pandas - Manipulação e análise de dados
Requests - Cliente HTTP otimizado
SQL Server - Banco de dados relacional
python-dotenv - Gestão segura de credenciais

📁 Arquitetura do Sistema
financial-integration/
├── src/
│   ├── main.py                 # Orquestrador principal
│   ├── api/
│   │   └── client.py          # Cliente API com paginação
│   ├── database/
│   │   ├── connection.py      # Gestão de conexões
│   │   └── models.py          # Modelos de dados
│   └── utils/
│       └── data_processor.py  # Processamento de dados
├── config/
│   └── .env.example          # Template de configuração
├── requirements.txt
└── README.md
⚙️ Fluxo de Execução
1️⃣ Primeira Execução (Carga Inicial)
Verificar tabela → Não existe → Criar tabela → Buscar todos os dados → Processar → Inserir
2️⃣ Execuções Subsequentes (Carga Incremental)
Verificar tabela → Existe → Buscar últimos 2 dias → Processar → Inserir novos
3️⃣ Otimizações Implementadas

✅ Evita consultas desnecessárias à API
✅ Processa apenas dados novos/alterados
✅ Previne duplicação de dados
✅ Minimiza uso de recursos do sistema
