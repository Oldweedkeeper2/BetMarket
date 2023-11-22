import asyncio
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils.file_garbage_collector import garbage_collector
from utils.generate_dynamic_path import generate_dynamic_zip_path


async def schedule_garbage_collector(relative_path: dict):
    now = datetime.now()
    run_date = now + timedelta(seconds=5)
    # scheduler.add_job(garbage_collector, 'date', run_date=run_date, id='garbage_collector', args=[relative_path])
    scheduler.add_job(
            garbage_collector,
            'interval',
            weeks=4,
            # первое срабатываение после запуска, можно убрать, если не нужно
            next_run_time=datetime.now() + timedelta(seconds=5),
            id='monthly_garbage_collector',
            args=[relative_path]
    )


async def scheduler_on_startup(relative_path: dict):
    global scheduler
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    # await schedule_garbage_collector(relative_path=relative_path)  # ВКЛЮЧИТЬ В ПРОДЕ
    scheduler.start()
