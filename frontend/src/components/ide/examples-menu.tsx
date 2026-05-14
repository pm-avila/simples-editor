import { useState } from "react";
import "./examples-menu.css";

export interface Example {
  id: string;
  name: string;
  description: string;
  code: string;
  category: "basico" | "entrada-saida" | "estruturas" | "avancado";
}

interface ExamplesMenuProps {
  onSelectExample: (code: string) => void;
}

const EXAMPLES: Example[] = [
  {
    id: "hello-world",
    name: "Olá Mundo",
    description: "Programa que exibe uma mensagem",
    category: "basico",
    code: `programa exemplo
inicio
  escreva "Olá, Mundo!"
fim`,
  },
  {
    id: "soma",
    name: "Soma Dois Números",
    description: "Lê dois números e exibe a soma",
    category: "entrada-saida",
    code: `programa soma
var a, b, resultado: inteiro
inicio
  leia a
  leia b
  resultado <- a + b
  escreva resultado
fim`,
  },
  {
    id: "tabuada",
    name: "Tabuada do 5",
    description: "Exibe a tabuada do número 5",
    category: "estruturas",
    code: `programa tabuada
var i, resultado: inteiro
inicio
  i <- 1
  enquanto i <= 10 faca
    resultado <- 5 * i
    escreva resultado
    i <- i + 1
  fim
fim`,
  },
  {
    id: "fibonacci",
    name: "Fibonacci",
    description: "Calcula sequência de Fibonacci",
    category: "avancado",
    code: `programa fibonacci
var n, a, b, temp, i: inteiro
inicio
  leia n
  a <- 0
  b <- 1
  i <- 0
  enquanto i < n faca
    escreva a
    temp <- a + b
    a <- b
    b <- temp
    i <- i + 1
  fim
fim`,
  },
  {
    id: "par-impar",
    name: "Par ou Ímpar",
    description: "Verifica se um número é par ou ímpar",
    category: "estruturas",
    code: `programa parImpar
var numero, resto: inteiro
inicio
  leia numero
  resto <- numero % 2
  se resto = 0 entao
    escreva "Par"
  senao
    escreva "Ímpar"
  fim
fim`,
  },
  {
    id: "maior",
    name: "Maior de Dois Números",
    description: "Compara dois números e exibe o maior",
    category: "basico",
    code: `programa maior
var a, b, maximo: inteiro
inicio
  leia a
  leia b
  se a > b entao
    maximo <- a
  senao
    maximo <- b
  fim
  escreva maximo
fim`,
  },
];

export function ExamplesMenu({ onSelectExample }: ExamplesMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<Example["category"] | "todos">("todos");

  const categories = [
    { id: "todos", label: "Todos os Exemplos" },
    { id: "basico", label: "Básico" },
    { id: "entrada-saida", label: "Entrada/Saída" },
    { id: "estruturas", label: "Estruturas" },
    { id: "avancado", label: "Avançado" },
  ];

  const filteredExamples = selectedCategory === "todos" 
    ? EXAMPLES 
    : EXAMPLES.filter(ex => ex.category === selectedCategory);

  const handleSelectExample = (code: string) => {
    onSelectExample(code);
    setIsOpen(false);
  };

  return (
    <div className="examples-menu">
      <button
        className="examples-menu-toggle"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Exemplos de código"
        title="Exemplos de código SIMPLES"
      >
        <span className="examples-menu-icon">⟨ 💾 ⟩</span>
        <span className="examples-menu-label">Exemplos</span>
      </button>

      {isOpen && (
        <div className="examples-menu-panel">
          <div className="examples-menu-header">
            <h3>Exemplos de Código</h3>
            <button
              className="examples-menu-close"
              onClick={() => setIsOpen(false)}
              aria-label="Fechar menu"
            >
              ✕
            </button>
          </div>

          <div className="examples-menu-categories">
            {categories.map(cat => (
              <button
                key={cat.id}
                className={`examples-menu-category ${selectedCategory === cat.id ? "active" : ""}`}
                onClick={() => setSelectedCategory(cat.id as any)}
              >
                {cat.label}
              </button>
            ))}
          </div>

          <div className="examples-menu-list">
            {filteredExamples.map(example => (
              <button
                key={example.id}
                className="examples-menu-item"
                onClick={() => handleSelectExample(example.code)}
                title={example.description}
              >
                <div className="examples-menu-item-name">{example.name}</div>
                <div className="examples-menu-item-desc">{example.description}</div>
              </button>
            ))}
          </div>

          <div className="examples-menu-footer">
            <p>Selecione um exemplo para carregar no editor</p>
          </div>
        </div>
      )}
    </div>
  );
}
