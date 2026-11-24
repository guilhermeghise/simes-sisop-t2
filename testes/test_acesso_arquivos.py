"""Casos de borda de acesso e dos custos de realocação do núcleo."""
import unittest
from unittest.mock import Mock

from simes.arquivos.estruturas import ErroSA
from simes.arquivos.simulador import montar_sistema


class TesteAcessoArquivos(unittest.TestCase):
    def setUp(self):
        self.sa = montar_sistema("contigua", total_blocos=20)
        self.sa.create("P", "/f", 4096)
        self.sa.open("P", "/f", "rw", "h")
        self.fcb = self.sa.fcbs[self.sa.tabelas_processo["P"]["h"].fcb_id]

    def test_append_usa_fim_atual_entre_handles(self):
        self.sa.open("Q", "/f", "a", "a")
        self.sa.seek("P", "h", 4096)
        self.sa.write("P", "h", 10)
        self.sa.seek("Q", "a", 0)
        self.sa.write("Q", "a", 20)
        self.assertEqual(self.fcb.tamanho, 4126)
        self.assertEqual(self.sa.tabelas_processo["Q"]["a"].posicao, 4126)

    def test_realocacao_conta_copia_e_escrita(self):
        self.sa.create("P", "/obstaculo", 4096)
        c = self.sa.camada
        antes = c.leituras, c.escritas
        self.sa.seek("P", "h", 4096)
        self.sa.write("P", "h", 1)
        self.assertEqual((c.leituras - antes[0], c.escritas - antes[1]), (1, 2))
        self.assertEqual(self.sa.alocador.realocacoes, 1)

    def test_fim_e_escrita_vazia_nao_alocam(self):
        self.sa.seek("P", "h", 100000)
        self.assertEqual(self.sa.read("P", "h", 10), 0)
        self.assertEqual(self.sa.write("P", "h", 0), 0)
        self.assertEqual(self.sa.tabelas_processo["P"]["h"].posicao, 100000)
        self.assertEqual((self.fcb.tamanho, len(self.fcb.blocos), self.fcb.sujo),
                         (4096, 1, False))

    def test_erros_de_argumento_modo_e_handle(self):
        self.sa.open("P", "/f", "w", "w")
        for funcao, args, codigo in (
            (self.sa.read, ("P", "w", 1), "EBADF"),
            (self.sa.read, ("Q", "h", 1), "EBADF"),
            (self.sa.write, ("P", "h", -1), "EINVAL"),
            (self.sa.read, ("P", "h", -1), "EINVAL"),
            (self.sa.seek, ("P", "h", -1), "EINVAL"),
        ):
            with self.subTest(funcao=funcao.__name__, args=args):
                with self.assertRaises(ErroSA) as ctx:
                    funcao(*args)
                self.assertEqual(ctx.exception.codigo, codigo)

    def test_trava_impede_acesso_sem_mudar_estado(self):
        self.sa._verificar_trava = Mock(side_effect=ErroSA("EBUSY"))
        for operacao in (self.sa.read, self.sa.write):
            with self.assertRaises(ErroSA):
                operacao("P", "h", 1)
        self.assertEqual(self.sa._verificar_trava.call_count, 2)
        self.assertEqual(self.sa.tabelas_processo["P"]["h"].posicao, 0)
        self.assertFalse(self.fcb.sujo)

    def test_sem_espaco_preserva_posicao_e_metadados(self):
        self.sa.seek("P", "h", 20 * 4096)
        with self.assertRaises(ErroSA) as ctx:
            self.sa.write("P", "h", 1)
        self.assertEqual(ctx.exception.codigo, "ENOSPC")
        self.assertEqual(self.sa.tabelas_processo["P"]["h"].posicao, 20 * 4096)
        self.assertEqual((self.fcb.tamanho, len(self.fcb.blocos), self.fcb.sujo),
                         (4096, 1, False))
