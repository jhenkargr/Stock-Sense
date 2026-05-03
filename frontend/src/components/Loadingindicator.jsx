import React from 'react';
import { Zap } from 'lucide-react';

const LoadingIndicator = () => {
  return (
    <div className="flex flex-col items-center justify-center py-24 gap-6 animate-in fade-in duration-300">
      <div className="relative">
        <div className="w-16 h-16 border-[1px] border-cyan-900 rounded-full" />
        <div className="absolute inset-0 border-t-2 border-cyan-400 rounded-full animate-spin" />
        <Zap className="absolute inset-0 m-auto w-6 h-6 text-cyan-500" />
      </div>
      <p className="text-cyan-600 tracking-[0.4em] text-[10px] font-black uppercase">
        DECRYPTING SECTOR DATA...
      </p>
    </div>
  );
};

export default LoadingIndicator;
