import { useState, useEffect } from 'react';
import { MaxUI } from '@maxhub/max-ui';
import Layout from './components/Layout';
import LoginScreen from './components/LoginScreen';
import { UserProfile } from './api/types';

function App() {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [checking, setChecking] = useState(true);

  // Функция проверки сессии
  const checkSession = async () => {
    try {
      const res = await fetch('/api/profile', {
        credentials: 'include',
      });
      if (res.ok) {
        const data = await res.json();
        setUser(data);
      } else {
        setUser(null);
      }
    } catch {
      setUser(null);
    } finally {
      setChecking(false);
    }
  };

  // Проверяем сессию при загрузке и при фокусе окна
  useEffect(() => {
    checkSession();
    window.addEventListener('focus', checkSession);
    return () => window.removeEventListener('focus', checkSession);
  }, []);

  if (checking) {
    return (
      <MaxUI colorScheme="light">
        <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          Проверка сессии...
        </div>
      </MaxUI>
    );
  }

  if (!user) {
    return (
      <MaxUI colorScheme="light">
        <LoginScreen onLogin={(userData) => setUser(userData)} />
      </MaxUI>
    );
  }

  return (
    <MaxUI colorScheme="light">
      <Layout user={user} />
    </MaxUI>
  );
}

export default App;