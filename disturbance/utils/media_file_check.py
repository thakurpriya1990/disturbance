import os
import argparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_MEDIA_PATH = os.path.normpath(BASE_DIR + "/media/")
ROOT_PRIVATE_MEDIA_PATH = os.path.normpath(BASE_DIR + "/private_media/")

def validate_paths(src_path, dst_path):
    #validate src_path
    if not src_path.startswith(ROOT_MEDIA_PATH):
        raise Exception("Source file path provided not within root media path:",ROOT_MEDIA_PATH)
    #validate dst_path
    if not dst_path.startswith(ROOT_PRIVATE_MEDIA_PATH):
        raise Exception("Destination file path provided not within root private media path:",ROOT_PRIVATE_MEDIA_PATH)

def normalise_paths(src_path, dst_path):
    try:
        src_path = os.path.normpath(src_path)
    except:
        raise Exception("Invalid source file path provided")

    try:
        dst_path = os.path.normpath(dst_path)
    except:
        raise Exception("Invalid destination file path provided")

    return src_path, dst_path

def get_dir_files(path, checked_paths=[]):
    
    #track checked_paths in case sub-directories loop back for some reason
    checked_paths = [path]
    files = []

    #iterate through files
    for item in os.listdir(path):
        #run func recursively for sub-directories
        pass

    return files

def check_missing_files(src_path, dst_path):
    #normalise paths
    src_path, dst_path = normalise_paths(src_path, dst_path)
    #validate paths
    validate_paths(src_path, dst_path)

    src_files = get_dir_files(src_path)
    dst_files = get_dir_files(dst_path)

    missing_files = []
    found_files = []

    return missing_files, found_files

def copy_missing_files(src_path, dst_path, overwrite=False):

    missing_files, found_files = check_missing_files(src_path, dst_path)

    #if overwrite is True then we also overwrite files that are not missing

def __main__():

    parser = argparse.ArgumentParser()
    parser.add_argument("src_path", help="file path of media directory or sub-directory, source path for checking/replacing missing files")
    parser.add_argument("dst_path", help="file path of private media directory or sub-directory, destination path for checking/replacing missing files")
    parser.add_argument("-o", "--overwrite", action="store_true", help="overwrite all files in specified destination path with those found in specified source path")
    args = parser.parse_args()
    
    print(args.src_path, args.dst_path, args.overwrite)
    copy_missing_files(args.src_path, args.dst_path, args.overwrite)

__main__()