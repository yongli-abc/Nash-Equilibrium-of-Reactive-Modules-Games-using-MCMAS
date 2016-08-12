import pyparsing as pp
import unittest
from parse import *

class TestIdentifiers(unittest.TestCase):
    parser = build_identifier_parser()

    def test_basics(self):
        a = "  abc123"
        self.assertIn("abc123", self.parser.parseString(a).asList())

        b = "_abc123  "
        self.assertIn("_abc123", self.parser.parseString(b).asList())

        c = "abc_123"
        self.assertIn("abc_123", self.parser.parseString(c).asList())

        d = "123_abc"
        self.assertRaises(pp.ParseException, self.parser.parseString, d)

    def test_exclude_boolean_lterals(self):
        a = "True"
        self.assertRaises(pp.ParseException, self.parser.parseString, a)

        b = "False"
        self.assertRaises(pp.ParseException, self.parser.parseString, b)

        c = "Trueabc"
        self.assertIn("Trueabc", self.parser.parseString(c).asList())

        d = "abcFalse"
        self.assertIn("abcFalse", self.parser.parseString(d).asList())

class TestPropositionalFormulae(unittest.TestCase):
    parser = build_propositional_formula_parser()

    def test_literals(self):
        a = "True"
        self.assertEqual(["True"], self.parser.parseString(a).asList())

        b = "False"
        self.assertEqual(["False"], self.parser.parseString(b).asList())

        c = "abc"
        self.assertEqual(["abc"], self.parser.parseString(c).asList())

    def test_negations(self):
        a = "!True"
        self.assertEqual(["!", "True"], self.parser.parseString(a).asList())

        b = "! False"
        self.assertEqual(["!", "False"], self.parser.parseString(b).asList())

        c = "!abc"
        self.assertEqual(["!", "abc"], self.parser.parseString(c).asList())

        d = "!!xyz"
        self.assertEqual(["!", "!", "xyz"], self.parser.parseString(d).asList())

    def test_ands(self):
        a = "True && False"
        self.assertEqual(["True", "&&", "False"], self.parser.parseString(a).asList())

        b = "True&& abc"
        self.assertEqual(["True", "&&", "abc"], self.parser.parseString(b).asList())

        c = "abc &&False"
        self.assertEqual(["abc", "&&", "False"], self.parser.parseString(c).asList())

        d = "abc&&xyz"
        self.assertEqual(["abc", "&&", "xyz"], self.parser.parseString(d).asList())

    def test_ors(self):
        a = "True || False"
        self.assertEqual(["True", "||", "False"], self.parser.parseString(a).asList())

        b = "True|| abc"
        self.assertEqual(["True", "||", "abc"], self.parser.parseString(b).asList())

        c = "abc ||False"
        self.assertEqual(["abc", "||", "False"], self.parser.parseString(c).asList())

        d = "abc||xyz"
        self.assertEqual(["abc", "||", "xyz"], self.parser.parseString(d).asList())

    def test_implications(self):
        a = "True -> False"
        self.assertEqual(["True", "->", "False"], self.parser.parseString(a).asList())

        b = "True-> abc"
        self.assertEqual(["True", "->", "abc"], self.parser.parseString(b).asList())

        c = "abc ->False"
        self.assertEqual(["abc", "->", "False"], self.parser.parseString(c).asList())

        d = "abc->xyz"
        self.assertEqual(["abc", "->", "xyz"], self.parser.parseString(d).asList())

    def test_nesting(self):
        a = "(!p)"
        self.assertEqual([["!", "p"]], self.parser.parseString(a).asList())

        b = "(!p"
        self.assertRaises(pp.ParseException, self.parser.parseString, b)

        c = "!p && q"
        self.assertEqual(["!", "p", "&&", "q"], self.parser.parseString(c).asList())

        d = "(p -> !q) && (q || !p)"
        self.assertEqual([["p", "->", "!", "q"], "&&", ["q", "||", "!", "p"]], self.parser.parseString(d).asList())

        e = "(((!p) && q) -> (p && (q || (!r))))"
        self.assertEqual([[[["!", "p"], "&&", "q"], "->", ["p", "&&", ["q", "||", ["!", "r"]]]]], self.parser.parseString(e).asList())

class TestLTLFormulae(unittest.TestCase):
    parser = build_LTL_formula_parser()

    def test_unary(self):
        a = "XTrue"
        self.assertEqual(["X", "True"], self.parser.parseString(a).asList())

        b = "F(!p)"
        self.assertEqual(["F", ["!", "p"]], self.parser.parseString(b).asList())

        c = "GFabc"
        self.assertEqual(["G", "F", "abc"], self.parser.parseString(c).asList())

    def test_binary(self):
        a = "abc U True"
        self.assertEqual(["abc", "U", "True"], self.parser.parseString(a).asList())


    def test_more(self):
        b = "p -> Fq"
        self.assertEqual(["p", "->", "F", "q"], self.parser.parseString(b).asList())

        c = "F(p->Gr)||((!q)Up)"
        self.assertEqual(["F", ["p", "->", "G", "r"], "||", [["!", "q"], "U", "p"]], self.parser.parseString(c).asList())

        d = "GFp->F(q||s)"
        self.assertEqual(["G", "F", "p", "->", "F", ["q", "||", "s"]], self.parser.parseString(d).asList())

class TestGuardedCommand(unittest.TestCase):
    parser = build_guarded_command_parser()

    def test_examples(self):
        a = "[] True ~> x := True, y := False"
        self.assertEqual(["[]", "True", "~>", ["x", ":=", "True"], ["y", ":=", "False"]], self.parser.parseString(a).asList())

        b = "[] (x && !y) ~> x:=False, y:=True"
        self.assertEqual(["[]", ["x", "&&", "!", "y"], "~>", ["x", ":=", "False"], ["y", ":=", "True"]], self.parser.parseString(b).asList())

        c = "[] (!x) ~> x:=True"
        self.assertEqual(["[]", ["!", "x"], "~>", ["x", ":=", "True"]], self.parser.parseString(c).asList())

        d = "[] True ~> u1 := True, d1 := False"
        self.assertEqual(["[]", "True", "~>", ["u1", ":=", "True"], ["d1", ":=", "False"]], self.parser.parseString(d).asList())

class TestRMLFile(unittest.TestCase):
    parser = build_RML_parser()

    def test_toggle(self):
        example = """
module toggle controls x,y
    init
    [] True ~> x := True, y := False
    [] True ~> x := False, y := True
    update
    [] (x && !y) ~> x := False, y := True
    [] (!x && y) ~> x := y, y := x
endmodule
        """
        r = self.parser.parseString(example)

    def test_peer_to_peer_communication(self):
        example = """
module m0 controls u0, d0
    init
    [] True ~> u0 := True, d0 := False
    [] True ~> u0 := False, d0 := True
    update
    [] True ~> u0 := True, d0 := False
    [] True ~> u0 := False, d0 := True
    goal
    GF(d0 && u1)
endmodule

module m1 controls u1, d1
    init
    [] True ~> u1 := True, d1 := False
    [] True ~> u1 := False, d1 := True
    update
    [] True ~> u1 := True, d1 := False
    [] True ~> u1 := False, d1 := True
    goal
    GF(d1 && u0)
endmodule
"""
        # print self.parser.parseString(example)[0]["update"][0]["condition_part"]

if __name__ == "__main__":
    unittest.main()
