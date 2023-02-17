import gzip
import io
import re
import argparse
import os
import os.path
import zipfile
import tarfile

try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

flag = 0
q = ""
list_java = ["default-jdk", "default-jre"]
list_pack = []


def procc_dep(li, result_list):
    global flag
    global q
    line = li

    if re.search(r'Package:', line):
        flag = 1
        q = line[9:]

    if re.search(r'Depends:', line) or re.search(r'Provides:', line):
        if re.search(r'Pre-Depends:', line):
            return result_list

        line = re.sub(r'Depends: ', '', line)
        line = re.sub(r'Provides: ', '', line)
        line = re.sub(r' \([^)]*\)', '', line)
        line = re.sub(r',', '', line)
        line = re.sub(r'\|', '', line)
        line = re.sub(r':any', '', line)

        finish = re.split(' +', line)
        for pack_dep in finish:
            s = []
            if pack_dep in list_java:
                if flag == 1:
                    flag = 0
                    list_pack.append(q)
                s.append(q)
                s.append(pack_dep)
                result_list.append(s)
            if re.search(r'java', pack_dep):
                if flag == 1:
                    flag = 0
                    list_pack.append(q)
                s.append(q)
                s.append(pack_dep)
                result_list.append(s)

    return result_list


def proc_list(content):
    dir_name = "binary-amd64"
    list_dir = []
    result = []
    if os.path.exists(content):
        for rootdir, dirs, files in os.walk(content):
            if (rootdir.split('/')[-1]) == dir_name:
                list_dir.append(rootdir)

        if len(list_dir) == 0:
            return "Check your path"
        for content in list_dir:

            for rootdir, dirs, files in os.walk(content):
                for file in files:
                    if (file.split('.')[0]) == 'Packages':
                        content = os.path.join(content, file)
                        break

            pa = content.split('/')[-1]

            if tarfile.is_tarfile(content):
                with tarfile.open(content, "r") as tar:
                    decoder = tar.extractfile("Packages")
                    a = decoder.readlines()

                    for line in a:
                        line = line.decode()
                        line = line[:-1]
                        result = procc_dep(line, result)

            elif zipfile.is_zipfile(content):
                with zipfile.ZipFile(content) as thezip:
                    with thezip.open('Packages', mode='r') as thefile:
                        f = thefile.readlines()

                        for line in f:
                            line = line[:-1]
                            line = line.decode()
                            result = procc_dep(line, result)

            elif pa.split(".")[-1] == 'gz':
                with gzip.open(content, 'rb') as f:
                    with io.TextIOWrapper(f, encoding='utf-8') as decoder:
                        f = decoder.readlines()

                        for line in f:
                            line = line[:-1]
                            result = procc_dep(line, result)

            else:
                with open(content, 'rb') as f:
                    f = f.readlines()
                    for line in f:
                        line = line.decode()
                        line = line[:-1]
                        result = procc_dep(line, result)
        return result
    else:
        return "Repository not found"


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Java-depends')
    parser.add_argument('-d', help='Add this argument and input local dir for repository')
    args = parser.parse_args()

    if args.d is not None:
        local_dir = args.d
        res = proc_list(local_dir)
        for key in res:
            print(key)
        print("____________________________________________________________")
        for pck in list_pack:
            print(pck)
    else:
        print("Wrong input")
