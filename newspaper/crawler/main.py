import asyncio

import aiomysql

from ..config import global_configs, logger, db
from .spiders import online_spiders, history_spiders


async def online_workflow():
    if not online_spiders:
        logger.info('no online_spiders online.')
        return
    # 确认 articles 表存在, 否则建表
    await db._ensure_article_table_exists()
    coros = [func() for func in online_spiders]
    done, fail = await asyncio.wait(coros, timeout=120)
    if fail:
        logger.warn(f'failing spiders: {len(fail)}')
    # print(done)
    pool = await db.get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            for task in done:
                articles = task.result()
                # print(result)
                if articles:
                    await db.add_articles(articles, cursor=cursor)


async def history_workflow():
    if not history_spiders:
        logger.info('ignore for no history_spiders online.')
        return
    # 确认 articles 表存在, 否则建表
    await db._ensure_article_table_exists()
    coros = [func() for func in history_spiders]
    done, fail = await asyncio.wait(coros, timeout=120)
    if fail:
        logger.warn(f'failing spiders: {len(fail)}')
    # print(done)
    pool = await db.get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            for task in done:
                articles = task.result()
                # print(result)
                if articles:
                    await db.add_articles(articles, cursor=cursor)