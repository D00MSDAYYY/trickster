import { useState } from 'react';
import { Flex, Panel, Tappable, IconButton, Typography } from '@maxhub/max-ui';
import Sidebar from './Sidebar';

// Заглушки иконок для хедера
const AccountIcon = () => <span style={{ fontSize: 24 }}>👤</span>;
const NotificationsIcon = () => <span style={{ fontSize: 24 }}>🔔</span>;

const Layout = ({ children }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const toggleSidebar = () => setIsSidebarOpen(!isSidebarOpen);
  const closeSidebar = () => setIsSidebarOpen(false);

  // Определяем мобильное устройство по ширине окна
  const isMobile = window.innerWidth < 768;

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* Десктопный сайдбар — всегда видимый на больших экранах */}
      {!isMobile && (
        <aside style={{ flexShrink: 0 }}>
          <Sidebar />
        </aside>
      )}

      {/* Мобильный сайдбар — выезжающая панель */}
      {isMobile && isSidebarOpen && (
        <>
          <Tappable
            onClick={closeSidebar}
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'rgba(0,0,0,0.5)',
              zIndex: 100,
            }}
          />
          <Panel
            mode="primary"
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              bottom: 0,
              width: 280,
              zIndex: 101,
              padding: 0,
              overflowY: 'auto',
            }}
          >
            <Sidebar onClose={closeSidebar} />
          </Panel>
        </>
      )}

      {/* Основной контент */}
      <main style={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Хедер с кнопками */}
        <header style={{ 
          padding: '12px 16px', 
          borderBottom: '1px solid var(--separator_common)',
          background: 'var(--background_content)'
        }}>
          <Flex justify="space-between" align="center">
            <IconButton onClick={toggleSidebar}>
              <AccountIcon />
            </IconButton>
            <Typography.Title variant="medium-strong">События</Typography.Title>
            <IconButton>
              <NotificationsIcon />
            </IconButton>
          </Flex>
        </header>

        {/* Область для страниц */}
        <div style={{ padding: 16 }}>
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;