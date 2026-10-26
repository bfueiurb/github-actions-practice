
import sys
import time
import threading
import subprocess
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

ROOT = Path(__file__).resolve().parent

IGNORED_DIRS = {
    ".git", "__pycache__", ".pytest_cache",
    ".venv", "venv", "target"
}


class TestFileHandler(FileSystemEventHandler):

    def __init__(self):
        self.timers = {}
        self.lock = threading.Lock()

    def on_modified(self, event):
        if not event.is_directory:
            self.handle_change(Path(event.src_path))

    def on_created(self, event):
        if not event.is_directory:
            self.handle_change(Path(event.src_path))

    def on_moved(self, event):
        if not event.is_directory:
            self.handle_change(Path(event.dest_path))

    def on_deleted(self, event):
        if not event.is_directory:
            self.handle_change(Path(event.src_path))

    def handle_change(self, path):
        try:
            relative = path.resolve().relative_to(ROOT)
        except ValueError:
            return

        if any(part in IGNORED_DIRS for part in relative.parts):
            return

        kind = None

        if relative.as_posix() in {
            "calculator.py",
            "test_calculator.py"
        }:
            kind = "python"

        elif (
            relative.parts[0] == "java-demo"
            and (
                relative.suffix == ".java"
                or relative.name == "pom.xml"
            )
        ):
            kind = "java"

        if kind is None:
            return

        # 合并短时间内的重复文件事件，避免连续运行测试
        with self.lock:
            old_timer = self.timers.get(kind)

            if old_timer is not None:
                old_timer.cancel()

            timer = threading.Timer(
                1.0, self.run_tests, args=(kind,)
            )
            timer.daemon = True
            self.timers[kind] = timer
            timer.start()

    def run_tests(self, kind):
        print(f"\n检测到文件变化，开始运行 {kind} 测试……")

        if kind == "python":
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "-v"],
                cwd=ROOT
            )
        else:
            result = subprocess.run(
                "mvn -B test",
                cwd=ROOT / "java-demo",
                shell=True
            )

        if result.returncode == 0:
            print(f"{kind} 测试通过")
        else:
            print(f"{kind} 测试失败，请检查上方日志")

        with self.lock:
            self.timers.pop(kind, None)


def main():
    observer = Observer()
    observer.schedule(
        TestFileHandler(),
        str(ROOT),
        recursive=True
    )
    observer.start()

    print("文件监听已启动。")
    print("保存 Python 或 Java 源文件后将自动执行测试。")
    print("按 Ctrl+C 可以停止监听。")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main()
