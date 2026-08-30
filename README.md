# 🏥 Internações do SUS em São Paulo — OCI + Select AI

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B)
![OCI](https://img.shields.io/badge/Oracle-Cloud%20Infrastructure-red)
![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)

Trabalho do curso tecnólogo em Ciência de Dados. Extrai dados de internações
hospitalares do estado de São Paulo (SIH/DataSUS), trata e carrega no **Oracle
Cloud Infrastructure (OCI)**, e responde perguntas analíticas usando o recurso
**Select AI** do Autonomous Database, além de um dashboard local em Streamlit.

---

## 📋 Sumário

- [Perguntas respondidas](#-perguntas-respondidas)
- [Estrutura do repositório](#-estrutura-do-repositório)
- [Como rodar](#-como-rodar)
- [Fonte dos dados](#-fonte-dos-dados)
- [Limitações conhecidas](#-limitações-conhecidas)

---

## ❓ Perguntas respondidas

| # | Pergunta |
|---|---|
| 1 | Quais municípios tiveram maior aumento de internações no último período? |
| 2 | Quais hospitais têm permanência média acima da média estadual? |
| 3 | Compare internações e leitos disponíveis por região de saúde. |

---

## 📁 Estrutura do repositório

```
extracao/   → script de tratamento dos dados brutos do SIH/CNES
dados/      → CSVs tratados, prontos para análise e carga no banco
dashboard/  → dashboard local em Streamlit
oci/        → script de carga direto no Oracle Autonomous Database
```

---

## 🚀 Como rodar

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Tratamento dos dados

```bash
cd extracao
python tratamento.py
```

### 3. Dashboard local (Streamlit)

```bash
cd dashboard
streamlit run dashboard_internacoes.py
```

> No Windows, também é possível usar `dashboard/abrir_dashboard.bat` (duplo clique — instala tudo e abre sozinho).

### 4. Carga no OCI Autonomous Database

> ⚠️ Requer o **Wallet** de conexão baixado do console OCI (não incluído no repositório por segurança — veja `.gitignore`).

```bash
cd oci
python extrai_carrega_datasus_oci.py
```

---

## 📊 Fonte dos dados

- **Sistema de Informações Hospitalares (SIH)**, via TabNet/DataSUS
- Extração automatizada com a biblioteca [PySUS](https://github.com/AlertaDengue/PySUS)
- **Estado:** São Paulo (SP)

---

## ⚠️ Limitações conhecidas

- Coluna original `DIAS_PERM` do SIH vem zerada — permanência recalculada pela diferença entre data de saída e data de internação
- ~54% das internações não têm dados demográficos completos (município, sexo, idade) — provavelmente registros de AIH de continuação
- Municípios identificados por código IBGE — tabela de nomes ainda não cruzada
- `REGSAUDE` representa **Região de Saúde** (subdivisão dentro dos 17 DRS do estado), não o DRS em si
