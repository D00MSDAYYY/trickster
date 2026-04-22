import { EventCard, EventInfo } from '../components/EventCard/EventCard';

const mockEvents: EventInfo[] = [
  {
    name: 'Конференция по React',
    tags: ['React', 'Frontend'],
    points: 150,
  },
  {
    name: 'Воркшоп по FastAPI',
    tags: ['Python', 'Backend', 'API'],
    points: 200,
  },
  {
    name: 'Встреча сообщества VK Mini Apps',
    tags: ['VK', 'Mini Apps', 'Сообщество'],
    points: 75,
  },
];

const HomePage = () => {
  const handleMoreClick = (eventName: string) => {
    console.log(`Переход к событию: ${eventName}`);
  };

  return (
    <div>
      {mockEvents.map((event) => (
        <EventCard
          key={event.name}
          eventInfo={event}
          onMoreClick={() => handleMoreClick(event.name)}
        />
      ))}
    </div>
  );
};

export default HomePage;