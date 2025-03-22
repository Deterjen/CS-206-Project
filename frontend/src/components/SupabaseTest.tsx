"use client"
import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';

export default function SupabaseTest() {
  const [status, setStatus] = useState<'loading' | 'connected' | 'error'>('loading');
  const [errorMessage, setErrorMessage] = useState<string>('');

  useEffect(() => {
    async function testConnection() {
      try {
        // Try to get the current timestamp from Supabase
        const { data, error } = await supabase.from('_realtime').select('*').limit(1);
        
        if (error) {
          setStatus('error');
          setErrorMessage(error.message);
        } else {
          setStatus('connected');
        }
      } catch (err) {
        setStatus('error');
        setErrorMessage(err instanceof Error ? err.message : 'Unknown error occurred');
      }
    }

    testConnection();
  }, []);

  return (
    <div className="p-4 m-4 border rounded-lg">
      <h2 className="text-lg font-bold mb-2">Supabase Connection Status</h2>
      <div className="flex items-center gap-2">
        <div className={`w-3 h-3 rounded-full ${
          status === 'loading' ? 'bg-yellow-500' :
          status === 'connected' ? 'bg-green-500' :
          'bg-red-500'
        }`} />
        <span>{status === 'loading' ? 'Testing connection...' :
               status === 'connected' ? 'Connected to Supabase!' :
               `Error: ${errorMessage}`}</span>
      </div>
    </div>
  );
} 