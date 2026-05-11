import { useState } from 'react';
import {
    Typography,
    Panel,
    Flex,
    Button,
    IconButton,
    Input,
} from '@maxhub/max-ui';

interface ReportPanelProps {
    onBack: () => void;
}

export const ReportPanel = ({ onBack }: ReportPanelProps) => {
    const [dateFrom, setDateFrom] = useState('');
    const [dateTo, setDateTo] = useState('');

    const handleGenerateReport = async () => {
        if (!dateFrom || !dateTo) {
            console.error('Выберите обе даты');
            return;
        }
        try {
            const res = await fetch(`/api/admin/report?date_from=${dateFrom}&date_to=${dateTo}`, {
                credentials: 'include',
            });
            if (!res.ok) throw new Error('Ошибка генерации отчёта');

            // Скачиваем файл
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `report_${dateFrom}_${dateTo}.xlsx`;
            a.click();
            window.URL.revokeObjectURL(url);
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
                {/* Заголовок с кнопкой назад */}
                <Flex justify="space-between" align="center" style={{ marginBottom: 20 }}>
                    <IconButton mode="tertiary" onClick={onBack}>
                        <span style={{ fontSize: 20 }}>←</span>
                    </IconButton>
                    <Typography.Title variant="medium-strong">Создание отчёта</Typography.Title>
                    <div style={{ width: 48 }} />
                </Flex>

                {/* Содержимое */}
                <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 16 }}>
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

                    <Button mode="primary" stretched onClick={handleGenerateReport}>
                        Сгенерировать
                    </Button>
                </div>
            </Panel>
        </div>
    );
};

export default ReportPanel;