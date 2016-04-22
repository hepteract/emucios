#!/usr/bin/env python2

from __future__ import print_function

import cPickle as pickle
import shelve
import types
import os

class FileSystem(object):
    def __init__(self, shelf, autosync = True, magic = None):
        self.shelf = shelf
        self.auto = autosync
        self.magic = magic if magic is not None else {}
        self.readcount = None
        self.path = 0xDEADBABA

    def __getitem__(self, name):
        if name in self.magic:
            return self.magic[name][0] ()
        
        elif name in ("", "."):
            return self
        else:
            return self.shelf[name]

    def __setitem__(self, name, value):
        if name == "readcount":
            self.readcount = value
        elif name in self.magic:
            self.magic[name][1] (value)
        else:
            self.shelf[name] = value
            if self.auto:
                self.flush()

    def __delitem__(self, name):
        del self.shelf[name]
        if self.auto:
            self.flush()

    def flush(self):
        self.walk( self.clean, dirty = True )

        self.shelf.sync()

    def clean(self, (key, value) ):
        try:
            pickle.dumps(value)
        except:
            return -1

    def set_path(self, path, value, create_paths = False):
        if path.startswith("/"):
            path = path[1:]
            
        path = path.split("/")
        cur = self
        for item in path[:-1]:
            if item not in cur.keys() and create_paths and item != "":
                cur[item] = {}
                
            cur = cur[item]
        cur[ path[-1] ] = value

    def del_path(self, path):
        if path.startswith("/"):
            path = path[1:]
            
        path = path.split("/")
        cur = self
        for item in path[:-1]:
            cur = cur[item]
        del cur[ path[-1] ]

    def get_path(self, path):
        if path.startswith("/"):
            path = path[1:]
            
        path = path.split("/")
        cur = self
        for item in path:
            cur = cur[item]
        if type(cur) is str and self.readcount:
            ret = cur[:self.readcount]
            self.readcount = None
            return ret
        else:
            return cur

    def keys(self):
        return self.shelf.keys()

    def values(self):
        return [value for key, value in self.items()]

    def items(self):
        for key in self.shelf.keys():
            yield key, self.shelf[key]

    def walk(self, func = None, item = None, dirty = False):
        ret = None

        if func is None:
            ret = []
            func = lambda item: ret.append(item)

        if item is None:
            item = self

        for key, value in item.items():
            if type(value) is type:
                if dirty: # Allow some functions to run on directories
                    err = func( (key, value) )

                    if err == -1:
                        del item[key]

                break # If we are in a directory with a class, this whole directory is bad and needs to be ignored
            if hasattr(value, 'keys'):
                self.walk(func, value)
            else:
                err = func( (key, value) )

                if err == -1:
                    del item[key]

        return ret

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
        if key != "":
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
#                with open(key, "w") as f:
#                    f.write( str(item) )
		pass

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
