import os
from time import strftime, gmtime
import inspect
import sys
import argparse
import configparser
import logging
import math
from itertools import chain, islice

from binr.debug import launch_server

from .fs import FileType 
from .archfs import FileSystem as archfs
from .fsdt import DataTables as fsdt
from .utils import print_table
from .fsrsc import ResourceManager as fsrsc
from .rsc import resource_id_from_filepath, ResourceId
from .mdl_viewer import Server as MdlViewer

LIB_PATH = os.path.dirname(os.path.abspath(os.path.join(inspect.getfile(inspect.currentframe()), "..")))

#########
# UTILS #
#########
def get_resource_id(args):
    if args.n:
        return resource_id_from_filepath(args.n)
    elif args.r:
        s = args.r.split("-")
        return ResourceId(
            folder_name = s[0],
            dirname_hash = int(s[1], 0x10),
            filename_hash = int(s[2], 0x10)
        )
    raise RuntimeError("You must specify a name or a resource_id")

########
# VIEW #
########

######
# FS #
######
def view_fs(conf, args):
    fs = get_fs(conf, args)
    print(">>> fs")
    print(fs)
    print()
    print(">>> folders")
    print_table(["NAME"], ((folder.name(), ) for folder in fs.folders()))

def view_folder(conf, args):
    folder = get_fs(conf, args).folder(args.folder)
    print(">>> folder")
    print(folder)
    print()
    print(">>> files")
    print_table(["TYPE", "DIRNAME_HASH", "FILENAME_HASH"], ((file.type(), "{:08X}".format(file.resource_id().dirname_hash), "{:08X}".format(file.resource_id().filename_hash)) for file in folder.files()))

def view_sub_folder(conf, args):
    if args.n:
        if not args.n.endswith("/"):
            args.n += "/"
        args.n += "0"
    elif args.r:
        args.r = "{}-00000000".format(args.r)
    resource_id = get_resource_id(args)
    folder = get_fs(conf, args).folder(resource_id.folder_name)
    print(">>> sub_folder")
    print(resource_id)
    print()
    print(">>> files")
    print_table(
        ["TYPE", "DIRNAME_HASH", "FILENAME_HASH"], 
        ((file.type(), "{:08X}".format(file.resource_id().dirname_hash), "{:08X}".format(file.resource_id().filename_hash)) 
            for file in filter(lambda f: f.resource_id().dirname_hash == resource_id.dirname_hash, folder.files())
        )
    )

def find_file(conf, args):
    if args.n:
        if not args.n.startswith("/"):
            args.n = "/" + args.n
        args.n = "0" + args.n
    elif args.r:
        args.r = "0-00000000-{}".format(args.r)
    resource_id = get_resource_id(args)
    fs = get_fs(conf, args)
    for folder in fs.folders():
        print(">>> {}".format(folder.name()))
        print_table(
            ["TYPE", "DIRNAME_HASH", "FILENAME_HASH"], 
            ((file.type(), "{:08X}".format(file.resource_id().dirname_hash), "{:08X}".format(file.resource_id().filename_hash)) 
                for file in filter(lambda f: f.resource_id().filename_hash == resource_id.filename_hash, folder.files())
            )
        )
        print()

BYTES_PER_LINE = 0x10
def print_data(data):
    for i in range(math.ceil(len(data) / BYTES_PER_LINE)):
        print(
            "{:<{size}}".format(" ".join("{:02X}".format(d) for d in data[i * BYTES_PER_LINE:(i+1) * BYTES_PER_LINE]), size=BYTES_PER_LINE * 3)
            + "| " + "".join(chr(d) if 0x20 <= d < 0x7F else "." for d in data[i * BYTES_PER_LINE:(i+1) * BYTES_PER_LINE])
        )

def view_file(conf, args):
    file = get_fs(conf, args).file_by_id(get_resource_id(args)).get()
    print(">>> file")
    print(file)
    buf = []
    if file.type() == FileType.STD:
        print()
        print(">>> data")
        print_data(file.data())
        buf.append(file.data())
    elif file.type() == FileType.TEX:
        print()
        print(">>> header")
        print_data(file.header())
        buf.append(file.header())
        for i, mipmap in enumerate(file.mipmaps()):
            print()
            print(">>> mipmap[{}]".format(i))
            print_data(mipmap)
            buf.append(mipmap)
    elif file.type() == FileType.MDL:
        print()
        print(">>> header")
        print_data(file.header())
        buf.append(file.header())
        print()
        print(">>> mesh_shapes")
        print_data(file.meshes_shape())
        buf.append(file.meshes_shape())
        for i, lod_buffers in enumerate(file.lods_buffers()):
            for j, lod_buffer in enumerate(lod_buffers):
                print()
                print(">>> lod[{}]_buffer[{}]".format(i, j))
                print_data(lod_buffer)
                buf.append(lod_buffer)
    if args.m and args.f:
        launch_server(args.m, args.f, buf[args.i])

