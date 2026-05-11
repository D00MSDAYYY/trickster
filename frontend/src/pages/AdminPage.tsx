import { useState } from 'react';
import { Typography, Panel, CellList, CellSimple } from '@maxhub/max-ui';
import EditEventsPanel from '../components/AdminPanels/EditEventsPanel';
import ReportPanel from '../components/AdminPanels/ReportPanel';

const AdminPage = () => {
  const [currentView, setCurrentView] = useState<'main' | 'editEvents' | 'createReport' | 'debugConsole'>('main');

  if (currentView === 'editEvents') {
    return <EditEventsPanel onBack={() => setCurrentView('main')} />;
  }

  if (currentView === 'createReport') {
    return <ReportPanel onBack={() => setCurrentView('main')} />;
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
        <Typography.Title variant="medium-strong" style={{ marginBottom: 16 }}>
          Администрирование
        </Typography.Title>

        <div style={{ flex: 1, overflowY: 'auto' }}>
          <CellList>
            <CellSimple
              title="Редактировать мероприятия"
              showChevron
              onClick={() => setCurrentView('editEvents')}
            />
            <CellSimple
              title="Создать отчёт"
              showChevron
              onClick={() => setCurrentView('createReport')}
            />
          </CellList>
        </div>
      </Panel>
    </div>
  );
};

export default AdminPage;