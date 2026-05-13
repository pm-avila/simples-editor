import { forwardRef, useEffect, useImperativeHandle, useRef } from "react";
import { Terminal } from "xterm";
import { FitAddon } from "xterm-addon-fit";
import "xterm/css/xterm.css";

export type TerminalPaneHandle = {
  write: (data: string) => void;
  clear: () => void;
  focus: () => void;
};

export type TerminalPaneProps = {
  onData?: (data: string) => void;
};

export const TerminalPane = forwardRef<TerminalPaneHandle, TerminalPaneProps>(function TerminalPane(
  { onData },
  ref,
) {
  const terminalHostRef = useRef<HTMLDivElement>(null);
  const terminalRef = useRef<Terminal | null>(null);

  useEffect(() => {
    const host = terminalHostRef.current;
    if (!host) return;

    const terminal = new Terminal();
    const fitAddon = new FitAddon();
    terminal.loadAddon(fitAddon);
    terminal.open(host);
    fitAddon.fit();
    const disposeOnData = terminal.onData((data) => onData?.(data));
    const handleResize = () => fitAddon.fit();
    window.addEventListener("resize", handleResize);

    terminalRef.current = terminal;

    return () => {
      window.removeEventListener("resize", handleResize);
      disposeOnData.dispose();
      terminal.dispose();
      terminalRef.current = null;
    };
  }, [onData]);

  useImperativeHandle(
    ref,
    () => ({
      write: (data: string) => terminalRef.current?.write(data),
      clear: () => terminalRef.current?.clear(),
      focus: () => terminalRef.current?.focus(),
    }),
    [],
  );

  return (
    <section className="terminal-pane" style={{ alignItems: "stretch", flexDirection: "column", gap: 8 }}>
      <span className="terminal-pane__label">Terminal</span>
      <div ref={terminalHostRef} style={{ flex: 1, minHeight: 0, width: "100%" }} />
    </section>
  );
});