#######
# MDL #
#######
def model_viewer(conf, args):
    MdlViewer(
        get_rsc(conf, args)
    ).run(host='localhost', port=8080)

def view_mdl(conf, args):
    mdl = get_rsc(conf, args).get_model_by_id(get_resource_id(args))
    print(">>> model")
    print(mdl) 
    print()
    print(">>> lods")
    print_table(["ID"], [[i] for i, _ in enumerate(mdl.lods())])

def view_lod(conf, args):
    lod = get_rsc(conf, args).get_model_by_id(get_resource_id(args)).lod(args.id)
    print(">>> lod")
    print(lod)
    print()
    print(">>> meshes")
    print_table(["ID"], [[i] for i, _ in enumerate(lod.meshes())])

def view_mesh(conf, args):
    mesh = get_rsc(conf, args).get_model_by_id(get_resource_id(args)).lod(args.lod_id).mesh(args.id)
    print(">>> mesh")
    print(mesh)
    print()
    print_table(
        ["ID", "POSITION", "NORMAL", "BLEND_WEIGHT", "BLEND_INDICES", "UV", "BINORMAL", "COLOR"],
        ([i] + list(values) for i, values in enumerate(zip(mesh.positions(), mesh.normals(), mesh.blend_weights(), mesh.blend_indices(), mesh.uvs(), mesh.binormals(), mesh.colors())))
    )
    print()
    print_table(["INDEX"], ([i] for i in mesh.indices()))

#######
# TEX #
#######
def view_tex(conf, args):
    tex = get_rsc(conf, args).get_texture_by_id(get_resource_id(args))
    print(">>> texture")
    print(tex) 

######
# DT #
######
def view_dt(conf, args):
    dt = get_dt(conf, args)
    print(">>> dt")
    print(dt)
    print()
    print(">>> tables")
    print_table(["NAME"], ((table.name(), ) for table in dt.tables()))

def view_table(conf, args):
    table = get_dt(conf, args).table(args.table)
    print(">>> table")
    print(table)
    print()
    print(">>> loc_tables")
    print_table(["NAME", "LANG"], ((loc_table.name(), loc_table.lang()) for loc_table in table.loc_tables()))

def view_loc_table(conf, args):
    loc_table = get_dt(conf, args).table(args.table).loc_table(args.lang)
    print(">>> loc_table")
    print(loc_table)
    print()
    print(">>> rows")
    rows = islice(loc_table.rows(), None)
    first_row = list(islice(rows, 1))
    if first_row:
        headers = ["ID"] + [str(i) for i in range(len(first_row[0].values))]
        print_table(headers, ([val.id] + list(val.values) for val in chain(first_row, rows)))

def view_row(conf, args):
    row = get_dt(conf, args).table(args.table).loc_table(args.lang).row(args.id)
    print(">>> id")
    print(row.id)
    print()
    print(">>> values")
    print_table(["INDEX", "VALUE"], ((i, val) for i, val in enumerate(row.values)))

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
    console_handler.setFormatter(logging.Formatter("[ %(asctime)s - %(levelname)s ] %(message)s"))
    console_handler.setLevel(logging.WARN)
    root_logger.addHandler(console_handler)

    # File handler
    log_filename = os.path.join(get_logging_path(conf), "ffxiv_tools_{}.log".format(strftime("%y%m%d_%H%M%S", gmtime())))

    if not os.path.exists(os.path.dirname(log_filename)):
        os.makedirs(os.path.dirname(log_filename))

    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s <%(filename)s %(lineno)d> %(funcName)s: %(message)s"))
    file_handler.setLevel(logging.DEBUG if args.debug else logging.INFO)
    root_logger.addHandler(file_handler)

##########
# CONFIG #
##########
def get_logging_path(conf):
    return conf["logging"]["path"]

def get_fs_by_name(conf, name):
    fs_section = conf["fs:{}".format(name)]
    fs_type = fs_section["type"]
    if fs_type == "archfs":
        return archfs(fs_section["path"])

def get_fs(conf, args):
    fs_name = args.fs
    if not fs_name:
        fs_name = conf["DEFAULT"]["fs"] 
    return get_fs_by_name(conf, fs_name)

def get_dt_by_name(conf, name):
    dt_section = conf["dt:{}".format(name)]
    dt_type = dt_section["type"]
    if dt_type == "fsdt":
        return fsdt(get_fs_by_name(conf, dt_section["fs"]))

def get_dt(conf, args):
    dt_name = args.dt
    if not dt_name:
        dt_name = conf["DEFAULT"]["dt"] 
    return get_dt_by_name(conf, dt_name)

def get_rsc_by_name(conf, name):
    rsc_section = conf["rsc:{}".format(name)]
    rsc_type = rsc_section["type"]
    if rsc_type == "fsrsc":
        return fsrsc(get_fs_by_name(conf, rsc_section["fs"]))

