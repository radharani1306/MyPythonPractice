#!/usr/bin/env python

import csv
import subprocess
import math
import json
import os
import shlex
from optparse import OptionParser


def split_by_manifest(filename, manifest, vcodec="copy", acodec="copy",
                      extra="", **kwargs):
    """ Split video into segments based on the given manifest file.
    Arguments:
        filename (str)      - Location of the video.
        manifest (str)      - Location of the manifest file.
        vcodec (str)        - Controls the video codec for the ffmpeg video
                            output.
        acodec (str)        - Controls the audio codec for the ffmpeg video
                            output.
        extra (str)         - Extra options for ffmpeg.
    """
    if not os.path.exists(manifest):
        print ("File does not exist: %s" % manifest)
        raise SystemExit

    with open(manifest) as manifest_file:
        manifest_type = manifest.split(".")[-1]
        if manifest_type == "json":
            config = json.load(manifest_file)
        elif manifest_type == "csv":
            config = csv.DictReader(manifest_file)
        else:
            print ("Format not supported. File must be a csv or json file")
            raise SystemExit

        split_cmd = ["ffmpeg", "-i", filename, "-vcodec", vcodec,
                     "-acodec", acodec, "-y"] + shlex.split(extra)
        try:
            fileext = filename.split(".")[-1]
        except IndexError as e:
            raise IndexError("No . in filename. Error: " + str(e))
        for video_config in config:
            split_str = ""
            split_args = []
            try:
                split_start = video_config["start_time"]
                split_length = video_config.get("end_time", None)
                if not split_length:
                    split_length = video_config["length"]
                filebase = video_config["rename_to"]
                if fileext in filebase:
                    filebase = ".".join(filebase.split(".")[:-1])

                split_args += ["-ss", str(split_start), "-t",
                    str(split_length), filebase + "." + fileext]
                print ("########################################################")
                print ("About to run: "+" ".join(split_cmd+split_args))
                print ("########################################################")
                subprocess.check_output(split_cmd+split_args)
            except KeyError as e:
                print ("############# Incorrect format ##############")
                if manifest_type == "json":
                    print ("The format of each json array should be:")
                    print ("{start_time: <int>, length: <int>, rename_to: <string>}")
                elif manifest_type == "csv":
                    print ("start_time,length,rename_to should be the first line ")
                    print ("in the csv file.")
                print ("#############################################")
                print (e)
                raise SystemExit

