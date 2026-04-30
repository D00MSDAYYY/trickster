import { useState } from 'react';
import { Typography, Panel, CellList, CellSimple } from '@maxhub/max-ui';
import EditEventsPanel from '../components/AdminPanels/EditEventsPanel';


const AdminPage = () => {
  const [currentView, setCurrentView] = useState<'main' | 'editEvents' | 'debugConsole'>('main');

  if (currentView === 'editEvents') {
    return <EditEventsPanel onBack={() => setCurrentView('main')} />;
  }


  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Panel
        mode="primary"
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          padding: 20,
          borderRadius: 16,
          overflow: 'hidden',
        }}
      >
        <div style={{ flex: 1, overflowY: 'auto' }}>
          <CellList>
            <CellSimple
              title="Редактировать мероприятия"
              showChevron
              onClick={() => setCurrentView('editEvents')}
            />
            <CellSimple
              title="Консоль отладки"
              showChevron
              onClick={() => setCurrentView('debugConsole')}
            />
          </CellList>
        </div>
      </Panel>
    </div>
  );
};



export default AdminPage;