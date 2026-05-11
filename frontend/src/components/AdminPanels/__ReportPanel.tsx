import { useState } from 'react';
import {
    Typography,
    Panel,
    Flex,
    Button,
    IconButton,
    Input,
    Switch,
} from '@maxhub/max-ui';

interface ReportPanelProps {
    onBack: () => void;
}

export const ReportPanel = ({ onBack }: ReportPanelProps) => {
    // ---- активная вкладка ----
    const [activeTab, setActiveTab] = useState<'auto' | 'manual'>('auto');

    // ---- поля для ручной отправки ----
    const [manualEmails, setManualEmails] = useState<string[]>(['']);
    const [dateFrom, setDateFrom] = useState('');
    const [dateTo, setDateTo] = useState('');

    // ---- поля для автоматической отправки ----
    const [autoEmails, setAutoEmails] = useState<string[]>(['']);
    const [frequencyMode, setFrequencyMode] = useState<'monthly' | 'custom'>('monthly');
    const [customDays, setCustomDays] = useState('30');
    const [sendTime, setSendTime] = useState('09:00'); // время отправки

    // ========== ручная отправка: управление списком email ==========
    const addManualEmail = () => setManualEmails([...manualEmails, '']);
    const removeManualEmail = (index: number) => {
        if (manualEmails.length === 1) return;
        setManualEmails(manualEmails.filter((_, i) => i !== index));
    };
    const updateManualEmail = (index: number, value: string) => {
        const updated = [...manualEmails];
        updated[index] = value;
        setManualEmails(updated);
    };

    const handleManualSubmit = () => {
        const validEmails = manualEmails.filter(e => e.trim() !== '');
        if (validEmails.length === 0) {
            console.error('Введите хотя бы один email');
            return;
        }
        console.log('Ручная отправка отчёта:', { emails: validEmails, dateFrom, dateTo });
    };

    // ========== авто‑отправка: управление списком email ==========
    const addAutoEmail = () => setAutoEmails([...autoEmails, '']);
    const removeAutoEmail = (index: number) => {
        if (autoEmails.length === 1) return;
        setAutoEmails(autoEmails.filter((_, i) => i !== index));
    };
    const updateAutoEmail = (index: number, value: string) => {
        const updated = [...autoEmails];
        updated[index] = value;
        setAutoEmails(updated);
    };

    const handleAutoSubmit = () => {
        const validEmails = autoEmails.filter(e => e.trim() !== '');
        if (validEmails.length === 0) {
            console.error('Введите хотя бы один email');
            return;
        }
        const frequency = frequencyMode === 'monthly' ? 'monthly' : `${customDays} days`;
        console.log('Автоматическая отправка отчёта:', {
            emails: validEmails,
            frequency,
            sendTime,
        });
    };

    // ========== общий стиль кнопок вкладок ==========
    const tabButton = (tab: 'auto' | 'manual', label: string) => (
        <Button
            mode={activeTab === tab ? 'primary' : 'tertiary'}
            onClick={() => setActiveTab(tab)}
            style={{ flex: 1, borderRadius: 12, fontWeight: 500 }}
        >
            {label}
        </Button>
    );

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
                {/* Заголовок с кнопкой назад */}
                <Flex justify="space-between" align="center" style={{ marginBottom: 20 }}>
                    <IconButton mode="tertiary" onClick={onBack}>
                        <span style={{ fontSize: 20 }}>←</span>
                    </IconButton>
                    <Typography.Title variant="medium-strong">Создание отчёта</Typography.Title>
                    <div style={{ width: 48 }} />
                </Flex>

                {/* Вкладки */}
                <Flex gap={8} style={{ marginBottom: 16 }}>
                    {tabButton('auto', 'Автоматически')}
                    {tabButton('manual', 'Вручную')}
                </Flex>

                {/* Содержимое вкладок */}
                <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 16 }}>
                    {activeTab === 'manual' ? (
                        /* ================= ВКЛАДКА «ВРУЧНУЮ» ================= */
                        <>
                            <div>
                                <Flex justify="space-between" align="center" style={{ marginBottom: 8 }}>
                                    <Typography.Title variant="small-strong">Email получатели</Typography.Title>
                                    <Button mode="tertiary" size="small" onClick={addManualEmail}>
                                        + Добавить
                                    </Button>
                                </Flex>
                                <Panel mode="secondary" style={{ padding: 16, borderRadius: 12, display: 'flex', flexDirection: 'column', gap: 8 }}>
                                    {manualEmails.map((email, index) => (
                                        <Flex key={index} gap={8} align="center">
                                            <Input
                                                type="email"
                                                placeholder="user@example.com"
                                                value={email}
                                                onChange={(e) => updateManualEmail(index, e.target.value)}
                                                style={{ flex: 1 }}
                                            />
                                            {manualEmails.length > 1 && (
                                                <IconButton
                                                    mode="tertiary"
                                                    size="small"
                                                    onClick={() => removeManualEmail(index)}
                                                >
                                                    <span>✕</span>
                                                </IconButton>
                                            )}
                                        </Flex>
                                    ))}
                                </Panel>
                            </div>

                            <div>
                                <Typography.Title variant="small-strong">Временной промежуток</Typography.Title>
                                <Panel mode="secondary" style={{ padding: 16, borderRadius: 12, marginTop: 12, display: 'flex', flexDirection: 'column', gap: 12 }}>
                                    <Input
                                        type="date"
                                        value={dateFrom}
                                        onChange={(e) => setDateFrom(e.target.value)}
                                    />
                                    <Input
                                        type="date"
                                        value={dateTo}
                                        onChange={(e) => setDateTo(e.target.value)}
                                    />
                                </Panel>
                            </div>

                            <Button mode="primary" stretched onClick={handleManualSubmit}>
                                Готово
                            </Button>
                        </>
                    ) : (
                        /* ================= ВКЛАДКА «АВТОМАТИЧЕСКИ» ================= */
                        <>
                            {/* Email получатели */}
                            <div>
                                <Flex justify="space-between" align="center" style={{ marginBottom: 8 }}>
                                    <Typography.Title variant="small-strong">Email получатели</Typography.Title>
                                    <Button mode="tertiary" size="small" onClick={addAutoEmail}>
                                        + Добавить
                                    </Button>
                                </Flex>
                                <Panel mode="secondary" style={{ padding: 16, borderRadius: 12, display: 'flex', flexDirection: 'column', gap: 8 }}>
                                    {autoEmails.map((email, index) => (
                                        <Flex key={index} gap={8} align="center">
                                            <Input
                                                type="email"
                                                placeholder="user@example.com"
                                                value={email}
                                                onChange={(e) => updateAutoEmail(index, e.target.value)}
                                                style={{ flex: 1 }}
                                            />
                                            {autoEmails.length > 1 && (
                                                <IconButton
                                                    mode="tertiary"
                                                    size="small"
                                                    onClick={() => removeAutoEmail(index)}
                                                >
                                                    <span>✕</span>
                                                </IconButton>
                                            )}
                                        </Flex>
                                    ))}
                                </Panel>
                            </div>

                            {/* Время отправки */}
                            <div>
                                <Typography.Title variant="small-strong">Время отправки</Typography.Title>
                                <Panel mode="secondary" style={{ padding: 16, borderRadius: 12, marginTop: 12 }}>
                                    <Flex justify="space-between" align="center">
                                        <Typography.Body>Во сколько отправлять</Typography.Body>
                                        <Input
                                            type="time"
                                            value={sendTime}
                                            onChange={(e) => setSendTime(e.target.value)}
                                            style={{ width: 120 }}
                                        />
                                    </Flex>
                                </Panel>
                            </div>

                            {/* Частота отправки */}
                            <div>
                                <Typography.Title variant="small-strong">Частота отправки</Typography.Title>
                                <Panel mode="secondary" style={{ padding: 16, borderRadius: 12, marginTop: 12, display: 'flex', flexDirection: 'column', gap: 12 }}>
                                    <Flex justify="space-between" align="center">
                                        <Typography.Body>Раз в месяц</Typography.Body>
                                        <Switch
                                            checked={frequencyMode === 'monthly'}
                                            onChange={(e) => setFrequencyMode(e.target.checked ? 'monthly' : 'custom')}
                                        />
                                    </Flex>
                                    {frequencyMode === 'custom' && (
                                        <Flex justify="space-between" align="center">
                                            <Typography.Body>Раз в N дней</Typography.Body>
                                            <Input
                                                type="number"
                                                value={customDays}
                                                onChange={(e) => setCustomDays(e.target.value)}
                                                style={{ width: 80 }}
                                                min={1}
                                                max={365}
                                            />
                                        </Flex>
                                    )}
                                </Panel>
                            </div>

                            <Button mode="primary" stretched onClick={handleAutoSubmit}>
                                Готово
                            </Button>
                        </>
                    )}
                </div>
            </Panel>
        </div>
    );
};

export default ReportPanel;