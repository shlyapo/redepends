import gzip
import io
import re
import argparse
import requests

try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

dict_deps = dict()


def dep_list(content):
    try:
        with gzip.open(content, 'rb') as f:
            with io.TextIOWrapper(f, encoding='utf-8') as decoder:

                f = decoder.readlines()
                dict_dep = dict()
                flag = 0
                q = list()
                # l = list()
                for line in f:

                    if re.search(r'Package:', line):
                        flag += 1
                        line = line[9:-1]
                        q.append(line)
                        two_deps = []

                        if flag > 1:
                            q.remove(q[0])
                            flag -= 1

                        if line not in dict_dep:
                            dict_dep[line] = two_deps

                    if re.search(r'Depends:', line):
                        if re.search(r'Pre-Depends:', line):
                            continue

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

    except FileNotFoundError:
        return "Repository not found"


def dfs(visited, graph, node):
    if node not in visited:
        print(node)
        visited.add(node)
        for neighbor in graph[node]:
            dfs(visited, graph, neighbor)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Redepends', prog='redepends')
    parser.add_argument('-p', type=str, help='Name of package', nargs="+")
    parser.add_argument('-d', type=str, help='Input dir for repository')
    args = parser.parse_args()

    l = args.d[:7]

    if l == "http://":

        try:
            r = requests.get(args.d)
            r.raise_for_status()
            with open('pack.gz', 'wb') as f:
                f.write(r.content)
            dd = dep_list('pack.gz')

        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)

    else:

        dir = args.d + "/dists/stable/main/binary-amd64/Packages.gz"
        dd = dep_list(dir)

    if isinstance(dd, str):
        print(dd)

    else:

        for pkg in args.p:

            if pkg in dd:
                vis = set()

                dfs(vis, dd, pkg)
            else:
                print("Package not found")
            print("________________________")
