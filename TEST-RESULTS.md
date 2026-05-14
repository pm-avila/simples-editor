# Sprint-03: Test Results

**Date:** 2026-05-12  
**Status:** ✅ **ALL TESTS PASSING**

## Test Summary

```
============================= test session starts ==============================
platform darwin -- Python 3.12.12, pytest-9.0.3, pluggy-1.6.0
rootdir: /Users/avilapm/Documents/IFSULDEMINAS/compiladores/visual_simples

collected 39 items

tests/test_compile_endpoint.py::TestCompileEndpointSuccess::test_post_compile_returns_nasm_on_success PASSED [  2%]
tests/test_compile_endpoint.py::TestCompileEndpointSuccess::test_post_compile_success_has_no_error_key PASSED [  5%]
tests/test_compile_endpoint.py::TestCompileEndpointFailure::test_post_compile_error_has_structured_fields PASSED [  7%]
tests/test_compile_endpoint.py::TestCompileEndpointFailure::test_post_compile_no_output_file_returns_422 PASSED [ 10%]
tests/test_compile_endpoint.py::TestCompileEndpointFailure::test_post_compile_returns_422_on_compiler_error PASSED [ 12%]
tests/test_compile_endpoint.py::TestCompileEndpointFailure::test_post_compile_timeout_returns_422 PASSED [ 15%]
tests/test_compile_endpoint.py::TestCompileEndpointValidation::test_post_compile_empty_code_returns_400 PASSED [ 17%]
tests/test_compile_endpoint.py::TestCompileEndpointValidation::test_post_compile_missing_code_returns_400 PASSED [ 20%]
tests/test_compile_endpoint.py::TestCompileEndpointValidation::test_post_compile_whitespace_only_returns_400 PASSED [ 23%]

tests/test_compiler_phase.py::TestPhaseNormalizationLexer::test_erro_lexer_keyword_maps_to_lexer PASSED [ 25%]
tests/test_compiler_phase.py::TestPhaseNormalizationLexer::test_erro_lexico_maps_to_lexer PASSED [ 28%]
tests/test_compiler_phase.py::TestPhaseNormalizationLexer::test_lexico_case_insensitive PASSED [ 30%]
tests/test_compiler_phase.py::TestPhaseNormalizationParser::test_erro_parser_keyword_maps_to_parser PASSED [ 33%]
tests/test_compiler_phase.py::TestPhaseNormalizationParser::test_erro_sintatico_maps_to_parser PASSED [ 35%]
tests/test_compiler_phase.py::TestPhaseNormalizationParser::test_sintatico_case_insensitive PASSED [ 38%]
tests/test_compiler_phase.py::TestPhaseNormalizationSemantic::test_erro_semantic_keyword_maps_to_semantic PASSED [ 41%]
tests/test_compiler_phase.py::TestPhaseNormalizationSemantic::test_erro_semantico_maps_to_semantic PASSED [ 43%]
tests/test_compiler_phase.py::TestPhaseNormalizationSemantic::test_semantico_case_insensitive PASSED [ 46%]
tests/test_compiler_phase.py::TestPhaseNormalizationFallback::test_no_location_falls_back_to_compile PASSED [ 48%]
tests/test_compiler_phase.py::TestPhaseNormalizationFallback::test_plain_erro_falls_back_to_compile PASSED [ 51%]
tests/test_compiler_phase.py::TestPhaseNormalizationFallback::test_unknown_phase_keyword_falls_back_to_compile PASSED [ 53%]
tests/test_compiler_phase.py::TestPhaseNormalizationFields::test_existing_plain_error_still_works PASSED [ 56%]
tests/test_compiler_phase.py::TestPhaseNormalizationFields::test_lexer_error_line_column_preserved PASSED [ 58%]
tests/test_compiler_phase.py::TestPhaseNormalizationFields::test_message_does_not_contain_phase_keyword PASSED [ 61%]
tests/test_compiler_phase.py::TestPhaseNormalizationFields::test_structured_error_has_all_required_fields PASSED [ 64%]

tests/test_compile_timeout.py::TestParseTimeout::test_custom_default_is_used PASSED [ 66%]
tests/test_compile_timeout.py::TestParseTimeout::test_custom_positive_value PASSED [ 69%]
tests/test_compile_timeout.py::TestParseTimeout::test_empty_string_falls_back_to_default PASSED [ 71%]
tests/test_compile_timeout.py::TestParseTimeout::test_float_string_falls_back_to_default PASSED [ 74%]
tests/test_compile_timeout.py::TestParseTimeout::test_negative_falls_back_to_default PASSED [ 76%]
tests/test_compile_timeout.py::TestParseTimeout::test_non_numeric_falls_back_to_default PASSED [ 79%]
tests/test_compile_timeout.py::TestParseTimeout::test_none_falls_back_to_default PASSED [ 82%]
tests/test_compile_timeout.py::TestParseTimeout::test_valid_integer_string_is_accepted PASSED [ 84%]
tests/test_compile_timeout.py::TestParseTimeout::test_zero_falls_back_to_default PASSED [ 87%]
tests/test_compile_timeout.py::TestTimeoutPassedToSubprocess::test_subprocess_receives_compile_timeout PASSED [ 89%]
tests/test_compile_timeout.py::TestTimeoutPassedToSubprocess::test_timeout_error_message_is_human_readable PASSED [ 92%]
tests/test_compile_timeout.py::TestTimeoutPassedToSubprocess::test_timeout_error_phase_is_compile PASSED [ 94%]
tests/test_compile_timeout.py::TestTimeoutPassedToSubprocess::test_timeout_expired_returns_structured_error PASSED [ 97%]
tests/test_compile_timeout.py::TestTimeoutEndpointResponse::test_endpoint_returns_422_on_timeout PASSED [100%]

============================== 39 passed in 0.08s ==============================
```

