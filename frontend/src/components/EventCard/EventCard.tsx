import { useState, useRef, useCallback, useEffect } from 'react';
import { Panel, Typography, Flex } from '@maxhub/max-ui';
import { clsx } from 'clsx';
import styles from './EventCard.module.scss';

export interface EventInfo {
  name: string;
  tags: string[];
  is_registered: boolean;
  points: number;
}

interface EventCardProps {
  eventInfo: EventInfo;
  onMoreClick: () => void;           // вызывается при нажатии на карточку
  onRegisterSwapped: () => void;     // вызывается при свайпе для регистрации
  onUnregisterSwapped: () => void;   // вызывается при свайпе для отмены регистрации
}

export const EventCard = ({
  eventInfo,
  onMoreClick,
  onRegisterSwapped,
  onUnregisterSwapped,
}: EventCardProps) => {
  const { name, tags, is_registered, points } = eventInfo;

  const REGISTERED_OFFSET = -60;
  const SWIPE_THRESHOLD = 60;

  const [offsetX, setOffsetX] = useState(is_registered ? REGISTERED_OFFSET : 0);

  useEffect(() => {
    setOffsetX(is_registered ? REGISTERED_OFFSET : 0);
  }, [is_registered]);

  const containerRef = useRef<HTMLDivElement>(null);
  const startXRef = useRef<number>(0);
  const currentOffsetRef = useRef<number>(0);
  const isDraggingRef = useRef<boolean>(false);

  const handleStart = useCallback((clientX: number) => {
    startXRef.current = clientX;
    currentOffsetRef.current = offsetX;
    isDraggingRef.current = true;
  }, [offsetX]);

  const handleMove = useCallback((clientX: number) => {
    if (!isDraggingRef.current) return;
    const diff = clientX - startXRef.current;
    let newOffset = currentOffsetRef.current + diff;
    newOffset = Math.min(0, Math.max(newOffset, -120));
    setOffsetX(newOffset);
  }, []);

  const handleEnd = useCallback(() => {
    if (!isDraggingRef.current) return;
    isDraggingRef.current = false;

    // Определяем направление свайпа
    const deltaX = offsetX - (is_registered ? REGISTERED_OFFSET : 0);
    
    // Свайп влево (отрицательное смещение) для регистрации
    if (deltaX < -SWIPE_THRESHOLD && !is_registered) {
      onRegisterSwapped();
    }
    // Свайп вправо (положительное смещение) для отмены регистрации
    else if (deltaX > SWIPE_THRESHOLD && is_registered) {
      onUnregisterSwapped();
    }
    else {
      // Возвращаем в состояние, соответствующее флагу
      setOffsetX(is_registered ? REGISTERED_OFFSET : 0);
    }
  }, [offsetX, is_registered, onRegisterSwapped, onUnregisterSwapped]);

  const touchHandlers = {
    onTouchStart: (e: React.TouchEvent) => handleStart(e.touches[0].clientX),
    onTouchMove: (e: React.TouchEvent) => handleMove(e.touches[0].clientX),
    onTouchEnd: handleEnd,
  };

  const onMouseMove = (e: MouseEvent) => handleMove(e.clientX);
  const onMouseUp = () => {
    handleEnd();
    window.removeEventListener('mousemove', onMouseMove);
    window.removeEventListener('mouseup', onMouseUp);
  };

  const mouseHandlers = {
    onMouseDown: (e: React.MouseEvent) => {
      e.preventDefault();
      handleStart(e.clientX);
      window.addEventListener('mousemove', onMouseMove);
      window.addEventListener('mouseup', onMouseUp);
    },
  };

  const topSectionStyle = {
    transform: `translateX(${offsetX}px)`,
    transition: isDraggingRef.current ? 'none' : 'transform 0.3s ease-out',
    paddingRight: offsetX < 0 ? `${-offsetX}px` : '0px',
  };

  const bottomPanelClass = clsx(
    styles.bottomPanel,
    is_registered && styles.bottomPanelRegistered
  );

  return (
    <div
      ref={containerRef}
      className={styles.container}
      {...touchHandlers}
      {...mouseHandlers}
    >
      {/* Нижняя панель (фон) */}
      <div className={bottomPanelClass}>
        <div className={styles.registrationLabel}>
          {is_registered ? 'Зарегистрирован' : ''}
        </div>
      </div>

      {/* Верхняя панель (основная информация) — нажатие вызывает onMoreClick */}
      <div
        className={styles.topPanel}
        style={topSectionStyle}
        onClick={onMoreClick}
      >
        <Panel mode="primary" className={styles.panelContent}>
          <Typography.Title variant="medium-strong">{name}</Typography.Title>
          <Typography.Body>Баллы: {points}</Typography.Body>
          <Flex gap={8} wrap="wrap" style={{ marginTop: 8 }}>
            {tags.map((tag, idx) => (
              <span key={idx} className={styles.tag}>
                🏷️ {tag}
              </span>
            ))}
          </Flex>
        </Panel>
      </div>
    </div>
  );
};