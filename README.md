# Redepends
How it works
![Image alt](https://github.com/shlyapo/redepends/raw/master/image/4.png)
## Usage

![Image alt](https://github.com/shlyapo/redepends/raw/master/image/7.png)

## Example
Start the terminal and go to directory, where this file is located.
Write command in following form:

python3 redepends.py -p 'Package name' -d "Directory" 

or

python3 redepends.py -p 'Package name' -u "Directory" 



You can write one or more packages. List their names without a comma separated by a space.

Ex: -p apt wine apport-retrace

And you can write local or network repository. Repository should be in quotes.

Ex: "http://ru.archive.ubuntu.com/ubuntu/dists/jammy/main/binary-amd64/Packages.gz" or "/media/elizabeth/Debian 11.4.0 amd64 1"

Local:

![Image alt](https://github.com/shlyapo/redepends/raw/master/image/5.png)

Network:

![Image alt](https://github.com/shlyapo/redepends/raw/master/image/6.png)
