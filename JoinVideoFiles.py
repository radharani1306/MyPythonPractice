import os
import subprocess as sp
import distutils.spawn as dist
import easygui as g
import time
import string
# take sequence number for sort
def extractd_sequence(elem):
     return int(elem[0:2])

def makeSafeFilename(inputFilename):
    # Set here the valid chars
    safechars = string.ascii_letters + string.digits + "~ -_."
    try:
        data=[]
        for c in inputFilename:
            if (c not in safechars):
                c = c.replace(c,'_')
            data.append(c)
        return "".join(data)
    except:
        return ""
    pass

def rename_file(root,name):
    checkname = makeSafeFilename(name)
    # checkname = checkname.encode("utf-8")
    if name != checkname:
        print("In:", root)
        print("There was an error with", name)
        if os.name == "nt":
            os.rename(root + "\\" + name, root + "\\" + checkname)
        else:
            os.rename(root + "/" + name, root + "/" + checkname)
        print(name, "has been renamed to", checkname)
    return checkname

def prepare_text_files(rootDir,out_dir_file):
    # Set the directory you want to start from

    temp = rootDir[rootDir.rindex("\\") + 1:]
    out_directory_name = os.path.join(out_dir_file, temp)
    if not os.path.exists(out_directory_name):
        print("Creating {}...".format(out_directory_name))
        os.makedirs(out_directory_name)


    txtfile_set = set()
    for dirName, subdirList, fileList in os.walk(rootDir):
        if not os.path.isfile(dirName):
            print('sud directory: %s' % dirName)
        txt_file = dirName[dirName.rindex("\\") + 1:]
        txt_file_path = "{}\\{}.txt".format(out_dir_file,txt_file)
        print(txt_file_path)
        for fname in fileList:
          with open(txt_file_path, "a+") as f:
                if (fname.endswith('.mp4')):
                    txtfile_set.add(txt_file)
                    #code to replace special character's in file
                    fname = rename_file(dirName, fname)
                    f.write("file \'{}\'\n".format(os.path.join(dirName,fname)))
    return txtfile_set

def process_videos(fname,destinationDir,choice_flag):

    out_file=fname+".mp4"
    in_file = fname + ".txt"
    BASE_DIR = destinationDir
    input_filename = os.path.join(BASE_DIR, in_file)
    output_filename = os.path.join(BASE_DIR, out_file)

    OS_WIN = True if os.name == "nt" else False

    # Find ffmpeg executable
    if OS_WIN:
        FFMPEG_BIN = 'ffmpeg.exe'
    else:
        try:
            FFMPEG_BIN = dist.find_executable("ffmpeg")
        except AttributeError:
            FFMPEG_BIN = 'ffmpeg'
    if(choice_flag == 0):
        command = [FFMPEG_BIN,
                   '-f', 'concat',
                   '-safe', '0',
                   '-i', input_filename,
                   '-map', '0',
                   '-map', '-0:a:m:language:eng',
                   '-codec', 'copy',
                   output_filename
                   ]
    else:
        command = [FFMPEG_BIN,
                       '-f', 'concat',
                       '-safe', '0',
                       '-i', input_filename,
                       '-map', '0:v',
                       '-vcodec', 'copy',
                       '-map', '0:a',
                        '-acodec', 'copy',
                       '-disposition:a:0', 'none',
                        '-disposition:a:1', 'default',
                       output_filename
                       ]
    print("ffmpeg command is:", command)

    if OS_WIN:
        sp.call(command, shell=True)
    else:
        sp.call(command)

def cleaning_process(fname,destinationDir):

    in_file = fname + ".txt"
    BASE_DIR = destinationDir
    input_filename = os.path.join(BASE_DIR, in_file)
    if os.path.exists(input_filename):
        os.remove(input_filename)


def combine_videos(sourceDir,destinationDir,choice):
    rootDir = sourceDir
    txt_files_set = prepare_text_files(rootDir,filename2)
    # txt_files_sortedset = sorted(txt_files_set,key = extractd_sequence)
    # print(txt_files_sortedset)

    #Tbis will combine all the video files
    for txt_name in txt_files_set:
        process_videos(txt_name,destinationDir,choice)
    # Tbis will combine all the video files
    for txt_name in txt_files_set:
        cleaning_process(txt_name,destinationDir)

if __name__ == "__main__":
    filename1 = g.diropenbox(title = "Select folder of Videos",default="F:/Python Videos/")
    filename2 = g.diropenbox(title = "select output folder",default="D:/Ram/")
    msg = "share your opinion"
    choices = ["0", "1", "2"]
    reply = g.buttonbox(msg, choices=choices)
    start_time = time.time()
    combine_videos(filename1,filename2,int(reply))
    print("time taken to process====>", (time.time() - start_time))

