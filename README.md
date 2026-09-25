# Agent Run Supervisor

Небольшой сервис принимает результат запуска AI-агента и решает, что делать с задачей дальше.

## Задача

После неуспешных запусков слишком много задач возвращается разработчикам. Нужно сократить их ручное участие и сделать обработку таких задач эффективнее.

Изучите сервис и внесите изменение, которое считаете наиболее полезным.

## Текущее устройство

- `src/agent_run_supervisor/models.py` — результаты запусков и решения supervisor-а;
- `src/agent_run_supervisor/policy.py` — текущая policy;
- `src/agent_run_supervisor/orchestrator.py` — применение решения и запись действий;
- `src/agent_run_supervisor/in_memory.py` — тестовые реализации портов;
- `fixtures/historical_runs.json` — примеры исторических запусков;
- `scripts/replay_history.py` — воспроизведение fixture через текущую policy.

## Запуск

Требуется Python 3.11 или новее. Внешние зависимости не нужны.

```shell
python -m unittest discover -s tests -v
python scripts/replay_history.py
```

На Windows также можно использовать `py -3` вместо `python`.
