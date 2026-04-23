import { useState } from 'react';
import { EventCard, EventInfo } from '../components/EventCard/EventCard';
import { EventInfoDisplayer } from '../components/EventInfoDisplayer';


interface EventPageProps {
  events: EventInfo[];
}

const EventsPage = ({ events }: EventPageProps) => {
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
      {events.map((event) => (
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

export default EventsPage;