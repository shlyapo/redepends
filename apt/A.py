import gzip
import io
import re

try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

dict_deps = dict()


def dep_list(content):
    with gzip.open(content, 'rb') as f:
        with io.TextIOWrapper(f, encoding='utf-8') as decoder:
            f = decoder.readlines()
            dict_dep = dict()
            flag = 0
            q = list()
            # l = list()
            for line in f:
                # line = line.decode('utf-8')
                if re.search(r'Package:', line):
                    flag += 1
                    line = line[9:-1]
                    q.append(line)
                    two_deps = []
                    if flag > 1:
                        q.remove(q[0])
                        flag -= 1
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
                        if len == "apt-utils":
                            print(1)
                        if len in dict_dep:
                            a = dict_dep.get(len)

                            a.append(s)
                            dict_dep[len] = a
                        else:
                            b.append(s)
                            dict_dep[len] = b
            return dict_dep


def dfs(visited, graph, node):
    if node not in visited:
        print(node)
        visited.add(node)
        for neighbor in graph[node]:
            dfs(visited, graph, neighbor)


if __name__ == '__main__':
    con = "/media/elizabeth/Debian 11.4.0 amd64 1/dists/stable/main/binary-amd64/Packages.gz"
    dd = dep_list(con)
    vis = set()
    if "apt-utils" in dd:
        for i in dd["apt-utils"]:
            print(i)
    k = "apt"
    dfs(vis, dd, k)
