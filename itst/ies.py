#!/usr/bin/env python
# IES - IEEE@UMD Exam Scanner Library - v1.0
# 

import magic
import colorama
import os
import sys
import re

format_exts = {
                # Self-contained documents
                "application/pdf"    :  ".pdf",
                "application/postscript" : [ ".ps", ".eps" ],
                
                # Microsoft Office
                "application/msword" : ".doc",
                "application/vnd.ms-powerpoint"
                    : ".ppt",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    : ".docx",
                
                # Images
                "image/x-ms-bmp" : ".bmp",
                "image/jpeg" : [ ".jpg", ".jpeg" ],
                "image/gif" : ".gif",
                "image/png" : ".png",
                "image/tiff" : [ ".tif", ".tiff" ],
                
                # Archive files
                "application/zip" : [ ".zip", ".pages" ],
                "application/x-rar" : ".rar",
                
                # Text file
                "text/plain" : ".txt"
                
            }

supported_mime_types = format_exts.keys()

def getScriptPath():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


# Parse file name into parts
def parseFileName(file_name):
    #file_re = re.compile(r"^([A-Z]{4}\d{3}[A-Z]*)_(\d{4})_([SUFW])_([A-Za-z-]+)_(.*)\.(?:(?i)pdf|doc|docx|ppt|pptx|jpg|jpeg|zip|rar|gif)$")

    ext_regex_part = "|".join([x[1:] if type(x) == str else "|".join([y[1:] for y in x]) for x in format_exts.values()])
    final_file_re_txt = r"^([A-Z]{4}\d{3}[A-Z]*)_(\d{4})_([SUFW])_([A-Za-z-]+)_(.*)\.(?:(?i)" + ext_regex_part + r")$"
    file_part_re_txt = r"^([A-Z]{4}\d{3}[A-Z]*)_(\d{4})_([SUFW])_([A-Za-z-]+)_(.*)"

    file_re = re.compile(final_file_re_txt)
    file_part_re = re.compile(file_part_re_txt)
        
    m = file_part_re.match(file_name)
    
    exam_info = {}
    
    if m:
        exam_info["class"] = m.group(1)
        exam_info["year"] = int(m.group(2))
        exam_info["semester"] = m.group(3)
        exam_info["professor"] = m.group(4)
        exam_info["exam"] = m.group(5)
        return exam_info
    else:
        return None

# Validation phase - ensure tests follow the format:
# CLASS_YEAR_SEMLETTER_TEACHER_EXAMINFO.pdf
#   CLASS should follow format: XXXX###[X] (XXXX = letters in all caps, ### = numbers, [X] = optional letter)
#   YEAR should follow format: ####
#   SEMLETTER should follow format:
#     S = spring
#     U = summer
#     F = fall
#     W = winter
#   TEACHER should follow format: an alphabetical string, with potentially dashes for the name (e.g. Bob-Martin will work)
#     Note that periods or other characters will fail to match.
#   EXAMINFO should follow format: anything string
# 
# NOTE that file must have trailing underscore for the match to be successful, e.g.
#   ENEE123_2010_S_Bob-Martin_.pdf will work, while
#   ENEE123_2010_S_Bob-Martin.pdf will NOT work.

