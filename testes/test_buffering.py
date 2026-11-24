"""Tempos e bloqueio do produtor em diferentes regimes do dispositivo."""
import unittest

from simes.es.buffering import simular_buffering


class TesteBuffering(unittest.TestCase):
    def test_simples_serializa_producao_e_gravacao(self):
        r = simular_buffering(1, 2, 8, 4)
        self.assertEqual(r["tempo_total_ms"], 40)
        self.assertEqual(r["bloqueio_produtor_ms"], 24)
        self.assertEqual(r["utilizacao_dispositivo_pct"], 80)

    def test_duplo_e_circular_com_consumidor_lento(self):
        # Duplo: esperas de 6 + 6 + 6 ms. Circular: 4 + 6 ms.
        for buffers, bloqueio in ((2, 18), (3, 10)):
            with self.subTest(buffers=buffers):
                r = simular_buffering(buffers, 2, 8, 5)
                self.assertEqual(r["tempo_total_ms"], 42)
                self.assertEqual(r["bloqueio_produtor_ms"], bloqueio)
                self.assertAlmostEqual(r["utilizacao_dispositivo_pct"], 100 * 40 / 42)

    def test_produtor_lento_e_taxas_iguais(self):
        for buffers in (2, 3):
            r = simular_buffering(buffers, 8, 2, 5)
            self.assertEqual(r["tempo_total_ms"], 42)
            self.assertEqual(r["bloqueio_produtor_ms"], 0)
            r = simular_buffering(buffers, 2, 2, 5)
            self.assertEqual(r["tempo_total_ms"], 12)
            self.assertEqual(r["bloqueio_produtor_ms"], 0)

    def test_vazio_e_um_bloco(self):
        for buffers in (1, 2, 3):
            self.assertEqual(simular_buffering(buffers, 2, 8, 0), {
                "tempo_total_ms": 0, "bloqueio_produtor_ms": 0,
                "utilizacao_dispositivo_pct": 0})
            self.assertEqual(simular_buffering(buffers, 2, 8, 1)["tempo_total_ms"], 10)

    def test_tempos_zero(self):
        self.assertEqual(simular_buffering(2, 0, 0, 5)["tempo_total_ms"], 0)
        self.assertEqual(simular_buffering(2, 0, 8, 5)["tempo_total_ms"], 40)
        self.assertEqual(simular_buffering(2, 8, 0, 5)["tempo_total_ms"], 40)

    def test_argumentos_invalidos(self):
        for args in ((0, 2, 8, 5), (1.5, 2, 8, 5), (2, -1, 8, 5),
                     (2, 2, -1, 5), (2, 2, 8, -1), (2, 2, 8, 1.5)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                simular_buffering(*args)
