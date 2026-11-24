"""O DMA tem custo por requisição, independente do tamanho e da duração."""
import unittest
from unittest.mock import patch

from simes.es.cpu import custo_cpu


class TesteDMA(unittest.TestCase):
    def test_custo_independe_de_blocos_e_usa_parametros(self):
        with patch("simes.es.cpu.P.CUSTO_PROGRAMAR_DMA_MS", 0.2), \
             patch("simes.es.cpu.P.CUSTO_INTERRUPCAO_MS", 0.4):
            for blocos, duracao in ((1, 0.01), (8, 10), (64, 100), (256, 1000)):
                with self.subTest(blocos=blocos):
                    self.assertAlmostEqual(custo_cpu("dma", blocos, duracao), 0.6)
