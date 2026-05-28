import { useEffect, useState } from 'react';

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'info';
  text: string;
}

interface ToastProps {
  messages: ToastMessage[];
  onDismiss: (id: string) => void;
}

const STYLES: Record<string, string> = {
  success: 'bg-green-600 text-white',
  error: 'bg-red-600 text-white',
  info: 'bg-blue-600 text-white',
};

function ToastItem({ msg, onDismiss }: { msg: ToastMessage; onDismiss: () => void }) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    requestAnimationFrame(() => setVisible(true));
    const t = setTimeout(() => {
      setVisible(false);
      setTimeout(onDismiss, 300);
    }, 4000);
    return () => clearTimeout(t);
  }, [onDismiss]);

  return (
    <div
      className={`px-4 py-3 rounded-lg shadow-lg text-sm font-medium transition-all duration-300 ${STYLES[msg.type]} ${
        visible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'
      }`}
    >
      {msg.text}
    </div>
  );
}

export default function Toast({ messages, onDismiss }: ToastProps) {
  if (messages.length === 0) return null;
  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm">
      {messages.map((m) => (
        <ToastItem key={m.id} msg={m} onDismiss={() => onDismiss(m.id)} />
      ))}
    </div>
  );
}
