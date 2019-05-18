import asyncio

from torequests.dummy import Requests

from ..config import db, spider_logger
from .spiders import history_spiders, online_spiders


async def test_spider_workflow():
    from .spiders import test_spiders
    from pprint import pprint
    for func in test_spiders:
        print('test start:', func.__doc__)
        result = await func()
        pprint(result)


async def clear_cache():
    url = 'http://127.0.0.1:9001/newspaper/articles.cache.clear'
    req = Requests()
    r = await req.get(url, timeout=2)
    spider_logger.info(f'clear_cache {r.text}')


async def online_workflow():
    if not online_spiders:
        spider_logger.info('no online_spiders online.')
        return
    # 确认 articles 表存在, 否则建表
    await db._ensure_article_table_exists()
    coros = [func() for func in online_spiders]
    done, fail = await asyncio.wait(coros, timeout=120)
    spider_logger.info(f'{"=" * 30}')
    if fail:
        spider_logger.warn(f'failing spiders: {len(fail)}')
    pool = await db.get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            for task in done:
                articles = task.result()
                # print(result)
                if articles:
                    insert_result = await db.add_articles(articles,
                                                          cursor=cursor)
                    spider_logger.info(
                        f'+ {insert_result} articles. [{articles[0].get("source")}]'
                    )
    await clear_cache()


async def history_workflow():
    if not history_spiders:
        spider_logger.info('ignore for no history_spiders online.')
        return
    # 确认 articles 表存在, 否则建表
    await db._ensure_article_table_exists()
    coros = [func() for func in history_spiders]
    done, fail = await asyncio.wait(coros, timeout=120)
    spider_logger.info(f'{"=" * 30}')
    if fail:
        spider_logger.warn(f'failing spiders: {len(fail)}')
    pool = await db.get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            for task in done:
                articles = task.result()
                # print(result)
                if articles:
                    insert_result = await db.add_articles(articles,
                                                          cursor=cursor)
                    spider_logger.info(
                        f'+ {insert_result} articles. [{articles[0].get("source")}]'
                    )
    await clear_cache()
