#!/usr/bin/env bash
set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
BACKEND_LOG="$BACKEND_DIR/backend.log"
FRONTEND_LOG="$FRONTEND_DIR/frontend.log"
BACKEND_PORT=8000
FRONTEND_PORT=5173

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Запуск Event Manager (бэкенд + фронтенд)${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# ---------- Проверка инструментов ----------
echo -e "${YELLOW}[1/5] Проверка окружения...${NC}"
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}Ошибка: python3 не найден. Установите Python 3.${NC}"
    exit 1
fi
if ! command -v node &>/dev/null; then
    echo -e "${RED}Ошибка: Node.js не найден. Установите Node.js.${NC}"
    exit 1
fi
if ! command -v npm &>/dev/null; then
    echo -e "${RED}Ошибка: npm не найден. Установите npm.${NC}"
    exit 1
fi
echo -e "  python3:  $(python3 --version 2>&1)"
echo -e "  node:     $(node -v 2>&1)"
echo -e "  npm:      $(npm -v 2>&1)"
echo ""

# Функция проверки порта (сначала lsof, потом ss, потом netstat)
port_in_use() {
    local port=$1
    if command -v lsof &>/dev/null; then
        lsof -i :"$port" -sTCP:LISTEN -t &>/dev/null
    elif command -v ss &>/dev/null; then
        ss -tuln | grep -q ":$port "
    elif command -v netstat &>/dev/null; then
        netstat -tuln | grep -q ":$port "
    else
        echo -e "${RED}Нет инструмента для проверки портов (lsof, ss, netstat). Установите lsof.${NC}"
        exit 1
    fi
}

# Функция получения PID по порту
get_pid_by_port() {
    local port=$1
    if command -v lsof &>/dev/null; then
        lsof -i :"$port" -sTCP:LISTEN -t 2>/dev/null
    elif command -v ss &>/dev/null; then
        ss -tlnp | grep ":$port " | grep -oP 'pid=\K[0-9]+'
    elif command -v netstat &>/dev/null; then
        netstat -tlnp | grep ":$port " | awk '{print $NF}' | grep -oP '[0-9]+'
    fi
}

# ---------- Подготовка бэкенда ----------
echo -e "${YELLOW}[2/5] Подготовка бэкенда...${NC}"
cd "$BACKEND_DIR"
if [ ! -d ".env" ]; then
    echo "  Создаю виртуальное окружение .env..."
    python3 -m venv .env
fi
source .env/bin/activate
if ! python -c "import fastapi" &>/dev/null; then
    echo "  Устанавливаю Python-зависимости (fastapi, uvicorn, pydantic)..."
    pip install --quiet fastapi uvicorn[standard] pydantic sqlmodel
else
    echo "  Python-зависимости уже установлены."
fi
if [ ! -f "main.py" ]; then
    echo -e "${RED}Ошибка: файл main.py не найден в $BACKEND_DIR${NC}"
    exit 1
fi
echo ""

# ---------- Подготовка фронтенда ----------
echo -e "${YELLOW}[3/5] Подготовка фронтенда...${NC}"
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    echo "  Устанавливаю npm-пакеты..."
    npm install --silent
else
    echo "  npm-пакеты уже установлены."
fi
echo ""

# ---------- Проверка портов ----------
echo -e "${YELLOW}[4/5] Проверка портов...${NC}"
for port in $BACKEND_PORT $FRONTEND_PORT; do
    service_name="Бэкенд"
    [ $port -eq $FRONTEND_PORT ] && service_name="Фронтенд"
    if port_in_use $port; then
        echo -e "  Порт ${port} (${service_name}) уже занят."
        read -p "  Завершить процесс на порту $port? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            pid=$(get_pid_by_port $port)
            if [ -n "$pid" ]; then
                kill "$pid" 2>/dev/null && echo "  Процесс PID $pid завершён."
                sleep 1
            fi
        else
            echo -e "${RED}  Невозможно продолжить, порт $port занят.${NC}"
            exit 1
        fi
    fi
done
echo ""

# ---------- Запуск серверов ----------
echo -e "${GREEN}[5/5] Запуск серверов...${NC}"

# Бэкенд
echo -e "  Запускаю бэкенд (uvicorn) на порту $BACKEND_PORT..."
cd "$BACKEND_DIR"
source .env/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!
echo "  PID бэкенда: $BACKEND_PID"
echo -n "  Ожидание готовности бэкенда"
for i in {1..10}; do
    if port_in_use $BACKEND_PORT; then
        echo -e " ${GREEN}✓ готов${NC}"
        break
    fi
    sleep 1
    echo -n "."
done
if ! port_in_use $BACKEND_PORT; then
    echo -e "\n${RED}Ошибка: бэкенд не запустился за 10 секунд.${NC}"
    echo "Последние строки лога:"
    tail -n 10 "$BACKEND_LOG"
    exit 1
fi

# Фронтенд
echo -e "  Запускаю фронтенд (Vite) на порту $FRONTEND_PORT..."
cd "$FRONTEND_DIR"
nohup npm run dev -- --host > "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!
echo "  PID фронтенда: $FRONTEND_PID"
echo -n "  Ожидание готовности фронтенда"
for i in {1..10}; do
    if port_in_use $FRONTEND_PORT; then
        echo -e " ${GREEN}✓ готов${NC}"
        break
    fi
    sleep 1
    echo -n "."
done
if ! port_in_use $FRONTEND_PORT; then
    echo -e "\n${RED}Ошибка: фронтенд не запустился за 10 секунд.${NC}"
    echo "Последние строки лога:"
    tail -n 10 "$FRONTEND_LOG"
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Оба сервера успешно запущены!${NC}"
echo -e "${GREEN}  Бэкенд:  http://<IP>:$BACKEND_PORT${NC}"
echo -e "${GREEN}  Фронтенд: http://<IP>:$FRONTEND_PORT${NC}"
echo -e "${GREEN}  Логи бэкенда:  $BACKEND_LOG${NC}"
echo -e "${GREEN}  Логи фронтенда: $FRONTEND_LOG${NC}"
echo -e "${GREEN}========================================${NC}"