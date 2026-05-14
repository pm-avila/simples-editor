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
      fontFamily: '"Share Tech Mono", "Cascadia Code", "Fira Code", Menlo, Consolas, monospace',
      fontSize: 13,
      lineHeight: 1.2,
      cursorStyle: 'block',
      theme: {
        background: '#0a0800',
        foreground: '#ffb000',
        cursor: '#ffb000',
        cursorAccent: '#0a0800',
        selectionBackground: 'rgba(255, 176, 0, 0.3)',
        black: '#0a0800',
        red: '#ff6b6b',
        green: '#ffb000',
        yellow: '#ff9000',
        blue: '#ffb000',
        magenta: '#ff9000',
        cyan: '#ffb000',
        white: '#ffb000',
        brightBlack: '#cc6600',
        brightRed: '#ff9000',
        brightGreen: '#ffb000',
        brightYellow: '#ffb000',
        brightBlue: '#ffb000',
        brightMagenta: '#ffb000',
        brightCyan: '#ffb000',
        brightWhite: '#ffb000',
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