def get_rsc(conf, args):
    rsc_name = args.rsc
    if not rsc_name:
        rsc_name = conf["DEFAULT"]["rsc"]
    return get_rsc_by_name(conf, rsc_name)

def read_config():
    config_file = os.path.expanduser("~/.ffxiv_tools.ini")
    if not os.path.exists(config_file):
        print("Config file not found at: {}".format(config_file))
        print("cp {0} {1}".format(os.path.join(LIB_PATH, "example.ffxiv_tools.ini"), config_file))
        sys.exit(1)
    config = configparser.ConfigParser(defaults={
        "lib_path": LIB_PATH,
        "pwd": os.getcwd()
    })
    config.read([config_file])
    return config

###########
# PROCESS #
###########

def add_resource_arg(parser):
    parser.add_argument("-n", required=False, help="name of the file")
    parser.add_argument("-r", required=False, help="resource id of the file {folder}-{dirhash}-{filehash}")

def main():
    conf = read_config()

    parser = argparse.ArgumentParser(description="ffxiv_tools command line interface")
    parser.add_argument("--fs")
    parser.add_argument("--dt")
    parser.add_argument("--rsc")
    parser.add_argument("--debug", action="store_true", default=False)
    subparsers = parser.add_subparsers(title="sub modules")

    ########################
    # find_file sub module #
    ########################
    find_file_parser = subparsers.add_parser("find_file")
    find_file_parser.add_argument("-n", required=False, help="name of the file")
    find_file_parser.add_argument("-r", required=False, help="resource id of the file {filehash}")
    find_file_parser.set_defaults(callback=find_file)

    ###########################
    # model_viewer sub module #
    ###########################
    model_viewer_parser = subparsers.add_parser("model_viewer")
    model_viewer_parser.set_defaults(callback=model_viewer)

    ###################
    # view sub module #
    ###################
    view_parser = subparsers.add_parser("view", help="view stuff")
    view_subparsers = view_parser.add_subparsers(title="objects")

    # FS
    view_fs_parser = view_subparsers.add_parser("fs")
    view_fs_parser.set_defaults(callback=view_fs)

    view_folder_parser = view_subparsers.add_parser("folder")
    view_folder_parser.add_argument("folder")
    view_folder_parser.set_defaults(callback=view_folder)

    view_sub_folder_parser = view_subparsers.add_parser("sub_folder")
    view_sub_folder_parser.add_argument("-n", required=False, help="name of the folder")
    view_sub_folder_parser.add_argument("-r", required=False, help="resource id of the file {folder}-{dirhash}")
    view_sub_folder_parser.set_defaults(callback=view_sub_folder)

    view_file_parser = view_subparsers.add_parser("file")
    add_resource_arg(view_file_parser)
    view_file_parser.add_argument("-m", required=False, help="module containing the func to apply")
    view_file_parser.add_argument("-f", required=False, help="func to apply")
    view_file_parser.add_argument("-i", required=False, help="buffer index", default=0, type=int)
    view_file_parser.set_defaults(callback=view_file)

    # MDL
    view_mdl_parser = view_subparsers.add_parser("mdl")
    add_resource_arg(view_mdl_parser)
    view_mdl_parser.set_defaults(callback=view_mdl)

    view_lod_parser = view_subparsers.add_parser("lod")
    add_resource_arg(view_lod_parser)
    view_lod_parser.add_argument("id", type=int, default=0, nargs="?")
    view_lod_parser.set_defaults(callback=view_lod)

    view_mesh_parser = view_subparsers.add_parser("mesh")
    add_resource_arg(view_mesh_parser)
    view_mesh_parser.add_argument("lod_id", type=int)
    view_mesh_parser.add_argument("id", type=int, default=0, nargs="?")
    view_mesh_parser.set_defaults(callback=view_mesh)

    # TEX
    view_tex_parser = view_subparsers.add_parser("tex")
    add_resource_arg(view_tex_parser)
    view_tex_parser.set_defaults(callback=view_tex)

    # DT
    view_dt_parser = view_subparsers.add_parser("dt")
    view_dt_parser.set_defaults(callback=view_dt)

    view_table_parser = view_subparsers.add_parser("table")
    view_table_parser.add_argument("table")
    view_table_parser.set_defaults(callback=view_table)

    view_loc_table_parser = view_subparsers.add_parser("loc_table")
    view_loc_table_parser.add_argument("table")
    view_loc_table_parser.add_argument("lang", nargs="?", default="")
    view_loc_table_parser.set_defaults(callback=view_loc_table)

    view_row_parser = view_subparsers.add_parser("row")
    view_row_parser.add_argument("table")
    view_row_parser.add_argument("lang", nargs="?", default="")
    view_row_parser.add_argument("id", type=int)
    view_row_parser.set_defaults(callback=view_row)

    args = parser.parse_args()

    setup_logging(conf, args)
    logging.info("Executing: {}".format(sys.argv))

    if not hasattr(args, "callback"):
        parser.print_help()
    else:
        args.callback(conf, args)

    sys.exit(0)
