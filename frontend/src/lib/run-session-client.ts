export type RunSessionClientEvents = {
  onStdout?: (data: string) => void;
  onEvent?: (payload: Record<string, unknown>) => void;
};

export type RunSessionClient = {
  start: (code: string) => void;
  sendStdin: (data: string) => void;
  stop: () => void;
};

function buildRunSessionWsUrl() {
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  return `${protocol}://${window.location.host}/ws/run`;
}

export function createRunSessionClient(events: RunSessionClientEvents = {}): RunSessionClient {
  let socket: WebSocket | null = null;
  let pendingCode: string | null = null;

  function ensureConnected() {
    if (socket && socket.readyState <= WebSocket.OPEN) return;
    socket = new WebSocket(buildRunSessionWsUrl());
    socket.onopen = () => {
      if (pendingCode !== null) {
        socket?.send(JSON.stringify({ type: "compile_and_run", code: pendingCode }));
        pendingCode = null;
      }
    };
    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(String(event.data)) as Record<string, unknown>;
        events.onEvent?.(payload);
        if (payload.type === "stdout" && typeof payload.data === "string") {
          events.onStdout?.(payload.data);
        }
      } catch {
        return;
      }
    };
  }

  return {
    start(code: string) {
      pendingCode = code;
      ensureConnected();
      if (socket?.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: "compile_and_run", code }));
        pendingCode = null;
      }
    },
    sendStdin(data: string) {
      if (socket?.readyState !== WebSocket.OPEN) return;
      socket.send(JSON.stringify({ type: "stdin", data }));
    },
    stop() {
      if (!socket) return;
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: "stop" }));
      }
      socket.close();
      socket = null;
      pendingCode = null;
    },
  };
}
