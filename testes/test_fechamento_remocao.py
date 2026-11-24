"""Persistência de metadados e vida útil de arquivos removidos abertos."""
import unittest

from simes.arquivos.estruturas import ErroSA
from simes.arquivos.simulador import montar_sistema


class TesteFechamentoRemocao(unittest.TestCase):
    def setUp(self):
        self.sa = montar_sistema("contigua", total_blocos=20)
        self.sa.create("P", "/f", 4096)
        self.sa.open("P", "/f", "rw", "h")
        self.sa.open("Q", "/f", "r", "h")
        self.fcb = self.sa.fcbs[self.sa.tabelas_processo["P"]["h"].fcb_id]

    def test_sujo_grava_uma_vez_e_fecha_contadores(self):
        self.sa.write("P", "h", 1)
        antes = self.sa.camada.escritas
        self.sa.close("Q", "h")
        self.assertEqual(self.sa.camada.escritas - antes, 1)
        self.assertFalse(self.fcb.sujo)
        self.assertEqual(self.sa.tabela_global[self.fcb.id].contador, 1)
        self.sa.close("P", "h")
        self.assertEqual(self.sa.camada.escritas - antes, 1)
        self.assertNotIn(self.fcb.id, self.sa.tabela_global)

    def test_unlink_sujo_libera_so_no_ultimo_close(self):
        self.sa.write("P", "h", 1)
        livres = self.sa.alocador.bitmap.livres()
        self.sa.unlink("P", "/f")
        self.sa.close("P", "h")
        self.assertIn(self.fcb.id, self.sa.fcbs)
        self.assertEqual(self.sa.alocador.bitmap.livres(), livres)
        self.assertEqual(self.sa.read("Q", "h", 1), 1)
        self.sa.close("Q", "h")
        self.assertNotIn(self.fcb.id, self.sa.fcbs)
        self.assertEqual(self.sa.alocador.bitmap.livres(), livres + 1)

    def test_unlink_fechado_libera_imediatamente(self):
        self.sa.close("P", "h")
        self.sa.close("Q", "h")
        livres = self.sa.alocador.bitmap.livres()
        self.sa.unlink("P", "/f")
        self.assertEqual(self.sa.alocador.bitmap.livres(), livres + 1)
        self.assertNotIn(self.fcb.id, self.sa.fcbs)

    def test_erros_nao_removem_entradas(self):
        self.sa.mkdir("P", "/d")
        for caminho, codigo in (("/", "EISDIR"), ("/d", "EISDIR"),
                                ("/f/x", "ENOTDIR"), ("/ausente", "ENOENT")):
            with self.subTest(caminho=caminho):
                with self.assertRaises(ErroSA) as ctx:
                    self.sa.unlink("P", caminho)
                self.assertEqual(ctx.exception.codigo, codigo)
        self.sa.close("P", "h")
        with self.assertRaises(ErroSA) as ctx:
            self.sa.close("P", "h")
        self.assertEqual(ctx.exception.codigo, "EBADF")
        self.assertEqual(self.sa.tabela_global[self.fcb.id].contador, 1)
