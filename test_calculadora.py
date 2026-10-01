from calculadora import somar


def test_somar_positivos():
    assert somar(2, 3) == 5


def test_somar_negativo():
    assert somar(-1, 1) == 0


def test_somar_decimais():
    assert somar(2.5, 1.5) == 4.0