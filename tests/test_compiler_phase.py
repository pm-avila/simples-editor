"""
Tests for compiler error phase normalization (issue #20).

Run with:
    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_compiler_phase.py -v
"""
import unittest

from backend.compiler import _parse_compiler_error


class TestPhaseNormalizationLexer(unittest.TestCase):

    def test_erro_lexico_maps_to_lexer(self):
        err = _parse_compiler_error("1:1: erro lexico: caracter invalido '@'")
        self.assertEqual(err["phase"], "lexer")

    def test_erro_lexer_keyword_maps_to_lexer(self):
        err = _parse_compiler_error("2:5: erro lexer: token inesperado")
        self.assertEqual(err["phase"], "lexer")

    def test_lexico_case_insensitive(self):
        err = _parse_compiler_error("1:1: erro Lexico: uppercase test")
        self.assertEqual(err["phase"], "lexer")


class TestPhaseNormalizationParser(unittest.TestCase):

    def test_erro_sintatico_maps_to_parser(self):
        err = _parse_compiler_error("3:2: erro sintatico: esperado 'fim'")
        self.assertEqual(err["phase"], "parser")

    def test_erro_parser_keyword_maps_to_parser(self):
        err = _parse_compiler_error("5:8: erro parser: declaracao invalida")
        self.assertEqual(err["phase"], "parser")

    def test_sintatico_case_insensitive(self):
        err = _parse_compiler_error("3:2: erro Sintatico: uppercase test")
        self.assertEqual(err["phase"], "parser")


class TestPhaseNormalizationSemantic(unittest.TestCase):

    def test_erro_semantico_maps_to_semantic(self):
        err = _parse_compiler_error("4:7: erro semantico: variavel 'x' nao declarada")
        self.assertEqual(err["phase"], "semantic")

    def test_erro_semantic_keyword_maps_to_semantic(self):
        err = _parse_compiler_error("6:3: erro semantic: type mismatch")
        self.assertEqual(err["phase"], "semantic")

    def test_semantico_case_insensitive(self):
        err = _parse_compiler_error("4:7: erro Semantico: uppercase test")
        self.assertEqual(err["phase"], "semantic")


class TestPhaseNormalizationFallback(unittest.TestCase):

    def test_plain_erro_falls_back_to_compile(self):
        err = _parse_compiler_error("4:7: erro: variavel 'y' nao declarada")
        self.assertEqual(err["phase"], "compile")

    def test_unknown_phase_keyword_falls_back_to_compile(self):
        err = _parse_compiler_error("1:1: erro desconhecido: algo errado")
        self.assertEqual(err["phase"], "compile")

    def test_no_location_falls_back_to_compile(self):
        err = _parse_compiler_error("fatal: arquivo nao encontrado")
        self.assertEqual(err["phase"], "compile")
        self.assertEqual(err["line"], 0)
        self.assertEqual(err["column"], 0)


class TestPhaseNormalizationFields(unittest.TestCase):

    def test_structured_error_has_all_required_fields(self):
        err = _parse_compiler_error("4:7: erro semantico: variavel 'x' nao declarada")
        self.assertIn("phase", err)
        self.assertIn("line", err)
        self.assertIn("column", err)
        self.assertIn("message", err)

    def test_lexer_error_line_column_preserved(self):
        err = _parse_compiler_error("10:3: erro lexico: caracter invalido")
        self.assertEqual(err["line"], 10)
        self.assertEqual(err["column"], 3)

    def test_message_does_not_contain_phase_keyword(self):
        err = _parse_compiler_error("4:7: erro semantico: variavel 'x' nao declarada")
        self.assertNotIn("semantico", err["message"])

    def test_existing_plain_error_still_works(self):
        """Ensure backward compat with errors from before phase normalization."""
        err = _parse_compiler_error("4:7: erro: variavel 'y' nao declarada")
        self.assertEqual(err["line"], 4)
        self.assertEqual(err["column"], 7)
        self.assertIn("variavel", err["message"])


if __name__ == "__main__":
    unittest.main()
