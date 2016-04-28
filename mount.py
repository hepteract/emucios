#!/usr/bin/python2

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn
from stat import S_IFDIR, S_IFLNK, S_IFREG
from errno import ENOENT

import logging

import archive
import time

MODE = 0o644

class FileSystem(LoggingMixIn, Operations):
    """FUSE wrapper for PYA format files"""

    def __init__(self, files):
        self.files = files
        self.data = {}
        self.fd = 0
    
    def truncate(self, path, length, fh = None):
        self.files.set_path(path,
                self.files.get_path(path)[:length]
                )

        self.data[path]["st_ctime"] = self.data[path]["st_mtime"] = time.time()
        
        return 0

    def chmod(self, path, mode):
        return 0

    def chown(self, path, uid, gid):
        return 0

    def create(self, path, mode):
        self.files.set_path(path, "")
        self.fd += 1
        return self.fd
    
#    def open(self, path, ino, fi = 0o777): # I have no clue what these args mean
#        self.fd += 1
#        return self.fd

    open = None

    def getattr(self, path, fh = None):
        now = 0 # Avoid programs thinking the file has been changed

        if path in self.data:
            pass
        elif hasattr( self.files.get_path( str(path) ), "keys" ):
            self.data[path] = dict(st_mode=(S_IFDIR | MODE), st_ctime=now,
                    st_mtime=now, st_atime=now, st_nlink=2)
        else:
            self.data[path] = dict(st_mode=(S_IFREG | MODE), st_ctime=now,
                    st_mtime=now, st_atime=now,
                    st_size = len(self.files.get_path( str(path) )),
                    st_uid = 1000, st_gid = 1000)

        self.data[path]["st_atime"] = time.time()

        return self.data[path]

    def read(self, path, size, offset, fh):
        return self.files.get_path(path) [offset:offset + size]

    def readlink(self, path):
        return self.files.get_path(path)

    def rename(self, old, new):
        self.files.set_path(new, self.files.get_path(old))
        self.files.del_path(old)

    def rmdir(self, path):
        self.files.del_path(path)

    def unlink(self, path):
        self.files.del_path(path)

    def write(self, path, data, offset, fh):
        self.files.set_path(path,
                self.files.get_path(path)[:offset] + data)
        self.data[path]["st_ctime"] = self.data[path]["st_mtime"] = time.time()
        return len(data)

    def readdir(self, path, fh):
        get = self.files.get_path( str(path) )

        yield '.'
        yield '..'

        if hasattr(get, "keys"):
            for key in get.keys():
                yield str(key)

logging.basicConfig(level=logging.DEBUG)
