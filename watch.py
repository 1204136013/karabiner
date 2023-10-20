#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os, sys, time, subprocess

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def log(s):
    print('[Monitor] %s' % s)


class MyFileSystemEventHander(FileSystemEventHandler):

    def __init__(self, fn):
        super(MyFileSystemEventHander, self).__init__()
        self.restart = fn

    def on_any_event(self, event):
        if event.src_path.endswith('.go'):
            log('Python source file changed: %s' % event.src_path)
            self.restart()


class ProcessManager:

    def __init__(self, command_build, command_run):
        self.command_build = command_build
        self.command_run = command_run
        self.process_build = None
        self.process_run = None

    def kill_process(self):
        process = self.process_run
        if process:
            log('Kill process [%s]...' % process.pid)
            process.kill()
            process.wait()
            log('Process ended with code %s.' % process.returncode)
            print('after', process)
            self.process_run = None

    def start_process(self):
        command_build = self.command_build
        command_run = self.command_run
        log('Start process %s' % ' '.join(command_build))
        build_code = subprocess.call(
            command_build,
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
            shell=True,
        )
        log('Process build ended with code %s.' % build_code)

        if build_code == 0:
            log('Start process %s' % ' '.join(command_run))
            self.process_run = subprocess.Popen(
                command_run,
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr,
                shell=True,
            )
        else:
            log("build error")

    def restart_process(self):
        self.kill_process()
        self.start_process()


def start_watch(path, callback):
    observer = Observer()
    p = ProcessManager(
        command_build=command1,
        command_run=command2,
    )
    observer.schedule(
        MyFileSystemEventHander(
            p.restart_process
        ),
        path,
        recursive=True
    )
    observer.start()
    log('Watching directory %s...' % path)
    p.start_process()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    command1 = 'make build'
    command2 = './bin/service.exe -f ./configs/dev.yaml'
    # command1 = 'sleep 3; echo a'
    # command2 = 'echo b'

    path = os.path.abspath('.')
    start_watch(path, None)