# progCallback(current_num, total_num, file_name)
# errCallback(errstr)
def scanDir(srcdir, progCallback, errCallback):
    print("Loading magic mime file...")
    
    if sys.platform == "win32":
        # Accomodate frozen exes
        if getattr(sys, 'frozen', False):
            print "Frozen EXE detected!"
            print "getScriptPath() returns: %s" % getScriptPath()
            magic_file_path = os.path.join(os.path.dirname(sys.executable), "magic-db", "magic.mgc")
            print "Trying path #1: %s" % magic_file_path
            if not os.path.exists(magic_file_path):
                # Probably PyInstaller --onefile, attempt to fetch _MEIPASS attribute.
                magic_file_path = os.path.join(getattr(sys, '_MEIPASS', os.getcwd()), "magic-db", "magic.mgc")
                print "Trying path #2: %s" % magic_file_path
        else:
            magic_file_path = os.path.join(getScriptPath(), "magic-db", "magic.mgc")
        try:
            fh = open(magic_file_path, "r")
            fh.close()
            mag = magic.Magic(magic_file=magic_file_path, mime=True)
        except IOError:
            print("ERROR: No magic file database found! (magic-db/magic.mgc)")
            errCallback("No magic file database found!\nMake sure the magic database (magic-db/magic.mgc) exists.")
            return
    else:
        try:
            mag = magic.Magic(mime=True)
        except:
            print("ERROR: Failed to initialize magic/load magic database!")
            errCallback("Failed to initialize magic/load magic database!")
            return

    print("Loading directory list...")

    all_files = os.listdir(srcdir)
    
    # To make things deterministic, ensure that we sort the files
    # alphabetically. Otherwise, some people may get the same files,
    # despite different ranges. (This is due to os.listdir() using
    # system file listing, which will differ and not be in the exact
    # same order on another system.)
    all_files.sort()
    
    processed_files = 0
    num_files = len(all_files)

    #file_re = re.compile(r"^([A-Z]{4}\d{3}[A-Z]*)_(\d{4})_([SUFW])_([A-Za-z-]+)_(.*)\.(?:(?i)pdf|doc|docx|ppt|pptx|jpg|jpeg|zip|rar|gif)$")

    ext_regex_part = "|".join([x[1:] if type(x) == str else "|".join([y[1:] for y in x]) for x in format_exts.values()])
    final_file_re_txt = r"^([A-Z]{4}\d{3}[A-Z]*)_(\d{4})_([SUFW])_([A-Za-z-]+)_(.*)\.(?:(?i)" + ext_regex_part + r")$"
    file_part_re_txt = r"^([A-Z]{4}\d{3}[A-Z]*)_(\d{4})_([SUFW])_([A-Za-z-]+)_(.*)"

    file_re = re.compile(final_file_re_txt)
    file_part_re = re.compile(file_part_re_txt)
    
    file_table = []
    bad_list = []

    print("Processing %i files..." % num_files)
    
    all_valid = True
    
    for file in all_files:
        processed_files += 1
        warn_msg = None
        
        progCallback(processed_files, num_files, file)
        
        #if file_re.match(file):
        #file_type = str(mag.from_file(os.path.join(srcdir, file)))
        
        cur_file_path = os.path.join(srcdir, file)
        
        if not os.path.isfile(cur_file_path):
            print "%i / %i | %s | Not a file, skipping." % (processed_files, num_files, file)
            continue
        
        try:
            fh = open(cur_file_path)
            fh.close()
            #file_type = str(mag.from_buffer(fh.read()))
            file_type = str(mag.from_file(cur_file_path))
            
        except IOError, err:
            print("ERROR: Could not open file: %s" % cur_file_path)
            print(str(err))
            errCallback("Could not open file: %s\n%s" % (cur_file_path, str(err)))
            return
        
        if file_part_re.match(file):
            #print "%i / %i | %s | %s" % (processed_files, num_files, file, file_type)
            
            if file_type in supported_mime_types:
                # Make sure correct file extension matches the type!
                if type(format_exts[file_type]) == str:
                    if not file.lower().endswith(format_exts[file_type]):
                        warn_msg = "%i / %i | %s | %s | Invalid file extension for the actual file type" % (processed_files, num_files, file, file_type)
                    else:
                        file_table.append([file, file_type])
                elif type(format_exts[file_type]) == list:
                    found_fext = False
                    for fext in format_exts[file_type]:
                        if file.lower().endswith(fext):
                            found_fext = True
                            break
                    if not found_fext:
                        warn_msg = "%i / %i | %s | %s | Invalid file extension for the actual file type" % (processed_files, num_files, file, file_type)
                    else:
                        file_table.append([file, file_type])
                else:
                    warn_msg = "%i / %i | %s | %s | ERROR: Unknown type for format_exts" % (processed_files, num_files, file, file_type)
            elif file_type == "inode/x-empty":
                if os.path.getsize(cur_file_path) == 0:
                    warn_msg = "%i / %i | %s | %s | Empty file detected" % (processed_files, num_files, file, file_type)
                else:
                    warn_msg = "%i / %i | %s | %s | Detected empty, but the file size indicates otherwise" % (processed_files, num_files, file, file_type)
            else:
                warn_msg = "%i / %i | %s | %s | Unknown MIME type" % (processed_files, num_files, file, file_type)
        else:
            warn_msg = "%i / %i | %s | %s | Skip due to not matching filename format" % (processed_files, num_files, file, file_type)
        
        if warn_msg:
            # Format warn_msg
            warn_msg_parts = warn_msg.split(" | ")
            warn_msg_parts[0] = "\033[1m%s\033[0m" % warn_msg_parts[0]
            warn_msg_parts[1] = "\033[36m%s\033[0m" % warn_msg_parts[1]
            warn_msg_parts[2] = "\033[35m%s\033[0m" % warn_msg_parts[2]
            warn_msg_parts[3] = "\033[31m%s\033[0m" % warn_msg_parts[3]
            warn_msg = " | ".join(warn_msg_parts) + "\033[0m"
            
            print(warn_msg)
            bad_list.append(warn_msg)
            all_valid = False
    
    if not all_valid:
        print("ERROR: Problems with the list of files detected.")
        errCallback("Problems with the list of files detected. Files include:\n\n" + "\n".join(bad_list))
        return
    
    return (file_table, num_files)

