import React, { useEffect, useState } from "react";

interface NodeStatus {
  public_key: string;
  balance: number;
  unconfirmed_transactions_count: number;
}

interface Toast {
  id: string;
  message: string;
  type: "success" | "error" | "info";
}

export const NodeDashboard: React.FC = () => {
  const [status, setStatus] = useState<NodeStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Form states
  const [recipient, setRecipient] = useState<string>("");
  const [amount, setAmount] = useState<string>("");
  const [transferLoading, setTransferLoading] = useState<boolean>(false);
  const [mineLoading, setMineLoading] = useState<boolean>(false);

  // Toast state
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = (message: string, type: "success" | "error" | "info") => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      removeToast(id);
    }, 4000);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const fetchStatus = async (showLoading = false) => {
    try {
      if (showLoading) setLoading(true);
      const response = await fetch("http://localhost:8000/node/status");
      if (!response.ok) {
        throw new Error("Error al obtener el estado del nodo");
      }
      const data = await response.json();
      setStatus(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || "Conexión perdida con el nodo");
    } finally {
      if (showLoading) setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus(true);
    // Polling every 5 seconds
    const interval = setInterval(() => fetchStatus(false), 5000);
    return () => clearInterval(interval);
  }, []);

  const handleCopyAddress = () => {
    if (status?.public_key) {
      navigator.clipboard.writeText(status.public_key);
      addToast("Dirección pública copiada al portapapeles", "success");
    }
  };

  const handleMine = async () => {
    try {
      setMineLoading(true);
      const response = await fetch("http://localhost:8000/mine");
      if (!response.ok) {
        throw new Error("Error durante el minado");
      }
      const data = await response.json();
      if (data.message && data.message.includes("No hay transacciones")) {
        addToast(data.message, "info");
      } else {
        addToast("¡Bloque minado con éxito! Se han recibido 50.0 FAB", "success");
      }
      // Immediate status update
      fetchStatus(false);
    } catch (err: any) {
      addToast(err.message || "Error al conectar con el servidor", "error");
    } finally {
      setMineLoading(false);
    }
  };

  const handleTransfer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!recipient.trim()) {
      addToast("Por favor ingresa la dirección destino", "error");
      return;
    }
    const numAmount = parseFloat(amount);
    if (isNaN(numAmount) || numAmount <= 0) {
      addToast("Por favor ingresa una cantidad válida y mayor a 0", "error");
      return;
    }

    try {
      setTransferLoading(true);
      const response = await fetch("http://localhost:8000/node/transfer", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          recipient: recipient.trim(),
          amount: numAmount,
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Error al realizar la transferencia");
      }

      addToast("Transferencia añadida con éxito a la mempool", "success");
      setRecipient("");
      setAmount("");
      // Immediate status update
      fetchStatus(false);
    } catch (err: any) {
      addToast(err.message || "Error en la red", "error");
    } finally {
      setTransferLoading(false);
    }
  };

  const truncateAddress = (address: string) => {
    if (!address) return "";
    return `${address.slice(0, 10)}...${address.slice(-10)}`;
  };

  return (
    <div className="w-full max-w-7xl mx-auto px-6 space-y-8">
      {/* Top Header Card */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Panel del Operador</h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Gestiona la billetera residente del nodo y ejecuta el Proof-of-Work local.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => fetchStatus(true)}
            disabled={loading}
            className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-xs font-semibold transition-all duration-200"
          >
            {loading ? "Actualizando..." : "Actualizar"}
          </button>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-indigo-50 dark:bg-indigo-950/30 border border-indigo-200 dark:border-indigo-800 rounded-full text-xs font-semibold text-indigo-700 dark:text-indigo-400">
            <span className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></span>
            Autosincronización: 5s
          </div>
        </div>
      </div>

      {/* Main Grid for Cards */}
      {error && !status ? (
        <div className="bg-rose-50 dark:bg-rose-950/20 border border-rose-200 dark:border-rose-800 p-6 rounded-2xl text-center">
          <p className="text-rose-700 dark:text-rose-400 font-semibold">{error}</p>
          <button
            onClick={() => fetchStatus(true)}
            className="mt-4 px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-semibold transition-all"
          >
            Reintentar Conexión
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Card 1: Balance (Highlighted) */}
          <div className="bg-gradient-to-br from-purple-600 to-indigo-600 text-white p-6 rounded-2xl shadow-lg shadow-purple-500/10 flex flex-col justify-between min-h-[140px] relative overflow-hidden">
            <div className="absolute right-0 top-0 translate-x-4 -translate-y-4 w-28 h-28 bg-white/5 rounded-full blur-xl pointer-events-none"></div>
            <div>
              <span className="text-xs font-medium text-purple-200 uppercase tracking-wider">Saldo del Nodo</span>
              <h3 className="text-3xl font-extrabold mt-1 tracking-tight">
                {status ? `${status.balance.toFixed(4)}` : "0.0000"}{" "}
                <span className="text-xl font-normal text-purple-200">FAB</span>
              </h3>
            </div>
            <p className="text-xs text-purple-200 mt-4">
              Recompensas de minería acumuladas en este host.
            </p>
          </div>

          {/* Card 2: Wallet Address */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 rounded-2xl shadow-sm flex flex-col justify-between min-h-[140px]">
            <div>
              <span className="text-xs font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                Dirección Pública (Wallet)
              </span>
              <div className="flex items-center gap-2 mt-2">
                <span className="font-mono text-sm text-slate-800 dark:text-slate-200 select-all">
                  {status ? truncateAddress(status.public_key) : "Cargando..."}
                </span>
                {status?.public_key && (
                  <button
                    onClick={handleCopyAddress}
                    className="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 rounded-lg transition-colors"
                    title="Copiar dirección completa"
                  >
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      viewBox="0 0 24 24"
                    >
                      <path d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                    </svg>
                  </button>
                )}
              </div>
            </div>
            <p className="text-xs text-slate-400 dark:text-slate-500">
              Llave pública ECDSA residente usada para firmar transacciones.
            </p>
          </div>

          {/* Card 3: Pending Transactions */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 rounded-2xl shadow-sm flex flex-col justify-between min-h-[140px]">
            <div>
              <span className="text-xs font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                Mempool (Pendientes)
              </span>
              <h3 className="text-3xl font-bold text-slate-950 dark:text-slate-50 mt-1 tracking-tight">
                {status ? status.unconfirmed_transactions_count : 0}
              </h3>
            </div>
            <p className="text-xs text-slate-400 dark:text-slate-500">
              Transacciones esperando ser confirmadas en el próximo bloque.
            </p>
          </div>
        </div>
      )}

      {/* Actions and Form Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Miner Card (Col span 2) */}
        <div className="lg:col-span-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 rounded-2xl shadow-sm flex flex-col justify-between space-y-6">
          <div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white">Minería del Nodo</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Ejecuta el proceso Proof-of-Work en el nodo. Esto consolidará las transacciones del mempool y otorgará 50.0 FAB de recompensa.
            </p>
          </div>

          <div className="py-4 flex items-center justify-center">
            {/* Pickaxe Graphic Element */}
            <div className={`w-20 h-20 rounded-full bg-slate-50 dark:bg-slate-950 flex items-center justify-center border border-slate-100 dark:border-slate-800 shadow-inner relative ${mineLoading ? "animate-pulse" : ""}`}>
              <svg
                className={`w-10 h-10 text-slate-400 dark:text-slate-500 ${mineLoading ? "animate-spin text-teal-500" : ""}`}
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
                viewBox="0 0 24 24"
              >
                <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z" />
                <path d="M12 22V12m0 0l-8-4.62M12 12l8-4.62M12 12v-10" />
              </svg>
            </div>
          </div>

          <button
            onClick={handleMine}
            disabled={mineLoading || !status}
            className="w-full py-4 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white font-bold rounded-xl shadow-md shadow-teal-500/10 active:scale-[0.98] transition-all duration-200 disabled:opacity-50 disabled:pointer-events-none flex items-center justify-center gap-2 text-sm"
          >
            {mineLoading ? (
              <>
                <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Minando Bloque...
              </>
            ) : (
              "Minar Bloque"
            )}
          </button>
        </div>

        {/* Transfer Form (Col span 3) */}
        <div className="lg:col-span-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 rounded-2xl shadow-sm flex flex-col justify-between space-y-6">
          <div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white">Transferencia Local</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Envía fondos desde la billetera de este nodo operador. Las transacciones se firman automáticamente y se envían a la red.
            </p>
          </div>

          <form onSubmit={handleTransfer} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-1.5">
                Dirección Destino
              </label>
              <input
                type="text"
                value={recipient}
                onChange={(e) => setRecipient(e.target.value)}
                placeholder="Ej. d5f7...f9a4"
                className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition-all duration-200 text-sm font-mono placeholder:text-slate-400"
                disabled={transferLoading || !status}
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-1.5">
                Monto (FAB)
              </label>
              <input
                type="number"
                step="any"
                min="0"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="Ej. 10.0"
                className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition-all duration-200 text-sm font-mono placeholder:text-slate-400"
                disabled={transferLoading || !status}
              />
            </div>
            <button
              type="submit"
              disabled={transferLoading || !status}
              className="w-full py-3.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-bold rounded-xl shadow-md shadow-purple-500/10 active:scale-[0.98] transition-all duration-200 disabled:opacity-50 disabled:pointer-events-none flex items-center justify-center gap-2 text-sm"
            >
              {transferLoading ? (
                <>
                  <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Procesando Transferencia...
                </>
              ) : (
                "Enviar Transferencia"
              )}
            </button>
          </form>
        </div>
      </div>

      {/* Floating Toast System */}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-3 max-w-sm w-full pointer-events-none">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`pointer-events-auto p-4 rounded-xl shadow-lg text-white text-xs font-semibold flex items-center justify-between gap-3 animate-slide-up transition-all duration-300 ${
              toast.type === "success"
                ? "bg-emerald-500"
                : toast.type === "error"
                ? "bg-rose-500"
                : "bg-blue-500"
            }`}
          >
            <div className="flex-1 pr-2">{toast.message}</div>
            <button
              onClick={() => removeToast(toast.id)}
              className="text-white/75 hover:text-white transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
                <path d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
