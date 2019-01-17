import argparse
import os
import sqlite3

db_insert_statement = 'INSERT INTO music_file(source_file_path) VALUES(?)'


class Amazong(object):

    def __init__(self, src_dir_path, dest_dir_path, dry_run):
        self._dry_run = dry_run or False
        if not os.path.isdir(src_dir_path):
            raise Exception("Source path must be a readable directory")

        self._src_dir_path = src_dir_path
        self._dest_dir_path = dest_dir_path
        pass

    def process(self):
        print("Process directory %s to directory %s, dry run = %s" % (
            self._src_dir_path, self._dest_dir_path, self._dry_run))
        # look for a database file in the destination directory
        with self.get_or_create_db() as db:
            self.prepare_table(db)
            db_cursor = db.cursor()
            self.store_file_paths(db_cursor)
            db.commit()

    def store_file_paths(self, db_cursor):
        os.path.walk(self._src_dir_path, store_path_to_file, db_cursor)

    def prepare_table(self, db):
        create_statement = ('CREATE TABLE IF NOT EXISTS music_file '
                            '(id INTEGER PRIMARY KEY AUTOINCREMENT, '
                            'source_file_path TEXT NOT NULL UNIQUE, digest TEXT);')
        cursor = db.cursor()
        cursor.execute(create_statement)
        db.commit()

    def get_or_create_db(self):
        if not os.path.isdir(self._dest_dir_path):
            os.makedirs(self._dest_dir_path)
        db_path = os.path.join(self._dest_dir_path, 'amazong.db')
        return sqlite3.connect(db_path)


def store_path_to_file(db_cursor, path, names):
    for name in names:
        file_path = os.path.join(path, name)
        if os.path.isfile(file_path):
            print("Storing Path: %s, Filename: %s" % (path, name))
            db_cursor.execute(db_insert_statement, (file_path,))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Maintain encoded music collection")
    parser.add_argument('-d', action='store_const',  dest='dry_run', const=True)
    parser.add_argument('src')
    parser.add_argument('dest')
    args = parser.parse_args()
    processor = Amazong(args.src, args.dest, args.dry_run)
    processor.process()
