import json
import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class TerminalXtermIntegrationTest(unittest.TestCase):
    def test_frontend_package_json_declares_xterm_dependencies(self):
        package_json = json.loads((ROOT / "frontend" / "package.json").read_text(encoding="utf-8"))
        dependencies = package_json.get("dependencies", {})
        self.assertIn("xterm", dependencies)
        self.assertIn("xterm-addon-fit", dependencies)

    def test_terminal_pane_imports_xterm_and_fit_addon(self):
        source = (ROOT / "frontend" / "src" / "components" / "ide" / "terminal-pane.tsx").read_text(
            encoding="utf-8"
        )
        self.assertIn('import { Terminal } from "xterm";', source)
        self.assertIn('import { FitAddon } from "xterm-addon-fit";', source)

    def test_terminal_pane_exposes_forward_ref_and_imperative_handle_api(self):
        source = (ROOT / "frontend" / "src" / "components" / "ide" / "terminal-pane.tsx").read_text(
            encoding="utf-8"
        )
        self.assertIn("forwardRef", source)
        self.assertIn("useImperativeHandle", source)
        self.assertRegex(source, re.compile(r"export\s+type\s+TerminalPaneHandle\s*=\s*{"))
        self.assertRegex(source, re.compile(r"write:\s*\(data:\s*string\)\s*=>\s*void"))
        self.assertRegex(source, re.compile(r"clear:\s*\(\)\s*=>\s*void"))
        self.assertRegex(source, re.compile(r"focus:\s*\(\)\s*=>\s*void"))
        self.assertRegex(source, re.compile(r"onData\??:\s*\(data:\s*string\)\s*=>\s*void"))
        self.assertRegex(source, re.compile(r"const\s+onDataRef\s*=\s*useRef\(onData\)"))
        self.assertRegex(source, re.compile(r"onDataRef\.current\s*=\s*onData"))
        self.assertRegex(source, re.compile(r"terminal\.onData\(\(data\)\s*=>\s*onDataRef\.current\?\.\(data\)\)"))
        self.assertRegex(source, re.compile(r"useEffect\(\(\)\s*=>\s*\{[\s\S]*\},\s*\[\s*\]\s*\)"))

    def test_ide_shell_wires_terminal_pane_ref_and_run_output_contract(self):
        source = (ROOT / "frontend" / "src" / "components" / "ide" / "ide-shell.tsx").read_text(encoding="utf-8")
        self.assertIn('import type { TerminalPaneHandle } from "./terminal-pane";', source)
        self.assertRegex(source, re.compile(r"const\s+terminalRef\s*=\s*useRef<TerminalPaneHandle>\(null\)"))
        self.assertRegex(
            source, re.compile(r"const\s+handleTerminalData\s*=\s*useCallback\(\(data:\s*string\)\s*=>\s*\{")
        )
        self.assertRegex(source, re.compile(r"terminalRef\.current\?\.(?:write|clear)\("))
        self.assertRegex(source, re.compile(r"<TerminalPane[\s\S]*ref=\{terminalRef\}"))
        self.assertRegex(source, re.compile(r"onData=\{handleTerminalData\}"))

    def test_terminal_styles_define_xterm_host_height_contract(self):
        styles = (ROOT / "frontend" / "src" / "styles.css").read_text(encoding="utf-8")
        self.assertRegex(styles, re.compile(r"\.terminal-pane__host\s*\{[\s\S]*height:\s*100%;"))
        self.assertRegex(styles, re.compile(r"\.terminal-pane\s+\.xterm\s*\{[\s\S]*height:\s*100%;"))

    def test_terminal_pane_markup_uses_terminal_host_class_contract(self):
        source = (ROOT / "frontend" / "src" / "components" / "ide" / "terminal-pane.tsx").read_text(
            encoding="utf-8"
        )
        self.assertRegex(source, re.compile(r'<div[\s\S]*className="terminal-pane__host"[\s\S]*ref=\{terminalHostRef\}'))

    def test_run_session_client_exposes_compile_and_stdin_contract(self):
        source = (ROOT / "frontend" / "src" / "lib" / "run-session-client.ts").read_text(encoding="utf-8")
        self.assertIn("new WebSocket", source)
        self.assertIn('"compile_and_run"', source)
        self.assertIn('"stdin"', source)
        self.assertIn("sendStdin", source)
        self.assertIn('"exit"', source)
        self.assertIn('"timeout"', source)
        self.assertNotIn('socket.close();\n      socket = null;\n      pendingCode = null;', source)

    def test_ide_shell_wires_terminal_input_and_stdout_for_leia_flow(self):
        source = (ROOT / "frontend" / "src" / "components" / "ide" / "ide-shell.tsx").read_text(encoding="utf-8")
        self.assertIn("createRunSessionClient", source)
        self.assertRegex(source, re.compile(r"const\s+stdinBufferRef\s*=\s*useRef\(\"\"\)"))
        self.assertRegex(source, re.compile(r"const\s+normalizeTerminalNewlines\s*=\s*\(data:\s*string\)\s*=>"))
        self.assertRegex(source, re.compile(r"data\.replace\(/\\r\?\\n/g,\s*\"\\r\\n\"\)"))
        self.assertRegex(source, re.compile(r'if\s*\(char\s*===\s*"\\r"\s*\|\|\s*char\s*===\s*"\\n"\)\s*\{[\s\S]*sendStdin\([\s\S]*\\n'))
        self.assertRegex(source, re.compile(r"stdinBufferRef\.current\s*\+=\s*char"))
        self.assertRegex(source, re.compile(r"onStdout:\s*\(data\)\s*=>\s*terminalRef\.current\?\.write\(normalizeTerminalNewlines\(data\)\)"))
        self.assertRegex(source, re.compile(r'payload\.type === "exec_started"[\s\S]*terminalRef\.current\?\.focus\('))
        self.assertRegex(source, re.compile(r'terminalRef\.current\?\.write\("\$ simplesc run\\r?\\n"\);'))
        self.assertRegex(source, re.compile(r"runSessionRef\.current\?\.start\("))
        self.assertRegex(source, re.compile(r'setStatus\("executing"\)'))
        self.assertRegex(source, re.compile(r'readOnly=\{status === "compiling" \|\| status === "executing"\}'))
        self.assertIn("rate_limited", source)

    def test_toolbar_exposes_clear_terminal_action(self):
        toolbar = (ROOT / "frontend" / "src" / "components" / "ide" / "toolbar.tsx").read_text(encoding="utf-8")
        shell = (ROOT / "frontend" / "src" / "components" / "ide" / "ide-shell.tsx").read_text(encoding="utf-8")
        self.assertRegex(toolbar, re.compile(r"onClearTerminal:\s*\(\)\s*=>\s*void"))
        self.assertRegex(toolbar, re.compile(r"onClick=\{onClearTerminal\}"))
        self.assertIn("Limpar terminal", toolbar)
        self.assertRegex(shell, re.compile(r"<Toolbar[\s\S]*onClearTerminal=\{\(\)\s*=>\s*terminalRef\.current\?\.clear\(\)\}"))


if __name__ == "__main__":
    unittest.main()
