from fractions import Fraction

from cpm_analyzer import Activity, CPMNetwork
from app import parse_duration


def test_parse_duration_accepts_fraction_strings():
    assert parse_duration("1/2") == Fraction(1, 2)
    assert parse_duration("3/2") == Fraction(3, 2)
    assert parse_duration("2.5") == Fraction(5, 2)


def test_cpm_supports_fractional_duration_values():
    activities = {
        "A": Activity("A", "Revisión", Fraction(1, 1), []),
        "B": Activity("B", "Avisar", Fraction(1, 2), ["A"]),
        "C": Activity("C", "Tienda", Fraction(1, 1), ["A"]),
        "D": Activity("D", "Explorar", Fraction(1, 2), ["A"]),
        "E": Activity("E", "Asegurar", Fraction(3, 1), ["C", "D"]),
        "F": Activity("F", "Distribuir", Fraction(7, 2), ["E"]),
        "G": Activity("G", "Coordinar", Fraction(1, 2), ["D"]),
        "H": Activity("H", "Clavar", Fraction(1, 2), ["G"]),
        "I": Activity("I", "Cavar", Fraction(3, 1), ["H"]),
    }

    network = CPMNetwork(activities).calcular()
    assert network.duracion_proyecto == Fraction(17, 2)
    assert network.ruta_critica == ["A", "C", "E", "F"]
