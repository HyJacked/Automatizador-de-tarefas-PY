#!/usr/bin/env python3
"""
Automatizador de Tarefas Repetitivas
=====================================
Utilitário de linha de comando para automatizar tarefas repetitivas comuns:
organização de arquivos por tipo, renomeação em lote, backups em .zip e
limpeza de arquivos antigos. Também suporta execução periódica (repetir a
cada N minutos), útil para deixar rodando em segundo plano.

Uso rápido:
    python automatizador.py organize ~/Downloads
    python automatizador.py rename ./fotos --prefixo ferias_ --inicio 1
    python automatizador.py backup ./meu_projeto ./backups
    python automatizador.py clean ./tmp --dias 15 --extensoes .tmp .log

Use --help em qualquer subcomando para ver todas as opções.
"""

import argparse
import logging
import os
import shutil
import sys
import time
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

# ---------- Configuração de logging ----------


def configurar_logging(verbose: bool = False) -> None:
    nivel = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=nivel,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("automatizador.log", encoding="utf-8"),
        ],
    )


logger = logging.getLogger(__name__)

# ---------- Mapeamento de categorias de arquivos ----------

CATEGORIAS = {
    "Imagens": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
    "Documentos": [".pdf", ".doc", ".docx", ".txt", ".odt", ".rtf"],
    "Planilhas": [".xls", ".xlsx", ".csv"],
    "Apresentacoes": [".ppt", ".pptx"],
    "Compactados": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Audio": [".mp3", ".wav", ".flac", ".m4a"],
    "Video": [".mp4", ".mkv", ".avi", ".mov"],
    "Executaveis": [".exe", ".msi", ".sh", ".bat"],
    "Codigo": [".py", ".js", ".html", ".css", ".java", ".c", ".cpp", ".json"],
}


def obter_categoria(extensao: str) -> str:
    extensao = extensao.lower()
    for categoria, extensoes in CATEGORIAS.items():
        if extensao in extensoes:
            return categoria
    return "Outros"


def evitar_conflito(caminho: Path) -> Path:
    """Se já existir um arquivo com o mesmo nome, adiciona um sufixo numérico."""
    if not caminho.exists():
        return caminho
    base, ext = caminho.stem, caminho.suffix
    contador = 1
    novo = caminho
    while novo.exists():
        novo = caminho.with_name(f"{base}_{contador}{ext}")
        contador += 1
    return novo


# ---------- Comando: organize ----------


def organizar_arquivos(diretorio: str, simular: bool = False) -> None:
    caminho = Path(diretorio)
    if not caminho.is_dir():
        logger.error("Diretório não encontrado: %s", diretorio)
        return

    total = 0
    for item in sorted(caminho.iterdir()):
        if item.is_file():
            categoria = obter_categoria(item.suffix)
            pasta_destino = caminho / categoria
            if not simular:
                pasta_destino.mkdir(exist_ok=True)
                destino = evitar_conflito(pasta_destino / item.name)
                shutil.move(str(item), str(destino))
            logger.info("%s -> %s/%s", item.name, categoria, item.name)
            total += 1

    logger.info("Organização concluída. %d arquivo(s) processado(s).", total)


# ---------- Comando: rename ----------


def renomear_em_lote(
    diretorio: str,
    prefixo: str = "",
    sufixo: str = "",
    iniciar_em: int = 1,
    simular: bool = False,
) -> None:
    caminho = Path(diretorio)
    if not caminho.is_dir():
        logger.error("Diretório não encontrado: %s", diretorio)
        return

    arquivos = sorted(f for f in caminho.iterdir() if f.is_file())
    contador = iniciar_em

    for arquivo in arquivos:
        novo_nome = f"{prefixo}{contador}{sufixo}{arquivo.suffix}"
        novo_caminho = evitar_conflito(arquivo.with_name(novo_nome))
        if not simular:
            arquivo.rename(novo_caminho)
        logger.info("%s -> %s", arquivo.name, novo_caminho.name)
        contador += 1

    logger.info("Renomeação concluída. %d arquivo(s) processado(s).", len(arquivos))


# ---------- Comando: backup ----------


