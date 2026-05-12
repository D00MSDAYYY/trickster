import { useState } from 'react';
import { Typography, Panel, CellList, CellSimple } from '@maxhub/max-ui';
import EditEventsPanel from '../components/AdminPanels/EditEventsPanel';
import ReportPanel from '../components/AdminPanels/ReportPanel';
import EditUsersPanel from '../components/AdminPanels/EditUsersPanel';

const AdminPage = () => {
  const [currentView, setCurrentView] = useState<
    'main' | 'editEvents' | 'createReport' | 'editUsers' | 'debugConsole'
  >('main');

  if (currentView === 'editEvents') {
    return <EditEventsPanel onBack={() => setCurrentView('main')} />;
  }

  if (currentView === 'createReport') {
    return <ReportPanel onBack={() => setCurrentView('main')} />;
  }

  if (currentView === 'editUsers') {
    return <EditUsersPanel onBack={() => setCurrentView('main')} />;
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
              title="Создать отчёт"
              showChevron
              onClick={() => setCurrentView('createReport')}
            />
            <CellSimple
              title="Редактировать мероприятия"
              showChevron
              onClick={() => setCurrentView('editEvents')}
            />
            <CellSimple
              title="Редактировать участников"
              showChevron
              onClick={() => setCurrentView('editUsers')}
            />
          </CellList>
        </div>
      </Panel>
    </div>
  );
};

export default AdminPage;