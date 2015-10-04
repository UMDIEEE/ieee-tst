#!/usr/bin/env python
# IES - IEEE@UMD Exam Scanner Library - v1.0
# 

import magic
import colorama
import os
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
                "application/zip" : ".zip",
                "application/x-rar" : ".rar",
                
                # Text file
                "text/plain" : ".txt"
                
            }

supported_mime_types = format_exts.keys()

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
    
    try:
        fh = open("magic-db/magic.mgc", "r")
        fh.close()
        mag = magic.Magic(magic_file="magic-db/magic.mgc", mime=True)
    except IOError:
        print("ERROR: No magic file database found! (magic-db/magic.mgc)")
        errCallback("No magic file database found!\nMake sure the magic database (magic-db/magic.mgc) exists.")
        return

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
    
    file_table = []
    bad_list = []

    print("Processing %i files:" % num_files)
    
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

# Folder format:
# CLASS_XXXX > #00s > ### > Prof > YEAR > Semester
# Ex: ENEE > 300s > 303 > Franklin > 2014 > Spring
