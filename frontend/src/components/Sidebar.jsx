import { CellList, CellSimple, Avatar, Typography } from '@maxhub/max-ui';

// Заглушки иконок (замените на реальные из Max UI)
const AccountIcon = () => <span>👤</span>;
const SettingsIcon = () => <span>⚙️</span>;

const Sidebar = ({ onClose }) => {
  return (
    <div style={{ width: 280, height: '100%', background: 'var(--background_content)' }}>
      <div style={{ padding: 20, borderBottom: '1px solid var(--separator_common)' }}>
        <Avatar.Container size={64}>
          <Avatar.Image src="https://i.pravatar.cc/100" />
        </Avatar.Container>
        <Typography.Title variant="medium-strong" style={{ marginTop: 12 }}>
          Пользователь
        </Typography.Title>
      </div>
      <CellList>
        <CellSimple
          before={<AccountIcon />}
          title="Аккаунт"
          onClick={() => console.log('Переход в аккаунт')}
        />
        <CellSimple
          before={<SettingsIcon />}
          title="Настройки"
          onClick={() => console.log('Переход в настройки')}
        />
      </CellList>
    </div>
  );
};

export default Sidebar;