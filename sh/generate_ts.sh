#!/bin/bash
set -euo pipefail

usage() {
    echo "Использование: $0 <входной_файл.py> <выходной_файл.tsx>"
    exit 1
}

if [ $# -ne 2 ]; then
    usage
fi

INPUT="$1"
OUTPUT="$2"

[ -f "$INPUT" ] || { echo "Ошибка: входной файл '$INPUT' не найден." >&2; exit 1; }

# Директория, где лежат external.py и internal.py
MODELS_DIR="$(dirname "$(realpath "$INPUT")")"
INTERNAL_FILE="$MODELS_DIR/internal.py"

EXCLUDE_ARGS=""
if [ -f "$INTERNAL_FILE" ]; then
    echo "Обнаружен internal.py, извлекаем модели для исключения..." >&2

    INTERNAL_MODELS=$(python - "$MODELS_DIR" << 'PYEOF'
import sys, json, importlib.util
from pathlib import Path
from pydantic import BaseModel

models_dir = sys.argv[1]
internal_path = Path(models_dir) / "internal.py"

spec = importlib.util.spec_from_file_location("internal", internal_path)
internal = importlib.util.module_from_spec(spec)
sys.modules["internal"] = internal
spec.loader.exec_module(internal)

models = []
for name, obj in vars(internal).items():
    if isinstance(obj, type) and issubclass(obj, BaseModel) and obj is not BaseModel:
        models.append(name)

print(json.dumps(models))
PYEOF
    )

    if [ $? -eq 0 ] && [ -n "$INTERNAL_MODELS" ]; then
        # Преобразуем JSON-массив в строку с пробелами для цикла
        MODELS_LIST=$(python -c "import sys,json; print(' '.join(json.loads('''$INTERNAL_MODELS''')))")
        echo "Модели для исключения: $MODELS_LIST" >&2
        for model in $MODELS_LIST; do
            EXCLUDE_ARGS="$EXCLUDE_ARGS --exclude $model"
        done
    else
        echo "Не удалось извлечь модели из internal.py, продолжаем без исключений." >&2
    fi
else
    echo "internal.py не найден, исключения не требуются." >&2
fi

# Проверка наличия инструментов
command -v pydantic2ts >/dev/null 2>&1 || {
    echo "pydantic2ts не найден. Установите: pip install pydantic-to-typescript" >&2
    exit 1
}

JSON2TS_CMD=""
if command -v json2ts >/dev/null 2>&1; then
    JSON2TS_CMD="json2ts"
elif command -v npx >/dev/null 2>&1; then
    JSON2TS_CMD="npx json-schema-to-typescript"
else
    echo "Установите json-schema-to-typescript (npm install -g ...) или npx" >&2
    exit 1
fi

echo "Конвертация '$INPUT' -> '$OUTPUT' ..."
pydantic2ts \
    --module "$INPUT" \
    --output "$OUTPUT" \
    --json2ts-cmd "$JSON2TS_CMD" \
    $EXCLUDE_ARGS

echo "Готово. Результат записан в '$OUTPUT'."