def get_video_length(filename):

    output = subprocess.check_output(("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filename)).strip()
    video_length = int(float(output))
    print ("Video length in seconds: "+str(video_length))

    return video_length

def ceildiv(a, b):
    return int(math.ceil(a / float(b)))

def split_by_seconds(filename, split_length, vcodec="copy", acodec="copy",
                     extra="", video_length=None, **kwargs):
    if split_length and split_length <= 0:
        print ("Split length can't be 0")
        raise SystemExit

    if not video_length:
        video_length = get_video_length(filename)
    split_count = ceildiv(video_length, split_length)
    if(split_count == 1):
        print ("Video length is less then the target split length.")
        raise SystemExit

    split_cmd = ["ffmpeg", "-i", filename, "-vcodec", vcodec, "-acodec", acodec] + shlex.split(extra)
    try:
        filebase = ".".join(filename.split(".")[:-1])
        fileext = filename.split(".")[-1]
    except IndexError as e:
        raise IndexError("No . in filename. Error: " + str(e))
    for n in range(0, split_count):
        split_args = []
        if n == 0:
            split_start = 0
        else:
            split_start = split_length * n

        split_args += ["-ss", str(split_start), "-t", str(split_length),
                       filebase + "-" + str(n+1) + "-of-" + \
                        str(split_count) + "." + fileext]
        print ("About to run: "+" ".join(split_cmd+split_args))
        subprocess.check_output(split_cmd+split_args)


def main():
    parser = OptionParser()

    parser.add_option("-f", "--file",
                        dest = "filename",
                        help = "File to split, for example sample.avi",
                        type = "string",
                        action = "store"
                        )
    parser.add_option("-s", "--split-size",
                        dest = "split_length",
                        help = "Split or chunk size in seconds, for example 10",
                        type = "int",
                        action = "store"
                        )
    parser.add_option("-c", "--split-chunks",
                        dest = "split_chunks",
                        help = "Number of chunks to split to",
                        type = "int",
                        action = "store"
                        )
    parser.add_option("-S", "--split-filesize",
                        dest = "split_filesize",
                        help = "Split or chunk size in bytes (approximate)",
                        type = "int",
                        action = "store"
                        )
    parser.add_option("--filesize-factor",
                        dest = "filesize_factor",
                        help = "with --split-filesize, use this factor in time to" \
                               " size heuristics [default: %default]",
                        type = "float",
                        action = "store",
                        default = 0.95
                        )
    parser.add_option("--chunk-strategy",
                        dest = "chunk_strategy",
                        help = "with --split-filesize, allocate chunks according to" \
                               " given strategy (eager or even)",
                        type = "choice",
                        action = "store",
                        choices = ['eager', 'even'],
                        default = 'eager'
                        )
    parser.add_option("-m", "--manifest",
                      dest = "manifest",
                      help = "Split video based on a json manifest file. ",
                      type = "string",
                      action = "store"
                     )
    parser.add_option("-v", "--vcodec",
                      dest = "vcodec",
                      help = "Video codec to use. ",
                      type = "string",
                      default = "copy",
                      action = "store"
                     )
    parser.add_option("-a", "--acodec",
                      dest = "acodec",
                      help = "Audio codec to use. ",
                      type = "string",
                      default = "copy",
                      action = "store"
                     )
    parser.add_option("-e", "--extra",
                      dest = "extra",
                      help = "Extra options for ffmpeg, e.g. '-e -threads 8'. ",
                      type = "string",
                      default = "",
                      action = "store"
                     )
    (options, args) = parser.parse_args()

    def bailout():
        parser.print_help()
        raise SystemExit

    if not options.filename:
        bailout()

    if options.manifest:
        split_by_manifest(**(options.__dict__))
    else:
        video_length = None
        if not options.split_length:
            video_length = get_video_length(options.filename)
            file_size = os.stat(options.filename).st_size
            split_filesize = None
            if options.split_filesize:
                split_filesize = int(options.split_filesize * options.filesize_factor)
            if split_filesize and options.chunk_strategy == 'even':
                options.split_chunks = ceildiv(file_size, split_filesize)
            if options.split_chunks:
                options.split_length = ceildiv(video_length, options.split_chunks)
            if not options.split_length and split_filesize:
                options.split_length = int(split_filesize / float(file_size) * video_length)
        if not options.split_length:
            bailout()
        split_by_seconds(video_length=video_length, **(options.__dict__))

if __name__ == '__main__':
    main()


# Command Line Video Splitter
# Simple command line Python script that splits video into multi chunks. Under the hood script uses FFMpeg so you will need to have that installed. No transcoding or modification of video happens, it just get's split properly.
#
# Run python ffmpeg-split.py -h to see the options. Here are few samples of how it could be used:
#
# Spliting video into equal chunks
# python ffmpeg-split.py -f big_video_file.mp4 -s 10
#
# This splits big_video_file.mp4 into chunks, and the size of chunk is 10 seconds. Each chunk will be suffixed with numeric index, for example big_video_file-0.mp4, big_video_file-1.mp4, etc.
#
# Spliting video into euqal chunks with some extra options
# python ffmpeg-split.py -f -i input.mp4 -s 600 -v libx264 -e '-vf "scale=320:240" -threads 8'
#
# This splits input.mp4 into chunks, and the size of chunk is 600 seconds. With extra option to scale output to 320:240 and use 8 threads to speed up.
#
# Splitting videos into unequal chunks
# In order to create unequal chunks of a video, you'll need to create manifest.json.
#
# manifest.json
#
# [
#     {
#         "start_time": 0,
#         "length": 34,
#         "rename_to": "video1"
#     },
#     {
#         "start_time": 35,
#         "length": 22,
#         "rename_to": "video2.mp4"
#     }
# ]
# Afterwards run:
#
# python ffmpeg-split.py -f big_video_file.mp4 -m manifest.json
#
# This splits big_video_file.mp4 into 2 video files, video1.mp4 and video2.mp4. The video1.mp4 is a 34 seconds clip, starting from 0:00 to 0:34 of the big_video_file.mp4.
#
# Alternatively, you can use a manifest.csv file to accomplish the task above.
#
# manifest.csv:
#
#
# start_time,length,rename_to
# 0,34,video1
# 35,22,video2
#
# Manifest Options
# start_time - number of seconds into the video or start time
# length - length of the video in seconds. The end time of the video is calculated by the start_time plus the length of the video.
# rename_to - name of the video clip to be saved
# end_time - end time of the video
# Additional Arguments
# -v or --vcodec ffmpeg video codec to be used.
# -a or --acodec ffmpeg audio codec to be used.
# -m or --manifest manifest file to control the splitting of videos.
# -f or --file video file to split.
# -s or --split-size seconds to evenly split the videos
# -e or --extra extra optional options for ffmpeg, e.g. '-e -threads 8' to use 8 threads to speed up.
# Notes:
# The -s and -m options should not be used together. If they are, -m option takes precedent over the -s option
