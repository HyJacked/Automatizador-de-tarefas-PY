# 🤖 Automatizador de Tarefas Repetitivas

Script de linha de comando em Python para automatizar tarefas repetitivas do
dia a dia: organizar arquivos, renomear em lote, criar backups e limpar
arquivos antigos. Não depende de nenhuma biblioteca externa para funcionar.

## ✨ Funcionalidades

- **`organize`** — organiza os arquivos de uma pasta em subpastas por categoria
  (Imagens, Documentos, Planilhas, Vídeos, etc.)
- **`rename`** — renomeia arquivos em lote com prefixo, sufixo e numeração
- **`backup`** — cria um backup `.zip` com timestamp de um arquivo ou pasta
- **`clean`** — remove arquivos mais antigos que N dias (com filtro por extensão)
- **`--repetir MINUTOS`** — disponível em `organize` e `backup`, executa a
  tarefa periodicamente, útil para deixar rodando em segundo plano
- **`--simular`** — modo "dry run": mostra o que seria feito sem alterar nada

## 📦 Instalação

```bash
git clone https://github.com/SEU_USUARIO/automatizador-tarefas.git
cd automatizador-tarefas
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt   # opcional, só para rodar os testes
```

O script em si (`automatizador.py`) não precisa de instalação de pacotes,
apenas do Python 3.10+.

## 🚀 Uso

```bash
# Organizar a pasta de Downloads por tipo de arquivo
python automatizador.py organize ~/Downloads

# Simular antes de aplicar de verdade
python automatizador.py organize ~/Downloads --simular

# Renomear fotos em lote: ferias_1.jpg, ferias_2.jpg, ...
python automatizador.py rename ./fotos --prefixo ferias_ --inicio 1

# Criar backup .zip de um projeto
python automatizador.py backup ./meu_projeto ./backups

# Remover arquivos temporários com mais de 15 dias
python automatizador.py clean ./tmp --dias 15 --extensoes .tmp .log

# Organizar Downloads automaticamente a cada 30 minutos
python automatizador.py organize ~/Downloads --repetir 30
```

Use `python automatizador.py <comando> --help` para ver todas as opções de
cada subcomando.

## 🧪 Testes

```bash
pip install -r requirements.txt
pytest tests/ -v
```

## 📁 Estrutura do projeto

```
automatizador-tarefas/
├── automatizador.py       # script principal
├── tests/
│   └── test_automatizador.py
├── requirements.txt
├── .gitignore
└── README.md
```

## 📝 Licença

Este projeto está sob a licença MIT — sinta-se à vontade para usar e adaptar.
