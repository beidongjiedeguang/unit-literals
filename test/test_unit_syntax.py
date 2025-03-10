from unit_syntax import transform
import unit_syntax
import pytest
import numpy
import pint


class AttrTest:
    def __init__(self):
        self.second = 7


attr_test = AttrTest()

dict_test = {"value": 37}

second = 1024

seven_furlong = unit_syntax.ureg.Quantity(7.0, "furlong")


def dbg_transform(code):
    from pprint import pprint

    tokens = list(transform.generate_tokens(code))
    pprint(tokens)
    pprint(transform.parse(iter(tokens)))
    pprint(transform.transform(code))


def do_mult(left, right):
    return left * right


def id(v):
    return v


def assert_quantity_exec(code, value, units):
    glo = dict(globals())
    exec(transform.transform(code), glo)
    result = glo["result"]

    u = unit_syntax.ureg.Quantity(value, units)
    result = result.to(u.units)

    if type(value) == float and type(result.magnitude) == float:
        assert result.magnitude == pytest.approx(value)
    elif type(result.magnitude) == numpy.ndarray:
        assert numpy.all(result.magnitude == value)
    else:
        assert result.magnitude == value
    assert result.units == u.units


def assert_quantity(code, value, units):
    code_assign = "result = " + code
    assert_quantity_exec(code_assign, value, units)


def test_all():
    assert_quantity_exec(
        """
from math import *
def surface_area(radius):
  return 2*pi*(radius meters)**2

def total_surface_force(radius):
    return (101 kilopascal)*surface_area(radius)
result = total_surface_force(1.0)
""",
        634601.716025,
        "N",
    )

    assert_quantity("12 meter", 12, "meter")
    assert_quantity("13 meter/s**2", 13, "meter/s**2")
    assert_quantity("2048 meter/second * 2 second", 4096, "meters")
    assert_quantity("(2048 meter)/second * 2 second", 4, "meter*second")
    assert_quantity("do_mult(3 kg, 5 s)", 15, "kg*s")
    assert_quantity("(3 kg) pounds", 6.61386786, "pounds")
    assert_quantity("[2, 5] T", [2, 5], "T")
    assert_quantity("attr_test.second degF", 7, "degF")
    assert_quantity("dict_test['value'] ns", 37, "ns")
    with pytest.raises(pint.errors.DimensionalityError):
        assert_quantity("2**4 meters", 16, "meters")
    assert_quantity("second * 1 meters", 1024, "meters")

    assert_quantity("3 attoparsec liters", 3, "attoparsec*liters")
    assert_quantity("37 tesla/(becquerel*second)", 37, "tesla/(becquerel*second)")

    assert_quantity("3.0*id(seven_furlong furlong)", 21.0, "furlongs")
    assert_quantity("(seven_furlong furlong)*id(3.0)", 21.0, "furlongs")

    # TODO
    # with pytest.raises(SyntaxError):
    #     assert_quantity("3 smoots", 3, "smoots")
