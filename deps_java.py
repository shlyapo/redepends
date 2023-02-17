import collections
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

dict_deps = dict()

flag = 0
q = []
l = 0
g = 0
list_java = []


def procc_dep(li, dict_d):
    global flag, g
    global q
    global l
    line = li
    dict_dep = dict()
    dict_dep = dict_d
    if re.search(r'Package:', line):
        flag += 1

        if l == 0 and g != 0:
            q.remove(q[0])

        if l == 1:
            q.remove(q[0])
            l = 0

        line = line[9:]
        q.append(line)

        two_deps = []

        if flag > 1 or l == 1:
            q.remove(q[0])
            flag -= 1
            l = 0

        if line not in dict_dep:
            dict_dep[line] = two_deps

    if re.search(r'Depends:', line) or re.search(r'Provides:', line):
        if re.search(r'Pre-Depends:', line):
            return dict_dep

        l += 1
        flag = 0
        line = re.sub(r'Depends: ', '', line)
        line = re.sub(r'Provides: ', '', line)
        line = re.sub(r' \([^)]*\)', '', line)
        line = re.sub(r',', '', line)
        line = re.sub(r'\|', '', line)
        line = re.sub(r':any', '', line)

        s = q[0]
        res = re.split(' +', line)
        for len in res:
            b = []

            if len in dict_dep:
                a = dict_dep.get(len)
                a.append(s)
                dict_dep[len] = a
            else:
                #if len in list_java:
                 #   b.append(s)
                  #  dict_dep[len] = b
                for jj in list_java:
                    if re.search(jj, len):
                        b.append(s)
                        dict_dep[len] = b

        if l == 2:
            q.remove(q[0])
            l = 0

    return dict_dep


def dep_list(content):
    dir_name = "binary-amd64"
    list_dir = []
    dict_de = dict()
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
                        da = procc_dep(line, dict_de)
                        dict_de = da



            elif zipfile.is_zipfile(content):
                with zipfile.ZipFile(content) as thezip:
                    with thezip.open('Packages', mode='r') as thefile:
                        f = thefile.readlines()

                        for line in f:
                            line = line[:-1]
                            line = line.decode()
                            da = procc_dep(line, dict_de)
                            dict_de = da


            elif pa.split(".")[-1] == 'gz':
                with gzip.open(content, 'rb') as f:
                    with io.TextIOWrapper(f, encoding='utf-8') as decoder:
                        f = decoder.readlines()

                        for line in f:
                            line = line[:-1]
                            da = procc_dep(line, dict_de)
                            dict_de = da


            else:
                with open(content, 'rb') as f:
                    f = f.readlines()
                    for line in f:
                        line = line.decode()
                        line = line[:-1]
                        da = procc_dep(line, dict_de)
                        dict_de = da
        return dict_de
    else:
        return "Repository not found"


def get_key(di, val):
    for k, v in di.items():
        if v == val:
            return k


def bfs(graph, root):
    list_deps = dict()
    list_deps[1] = [root]
    visited, queue = set(), collections.deque([root])
    visited.add(root)

    while queue:
        key_dep = 0
        vertex = queue.popleft()
        for val in list_deps.values():
            if val[-1] == vertex:
                key_dep = get_key(list_deps, val)

        if key_dep == 0:
            continue

        for neighbour in graph[vertex]:
            if neighbour == graph[vertex][0]:
                list_deps[key_dep].append(neighbour)
            else:
                keys = list_deps.keys()
                list_deps[len(keys) + 1] = list_deps[key_dep][:-1]
                list_deps[len(keys)].append(neighbour)
                queue.append(neighbour)

    return list_deps


def counter(list_d):
    result_dict = dict()
    for dct in list_d:
        for val in dct.values():
            for v in val:
                if v in result_dict:
                    count = result_dict[v]
                    result_dict[v] = count + 1
                else:
                    result_dict[v] = 1
    result_dict = dict(sorted(result_dict.items(), key=lambda item: item[1], reverse=True))
    return result_dict


if __name__ == '__main__':
    list_dict = []
    parser = argparse.ArgumentParser(description='Redepends', prog='redepends')
    parser.add_argument('-p', type=str, help='Name of package', nargs="+")
    parser.add_argument('-d', help='Add this argument and input local dir for repository')
    args = parser.parse_args()

    if args.d is not None:
        list_java = args.p
        local_dir = args.d
        dict_deps = dep_list(local_dir)

    else:
        print("Wrong input")

    if isinstance(dict_deps, str):
        print(dict_deps)

    else:
        file = open("output.txt", "w")
        for pkg in args.p:
            for p in dict_deps:
                if re.search(pkg, p):
                    #if pkg in dict_deps:
                    vis = set()
                    step = ""
                    d = bfs(dict_deps, p)
                    list_dict.append(d)
                    for key, value in d.items():
                        file.writelines("%s\n" % f'{key}:{value}')
                        print(key, ':', value)
        ddd = counter(list_dict)
        print("____________________________________________________")
        file.writelines("%s\n" % "____________________________________________________/n")
        for key, value in ddd.items():
            print(key, ':', value)
            file.writelines("%s\n" % f'{key}:{value}')
        file.close()
