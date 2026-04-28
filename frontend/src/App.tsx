import { useState } from 'react';
import { MaxUI } from '@maxhub/max-ui';
import Layout from './components/Layout';
import LoginScreen from './components/LoginScreen';

export interface UserData {
  nickname: string;
  points: number;
  company: string;
}

function App() {
  const [user, setUser] = useState<UserData | null>(null);

  if (!user) {
    return (
      <MaxUI platform="ios" colorScheme="light">
        <LoginScreen onLogin={(userData) => setUser(userData)} />
      </MaxUI>
    );
  }

  return (
    <MaxUI platform="ios" colorScheme="light">
      <Layout user={user} />
    </MaxUI>
    
  );
}

export default App;