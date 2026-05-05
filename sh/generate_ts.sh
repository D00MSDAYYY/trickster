#!/bin/bash
#
# Скрипт для преобразования Pydantic моделей (из файла) в TypeScript интерфейсы
# Использует pydantic-to-typescript (https://github.com/phillduffy/pydantic-to-typescript)
#
# Зависимости:
#   - Python 3.7+ + пакет pydantic-to-typescript
#   - Node.js + пакет json-schema-to-typescript (можно через npx)
#
# Установка:
#   pip install pydantic-to-typescript
#   npm install -g json-schema-to-typescript   # или используйте npx
#

set -euo pipefail

usage() {
    echo "Использование: $0 <входной_файл.py> <выходной_файл.tsx>"
    echo ""
    echo "Пример:"
    echo "  $0 src/models.py ../frontend/src/apiTypes.ts"
    exit 1
}

if [ $# -ne 2 ]; then
    usage
fi

INPUT="$1"
OUTPUT="$2"

# Проверка существования входного файла
if [ ! -f "$INPUT" ]; then
    echo "Ошибка: входной файл '$INPUT' не найден."
    exit 1
fi

# Проверка наличия pydantic2ts
if ! command -v pydantic2ts &> /dev/null; then
    echo "pydantic2ts не найден."
    echo "Установите его: pip install pydantic-to-typescript"
    exit 1
fi

# Проверка доступности json-schema-to-typescript (нужна для работы)
# Можно либо установить глобально, либо использовать путём указания --json2ts-cmd
JSON2TS_CMD=""
if command -v json2ts &> /dev/null; then
    JSON2TS_CMD="json2ts"
elif command -v npx &> /dev/null; then
    # Используем npx json-schema-to-typescript
    JSON2TS_CMD="npx json-schema-to-typescript"
else
    echo "Не найден ни json2ts, ни npx. Пожалуйста, установите Node.js и json-schema-to-typescript."
    echo "  npm install -g json-schema-to-typescript"
    echo "или воспользуйтесь npx: 'npx json-schema-to-typescript'."
    exit 1
fi

# Запускаем pydantic2ts, передавая путь к файлу как модуль
# При необходимости можно исключить некоторые модели через --exclude
echo "Конвертация '$INPUT' -> '$OUTPUT' ..."
pydantic2ts \
    --module "$INPUT" \
    --output "$OUTPUT" \
    --json2ts-cmd "$JSON2TS_CMD"

echo "Готово. Результат записан в '$OUTPUT'."