# progCallback(current_num, total_num, file_name)
# errCallback(errstr)
def validateDir(srcdir, progCallback, errCallback):
    print("Loading directory list...")

    all_files = os.listdir(srcdir)
    processed_files = 0
    num_files = len(all_files)

    #file_re = re.compile(r"^([A-Z]{4}\d{3}[A-Z]*)_(\d{4})_([SUFW])_([A-Za-z-]+)_(.*)\.(?:(?i)pdf|doc|docx|ppt|pptx|jpg|jpeg|zip|rar|gif)$")

    ext_regex_part = "|".join([x[1:] if type(x) == str else "|".join([y[1:] for y in x]) for x in format_exts.values()])
    final_file_re_txt = r"^([A-Z]{4}\d{3}[A-Z]*)_(\d{4})_([SUFW])_([A-Za-z-]+)_(.*)\.(?:(?i)" + ext_regex_part + r")$"
    file_part_re_txt = r"^([A-Z]{4}\d{3}[A-Z]*)_(\d{4})_([SUFW])_([A-Za-z-]+)_(.*)"

    file_re = re.compile(final_file_re_txt)
    file_part_re = re.compile(file_part_re_txt)
    
    file_list = []
    bad_list = []

    print("Validating %i files (filename format only)..." % num_files)
    
    all_valid = True
    
    for file in all_files:
        processed_files += 1
        warn_msg = None
        
        progCallback(processed_files, num_files, file)
        
        #if file_re.match(file):
        #file_type = str(mag.from_file(os.path.join(srcdir, file)))
        
        cur_file_path = os.path.join(srcdir, file)
        
        if not os.path.isfile(cur_file_path):
            print "%i / %i | %s | Not a file, skipping." % (processed_files, num_files, file)
            continue
        
        if file_part_re.match(file):
            file_list.append(file)
        else:
            warn_msg = "%i / %i | %s | Invalid filename format" % (processed_files, num_files, file)
        
        if warn_msg:
            # Format warn_msg
            warn_msg_parts = warn_msg.split(" | ")
            warn_msg_parts[0] = "\033[1m%s\033[0m" % warn_msg_parts[0]
            warn_msg_parts[1] = "\033[36m%s\033[0m" % warn_msg_parts[1]
            warn_msg_parts[2] = "\033[35m%s\033[0m" % warn_msg_parts[2]
            warn_msg = " | ".join(warn_msg_parts) + "\033[0m"
            
            print(warn_msg)
            bad_list.append(warn_msg)
            all_valid = False
    
    if not all_valid:
        print("ERROR: Problems with the list of files detected.")
        errCallback("Problems with the list of files detected. Files include:\n\n" + "\n".join(bad_list))
        return
    
    return (file_list, num_files)

# Folder format:
# CLASS_XXXX > #00s > ### > Prof > YEAR > Semester
# Ex: ENEE > 300s > 303 > Franklin > 2014 > Spring
