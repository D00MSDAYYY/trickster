import { useState } from 'react';
import { EventCard, EventInfo } from '../components/EventCard/EventCard';
import { EventInfoDisplayer } from '../components/EventInfoDisplayer';

const mockEvents: EventInfo[] = [
  { name: 'Конференция по React', tags: ['React', 'Frontend'], is_registered: false, points: 150 },
  { name: 'Воркшоп по FastAPI', tags: ['Python', 'Backend', 'API'], is_registered: true, points: 200 },
  { name: 'Встреча сообщества VK Mini Apps', tags: ['VK', 'Mini Apps', 'Сообщество'], is_registered: false, points: 75 },
  { name: 'Встреча сообщества VK Mini Apps', tags: ['VK', 'Mini Apps', 'Сообщество'], is_registered: false, points: 75 },
  { name: 'Встреча сообщества VK Mini Apps', tags: ['VK', 'Mini Apps', 'Сообщество'], is_registered: false, points: 75 },
  { name: 'Встреча сообщества VK Mini Apps', tags: ['VK', 'Mini Apps', 'Сообщество'], is_registered: false, points: 75 },
  { name: 'Встреча сообщества VK Mini Apps', tags: ['VK', 'Mini Apps', 'Сообщество'], is_registered: false, points: 75 },
  { name: 'Встреча сообщества VK Mini Apps', tags: ['VK', 'Mini Apps', 'Сообщество'], is_registered: false, points: 75 },
  { name: 'Встреча сообщества VK Mini Apps', tags: ['VK', 'Mini Apps', 'Сообщество'], is_registered: false, points: 75 },
  { name: 'Встреча сообщества VK Mini Apps', tags: ['VK', 'Mini Apps', 'Сообщество'], is_registered: false, points: 75 },
];

const HomePage = () => {
  const [selectedEvent, setSelectedEvent] = useState<EventInfo | null>(null);

  const handleMoreClick = (event: EventInfo) => setSelectedEvent(event);
  const handleBack = () => setSelectedEvent(null);
  const handleRegisterSwapped = (eventName: string) => console.log(`Зарегистрирован: ${eventName}`);
  const handleUnregisterSwapped = (eventName: string) => console.log(`Отмена: ${eventName}`);

  if (selectedEvent) {
    return <EventInfoDisplayer eventName={selectedEvent.name} onBack={handleBack} />;
  }

  return (
    <>
      {mockEvents.map((event) => (
        <EventCard
          key={event.name}
          eventInfo={event}
          onMoreClick={() => handleMoreClick(event)}
          onRegisterSwapped={() => handleRegisterSwapped(event.name)}
          onUnregisterSwapped={() => handleUnregisterSwapped(event.name)}
        />
      ))}
    </>
  );
};

export default HomePage;