from engine.sdl import current_time

from typing import Callable, List


class Task:
    __slots__ = 'callback', 'delay', 'execute_at', 'repeat', 'done'

    def __init__(
            self, callback: Callable[[], None], delay: int,
            execute_at: int, repeat: bool, done: bool = False):
        self.callback = callback
        self.delay = delay
        self.execute_at = execute_at
        self.repeat = repeat
        self.done = done

    def ready(self, t: int) -> bool:
        return t >= self.execute_at

    def execute(self) -> None:
        self.callback()
        if self.repeat:
            self.execute_at += self.delay
        else:
            self.done = True


Tasks = List[Task]


class Timer:
    __slots__ = 'tasks'

    def __init__(self) -> None:
        self.tasks: Tasks = []

    def add_task(self, callback: Callable[[], None], delay: int, repeat: bool = False) -> None:
        execute_at = current_time() + delay
        self.tasks.append(Task(callback, delay, execute_at, repeat))

    def update(self) -> None:
        self.execute_ready_tasks()
        self.remove_done_tasks()

    def execute_ready_tasks(self) -> None:
        t = current_time()
        for task in self.tasks:
            if task.ready(t):
                task.execute()

    def remove_done_tasks(self) -> None:
        # FIXME This might be inefficient.
        # Is there a better way?
        self.tasks = [t for t in self.tasks if not t.done]
