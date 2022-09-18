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


def procc_dep(line, dict_dep):
    if re.search(r'Package:', line):
        global flag
        global q
        flag += 1

        line = line[9:-1]
        q.append(line)
        two_deps = []

        if flag > 1:
            q.remove(q[0])
            flag -= 1

        if line not in dict_dep:
            dict_dep[line] = two_deps

    if re.search(r'Depends:', line) or re.search(r'Provides:', line):
        if re.search(r'Pre-Depends:', line):
            return dict_dep

        flag = 0
        line = line[9:-1]
        line = re.sub(r' \([^)]*\)', '', line)
        line = re.sub(r',', '', line)
        line = re.sub(r'\|', '', line)
        line = re.sub(r':any', '', line)
        s = q[0]
        q.remove(q[0])
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

    return dict_dep


def dep_list(content):
    dir_name = "binary-amd64"
    list_dir = []

    if os.path.exists(content):
        for address, dirs, folders in os.walk(content):
            if dir_name in folders:
                p = os.path.join(address, dir_name)
                list_dir.append(p)

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
                if ans <= count:
                    content = list_dir[ans]
                    break
                else:
                    print("Wrong input")
            else:
                print("Wrong input")

        for address, dirs, filenames in os.walk(content):
            for file in filenames:
                a = re.split(".", file)
                if a[0] == "Packages":
                    content = content + file
                    break

        if tarfile.is_tarfile(content):
            with tarfile.open(content, "r") as tar:
                with io.TextIOWrapper(tar, encoding='utf-8') as decoder:
                    f = decoder.readlines()
                    for line in f:
                        line = line[2:-1]
                        d = procc_dep(line, d)
                    return d

        elif zipfile.is_zipfile(content):
            with zipfile.ZipFile(content) as thezip:
                with thezip.open('Packages', mode='r') as thefile:
                    f = thefile.readlines()
                    for line in f:
                        line = line[2:-1]
                        d = procc_dep(line, d)
                    return d
        else:
            with io.TextIOWrapper(content, encoding='utf-8') as decoder:
                f = decoder.readlines()
                for line in f:
                    d = procc_dep(line, d)
                return d
    else:
        return "Repository not found"

        # with gzip.open(content, 'rb') as f:


def dfs(visited, graph, node, step):
    if node not in visited:
        print(step + node)
        visited.add(node)
        for neighbor in graph[node]:
            dfs(visited, graph, neighbor, step)
            if neighbor is graph[-1]:
                step = step + "."


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Redepends', prog='redepends')
    parser.add_argument('-p', type=str, help='Name of package', nargs="+")
    parser.add_argument('-d', type=str, help='Input dir for repository')
    args = parser.parse_args()

    if ":" in args.d:

        try:
            r = requests.get(args.d)
            r.raise_for_status()
            if tarfile.is_tarfile(r.content):
                with open('pack.tar', 'wb') as f:  # подумать
                    f.write(r.content)
                    with io.TextIOWrapper('pack.tar', encoding='utf-8') as decoder:
                        f = decoder.readlines()
                        for line in f:
                            line = line[2:-1]
                            d = procc_dep(line, d)

            elif zipfile.is_zipfile(r.content):
                with open('pack.gz', 'wb') as f:  # подумать
                    f.write(r.content)
                with zipfile.ZipFile('pack.gz') as thezip:
                    with thezip.open('Packages', mode='r') as thefile:
                        f = thefile.readlines()
                        for line in f:
                            line = line[2:-1]
                            d = procc_dep(line, d)
            else:
                with open('pack', 'wb') as f:  # подумать
                    f.write(r.content)
                with io.TextIOWrapper('pack', encoding='utf-8') as decoder:
                    f = decoder.readlines()
                    for line in f:
                        d = procc_dep(line, d)

        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)

    else:

        dir = args.d  # "/dists/stable/main/binary-amd64/Packages.gz"
        print(dir)
        dd = dep_list(dir)

    if isinstance(dd, str):
        print(dd)

    else:

        for pkg in args.p:

            if pkg in dd:
                vis = set()
                step = ""
                dfs(vis, dd, pkg, step)
            else:
                print("Package not found")
            print("________________________")