def criar_backup(origem: str, destino: str) -> None:
    caminho_origem = Path(origem)
    if not caminho_origem.exists():
        logger.error("Origem não encontrada: %s", origem)
        return

    Path(destino).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_zip = f"{caminho_origem.name}_backup_{timestamp}.zip"
    caminho_zip = Path(destino) / nome_zip

    with zipfile.ZipFile(caminho_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        if caminho_origem.is_file():
            zipf.write(caminho_origem, caminho_origem.name)
        else:
            for arquivo in caminho_origem.rglob("*"):
                if arquivo.is_file():
                    zipf.write(arquivo, arquivo.relative_to(caminho_origem.parent))

    tamanho_mb = caminho_zip.stat().st_size / (1024 * 1024)
    logger.info("Backup criado: %s (%.2f MB)", caminho_zip, tamanho_mb)


# ---------- Comando: clean ----------


def limpar_arquivos_antigos(
    diretorio: str,
    dias: int = 30,
    extensoes: list | None = None,
    simular: bool = False,
) -> None:
    caminho = Path(diretorio)
    if not caminho.is_dir():
        logger.error("Diretório não encontrado: %s", diretorio)
        return

    limite = datetime.now() - timedelta(days=dias)
    total = 0
    espaco_liberado = 0

    for arquivo in caminho.rglob("*"):
        if not arquivo.is_file():
            continue
        if extensoes and arquivo.suffix.lower() not in extensoes:
            continue

        modificado = datetime.fromtimestamp(arquivo.stat().st_mtime)
        if modificado < limite:
            tamanho = arquivo.stat().st_size
            if not simular:
                arquivo.unlink()
            logger.info("Removido: %s (modificado em %s)", arquivo, modificado.date())
            total += 1
            espaco_liberado += tamanho

    logger.info(
        "Limpeza concluída. %d arquivo(s) removido(s), %.2f MB liberados.",
        total,
        espaco_liberado / (1024 * 1024),
    )


# ---------- Execução periódica ----------


def executar_periodicamente(funcao, intervalo_minutos: int, *args, **kwargs) -> None:
    logger.info(
        "Iniciando execução periódica a cada %d minuto(s). Pressione Ctrl+C para parar.",
        intervalo_minutos,
    )
    try:
        while True:
            funcao(*args, **kwargs)
            time.sleep(intervalo_minutos * 60)
    except KeyboardInterrupt:
        logger.info("Execução periódica interrompida pelo usuário.")


# ---------- CLI ----------


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="automatizador",
        description="Automatizador de Tarefas Repetitivas - organize, renomeie, "
        "faça backup e limpe arquivos automaticamente.",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Exibe logs detalhados (debug)")
    subparsers = parser.add_subparsers(dest="comando", required=True)

    p_organize = subparsers.add_parser("organize", help="Organiza arquivos de um diretório por categoria")
    p_organize.add_argument("diretorio", help="Caminho do diretório a organizar")
    p_organize.add_argument("--simular", action="store_true", help="Mostra o que seria feito sem alterar nada")
    p_organize.add_argument("--repetir", type=int, metavar="MINUTOS", help="Executa repetidamente a cada N minutos")

    p_rename = subparsers.add_parser("rename", help="Renomeia arquivos em lote")
    p_rename.add_argument("diretorio", help="Caminho do diretório")
    p_rename.add_argument("--prefixo", default="", help="Prefixo do novo nome")
    p_rename.add_argument("--sufixo", default="", help="Sufixo do novo nome")
    p_rename.add_argument("--inicio", type=int, default=1, help="Número inicial da numeração")
    p_rename.add_argument("--simular", action="store_true")

    p_backup = subparsers.add_parser("backup", help="Cria um backup .zip de um arquivo ou pasta")
    p_backup.add_argument("origem", help="Arquivo ou pasta de origem")
    p_backup.add_argument("destino", help="Pasta onde salvar o backup")
    p_backup.add_argument("--repetir", type=int, metavar="MINUTOS")

    p_clean = subparsers.add_parser("clean", help="Remove arquivos mais antigos que N dias")
    p_clean.add_argument("diretorio", help="Caminho do diretório")
    p_clean.add_argument("--dias", type=int, default=30, help="Idade mínima em dias para remoção")
    p_clean.add_argument("--extensoes", nargs="*", help="Filtrar por extensões, ex: .tmp .log")
    p_clean.add_argument("--simular", action="store_true")

    return parser


def main() -> None:
    parser = construir_parser()
    args = parser.parse_args()
    configurar_logging(args.verbose)

    if args.comando == "organize":
        if getattr(args, "repetir", None):
            executar_periodicamente(organizar_arquivos, args.repetir, args.diretorio, args.simular)
        else:
            organizar_arquivos(args.diretorio, args.simular)

    elif args.comando == "rename":
        renomear_em_lote(args.diretorio, args.prefixo, args.sufixo, args.inicio, args.simular)

    elif args.comando == "backup":
        if getattr(args, "repetir", None):
            executar_periodicamente(criar_backup, args.repetir, args.origem, args.destino)
        else:
            criar_backup(args.origem, args.destino)

    elif args.comando == "clean":
        extensoes = [e.lower() for e in args.extensoes] if args.extensoes else None
        limpar_arquivos_antigos(args.diretorio, args.dias, extensoes, args.simular)


if __name__ == "__main__":
    main()
