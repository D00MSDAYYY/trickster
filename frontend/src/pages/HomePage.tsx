import { EventCard, EventInfo } from '../components/EventCard/EventCard';

const mockEvents: EventInfo[] = [
  {
    name: 'Конференция по React',
    tags: ['React', 'Frontend'],
    is_registered: false,
    points: 150,
  },
  {
    name: 'Воркшоп по FastAPI',
    tags: ['Python', 'Backend', 'API'],
    is_registered: true,
    points: 200,
  },
  {
    name: 'Встреча сообщества VK Mini Apps',
    tags: ['VK', 'Mini Apps', 'Сообщество'],
    is_registered: false,
    points: 75,
  },
];

const HomePage = () => {
  const handleMoreClick = (eventName: string) => {
    console.log(`Переход к событию: ${eventName}`);
  };

  const handleRegister = (eventName: string) => {
    console.log(`Зарегистрирован на: ${eventName}`);
  };

  const handleUnregister = (eventName: string) => {
    console.log(`Отмена регистрации: ${eventName}`);
  };

  return (
    <div>
      {mockEvents.map((event) => (
        <EventCard
          key={event.name}
          eventInfo={event}
          onMoreClick={() => handleMoreClick(event.name)}
          onRegisterSwapped={() => handleRegister(event.name)}
          onUnregisterSwapped={() => handleUnregister(event.name)}
        />
      ))}
    </div>
  );
};

// 👇 Вот эта строка решает проблему
export default HomePage;