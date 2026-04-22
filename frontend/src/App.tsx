import { MaxUI } from '@maxhub/max-ui';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';

function App() {
  return (
    <MaxUI colorScheme="light">
      <Layout>
        <HomePage />
      </Layout>
    </MaxUI>
  );
}

export default App;