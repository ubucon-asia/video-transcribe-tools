# -*- coding: utf-8 -*-
#
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import srt
from google.cloud import storage
import socket

def load_srt(filename):
    # load original .srt file
    # parse .srt file to list of subtitles
    print("Loading {}".format(filename))
    with open(filename) as f:
        text = f.read()
    return list(srt.parse(text))


def process_translations(subs, indexfile, out_bucket):
    # read index.csv and foreach translated file,
    storage_client = storage.Client()
    bucket = storage_client.bucket(out_bucket)

    print("Updating subtitles for each translated language")
    with open(indexfile) as f:
        lines = f.readlines()
    # copy orig subs list and replace content for each line
    for line in lines:
        index_list = line.split(",")
        lang = index_list[1]
        langfile = index_list[2].split("/")[-1]
        lang_subs = update_srt(lang, langfile, subs)
        content = write_srt(lang, lang_subs)
        write_to_file(content, f"out/{lang}.srt")
    return


def update_srt(lang, langfile, subs):
    # change subtitles' content to translated lines

    with open(langfile) as f:
        lines = f.readlines()
    i = 0
    for line in lines:
        subs[i].content = line
        i += 1
    return subs


def write_srt(lang, lang_subs):
    filename = lang + ".srt"
    content = srt.compose(lang_subs, strict=True)
    f = open(filename, "w")
    f.write(content)
    f.close()
    print("Wrote SRT file {}".format(filename))
    return content

def upload_to_bucket(content, bucket_obj, dest_filename):
    blob = bucket_obj.blob(dest_filename)
    blob.upload_from_string(content, timeout=(120, 120))

def write_to_file(content, dest_filepath):
    f = open(dest_filepath, 'w')
    f.write(content)
    f.close()

def main():
    socket.setdefaulttimeout(300)
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--srt",
        type=str,
        default="en.srt",
    )
    parser.add_argument(
        "--index",
        type=str,
        default="index.csv",
    )
    parser.add_argument(
        "--out_bucket",
        type=str,
    )
    args = parser.parse_args()

    subs = load_srt(args.srt)
    process_translations(subs, args.index, args.out_bucket)


if __name__ == "__main__":
    main()
