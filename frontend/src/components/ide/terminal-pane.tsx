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
  const onDataRef = useRef(onData);

  useEffect(() => {
    onDataRef.current = onData;
  }, [onData]);

  useEffect(() => {
    const host = terminalHostRef.current;
    if (!host) return;

    const terminal = new Terminal({
      cursorBlink: true,
      fontFamily: '"Cascadia Code", "Fira Code", Menlo, Consolas, monospace',
      fontSize: 13,
      theme: {
        background: "#1e1e1e",
        foreground: "#d4d4d4",
      },
    });
    const fitAddon = new FitAddon();
    terminal.loadAddon(fitAddon);
    terminal.open(host);

    const fit = () => {
      try { fitAddon.fit(); } catch { /* ignore if not ready */ }
    };

    // Defer first fit so the host has final dimensions
    const rafId = requestAnimationFrame(() => fit());

    const disposeOnData = terminal.onData((data) => onDataRef.current?.(data));

    const resizeObserver = new ResizeObserver(() => fit());
    resizeObserver.observe(host);

    terminalRef.current = terminal;

    return () => {
      cancelAnimationFrame(rafId);
      resizeObserver.disconnect();
      disposeOnData.dispose();
      terminal.dispose();
      terminalRef.current = null;
    };
  }, []);

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
    <section className="terminal-pane">
      <span className="terminal-pane__label">Terminal</span>
      <div className="terminal-pane__host" ref={terminalHostRef} />
    </section>
  );
});
