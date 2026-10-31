---
title: "tpstats"
source_url: https://cassandra.apache.org/doc/5.0/cassandra/managing/tools/nodetool/tpstats.html
cassandra_version: "5.0"
section: tools
retrieved: 2026-10-31
---

> Source: Apache Cassandra documentation, version 5.0, https://cassandra.apache.org/doc/5.0/cassandra/managing/tools/nodetool/tpstats.html. Licensed under the Apache License 2.0.

# tpstats

## Usage

```
NAME
        nodetool tpstats - Print usage statistics of thread pools

SYNOPSIS
        nodetool [(-h <host> | --host <host>)] [(-p <port> | --port <port>)]
                [(-pp | --print-port)] [(-pw <password> | --password <password>)]
                [(-pwf <passwordFilePath> | --password-file <passwordFilePath>)]
                [(-u <username> | --username <username>)] tpstats
                [(-F <format> | --format <format>)]

OPTIONS
        -F <format>, --format <format>
            Output format (json, yaml)

        -h <host>, --host <host>
            Node hostname or ip address

        -p <port>, --port <port>
            Remote jmx agent port number

        -pp, --print-port
            Operate in 4.0 mode with hosts disambiguated by port number

        -pw <password>, --password <password>
            Remote jmx agent password

        -pwf <passwordFilePath>, --password-file <passwordFilePath>
            Path to the JMX password file

        -u <username>, --username <username>
            Remote jmx agent username
```
