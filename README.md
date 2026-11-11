# Аналитическая платформа для выявления опасных участков дорог и прогнозирования риска ДТП

Аналитическая платформа для выявления опасных участков дорог и прогнозирования рисков ДТП на основе исторических данных. Помогает дорожным службам принимать решения на основе данных.

**Вариант:** 5. Аналитика ДТП и опасных участков · **Город / регион:** Уфа

## Команда

| Участник | Роль в ЛР 1 | GitHub |
|---|---|---|
| Рязанов М. | Аналитик предметной области | @rjazanov |
| Ковальчук В. | Менеджер проекта | @renvoid72 |

## Ссылки

- Доска проекта: [Доска проекта](https://github.com/users/renvoid72/projects/1/views/1)
- Релизы: [v0.1-initiation](https://github.com/renvoid72/pm-lab-5-CIA/releases/tag/v0.1-initiation) · [v0.2-scope](https://github.com/renvoid72/pm-lab-5-CIA/releases/tag/v0.2-scope)
- Устав проекта: [docs/charter.md](docs/charter.md)
- Требования, карта историй и MVP: [docs/requirements.md](docs/requirements.md)
- WBS и словарь: [docs/wbs.md](docs/wbs.md)
- Реестр источников данных: [data/sources.md](data/sources.md)
- Отчёт о качестве данных: [docs/data-quality.md](docs/data-quality.md)
- Первая карта: [docs/img/accidents_by_district.png](docs/img/accidents_by_district.png) · [интерактивная](docs/maps/analysis_v0.html) 
- Задания: [ЛР 1](docs/tasks/lab-1-assignment.md) · [ЛР 2](docs/tasks/lab-2-assignment.md)

## Статус

| ЛР | Тема | Статус |
|---|---|---|
| 1 | Инициация проекта | выполнено |
| 2 | Требования, содержание, данные | выполнено |
| 3 | Планирование | |
| 4 | Риски и качество | |
| 5 | Исполнение и мониторинг | |
| 6 | Завершение и защита | |

---


## Правила работы

- Нет задачи в трекере, нет работы.
- Каждый документ попадает в `main` через Pull Request. В описании PR пишите `Closes #N`.
- Каждый участник должен быть и автором PR, и ревьюером.
- Если вы использовали ИИ-ассистента, запишите это в [docs/ai-usage.md](docs/ai-usage.md).
- Сообщения коммитов: `тип: описание (#N)`, например `docs: add stakeholder register (#5)`.

## Структура репозитория

```
├── README.md
├── requirements.txt
├── docs/
│   ├── team-agreement.md        командный договор
│   ├── business-case.md         проблема, ценность, альтернативы
│   ├── charter.md               устав проекта
│   ├── stakeholders.md          стейкхолдеры, матрица, RACI
│   ├── gonogo.md                решение Go/No-Go
│   ├── requirements.md          требования, карта историй, MVP
│   ├── wbs.md                   WBS и словарь пакетов работ
│   ├── definition-of-done.md    DoR и DoD
│   ├── data-quality.md          профиль данных и осуществимость
│   ├── adr/                     записи о принятых решениях
│   ├── meetings/                интервью и протоколы обзоров
│   ├── img/                     статичные карты для отчёта
│   ├── maps/                    интерактивные карты
│   ├── ai-usage.md              журнал использования ИИ
│   └── tasks/                   тексты заданий лабораторных работ
├── data/
│   ├── sources.md               реестр источников с оценками
│   ├── README.md                как получить данные
│   ├── raw/                     сырые данные (в Git только .gitkeep)
│   ├── manual/                  таблицы ручного сбора
│   └── processed/               очищенные слои
├── notebooks/
│   ├── 01_data_collection.ipynb
│   ├── 02_data_profiling.ipynb
│   ├── 03_spatial_analysis.ipynb
│   ├── 04_plan_calculator.ipynb
│   └── README.md
├── scripts/
│   └── fetch_gibdd.py           выгрузка ДТП со stat.gibdd.ru
└── .github/                     шаблоны задач и PR, автоматизация
```
