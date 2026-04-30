#!/usr/bin/env bash
set -euo pipefail

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

BACKEND_PORT=8000
FRONTEND_PORT=5173

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}   Остановка Event Manager${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""

# Функция остановки процесса по порту
stop_port() {
    local port=$1
    local service_name=$2
    local pids

    # Получаем PID(ы), слушающие порт
    pids=$(ss -tlnp | grep ":$port " | grep -oP 'pid=\K[0-9]+' || true)

    if [ -z "$pids" ]; then
        echo -e "  ${service_name} (порт $port): ${YELLOW}не запущен${NC}"
        return 0
    fi

    echo -n "  Останавливаю ${service_name} (порт $port)... "
    for pid in $pids; do
        # Вежливо просим завершиться
        kill "$pid" 2>/dev/null || true
        sleep 0.5
        # Если ещё жив, принудительно
        if kill -0 "$pid" 2>/dev/null; then
            echo -n "(принудительно) "
            kill -9 "$pid" 2>/dev/null || true
        fi
    done
    sleep 1

    # Проверяем, освободился ли порт
    if ss -tlnp | grep -q ":$port "; then
        echo -e "${RED}не удалось остановить${NC}"
        return 1
    else
        echo -e "${GREEN}остановлен${NC}"
        return 0
    fi
}

# Останавливаем бэкенд и фронтенд
stop_port $BACKEND_PORT "Бэкенд (uvicorn)"
stop_port $FRONTEND_PORT "Фронтенд (Vite)"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Серверы остановлены${NC}"
echo -e "${GREEN}========================================${NC}"