# Celery

Celery loads the Django settings and automatically discovers `tasks.py` in
installed apps. Redis must be running before the worker starts.

## Install and run

From the project root in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\scripts\start-celery.ps1
```

Keep the worker running alongside Django. Stop it with Ctrl+C and restart it
after changing task code. The script uses the `solo` pool for local Windows
development. Celery does not officially support Windows; use Linux or WSL for
production and start the worker there with:

```sh
python -m celery -A ai_asistant_with_sina worker --loglevel=info
```

## Configuration

Set environment variables in the root `.env` when using another Redis server:

| Setting | Default |
| --- | --- |
| `CELERY_BROKER_URL` | `redis://127.0.0.1:6379/2` |
| `CELERY_RESULT_BACKEND` | `redis://127.0.0.1:6379/3` |
| `CELERY_RESULT_EXPIRES` | `3600` seconds |
| `CELERY_TASK_ALWAYS_EAGER` | `False` |

The Django cache uses database 1; task messages use database 2 and results use
database 3. The project queue is `ai_assistant_with_sina`. Only JSON messages are
accepted. No extra Django app or database migration is needed.

## Verify and add tasks

With the worker running:

```powershell
.\.venv\Scripts\python.exe manage.py shell -c "from question.tasks import ping; result = ping.delay(); print(result.get(timeout=15)); result.forget()"
```

Expected output: `pong`. This exercises the real broker, worker and result
backend. For background work, define a function with `@shared_task` in an app's
`tasks.py`, then submit it with `.delay(...)`. Pass IDs or other JSON values
instead of model instances. Use `.delay_on_commit(...)` for tasks that depend on
database writes, so the worker sees committed records.

This setup enables the task infrastructure; existing analysis and exercise views
continue to run their current processing synchronously until explicitly moved
into tasks. No periodic jobs are configured, so Celery Beat is not required.

References: [Django integration](https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html),
[Redis](https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/redis.html),
[platform support](https://docs.celeryq.dev/en/stable/getting-started/introduction.html).
