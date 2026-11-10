# Публикация на GitHub

## Что попадёт в репозиторий

Исходники, protobuf-контракт и сгенерированные bindings, тесты, документация,
пример конфигурации и workflow GitHub Actions.

`.gitignore` исключает `.env`, виртуальное окружение, загрузки, локальный
`invoice.pdf`, PDF-методички из `docs/` и служебные каталоги. Файлы остаются
на компьютере. Если нужен публичный пример счёта, добавь отдельно документ
с вымышленными данными и понятными правами на распространение.

## Перед первой публикацией

```bash
python -m pytest -q
git init
git status --short --untracked-files=all
git check-ignore .env .venv/ uploads/ invoice.pdf
```

Просмотри список файлов: там не должно быть ключей, реальных счетов и личных
данных. `.gitignore` не удаляет файлы, уже добавленные в Git. Если ключ ранее
попал в опубликованную историю, его нужно заменить в Azure.

Добавь файлы и проверь подготовленный коммит:

```bash
git add .
git diff --cached --stat
git diff --cached
```

Затем создай первый коммит:

```bash
git commit -m "Prepare invoice processing service for portfolio"
git branch -M main
```

Создай пустой репозиторий на GitHub без автоматического README и подставь свой
адрес вместо `YOUR_USERNAME`:

```bash
git remote add origin https://github.com/YOUR_USERNAME/invoice-processing-service.git
git push -u origin main
```

Если Git уже настроен, используй существующий репозиторий и remote.
Если среда ограничивает запись в `.git`, выполни команды инициализации и
публикации в своём обычном терминале.

## Оформление страницы

- Название: `invoice-processing-service`.
- Description: `Asynchronous invoice processing with FastAPI, gRPC and Azure AI Document Intelligence.`
- Topics: `python`, `fastapi`, `grpc`, `azure`, `asyncio`, `document-intelligence`.
- После push проверь вкладку Actions: результат облачного workflow будет виден там.

Лицензия пока не добавлена: выбери её осознанно, если хочешь разрешить другим
использовать и распространять код. Учебные PDF не включены в публикуемые файлы.
