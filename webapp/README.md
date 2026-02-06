# Teacher Taplink Webapp

Мини-сайт + админка на FastAPI с хранением данных в `data.json`.

## Запуск

```bash
pip install -r requirements.txt
python -m uvicorn webapp.app:app --reload --port 8000
```

Открыть:
- Сайт: http://localhost:8000
- Админка: http://localhost:8000/admin

## Как заменить фото педагога

1. Скопируйте ваши реальные фото в `webapp/static/images/`.
2. Переименуйте их в `teacher-1.svg` и `teacher-2.svg` **или** обновите пути в `templates/index.html`.

## Что умеет админка

- Метатеги (title/description/keywords/OG)
- Управление контентом
- CRUD услуг, прайс-листа, групп, отзывов
- Парсеры контента и отзывов (демо)
