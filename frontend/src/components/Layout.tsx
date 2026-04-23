import { useState } from 'react';
import { IconButton, Typography } from '@maxhub/max-ui';
import EventsPage from '../pages/EventsPage';
import { EventInfo } from './EventCard/EventCard';
import ProfilePage from '../pages/ProfilePage';
import NotificationsPage from '../pages/NotificationsPage';
import AdminPage from '../pages/AdminPage';

const mockEvents: EventInfo[] = [
  {
    name: 'Конференция по React',
    tags: ['React', 'Frontend'],
    is_registered: false,
    points: 150,
    date: '25 мая 2025, 10:00',
  },
  {
    name: 'Воркшоп по FastAPI',
    tags: ['Python', 'Backend', 'API'],
    is_registered: true,
    points: 200,
    date: '27 мая 2025, 14:00',
  },
  {
    name: 'Встреча сообщества VK Mini Apps',
    tags: ['VK', 'Mini Apps', 'Сообщество'],
    is_registered: false,
    points: 75,
    date: '30 мая 2025, 18:30',
  },
  {
    name: 'Хакатон по мобильной разработке',
    tags: ['iOS', 'Android', 'Flutter'],
    is_registered: true,
    points: 300,
    date: '1–3 июня 2025',
  },
  {
    name: 'Лекция по дизайну интерфейсов',
    tags: ['UI/UX', 'Figma', 'Проектирование'],
    is_registered: false,
    points: 120,
    date: '5 июня 2025, 16:00',
  },
  {
    name: 'Курс по Docker и Kubernetes',
    tags: ['DevOps', 'Контейнеры', 'Оркестрация'],
    is_registered: false,
    points: 250,
    date: '10 июня 2025, 19:00',
  },
  {
    name: 'Вебинар по карьере в IT',
    tags: ['Резюме', 'Собеседования', 'Soft Skills'],
    is_registered: true,
    points: 50,
    date: '12 июня 2025, 20:00',
  },
  {
    name: 'Открытие летнего IT-лагеря',
    tags: ['Обучение', 'Нетворкинг', 'Активный отдых'],
    is_registered: false,
    points: 180,
    date: '15 июня 2025',
  },
  {
    name: 'Соревнования по спортивному программированию',
    tags: ['Алгоритмы', 'C++', 'Python'],
    is_registered: false,
    points: 400,
    date: '20 июня 2025, 11:00',
  },
  {
    name: 'Мастер-класс по публичным выступлениям',
    tags: ['Ораторство', 'Презентации', 'Коммуникация'],
    is_registered: false,
    points: 90,
    date: '22 июня 2025, 17:00',
  },
];

const AdminIcon = () => <span style={{ fontSize: 24 }}>🔧</span>;
const AccountIcon = () => <span style={{ fontSize: 24 }}>👤</span>;
const NotificationsIcon = () => <span style={{ fontSize: 24 }}>🔔</span>;
const EventIcon = () => <span style={{ fontSize: 24 }}>🎉</span>;

const Layout = () => {
  const [currentPage, setCurrentPage] = useState('home');

  const handleEventClick = () => setCurrentPage('home');
  const handleProfileClick = () => setCurrentPage('profile');
  const handleNotificationsClick = () => {
    setCurrentPage('notifications');
  };
  const handleAdminClick = () => setCurrentPage('admin');

  const activeButtonStyle = {
    filter: 'brightness(0.85)',
    background: 'rgba(0, 0, 0, 0.05)',
    transition: 'filter 0.2s ease, background 0.2s ease',
  };

  const pageBackground = 'rgba(0, 0, 0, 0.05)';

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <main style={{
        flexGrow: 1,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        height: '100vh', // фиксируем высоту на весь экран
      }}>
        <header style={{
          padding: '12px 16px',
          borderBottom: '1px solid var(--separator_common)',
          background: 'var(--background_content)',
          flexShrink: 0,
        }}>
          <Typography.Title variant="medium-strong" style={{ textAlign: 'center' }}>
            {currentPage === 'home' && 'События'}
            {currentPage === 'profile' && 'Профиль'}
            {currentPage === 'notifications' && 'Уведомления'}
            {currentPage === 'admin' && 'Панель администратора'}

          </Typography.Title>
        </header>

        {/* Область с прокруткой */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          background: pageBackground,
          transition: 'background 0.2s ease',
        }}>
          <div style={{ padding: 16 }}>
            {currentPage === 'admin' && <AdminPage />}
            {currentPage === 'profile' && <ProfilePage nickname="ivanov" points={150} />}
            {currentPage === 'home' && <EventsPage events={mockEvents} />}
            {currentPage === 'notifications' && <NotificationsPage />}
          </div>
        </div>

        <footer style={{
          display: 'flex',
          background: 'transparent',
          flexShrink: 0,
          height: '55px',              // фиксированная высота футера
          alignItems: 'stretch',       // чтобы кнопки растягивались на всю высоту
          boxShadow: '0 -2px 8px rgba(0, 0, 0, 0.15)'
        }}>
          <div style={{ flex: 1, display: 'flex', justifyContent: 'center' }}>
            <IconButton
              onClick={handleAdminClick}
              style={{
                width: '100%',
                height: '100%',         // кнопка занимает всю высоту футера
                ...(currentPage === 'admin' ? activeButtonStyle : {})
              }}
            >
              <AdminIcon />
            </IconButton>
          </div>

          <div style={{ flex: 1, display: 'flex', justifyContent: 'center' }}>
            <IconButton
              onClick={handleProfileClick}
              style={{
                width: '100%',
                height: '100%',         // кнопка занимает всю высоту футера
                ...(currentPage === 'profile' ? activeButtonStyle : {})
              }}
            >
              <AccountIcon />
            </IconButton>
          </div>
          <div style={{ flex: 1, display: 'flex', justifyContent: 'center' }}>
            <IconButton
              onClick={handleEventClick}
              style={{
                width: '100%',
                height: '100%',
                ...(currentPage === 'home' ? activeButtonStyle : {})
              }}
            >
              <EventIcon />
            </IconButton>
          </div>
          <div style={{ flex: 1, display: 'flex', justifyContent: 'center' }}>
            <IconButton
              onClick={handleNotificationsClick}
              style={{
                width: '100%',
                height: '100%',
                ...(currentPage === 'notifications' ? activeButtonStyle : {})
              }}
            >
              <NotificationsIcon />
            </IconButton>
          </div>

        </footer>
      </main>
    </div>
  );
};

export default Layout;