## Breakdown by Category

### ✅ Endpoint Tests (9 tests)
- `test_post_compile_returns_nasm_on_success` — POST /api/compile returns {ok: true, nasm: "..."}
- `test_post_compile_success_has_no_error_key` — No error field on success
- `test_post_compile_error_has_structured_fields` — Error has phase, line, column, message
- `test_post_compile_no_output_file_returns_422` — .asm not found → 422
- `test_post_compile_returns_422_on_compiler_error` — Compiler error → 422
- `test_post_compile_timeout_returns_422` — Timeout → 422
- `test_post_compile_empty_code_returns_400` — Empty code → 400
- `test_post_compile_missing_code_returns_400` — Missing code field → 400
- `test_post_compile_whitespace_only_returns_400` — Whitespace only → 400

### ✅ Phase Normalization Tests (16 tests)
- `test_erro_lexer_keyword_maps_to_lexer` — "lexer" → phase: "lexer"
- `test_erro_lexico_maps_to_lexer` — "lexico" → phase: "lexer"
- `test_lexico_case_insensitive` — "LEXICO" → phase: "lexer"
- `test_erro_parser_keyword_maps_to_parser` — "parser" → phase: "parser"
- `test_erro_sintatico_maps_to_parser` — "sintatico" → phase: "parser"
- `test_sintatico_case_insensitive` — "SINTATICO" → phase: "parser"
- `test_erro_semantic_keyword_maps_to_semantic` — "semantic" → phase: "semantic"
- `test_erro_semantico_maps_to_semantic` — "semantico" → phase: "semantic"
- `test_semantico_case_insensitive` — "SEMANTICO" → phase: "semantic"
- `test_no_location_falls_back_to_compile` — No line/col → phase: "compile"
- `test_plain_erro_falls_back_to_compile` — No phase keyword → phase: "compile"
- `test_unknown_phase_keyword_falls_back_to_compile` — Unknown phase → phase: "compile"
- `test_existing_plain_error_still_works` — Legacy error format supported
- `test_lexer_error_line_column_preserved` — Line/column not lost
- `test_message_does_not_contain_phase_keyword` — Message field clean
- `test_structured_error_has_all_required_fields` — All fields present

### ✅ Timeout Tests (14 tests)
- `test_custom_default_is_used` — Custom default applied
- `test_custom_positive_value` — Positive value accepted
- `test_empty_string_falls_back_to_default` — Empty → default
- `test_float_string_falls_back_to_default` — Float → default (integers only)
- `test_negative_falls_back_to_default` — Negative → default
- `test_non_numeric_falls_back_to_default` — Non-numeric → default
- `test_none_falls_back_to_default` — None → default
- `test_valid_integer_string_is_accepted` — Valid integer accepted
- `test_zero_falls_back_to_default` — Zero → default (no non-positive)
- `test_subprocess_receives_compile_timeout` — Timeout passed to subprocess
- `test_timeout_error_message_is_human_readable` — "compilação excedeu o limite"
- `test_timeout_error_phase_is_compile` — phase: "compile" on timeout
- `test_timeout_expired_returns_structured_error` — Structured error returned
- `test_endpoint_returns_422_on_timeout` — Endpoint returns 422

## TypeScript Validation

```bash
$ cd frontend && ./node_modules/.bin/tsc --noEmit
# No errors
```

## What's Ready to Run

### Local Testing
```bash
# Backend
cd /repo && PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_compile*.py -v

# Frontend
cd frontend && npm install && ./node_modules/.bin/tsc --noEmit
```

### Full Stack (requires Docker)
```bash
docker-compose up --build
# Access: http://localhost
```

## How It Works in the IDE

1. **Write SIMPLES code** in the left panel (MonacoEditorPane)
2. **Click RUN** button
3. **If compilation succeeds:**
   - Right panel (NasmPane) fills with generated NASM x32 assembly
4. **If compilation fails:**
   - Error line/column highlighted in the editor
   - Right panel shows error message as a NASM comment

## Key Implementation Details

- **Backend:** Flask + Python 3.12 + subprocess wrapper
- **Frontend:** React 18 + TypeScript 5 + Monaco Editor
- **Compiler:** `simplesc` stub (runs in Docker)
- **Phase normalization:** lexico→lexer, sintatico→parser, semantico→semantic
- **Timeout:** 15 seconds (configurable via COMPILE_TIMEOUT env var)
- **Error handling:** Structured JSON with phase, line, column, message
- **Frontend sync:** Real-time assembly panel update on successful compile

---

**All systems operational and ready for demonstration!** 🚀
