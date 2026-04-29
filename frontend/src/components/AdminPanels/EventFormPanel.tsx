import { useState } from 'react';
import { Typography, Panel, Flex, Button, Input, Switch } from '@maxhub/max-ui';
import type { EventDetail } from '../../api/types';

interface EventFormPanelProps {
  initial?: Partial<EventDetail>;   // если передано – режим редактирования
  onSave: (data: Record<string, any>) => void;
  onCancel: () => void;
}

export const EventFormPanel = ({ initial, onSave, onCancel }: EventFormPanelProps) => {
  const [name, setName] = useState(initial?.name || '');
  const [description, setDescription] = useState(initial?.description || '');
  const [tagsStr, setTagsStr] = useState(initial?.tags?.join(', ') || '');
  const [points, setPoints] = useState(String(initial?.points ?? 0));
  const [date, setDate] = useState(initial?.date ? initial.date.slice(0, 16) : ''); // для datetime-local
  const [link, setLink] = useState(initial?.link || '');
  const [isArchived, setIsArchived] = useState(initial?.is_archived ?? false);

  const handleSubmit = () => {
    if (!name.trim()) return;
    const tagsArray = tagsStr.split(',').map(t => t.trim()).filter(Boolean);
    const body = {
      name,
      description: description || null,
      tags: tagsArray,
      points: parseInt(points, 10) || 0,
      date: new Date(date).toISOString(),
      link: link || null,
      is_archived: isArchived,
    };
    onSave(body);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      <Typography.Title variant="medium-strong">
        {initial ? 'Редактирование мероприятия' : 'Новое мероприятие'}
      </Typography.Title>

      <Input placeholder="Название" value={name} onChange={(e) => setName(e.target.value)} />
      <Input placeholder="Описание" value={description} onChange={(e) => setDescription(e.target.value)} />
      <Input placeholder="Теги (через запятую)" value={tagsStr} onChange={(e) => setTagsStr(e.target.value)} />
      <Input placeholder="Баллы" type="number" value={points} onChange={(e) => setPoints(e.target.value)} />
      <Input placeholder="Дата и время" type="datetime-local" value={date} onChange={(e) => setDate(e.target.value)} />
      <Input placeholder="Ссылка (https://...)" value={link} onChange={(e) => setLink(e.target.value)} />
      <Flex justify="space-between" align="center">
        <Typography.Body>В архив</Typography.Body>
        <Switch checked={isArchived} onChange={(e) => setIsArchived(e.target.checked)} />
      </Flex>

      <Flex gap={12} justify="flex-end" style={{ marginTop: 20 }}>
        <Button mode="secondary" onClick={onCancel}>Отмена</Button>
        <Button mode="primary" onClick={handleSubmit}>Сохранить</Button>
      </Flex>
    </div>
  );
};