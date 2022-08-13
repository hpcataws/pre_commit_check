import platform
import os


def skipIfDarwin(func):
    def wrapper():
        if platform.system() != 'Darwin':
            func()
    return wrapper


def skipIfLinux(func):
    def wrapper():
        if platform.system() != 'Linux':
            func()
    return wrapper


def skipIfWindows(func):
    def wrapper():
        if platform.system() != 'Windows':
            func()
    return wrapper


def skipIfGitHubAction(func):
    def wrapper():
        if 'GITHUB_ACTIONS' not in os.environ:
            func()
    return wrapper
