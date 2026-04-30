import { useState } from 'react';
import { Typography, Panel, Switch, Input, IconButton, Flex, Button } from '@maxhub/max-ui';
import type { UserProfile } from '../api/types';

interface SettingsPanelProps {
  onBack: () => void;
  user: UserProfile;
}

export const SettingsPanel = ({ onBack, user }: SettingsPanelProps) => {
  // Инициализируем состояния из переданного объекта user
  const [notifyThreeDays, setNotifyThreeDays] = useState(user.notify_three_days ?? false);
  const [companyName, setCompanyName] = useState(user.company ?? '');

  const handleSave = async () => {
    try {
      const body = {
        company: companyName,
        notify_three_days: notifyThreeDays,
      };
      const res = await fetch('/api/profile', {
        method: 'PATCH',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const error = await res.json();
        console.error('Ошибка сохранения:', error.detail);
        return;
      }
      // Обновляем все поля локального объекта user тем, что вернул сервер (или просто присваиваем)
      const updatedUser: UserProfile = await res.json();
      Object.assign(user, updatedUser);
      console.log('Профиль обновлён');
    } catch (err) {
      console.error(err);
    }
  };

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
        <Flex justify="space-between" align="center" style={{ marginBottom: 20 }}>
          <IconButton mode="tertiary" onClick={onBack}>
            <span style={{ fontSize: 20 }}>←</span>
          </IconButton>
          <Typography.Title variant="medium-strong">Настройки</Typography.Title>
          <div style={{ width: 48 }} />
        </Flex>

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

        <div style={{ marginTop: 16 }}>
          <Button mode="primary" stretched onClick={handleSave}>
            Сохранить
          </Button>
        </div>
      </Panel>
    </div>
  );
};