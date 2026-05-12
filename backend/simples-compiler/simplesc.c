/*
 * simplesc stub — placeholder para o compilador SIMPLES real.
 * Uso: simplesc <fonte.simples> -o <saida.asm>
 *
 * Substitua este arquivo pela implementação real do compilador.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static const char *NASM_SKELETON =
    "section .data\n"
    "    msg db 'stub: substitua pelo compilador real', 10\n"
    "    msglen equ $ - msg\n"
    "\n"
    "section .text\n"
    "    global _start\n"
    "_start:\n"
    "    mov eax, 4\n"
    "    mov ebx, 1\n"
    "    mov ecx, msg\n"
    "    mov edx, msglen\n"
    "    int 0x80\n"
    "    mov eax, 1\n"
    "    mov ebx, 0\n"
    "    int 0x80\n";

int main(int argc, char *argv[]) {
    const char *source_file = NULL;
    const char *output_file = NULL;

    /* Parsing de argumentos: simplesc <fonte> -o <saida> */
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-o") == 0 && i + 1 < argc) {
            output_file = argv[++i];
        } else if (argv[i][0] != '-') {
            source_file = argv[i];
        }
    }

    if (!source_file || !output_file) {
        fprintf(stderr, "1:1: erro: uso: simplesc <fonte.simples> -o <saida.asm>\n");
        return 1;
    }

    /* Verifica se o arquivo fonte existe */
    FILE *src = fopen(source_file, "r");
    if (!src) {
        fprintf(stderr, "1:1: erro: arquivo nao encontrado: %s\n", source_file);
        return 1;
    }
    fclose(src);

    /* Escreve o skeleton NASM de saida */
    FILE *out = fopen(output_file, "w");
    if (!out) {
        fprintf(stderr, "1:1: erro: nao foi possivel criar: %s\n", output_file);
        return 1;
    }
    fputs(NASM_SKELETON, out);
    fclose(out);

    return 0;
}
