import React, { useEffect, useState } from "react";

export interface Transaction {
  sender: string;
  recipient: string;
  amount: number;
  timestamp: number;
  id: string;
  signature: string;
}

export interface Block {
  index: number;
  timestamp: number;
  transactions: Transaction[];
  previous_hash: string;
  nonce: number;
  hash: string;
}

export const BlockExplorer: React.FC = () => {
  const [blocks, setBlocks] = useState<Block[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedBlock, setExpandedBlock] = useState<number | null>(null);

  const fetchChain = async () => {
    try {
      setLoading(true);
      const response = await fetch("http://localhost:8000/chain");
      if (!response.ok) {
        throw new Error("Error al consultar la cadena de bloques");
      }
      const data = await response.json();
      setBlocks(data.chain || []);
      setError(null);
    } catch (err: any) {
      setError(err.message || "Error de conexión con el nodo");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchChain();
    // Auto-refresh every 10 seconds for real-time vibe
    const interval = setInterval(fetchChain, 10000);
    return () => clearInterval(interval);
  }, []);

  const truncateHash = (hash: string) => {
    if (!hash || hash === "0") return hash;
    if (hash.length <= 12) return hash;
    return `${hash.slice(0, 6)}...${hash.slice(-6)}`;
  };

  const formatDate = (timestamp: number) => {
    // Check if timestamp is in seconds or milliseconds
    const date = new Date(timestamp * 1000);
    return date.toLocaleString();
  };

  return (
    <div className="w-full max-w-7xl mx-auto p-6 space-y-8">
      {/* Header section with Node status */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-gray-200 dark:border-gray-800 pb-6">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 dark:text-white bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
            Explorador de Bloques FabiCoin
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Visualiza el estado actual, las transacciones y la inmutabilidad de la red en tiempo real.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchChain}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg font-medium shadow-md hover:from-purple-700 hover:to-indigo-700 transition-all duration-200"
          >
            Sincronizar
          </button>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-800 rounded-full text-xs font-semibold text-green-700 dark:text-green-400">
            <span className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse"></span>
            Conectado al Nodo
          </div>
        </div>
      </div>

      {/* Loading state */}
      {loading && blocks.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 space-y-4">
          <div className="w-12 h-12 border-4 border-purple-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-gray-500 dark:text-gray-400 font-medium">
            Cargando cadena de bloques...
          </p>
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 rounded-xl flex items-center gap-3 text-red-700 dark:text-red-400">
          <svg className="w-6 h-6 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div>
            <p className="font-semibold">Error de Conexión</p>
            <p className="text-sm opacity-90">{error}. Verifica que el backend esté corriendo en http://localhost:8000.</p>
          </div>
        </div>
      )}

      {/* Blocks Grid */}
      {!loading && blocks.length === 0 && !error && (
        <div className="text-center py-20 bg-gray-50 dark:bg-gray-900 rounded-2xl border-2 border-dashed border-gray-200 dark:border-gray-800">
          <p className="text-gray-500 dark:text-gray-400 font-semibold text-lg">
            La blockchain está vacía o no tiene bloques.
          </p>
        </div>
      )}

      {blocks.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {blocks.map((block) => (
            <div
              key={block.index}
              className="bg-white dark:bg-gray-950 border border-gray-150 dark:border-gray-850 rounded-2xl shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all duration-300 flex flex-col justify-between overflow-hidden"
            >
              <div className="p-6 space-y-4">
                {/* Card Header */}
                <div className="flex items-center justify-between">
                  <span className="px-3 py-1 bg-gradient-to-r from-purple-500 to-indigo-500 text-white font-bold text-xs rounded-full uppercase tracking-wider shadow-sm">
                    Bloque #{block.index}
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400 font-semibold">
                    Nonce: {block.nonce}
                  </span>
                </div>

                {/* Block hashes info */}
                <div className="space-y-2">
                  <div>
                    <span className="text-xs text-gray-400 font-medium block">HASH</span>
                    <code className="text-sm font-mono font-bold text-gray-800 dark:text-gray-200 bg-gray-100 dark:bg-gray-900 px-2 py-1 rounded select-all break-all block">
                      {truncateHash(block.hash)}
                    </code>
                  </div>
                  <div>
                    <span className="text-xs text-gray-400 font-medium block">PREVIOUS HASH</span>
                    <code className="text-xs font-mono text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-900/50 px-2 py-1 rounded select-all break-all block">
                      {truncateHash(block.previous_hash)}
                    </code>
                  </div>
                </div>

                {/* Details list */}
                <div className="grid grid-cols-2 gap-4 py-2 border-t border-b border-gray-100 dark:border-gray-900 text-xs">
                  <div>
                    <span className="text-gray-400 font-medium block">FECHA</span>
                    <span className="font-semibold text-gray-700 dark:text-gray-300">
                      {formatDate(block.timestamp)}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-400 font-medium block">TRANSACCIONES</span>
                    <span className="font-semibold text-gray-700 dark:text-gray-300">
                      {block.transactions.length}{" "}
                      {block.transactions.length === 1 ? "Tx" : "Txs"}
                    </span>
                  </div>
                </div>
              </div>

              {/* Transactions Expander (If any) */}
              {block.transactions.length > 0 ? (
                <div className="border-t border-gray-100 dark:border-gray-900 bg-gray-50 dark:bg-gray-900/30">
                  <button
                    onClick={() =>
                      setExpandedBlock(
                        expandedBlock === block.index ? null : block.index
                      )
                    }
                    className="w-full px-6 py-3 text-xs font-semibold text-purple-600 dark:text-purple-400 hover:text-purple-700 hover:bg-gray-100 dark:hover:bg-gray-900/60 transition-all flex items-center justify-between"
                  >
                    <span>
                      {expandedBlock === block.index
                        ? "Ocultar Transacciones"
                        : "Ver Transacciones"}
                    </span>
                    <svg
                      className={`w-4 h-4 transition-transform duration-200 ${
                        expandedBlock === block.index ? "rotate-180" : ""
                      }`}
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>

                  {/* Render transactions details if expanded */}
                  {expandedBlock === block.index && (
                    <div className="px-6 pb-4 pt-2 border-t border-gray-100 dark:border-gray-900 divide-y divide-gray-100 dark:divide-gray-900 text-xs">
                      {block.transactions.map((tx, idx) => (
                        <div key={tx.id || idx} className="py-2.5 space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="font-mono text-purple-500 font-semibold">
                              TX #{idx + 1}
                            </span>
                            <span className="font-bold text-gray-800 dark:text-gray-200">
                              {tx.amount} FAB
                            </span>
                          </div>
                          <div className="grid grid-cols-1 gap-0.5 text-[10px] text-gray-500 dark:text-gray-400 font-mono">
                            <span className="truncate">FROM: {tx.sender}</span>
                            <span className="truncate">TO: {tx.recipient}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <div className="px-6 py-3 bg-gray-50 dark:bg-gray-900/20 text-center text-xs text-gray-400 font-medium border-t border-gray-100 dark:border-gray-900">
                  Bloque vacío (sin transacciones)
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
