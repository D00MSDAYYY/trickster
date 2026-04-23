import { useState, useEffect } from 'react';
import { Typography, Panel, Switch, Input, IconButton, Flex } from '@maxhub/max-ui';

interface SettingsPanelProps {
  onBack: () => void;
}

export const SettingsPanel = ({ onBack }: SettingsPanelProps) => {
  const [notifyThreeDays, setNotifyThreeDays] = useState(false);
  const [companyName, setCompanyName] = useState('');

  // Автоматически "сохраняем" при любом изменении
  useEffect(() => {
    console.log('Настройки автоматически обновлены:', { notifyThreeDays, companyName });
    // Здесь мог бы быть запрос к API
  }, [notifyThreeDays, companyName]);

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Panel
        mode="primary"
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          padding: 12,
          borderRadius: 16,
          overflow: 'hidden',
        }}
      >
        {/* Заголовок со стрелкой назад и названием */}
        <Flex justify="space-between" align="center" style={{ marginBottom: 20 }}>
          <IconButton mode="tertiary" onClick={onBack}>
            <span style={{ fontSize: 20 }}>←</span>
          </IconButton>
          <Typography.Title variant="medium-strong">Настройки</Typography.Title>
          {/* Пустой блок для сохранения центрирования заголовка */}
          <div style={{ width: 48 }} /> {/* примерно ширина иконки */}
        </Flex>

        {/* Прокручиваемое содержимое */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 16, overflowY: 'auto' }}>
          <div>
            <Typography.Title variant="small-strong">Уведомления</Typography.Title>
            <Panel mode="secondary" style={{ padding: 16, borderRadius: 12, marginTop: 12 }}>
              <Flex justify="space-between" align="center">
                <Typography.Body>Присылать за 3 дня до мероприятия</Typography.Body>
                <Switch
                  checked={notifyThreeDays}
                  onChange={(e) => setNotifyThreeDays(e.target.checked)}
                />
              </Flex>
            </Panel>
          </div>

          <div>
            <Typography.Title variant="small-strong">Компания</Typography.Title>
            <Panel mode="secondary" style={{ padding: 16, borderRadius: 12, marginTop: 12 }}>
              <Input
                placeholder="Введите название"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
              />
            </Panel>
          </div>
        </div>
      </Panel>
    </div>
  );
};