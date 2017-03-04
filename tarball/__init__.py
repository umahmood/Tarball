# -*- coding: utf-8 -*-
import os
import time
import tarfile

from fman import (
    DirectoryPaneCommand, 
    show_status_message,
    show_prompt,
)

__author__     = "Usman Mahmood"
__license__    = "MIT"
__version__    = "1.0.1"
__maintainer__ = "Usman Mahmood"

class Tarball(DirectoryPaneCommand):
    def __call__(self):
        current_dir    = self.pane.get_path()
        selected_files = self.pane.get_selected_files()
        if len(selected_files) == 0: 
            show_status_message("Tarball: no file(s) selected", timeout_secs=3)
            return            

        # single selected file which is tarball means we extract
        if len(selected_files) == 1 and self.is_tarfile(selected_files[0]):            
            self.extract_tar_file(selected_files[0], current_dir)
        else:
            self.create_tar_file(selected_files, current_dir)

        for file_path in selected_files:
            self.pane.toggle_selection(file_path)

    def extract_tar_file(self, tarball_path, current_dir):
        """
        Extract tar file under the current directory

        @param tarball_path (string) - path to tarball to extract.
        @param current_dir  (string) - directory to extract tarball under.

        @return None
        """
        ext, r, _ = self.get_tarfile_type(tarball_path)
        if not ext: return
        dir_name    = os.path.basename(tarball_path).replace(ext, "")
        target_path = current_dir + os.sep + dir_name 
        try:
            os.mkdir(target_path)       
        except FileExistsError:
            timestamp   = int(time.time())
            target_path = target_path + '_' + str(timestamp)
            os.mkdir(target_path)

        with tarfile.open(tarball_path, mode=r) as tar:
            tar.extractall(path=target_path)

    def create_tar_file(self, selected_files, current_dir):
        """
        Create a tar file from a given set of files in the current directory.

        @param selected_files (list)   - list of files to tar.
        @param current_dir    (string) - parent directory were selected files reside.

        @return None
        """
        prompt_msg="""Tarball

Enter file name 

(!) Make sure to include file extension e.g. file.tar, file.tar.gz"""

        target_file, _ = show_prompt(prompt_msg)    
        if not target_file: return

        ext, _, w = self.get_tarfile_type(target_file)
        if not ext: return

        self.pane.set_path(current_dir)
        with tarfile.open(current_dir + os.sep + target_file, mode=w) as tar:
            for file in selected_files:
                filename = os.path.basename(file)
                tar.add(file, arcname=filename)

    def is_tarfile(self, filename):
        """
        Determines if 'filename' is a valid tar file.

        @param filename (string) - tar file name

        @return (boolean)
        """
        try:
            return tarfile.is_tarfile(filename)
        except (FileNotFoundError, IsADirectoryError) as e:
            return False

    def get_tarfile_type(self, filename):
        """
        Get tar file type returns the type of tar file i.e. .tar, 
        .tar.gz etc... as well as the correct read and write modes 
        for the file.

        See https://docs.python.org/3.4//library/tarfile.html for
        supported archive file types.

        @param filename (string) - tar file name

        @return (tuple) - (file extension, read_mode, write_mode)
        """
        opts = (None, None, None)
        if filename.endswith(".tar"):
            opts = ".tar", "r:*", "w:"
        elif filename.endswith(".tar.gz"):
            opts = ".tar.gz", "r:gz", "w:gz"
        elif filename.endswith(".tar.bz2"):
            opts = ".tar.bz2", "r:bz2", "w:bz2"
        elif filename.endswith(".tar.lzma"):
            opts = ".tar.lzma", "r:xz", "w:xz"
        return opts          
