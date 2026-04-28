import { useState, useEffect } from 'react';
import { EventCard, EventInfo } from '../components/EventCard/EventCard';
import { EventInfoDisplayer } from '../components/EventInfoDisplayer';

const EventsPage = () => {
  const [events, setEvents] = useState<EventInfo[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<EventInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Загрузка событий с сервера
  useEffect(() => {
    const fetchEvents = async () => {
      try {
        setLoading(true);
        const res = await fetch('/api/events', {
          credentials: 'include', // отправляем куки сессии
        });
        if (!res.ok) {
          throw new Error('Ошибка загрузки событий');
        }
        const data: EventInfo[] = await res.json();
        setEvents(data);
      } catch (err: any) {
        setError(err.message || 'Неизвестная ошибка');
      } finally {
        setLoading(false);
      }
    };
    fetchEvents();
  }, []);

  const handleMoreClick = (event: EventInfo) => setSelectedEvent(event);
  const handleBack = () => setSelectedEvent(null);

  const handleRegisterSwapped = async (eventId: number) => {
    try {
      await fetch(`/api/events/${eventId}/register`, {
        method: 'POST',
        credentials: 'include',
      });
      // Обновляем локальное состояние: помечаем событие как зарегистрированное
      setEvents(prev => prev.map(e => e.id === eventId ? { ...e, is_registered: true } : e));
      console.log(`Зарегистрирован на событие ${eventId}`);
    } catch (err) {
      console.error('Ошибка регистрации', err);
    }
  };

  const handleUnregisterSwapped = async (eventId: number) => {
    try {
      await fetch(`/api/events/${eventId}/register`, {
        method: 'DELETE',
        credentials: 'include',
      });
      setEvents(prev => prev.map(e => e.id === eventId ? { ...e, is_registered: false } : e));
      console.log(`Отмена регистрации на событие ${eventId}`);
    } catch (err) {
      console.error('Ошибка отмены регистрации', err);
    }
  };

  if (loading) return <div style={{ padding: 16 }}>Загрузка событий...</div>;
  if (error) return <div style={{ padding: 16, color: 'red' }}>Ошибка: {error}</div>;

  if (selectedEvent) {
    return <EventInfoDisplayer eventName={selectedEvent.name} onBack={handleBack} />;
  }

  return (
    <>
      {events.map((event) => (
        <EventCard
          key={event.id}
          eventInfo={event}
          onMoreClick={() => handleMoreClick(event)}
          onRegisterSwapped={() => handleRegisterSwapped(event.id)}
          onUnregisterSwapped={() => handleUnregisterSwapped(event.id)}
        />
      ))}
    </>
  );
};

export default EventsPage;