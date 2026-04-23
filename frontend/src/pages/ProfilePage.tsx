import { Typography, Panel, Container, Avatar, CellList, CellSimple } from '@maxhub/max-ui';

const ProfilePage = () => {
  return (
    <Container>
      <Panel mode="primary" style={{ padding: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 20 }}>
          <Avatar.Container size={72}>
            <Avatar.Image src="https://i.pravatar.cc/150" />
          </Avatar.Container>
          <div>
            <Typography.Title variant="large-strong">Иван Иванов</Typography.Title>
            <Typography.Body>@ivanov</Typography.Body>
          </div>
        </div>

        <CellList>
          <CellSimple title="Редактировать профиль" showChevron />
          <CellSimple title="Настройки" showChevron />
          <CellSimple title="О приложении" showChevron />
          <CellSimple title="Выйти" />
        </CellList>
      </Panel>
    </Container>
  );
};

export default ProfilePage;