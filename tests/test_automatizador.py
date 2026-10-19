"""Testes básicos para o Automatizador de Tarefas Repetitivas."""

import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from automatizador import (  # noqa: E402
    obter_categoria,
    organizar_arquivos,
    renomear_em_lote,
    criar_backup,
    limpar_arquivos_antigos,
)


def test_obter_categoria():
    assert obter_categoria(".jpg") == "Imagens"
    assert obter_categoria(".pdf") == "Documentos"
    assert obter_categoria(".xyz") == "Outros"


def test_organizar_arquivos(tmp_path):
    (tmp_path / "foto.png").write_text("x")
    (tmp_path / "doc.pdf").write_text("x")

    organizar_arquivos(str(tmp_path))

    assert (tmp_path / "Imagens" / "foto.png").exists()
    assert (tmp_path / "Documentos" / "doc.pdf").exists()


def test_renomear_em_lote(tmp_path):
    (tmp_path / "a.txt").write_text("x")
    (tmp_path / "b.txt").write_text("x")

    renomear_em_lote(str(tmp_path), prefixo="arquivo_", iniciar_em=1)

    nomes = sorted(p.name for p in tmp_path.iterdir())
    assert nomes == ["arquivo_1.txt", "arquivo_2.txt"]


def test_criar_backup(tmp_path):
    origem = tmp_path / "projeto"
    origem.mkdir()
    (origem / "arquivo.txt").write_text("conteudo")

    destino = tmp_path / "backups"
    criar_backup(str(origem), str(destino))

    zips = list(destino.glob("*.zip"))
    assert len(zips) == 1
    with zipfile.ZipFile(zips[0]) as z:
        assert any("arquivo.txt" in n for n in z.namelist())


def test_limpar_arquivos_antigos(tmp_path):
    recente = tmp_path / "recente.txt"
    recente.write_text("x")

    limpar_arquivos_antigos(str(tmp_path), dias=30)

    # Arquivo recente não deve ser removido
    assert recente.exists()
