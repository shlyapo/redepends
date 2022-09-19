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
l=0


def procc_dep(li, dict_d):
    global flag
    global q
    global l
    line =""
    line = li
    dict_dep = dict()
    dict_dep = dict_d
    if re.search(r'Package:', line):
        flag += 1
        if l == 1:
            q.remove(q[0])

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
        l+=1
        flag = 0
        #line = line[9:-1]
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

    return dict_dep


def dep_list(content):
    dir_name = "binary-amd64"
    list_dir = []

    if os.path.exists(content):
        for rootdir, dirs, files in os.walk(content):
            if (rootdir.split('/')[-1]) == dir_name:
                list_dir.append(rootdir)

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
                    content = list_dir[ans-1]
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
            with tarfile.open(content, "r") as tar:
                decoder = tar.extractfile("Packages")
                a = decoder.readlines
                for line in a:
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

        elif pa.split(".")[-1] == 'gz':
            dict_de = dict()
            with gzip.open(content, 'rb') as f:
                with io.TextIOWrapper(f, encoding='utf-8') as decoder:
                    f = decoder.readlines()
                    for line in f:
                        da = procc_dep(line, dict_de)
                        dict_de = da
                    return dict_de

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
            if neighbor is graph[node][0]:
                step = step + '.'
            dfs(visited, graph, neighbor, step)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Redepends', prog='redepends')
    parser.add_argument('-p', type=str, help='Name of package', nargs="+")
    parser.add_argument('-u',
                        help='Add this arquments and url')
    parser.add_argument('-d', help='Input local dir for repository')
    args = parser.parse_args()

    if args.d is not None and args.u is not None:
         print("Wrong input")

    elif args.u is not  None: # think

        try:
            r = requests.get(args.u)
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

    elif args.d is not None:

        dir = args.d  # "/dists/stable/main/binary-amd64/Packages.gz"
        dd = dep_list(dir)

    else:
        print("Wrong input")

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
