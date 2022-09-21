import collections
import gzip
import io
import re
import argparse
import requests
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
                b.append(s)
                dict_dep[len] = b

        if l == 2:
            q.remove(q[0])
            l = 0

    return dict_dep


def dep_list(content):
    dir_name = "binary-amd64"
    list_dir = []

    if os.path.exists(content):
        for rootdir, dirs, files in os.walk(content):
            if (rootdir.split('/')[-1]) == dir_name:
                list_dir.append(rootdir)

        if len(list_dir) == 0:
            return "Check your path"

        while True:
            print("Choose dir, that you need")
            count = 0
            for i in list_dir:
                count += 1
                print(count)
                print(i)

            ans = input()
            if ans.isdigit():
                ans = int(ans)
                if 0 < ans <= count:
                    content = list_dir[ans - 1]
                    break
                else:
                    print("Wrong input")
            else:
                print("Wrong input")

        for rootdir, dirs, files in os.walk(content):
            for file in files:
                if (file.split('.')[0]) == 'Packages':
                    content = os.path.join(content, file)
                    break

        pa = content.split('/')[-1]

        if tarfile.is_tarfile(content):
            dict_de = dict()
            with tarfile.open(content, "r") as tar:
                decoder = tar.extractfile("Packages")
                a = decoder.readlines()

                for line in a:
                    line = line.decode()
                    line = line[:-1]
                    da = procc_dep(line, dict_de)
                    dict_de = da

                return dict_de

        elif zipfile.is_zipfile(content):
            dict_de = dict()
            with zipfile.ZipFile(content) as thezip:
                with thezip.open('Packages', mode='r') as thefile:
                    f = thefile.readlines()

                    for line in f:
                        line = line[:-1]
                        line = line.decode()
                        da = procc_dep(line, dict_de)
                        dict_de = da
                    return dict_de

        elif pa.split(".")[-1] == 'gz':
            dict_de = dict()
            with gzip.open(content, 'rb') as f:
                with io.TextIOWrapper(f, encoding='utf-8') as decoder:
                    f = decoder.readlines()

                    for line in f:
                        line = line[:-1]
                        da = procc_dep(line, dict_de)
                        dict_de = da
                    return dict_de

        else:
            dict_de = dict()
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Redepends', prog='redepends')
    parser.add_argument('-p', type=str, help='Name of package', nargs="+")
    parser.add_argument('-u',
                        help='Add this arqument and url')
    parser.add_argument('-d', help='Add this argument and input local dir for repository')
    args = parser.parse_args()

    if args.d is not None and args.u is not None:
        print("Wrong input")
        args.u = None
        args.d = None

    elif args.u is not None:

        try:
            r = requests.get(args.u)
            r.raise_for_status()
            pack = args.u.split("/")[-1]
            with open(pack, 'wb') as f:
                f.write(r.content)

            if tarfile.is_tarfile(pack):
                dict_de = dict()
                with tarfile.open(pack, "r") as tar:
                    decoder = tar.extractfile("Packages")
                    a = decoder.readlines()

                    for line in a:
                        line = line.decode()
                        line = line[:-1]
                        da = procc_dep(line, dict_de)
                        dict_de = da

            elif zipfile.is_zipfile(pack):
                dict_de = dict()
                print(22)
                with zipfile.ZipFile(pack) as thezip:
                    with thezip.open('Packages', mode='r') as thefile:
                        f = thefile.readlines()

                        for line in f:
                            line = line[:-1]
                            line = line.decode()
                            da = procc_dep(line, dict_de)
                            dict_de = da

            elif pack.split(".")[-1] == 'gz':
                dict_de = dict()
                with gzip.open(pack, 'rb') as f:
                    with io.TextIOWrapper(f, encoding='utf-8') as decoder:
                        f = decoder.readlines()
                        for line in f:
                            line = line[:-1]
                            da = procc_dep(line, dict_de)
                            dict_de = da

            else:
                dict_de = dict()
                with open(pack, 'rb') as f:
                    f = f.readlines()
                    for line in f:
                        line = line.decode()
                        line = line[:-1]
                        da = procc_dep(line, dict_de)
                        dict_de = da

            dict_deps = dict_de
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)

    elif args.d is not None:

        local_dir = args.d
        dict_deps = dep_list(local_dir)

    else:
        print("Wrong input")

    if isinstance(dict_deps, str):
        print(dict_deps)

    else:

        for pkg in args.p:

            if pkg in dict_deps:
                vis = set()
                step = ""
                d = bfs(dict_deps, pkg)
                for key, value in d.items():
                    print(key, ':', value)

            else:
                print("Package not found")
            print("________________________")
