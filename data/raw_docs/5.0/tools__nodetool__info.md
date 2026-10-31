---
title: "info"
source_url: https://cassandra.apache.org/doc/5.0/cassandra/managing/tools/nodetool/info.html
cassandra_version: "5.0"
section: tools
retrieved: 2026-10-31
---

> Source: Apache Cassandra documentation, version 5.0, https://cassandra.apache.org/doc/5.0/cassandra/managing/tools/nodetool/info.html. Licensed under the Apache License 2.0.

# info

## Usage

```
NAME
        nodetool info - Print node information (uptime, load, ...)

SYNOPSIS
        nodetool [(-h <host> | --host <host>)] [(-p <port> | --port <port>)]
                [(-pp | --print-port)] [(-pw <password> | --password <password>)]
                [(-pwf <passwordFilePath> | --password-file <passwordFilePath>)]
                [(-u <username> | --username <username>)] info
                [(-O | --out-of-range-ops)] [(-T | --tokens)]

OPTIONS
        -h <host>, --host <host>
            Node hostname or ip address

        -O, --out-of-range-ops
            Display per-keyspace counts of operations for invalid tokens

        -p <port>, --port <port>
            Remote jmx agent port number

        -pp, --print-port
            Operate in 4.0 mode with hosts disambiguated by port number

        -pw <password>, --password <password>
            Remote jmx agent password

        -pwf <passwordFilePath>, --password-file <passwordFilePath>
            Path to the JMX password file

        -T, --tokens
            Display all tokens

        -u <username>, --username <username>
            Remote jmx agent username
```
