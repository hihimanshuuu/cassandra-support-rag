---
title: "Installing Cassandra"
source_url: https://cassandra.apache.org/doc/4.0/cassandra/getting_started/installing.html
cassandra_version: "4.0"
section: getting_started
retrieved: 2026-10-31
---

> Source: Apache Cassandra documentation, version 4.0, https://cassandra.apache.org/doc/4.0/cassandra/getting_started/installing.html. Licensed under the Apache License 2.0.

# Installing Cassandra

These are the instructions for deploying the supported releases of
Apache Cassandra on Linux servers.

Cassandra runs on a wide array of Linux distributions including (but not
limited to):

* Ubuntu, most notably LTS releases 16.04 to 18.04
* CentOS & RedHat Enterprise Linux (RHEL) including 6.6 to 7.7
* Amazon Linux AMIs including 2016.09 through to Linux 2
* Debian versions 8 & 9
* SUSE Enterprise Linux 12

This is not an exhaustive list of operating system platforms, nor is it
prescriptive. However, users will be well-advised to conduct exhaustive
tests of their own particularly for less-popular distributions of Linux.
Deploying on older versions is not recommended unless you have previous
experience with the older distribution in a production environment.

## Prerequisites

* Install the latest version of Java 8 or Java 11, either the
  [Oracle
  Java Standard Edition 8](http://www.oracle.com/technetwork/java/javase/downloads/index.html) / [Oracle Java Standard Edition 11 (Long Term Support)](http://www.oracle.com/technetwork/java/javase/downloads/index.html)
  or [OpenJDK 8](http://openjdk.java.net/) / [OpenJDK 11](http://openjdk.java.net/). To
  verify that you have the correct version of java installed, type
  `java -version`.
* **NOTE**: Experimental support for Java 11 was added in Cassandra 4.0
  ([CASSANDRA-9608](https://issues.apache.org/jira/browse/CASSANDRA-9608)).
  Full support is effective Cassandra 4.0.2 version ([CASSANDRA-16894](https://issues.apache.org/jira/browse/CASSANDRA-16894))
  For more information, see
  [NEWS.txt](https://github.com/apache/cassandra/blob/trunk/NEWS.txt).
* For using cqlsh, the latest version of
  Python 3.6+ or Python 2.7 (support deprecated). To verify
  that you have the correct version of Python installed, type
  `python --version`.

## Choosing an installation method

There are three methods of installing Cassandra that are common:

* Docker image
* Tarball binary file
* Package installation (RPM, YUM)

If you are a current Docker user, installing a Docker image is simple.
You’ll need to install Docker Desktop for Mac, Docker Desktop for Windows,
or have `docker` installed on Linux.
Pull the appropriate image and then start Cassandra with a run command.

For most users, installing the binary tarball is also a simple choice.
The tarball unpacks all its contents into a single location with
binaries and configuration files located in their own subdirectories.
The most obvious attribute of the tarball installation is it does not
require `root` permissions and can be installed on any Linux
distribution.

Packaged installations require `root` permissions, and are most appropriate for
production installs.
Install the RPM build on CentOS and RHEL-based distributions if you want to
install Cassandra using YUM.
Install the Debian build on Ubuntu and other Debian-based
distributions if you want to install Cassandra using APT.
Note that both the YUM and APT methods required `root` permissions and
will install the binaries and configuration files as the `cassandra` OS user.

## Installing the docker image

1. Pull the docker image. For the latest image, use:

```
docker pull cassandra:latest
```

This `docker pull` command will get the latest version of the 'Docker Official'
Apache Cassandra image available from the [Dockerhub](https://hub.docker.com/_/cassandra).

2. Start Cassandra with a `docker run` command:

```
docker run --name cass_cluster cassandra:latest
```

The `--name` option will be the name of the Cassandra cluster created.

3. Start the CQL shell, `cqlsh` to interact with the Cassandra node created:

```
docker exec -it cass_cluster cqlsh
```

## Installing the binary tarball

1. Verify the version of Java installed. For example:

* Command
* Result

```
$ java -version
```

```
openjdk version "1.8.0_222"
OpenJDK Runtime Environment (build 1.8.0_222-8u222-b10-1ubuntu1~16.04.1-b10)
OpenJDK 64-Bit Server VM (build 25.222-b10, mixed mode)
```

2. Download the binary tarball from one of the mirrors on the
   [Apache Cassandra Download](http://cassandra.apache.org/download/) site.
   For example, to download Cassandra 4.0:

```
$ curl -OL http://apache.mirror.digitalpacific.com.au/cassandra/4.0.0/apache-cassandra-4.0.0-bin.tar.gz
```

|  |  |
| --- | --- |
|  | The mirrors only host the latest versions of each major supported release. To download an earlier version of Cassandra, visit the [Apache Archives](http://archive.apache.org/dist/cassandra/). |

3. OPTIONAL: Verify the integrity of the downloaded tarball using one of
   the methods [here](https://www.apache.org/dyn/closer.cgi#verify). For
   example, to verify the hash of the downloaded file using GPG:

* Command
* Result

```
$ gpg --print-md SHA256 apache-cassandra-4.0.0-bin.tar.gz
```

```
apache-cassandra-4.0.0-bin.tar.gz: 28757DDE 589F7041 0F9A6A95 C39EE7E6
                                   CDE63440 E2B06B91 AE6B2006 14FA364D
```

Compare the signature with the SHA256 file from the Downloads site:

* Command
* Result

```
$ curl -L https://downloads.apache.org/cassandra/4.0.0/apache-cassandra-4.0.0-bin.tar.gz.sha256
```

```
28757dde589f70410f9a6a95c39ee7e6cde63440e2b06b91ae6b200614fa364d
```

4. Unpack the tarball:

```
$ tar xzvf apache-cassandra-4.0.0-bin.tar.gz
```

The files will be extracted to the `apache-cassandra-4.0.0/` directory.
This is the tarball installation location.

5. Located in the tarball installation location are the directories for
   the scripts, binaries, utilities, configuration, data and log files:

```
<tarball_installation>/
    bin/		(1)
    conf/		(2)
    data/		(3)
    doc/
    interface/
    javadoc/
    lib/
    logs/		(4)
    pylib/
    tools/		(5)
```

|  |  |
| --- | --- |
| **1** | location of the commands to run cassandra, cqlsh, nodetool, and SSTable tools |
| **2** | location of cassandra.yaml and other configuration files |
| **3** | location of the commit logs, hints, and SSTables |
| **4** | location of system and debug logs <5>location of cassandra-stress tool |

For information on how to configure your installation, see
[Configuring
Cassandra](http://cassandra.apache.org/doc/latest/getting_started/configuring.html).

6. Start Cassandra:

```
$ cd apache-cassandra-4.0.0/ && bin/cassandra
```

|  |  |
| --- | --- |
|  | This will run Cassandra as the authenticated Linux user. |

6. Monitor the progress of the startup with:

* Command
* Result

```
$ tail -f logs/system.log
```

Cassandra is ready when you see an entry like this in the `system.log`:

```
INFO  [main] 2019-12-17 03:03:37,526 Server.java:156 - Starting listening for CQL clients on localhost/127.0.0.1:9042 (unencrypted)...
```

You can monitor the progress of the startup with:

* Command
* Result

```
$ tail -f logs/system.log
```

Cassandra is ready when you see an entry like this in the `system.log`:

```
INFO  [main] 2019-12-17 03:03:37,526 Server.java:156 - Starting listening for CQL clients on localhost/127.0.0.1:9042 (unencrypted)...
```

|  |  |
| --- | --- |
|  | For information on how to configure your installation, see [Configuring Cassandra](http://cassandra.apache.org/doc/latest/getting_started/configuring.html). |

7. Check the status of Cassandra:

```
$ bin/nodetool status
```

The status column in the output should report `UN` which stands for
"Up/Normal".

Alternatively, connect to the database with:

```
$ bin/cqlsh
```

## Installing the Debian packages

1. Verify the version of Java installed. For example:

* Command
* Result

```
$ java -version
```

```
openjdk version "1.8.0_222"
OpenJDK Runtime Environment (build 1.8.0_222-8u222-b10-1ubuntu1~16.04.1-b10)
OpenJDK 64-Bit Server VM (build 25.222-b10, mixed mode)
```

2. Add the Apache repository of Cassandra to the file
   `cassandra.sources.list`.
   The latest major version is 4.0 and the corresponding distribution name is `40x` (with an "x" as the suffix).
   For older releases use:

   * `40x` for C\* 4.0 series
   * `311x` for C\* {311\_version} series
   * `30x` for C\* {30\_version} series
   * `22x` for C\* {22\_version} series
   * `21x` for C\* {21\_version} series

For example, to add the repository for version 4.0 (`40x`):

```
$ echo "deb [signed-by=/etc/apt/keyrings/apache-cassandra.asc] https://debian.cassandra.apache.org 40x main" | sudo tee -a /etc/apt/sources.list.d/cassandra.sources.list
deb https://debian.cassandra.apache.org 40x main
```

3. Add the Apache Cassandra repository keys to the list of trusted keys
   on the server:

* Command
* Result

```
$ curl -o /etc/apt/keyrings/apache-cassandra.asc https://downloads.apache.org/cassandra/KEYS
```

```
% Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  266k  100  266k    0     0   320k      0 --:--:-- --:--:-- --:--:--  320k
OK
```

4. Update the package index from sources:

```
$ sudo apt-get update
```

5. Install Cassandra with APT:

```
$ sudo apt-get install cassandra
```

|  |  |
| --- | --- |
|  | For information on how to configure your installation, see [Configuring Cassandra](http://cassandra.apache.org/doc/latest/getting_started/configuring.html). |

6. Monitor the progress of the startup with:

* Command
* Result

```
$ tail -f logs/system.log
```

Cassandra is ready when you see an entry like this in the `system.log`:

```
INFO  [main] 2019-12-17 03:03:37,526 Server.java:156 - Starting listening for CQL clients on localhost/127.0.0.1:9042 (unencrypted)...
```

|  |  |
| --- | --- |
|  | For information on how to configure your installation, see [Configuring Cassandra](http://cassandra.apache.org/doc/latest/getting_started/configuring.html). |

7. Check the status of Cassandra:

```
$ nodetool status
```

The status column in the output should report `UN` which stands for
"Up/Normal".

Alternatively, connect to the database with:

```
$ cqlsh
```

## Installing the RPM packages

1. Verify the version of Java installed. For example:

* Command
* Result

```
$ java -version
```

```
openjdk version "1.8.0_222"
OpenJDK Runtime Environment (build 1.8.0_222-8u222-b10-1ubuntu1~16.04.1-b10)
OpenJDK 64-Bit Server VM (build 25.222-b10, mixed mode)
```

2. Add the Apache repository of Cassandra to the file
   `/etc/yum.repos.d/cassandra.repo` (as the `root` user).
   The latest major version is 4.0 and the corresponding distribution name is `40x` (with an "x" as the suffix).
   For older releases use:

   * `40x` for C\* 4.0 series
   * `311x` for C\* {311\_version} series
   * `30x` for C\* {30\_version} series
   * `22x` for C\* {22\_version} series
   * `21x` for C\* {21\_version} series

For example, to add the repository for version 4.0 (`40x`):

```
[cassandra]
name=Apache Cassandra
baseurl=https://redhat.cassandra.apache.org/40x/
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://downloads.apache.org/cassandra/KEYS
```

3. Update the package index from sources:

```
$ sudo yum update
```

4. Install Cassandra with YUM:

```
$ sudo yum install cassandra
```

|  |  |
| --- | --- |
|  | A new Linux user `cassandra` will get created as part of the installation. The Cassandra service will also be run as this user. |

5. Start the Cassandra service:

```
$ sudo service cassandra start
```

6. Monitor the progress of the startup with:

* Command
* Result

```
$ tail -f logs/system.log
```

Cassandra is ready when you see an entry like this in the `system.log`:

```
INFO  [main] 2019-12-17 03:03:37,526 Server.java:156 - Starting listening for CQL clients on localhost/127.0.0.1:9042 (unencrypted)...
```

|  |  |
| --- | --- |
|  | For information on how to configure your installation, see [Configuring Cassandra](http://cassandra.apache.org/doc/latest/getting_started/configuring.html). |

7. Check the status of Cassandra:

```
$ nodetool status
```

The status column in the output should report `UN` which stands for
"Up/Normal".

Alternatively, connect to the database with:

```
$ cqlsh
```

## Further installation info

For help with installation issues, see the
[Troubleshooting](http://cassandra.apache.org/doc/latest/troubleshooting/index.html)
section.
