import { contextBridge, ipcRenderer } from 'electron';

// Expose a limited, type‑safe API to the renderer process.
// All calls go through ipcRenderer.invoke which forwards to the main process.

const api = {
  // ---------- Agent actions ----------
  runMission: async (input: string) => {
    return await ipcRenderer.invoke('agent:run', input);
  },
  cancelMission: async () => {
    return await ipcRenderer.invoke('agent:cancel');
  },

  // ---------- Memory actions ----------
  getMemory: async () => {
    return await ipcRenderer.invoke('memory:get');
  },
  getFacts: async () => {
    return await ipcRenderer.invoke('memory:facts');
  },
  clearMemory: async () => {
    return await ipcRenderer.invoke('memory:clear');
  },
  resetAll: async () => {
    return await ipcRenderer.invoke('memory:reset');
  },

  // ---------- System actions ----------
  getOllamaStatus: async () => {
    return await ipcRenderer.invoke('system:ollama-status');
  },

  // ---------- Event listeners (streaming) ----------
  onAgentStep: (callback: (data: any) => void) => {
    const listener = (_event: any, payload: any) => callback(payload);
    ipcRenderer.on('agent:step', listener);
    return () => ipcRenderer.removeListener('agent:step', listener);
  },
  onAgentLog: (callback: (data: any) => void) => {
    const listener = (_event: any, payload: any) => callback(payload);
    ipcRenderer.on('agent:log', listener);
    return () => ipcRenderer.removeListener('agent:log', listener);
  },
  onAgentDone: (callback: (data: any) => void) => {
    const listener = (_event: any, payload: any) => callback(payload);
    ipcRenderer.on('agent:done', listener);
    return () => ipcRenderer.removeListener('agent:done', listener);
  }
};

contextBridge.exposeInMainWorld('kiraAPI', api);
