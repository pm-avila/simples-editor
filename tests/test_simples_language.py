import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class SimplesLanguageContractTest(unittest.TestCase):
    def test_simples_language_module_exists(self):
        path = ROOT / "frontend" / "src" / "components" / "ide" / "simples-language.ts"
        self.assertTrue(path.exists(), f"missing: {path}")

    def test_keywords_match_prd_contract(self):
        content = (
            ROOT / "frontend" / "src" / "components" / "ide" / "simples-language.ts"
        ).read_text(encoding="utf-8")
        expected_keywords = [
            "programa", "inicio", "fim",
            "inteiro", "flutuante", "vazio",
            "se", "entao", "senao", "fimse",
            "enquanto", "fimenquanto",
            "para", "de", "ate", "passo", "faca", "fimpara",
            "leia", "escreva", "escreval",
            "e", "ou", "nao",
            "div",
            "procedimento", "retorna",
        ]
        for keyword in expected_keywords:
            self.assertIn(f'"{keyword}"', content)

    def test_tokenizer_covers_prd_operator_delimiter_and_numbers(self):
        content = (
            ROOT / "frontend" / "src" / "components" / "ide" / "simples-language.ts"
        ).read_text(encoding="utf-8")
        self.assertIn('operators: ["<-", "+", "-", "*", "div", ">", "<", "=", "<>", ">=", "<="]', content)
        self.assertIn(r'/\\d+\\.\\d+/', content)
        self.assertIn(r'/\\d+/', content)
        self.assertIn(r'/[(),;]/', content)


if __name__ == "__main__":
    unittest.main()
