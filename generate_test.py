import unittest
from generate import *
from parse import *

class TestGenerator(unittest.TestCase):
    parser = build_propositional_formula_parser()
    parser_LTL = build_LTL_formula_parser()

    def test_translate_formula(self):
        a = "m && (p || q)"
        result = self.parser.parseString(a)
        trans_result = translate_formula(result.asList())
        self.assertEqual("m and (p or q)", trans_result)

        b = "m -> p -> q"
        result = self.parser.parseString(b)
        trans_result = translate_formula(result.asList())
        self.assertEqual("!(m) or (!(p) or (q))", trans_result)

        c = "(m -> p) -> q"
        result = self.parser.parseString(c)
        trans_result = translate_formula(result.asList())
        self.assertEqual("!((!(m) or (p))) or (q)", trans_result)

        d = "q -> p && r"
        result = self.parser.parseString(d)
        trans_result = translate_formula(result.asList())
        self.assertEqual("!(q) or (p and r)", trans_result)

        e = "q && r -> p"
        result = self.parser.parseString(e)
        trans_result = translate_formula(result.asList())
        self.assertEqual("!(q and r) or (p)", trans_result)

    def test_translate_formula_LTL(self):
        a = "GF(d0 && u1)"
        result = self.parser_LTL.parseString(a)
        trans_result = translate_formula(result.asList())
        self.assertEqual("G F (d0 and u1)", trans_result)

if __name__ == "__main__":
    unittest.main()
