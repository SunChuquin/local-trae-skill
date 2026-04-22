"""
定时任务服务 - 自动更新知识库摘要
"""
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from app.services.kb_summary_service import regenerate_all_summaries
from app.utils.logger import logger

TASK_INTERVAL_HOURS = 24


class ScheduleTask:
    """定时任务管理器"""
    
    def __init__(self):
        self._task: Optional[asyncio.Task] = None
        self._running = False
    
    async def start(self):
        """启动定时任务"""
        if self._running:
            logger.warning("定时任务已在运行中")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._run_schedule())
        logger.info(f"定时摘要更新任务已启动（每 {TASK_INTERVAL_HOURS} 小时执行一次）")
    
    async def stop(self):
        """停止定时任务"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("定时摘要更新任务已停止")
    
    async def _run_schedule(self):
        """运行定时任务循环"""
        while self._running:
            try:
                await self._execute_task()
            except Exception as e:
                logger.error(f"定时摘要更新任务执行失败: {str(e)}")
            
            await asyncio.sleep(TASK_INTERVAL_HOURS * 3600)
    
    async def _execute_task(self):
        """执行摘要更新任务"""
        logger.info("=" * 50)
        logger.info("开始执行定时摘要更新任务")
        logger.info("=" * 50)
        
        start_time = datetime.now()
        
        try:
            results = await regenerate_all_summaries()
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            logger.info("=" * 50)
            logger.info(f"定时摘要更新任务完成")
            logger.info(f"总知识库数: {results['total']}")
            logger.info(f"成功: {results['success']}")
            logger.info(f"失败: {results['failed']}")
            logger.info(f"耗时: {elapsed:.2f} 秒")
            logger.info("=" * 50)
            
        except Exception as e:
            logger.error(f"定时摘要更新任务异常: {str(e)}")
            raise
    
    async def run_now(self):
        """立即执行一次任务"""
        logger.info("手动触发摘要更新任务")
        await self._execute_task()


schedule_task = ScheduleTask()
