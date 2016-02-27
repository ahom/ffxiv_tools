import os
from time import strftime, gmtime
import inspect
import sys
import argparse
import configparser
import logging
from itertools import chain, islice

from binr.debug import launch_server

from .fs import FileType, FileRef
from .archfs import FileSystem as archfs
from .fsdt import DataTables as fsdt
from .utils import print_table

LIB_PATH = os.path.dirname(os.path.abspath(os.path.join(inspect.getfile(inspect.currentframe()), '..')))

############
# COMMANDS #
############
########
# VIEW #
########
def view_fs(conf, args):
    fs = get_fs(conf, args)
    print('>>> fs')
    print(fs)
    print()
    print('>>> folders')
    _list_folders(fs.folders())

def view_folder(conf, args):
    folder = get_fs(conf, args).folder(args.folder)
    print('>>> folder')
    print(folder)
    print()
    print('>>> files')
    _list_files(folder.files())

BYTES_PER_LINE = 0x10
def print_data(data):
    for i in range((len(data) // BYTES_PER_LINE) + 1):
        print(
            '{:<{size}}'.format(' '.join('{:02X}'.format(d) for d in data[i * BYTES_PER_LINE:(i+1) * BYTES_PER_LINE]), size=BYTES_PER_LINE * 3)
            + '| ' + ''.join(chr(d) if 0x20 <= d < 0x7F else '.' for d in data[i * BYTES_PER_LINE:(i+1) * BYTES_PER_LINE])
        )

def view_file(conf, args):
    _view_file(args, get_fs(conf, args).folder(args.folder).file(FileRef(args.folder, int(args.dirname_hash, 0x10), int(args.filename_hash, 0x10))))

def view_filename(conf, args):
    _view_file(args, get_fs(conf, args).file(args.filename))

def _view_file(args, file):
    file = file.read()
    print('>>> file')
    print(file)
    buf = []
    if file.type() == FileType.STD:
        print()
        print('>>> data')
        print_data(file.data())
        buf.append(file.data())
    elif file.type() == FileType.TEX:
        print()
        print('>>> header')
        print_data(file.header())
        buf.append(file.header())
        print()
        print('>>> mipmaps')
        print_data(file.mipmaps())
        buf.append(file.mipmaps())
    elif file.type() == FileType.MDL:
        print()
        print('>>> header')
        print_data(file.header())
        buf.append(file.header())
        print()
        print('>>> mesh_headers')
        print_data(file.mesh_headers())
        buf.append(file.mesh_headers())
        print()
        print('>>> lods_buffers')
        print_data(file.lods_buffers())
        buf.append(file.lods_buffers())
    if args.m and args.f:
        launch_server(args.m, args.f, buf[args.i])

def view_dt(conf, args):
    dt = get_dt(conf, args)
    print('>>> dt')
    print(dt)
    print()
    print('>>> tables')
    _list_tables(dt.tables())

def view_table(conf, args):
    table = get_dt(conf, args).table(args.table)
    print('>>> table')
    print(table)
    print()
    print('>>> loc_tables')
    _list_loc_tables(table.loc_tables())

def view_loc_table(conf, args):
    loc_table = get_dt(conf, args).table(args.table).loc_table(args.lang if args.lang else '')
    print('>>> loc_table')
    print(loc_table)
    print()
    print('>>> rows')
    _list_rows(loc_table.rows())

def view_row(conf, args):
    row = get_dt(conf, args).table(args.table).loc_table(args.lang if args.lang else '').row(args.id)
    print('>>> id')
    print(row.id)
    print()
    print('>>> values')
    for val in row.values:
        print(val)

########
# LIST #
########
def _list_files(files):
    print_table(['DIRNAME_HASH', 'FILENAME_HASH'], (('{:08X}'.format(file.fileref().dirname_hash()), '{:08X}'.format(file.fileref().filename_hash())) for file in files))

def _list_folders(folders):
    print_table(['NAME'], ((folder.name(), ) for folder in folders))

def _list_tables(tables):
    print_table(['NAME'], ((table.name(), ) for table in tables))

def _list_loc_tables(loc_tables):
    print_table(['NAME', 'LANG'], ((loc_table.name(), loc_table.lang()) for loc_table in loc_tables))

def _list_rows(rows):
    first_row = list(islice(rows, 1))
    if first_row:
        headers = ['ID'] + [str(i) for i in range(len(first_row[0].values))]
        print_table(headers, ([val.id] + list(val.values) for val in chain(first_row, islice(rows, 1, None))))

###########
# LOGGING #
###########
def setup_logging(conf, args):
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)
    root_logger.setLevel(logging.NOTSET)

    # Console handler
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(logging.Formatter('[ %(asctime)s - %(levelname)s ] %(message)s'))
    console_handler.setLevel(logging.WARN)
    root_logger.addHandler(console_handler)

    # File handler
    log_filename = os.path.join(get_logging_path(conf), 'ffxiv_tools_%s.log' % strftime('%y%m%d_%H%M%S', gmtime()))

    if not os.path.exists(os.path.dirname(log_filename)):
        os.makedirs(os.path.dirname(log_filename))

    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s <%(filename)s %(lineno)d> %(funcName)s: %(message)s'))
    file_handler.setLevel(logging.DEBUG if args.debug else logging.INFO)
    root_logger.addHandler(file_handler)

##########
# CONFIG #
##########
def get_logging_path(conf):
    return conf['logging']['path']

def get_fs_by_name(conf, name):
    fs_section = conf['fs:%s' % name]
    fs_type = fs_section['type']
    if fs_type == 'archfs':
        return archfs(fs_section['path'])

def get_fs(conf, args):
    fs_name = args.fs
    if not fs_name:
        fs_name = conf['DEFAULT']['fs'] 
    return get_fs_by_name(conf, fs_name)

def get_dt_by_name(conf, name):
    dt_section = conf['dt:%s' % name]
    dt_type = dt_section['type']
    if dt_type == 'fsdt':
        return fsdt(get_fs_by_name(conf, dt_section['fs']))

def get_dt(conf, args):
    dt_name = args.dt
    if not dt_name:
        dt_name = conf['DEFAULT']['dt'] 
    return get_dt_by_name(conf, dt_name)

def read_config():
    config_file = os.path.expanduser("~/.ffxiv_tools.ini")
    if not os.path.exists(config_file):
        print("Config file not found at: %s" % config_file)
        print("cp %s %s" % (os.path.join(LIB_PATH, 'example.ffxiv_tools.ini'), config_file))
        sys.exit(1)
    config = configparser.ConfigParser(defaults={
        'lib_path': LIB_PATH,
        'pwd': os.getcwd()
    })
    config.read([config_file])
    return config

###########
# PROCESS #
###########

def main():
    conf = read_config()

    parser = argparse.ArgumentParser(description='ffxiv_tools command line interface')
    parser.add_argument('--fs')
    parser.add_argument('--dt')
    parser.add_argument('--debug', action='store_true', default=False)
    subparsers = parser.add_subparsers(title='sub modules')

    ###################
    # view sub module #
    ###################
    view_parser = subparsers.add_parser('view', help='view stuff')
    view_subparsers = view_parser.add_subparsers(title='objects')

    view_fs_parser = view_subparsers.add_parser('fs')
    view_fs_parser.set_defaults(callback=view_fs)

    view_folder_parser = view_subparsers.add_parser('folder')
    view_folder_parser.add_argument('folder')
    view_folder_parser.set_defaults(callback=view_folder)

    view_filename_parser = view_subparsers.add_parser('filename')
    view_filename_parser.add_argument('filename')
    view_filename_parser.add_argument('-m', required=False, help='module containing the func to apply')
    view_filename_parser.add_argument('-f', required=False, help='func to apply')
    view_filename_parser.add_argument('-i', required=False, help='buffer index', default=0, type=int)
    view_filename_parser.set_defaults(callback=view_filename)

    view_file_parser = view_subparsers.add_parser('file')
    view_file_parser.add_argument('folder')
    view_file_parser.add_argument('dirname_hash')
    view_file_parser.add_argument('filename_hash')
    view_file_parser.add_argument('-m', required=False, help='module containing the func to apply')
    view_file_parser.add_argument('-f', required=False, help='func to apply')
    view_file_parser.add_argument('-i', required=False, help='buffer index', default=0, type=int)
    view_file_parser.set_defaults(callback=view_file)

    view_dt_parser = view_subparsers.add_parser('dt')
    view_dt_parser.set_defaults(callback=view_dt)

    view_table_parser = view_subparsers.add_parser('table')
    view_table_parser.add_argument('table')
    view_table_parser.set_defaults(callback=view_table)

    view_loc_table_parser = view_subparsers.add_parser('loc_table')
    view_loc_table_parser.add_argument('table')
    view_loc_table_parser.add_argument('lang', nargs='?')
    view_loc_table_parser.set_defaults(callback=view_loc_table)

    view_row_parser = view_subparsers.add_parser('row')
    view_row_parser.add_argument('table')
    view_row_parser.add_argument('lang', nargs='?')
    view_row_parser.add_argument('id', type=int)
    view_row_parser.set_defaults(callback=view_row)

    args = parser.parse_args()

    setup_logging(conf, args)
    logging.info('Executing: %s' % sys.argv)

    if not hasattr(args, 'callback'):
        parser.print_help()
    else:
        args.callback(conf, args)

    sys.exit(0)
