#!/usr/bin/env python2

import cPickle as pickle
import shelve
import types
import os

class FileSystem(object):
    def __init__(self, shelf, autosync = True):
        self.shelf = shelf
        self.auto = autosync

    def __getitem__(self, name):
        if name == "":
            return self
        else:
            return self.shelf[name]

    def __setitem__(self, name, value):
        self.shelf[name] = value
        if self.auto:
            self.flush()

    def __delitem__(self, name):
        del self.shelf[name]
        if self.auto:
            self.flush()

    def flush(self):
        self.shelf.sync()

    def set_path(self, path, value, create_paths = False):
        path = path.split("/")
        cur = self
        for item in path[:-1]:
            if item not in cur.keys() and create_paths and item != "":
                cur[item] = {}
                
            cur = cur[item]
        cur[ path[-1] ] = value

    def get_path(self, path):
        path = path.split("/")
        cur = self
        for item in path:
            cur = cur[item]
        return cur

    def keys(self):
        return self.shelf.keys()

    def values(self):
        return [value for key, value in self.items()]

    def items(self):
        for key in self.shelf.keys():
            yield key, self.shelf[key]

    def __getattr__(self, name):
        return getattr(self.shelf, name)

class Archive(FileSystem):
    def extract(self):
        _extract(self.shelf)

    def compress(self, loc):
        _compress(loc, self)

def _extract(archive):
    orig = os.getcwd()

    for key in archive.keys():
        item = archive[key]
        if type(item) is dict:
            try:
                os.mkdir(key)
            except OSError:
                pass
            os.chdir(key)
            _extract(item)
            os.chdir("..")
        elif type(item) is str:
            with open(key, "w") as f:
                f.write(item)
        else:
            with open(key, "wb") as f:
                f.write( pickle.dumps(item) )

    os.chdir(orig)

def _compress(loc, archive):
    orig = os.getcwd()
    os.chdir(loc)
    tree = os.walk(".")

    for directory in tree:
        for subdir in directory[1]:
            archive.set_path(os.path.join(directory[0][1:], subdir), {}, True)
        for filename in directory[2]:
            path = os.path.join(directory[0], filename)
            with open(path) as f:
                archive.set_path(path[1:], f.read(), True)
    os.chdir(orig)
    return archive

def open_archive(filename, archive = True):
    shelf = shelve.open(filename, writeback = True)
    if archive:
        return Archive(shelf)
    else:
        return FileSystem(shelf)
