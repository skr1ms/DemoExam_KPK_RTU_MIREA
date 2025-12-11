"""
Хелперы для работы с async функциями в Qt
"""

import asyncio
import threading
from typing import Coroutine, Any
from PySide6.QtCore import QObject, Signal, QThread


_loop_lock = threading.Lock()
_loop = None


def _get_or_create_loop():
    """Получить или создать event loop для текущего потока"""
    global _loop
    with _loop_lock:
        if _loop is None or _loop.is_closed():
            _loop = asyncio.new_event_loop()
            asyncio.set_event_loop(_loop)
        return _loop


class AsyncHelper(QObject):
    """Хелпер для запуска async функций из синхронного Qt кода"""

    finished = Signal(object)
    error = Signal(Exception)

    def __init__(self):
        super().__init__()
        self.loop = None
        self.thread = None

    def run_async(self, coro: Coroutine) -> None:
        """Запустить async функцию в отдельном потоке"""

        def run_in_thread():
            """Создать новый event loop в потоке"""
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            try:
                result = self.loop.run_until_complete(coro)
                self.finished.emit(result)
            except Exception as e:
                self.error.emit(e)
            finally:
                try:
                    pending = asyncio.all_tasks(self.loop)
                    if pending:
                        for task in pending:
                            task.cancel()
                        self.loop.run_until_complete(
                            asyncio.gather(*pending, return_exceptions=True)
                        )
                except Exception:
                    pass
                finally:
                    self.loop.close()

        self.thread = QThread()
        self.thread.run = run_in_thread
        self.thread.start()


def run_async_sync(coro: Coroutine) -> Any:
    """
    Запустить async функцию синхронно (блокирующий вызов)
    Использует глобальный event loop для всех вызовов
    """
    try:
        loop = asyncio.get_running_loop()
        raise RuntimeError(
            "Cannot run async function synchronously when event loop is already running. "
            "Use AsyncHelper.run_async() instead."
        )
    except RuntimeError as e:
        if "already running" in str(e):
            raise
        loop = _get_or_create_loop()
        try:
            return loop.run_until_complete(coro)
        except Exception as ex:
            if loop.is_closed():
                with _loop_lock:
                    _loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(_loop)
                    loop = _loop
                return loop.run_until_complete(coro)
            raise ex


def close_loop():
    """Закрыть глобальный event loop (вызывать при выходе из приложения)"""
    global _loop
    with _loop_lock:
        if _loop is not None and not _loop.is_closed():
            try:
                pending = asyncio.all_tasks(_loop)
                if pending:
                    for task in pending:
                        task.cancel()
                    _loop.run_until_complete(
                        asyncio.gather(*pending, return_exceptions=True)
                    )
            except Exception:
                pass
            finally:
                _loop.close()
                _loop = None
