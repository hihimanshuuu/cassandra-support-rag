---
title: "flush"
source_url: https://cassandra.apache.org/doc/5.0/cassandra/managing/tools/nodetool/flush.html
cassandra_version: "5.0"
section: tools
retrieved: 2026-10-31
---

> Source: Apache Cassandra documentation, version 5.0, https://cassandra.apache.org/doc/5.0/cassandra/managing/tools/nodetool/flush.html. Licensed under the Apache License 2.0.

# flush

## Usage

```
NAME
        nodetool flush - Flush one or more tables

SYNOPSIS
        nodetool [(-h <host> | --host <host>)] [(-p <port> | --port <port>)]
                [(-pp | --print-port)] [(-pw <password> | --password <password>)]
                [(-pwf <passwordFilePath> | --password-file <passwordFilePath>)]
                [(-u <username> | --username <username>)] flush [--] [<keyspace>
                <tables>...]

OPTIONS
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

        --
            This option can be used to separate command-line options from the
            list of argument, (useful when arguments might be mistaken for
            command-line options

        [<keyspace> <tables>...]
            The keyspace followed by one or many tables
```
