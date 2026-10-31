---
title: "Troubleshooting"
source_url: https://cassandra.apache.org/doc/5.0/cassandra/troubleshooting/index.html
cassandra_version: "5.0"
section: troubleshooting
retrieved: 2026-10-31
---

> Source: Apache Cassandra documentation, version 5.0, https://cassandra.apache.org/doc/5.0/cassandra/troubleshooting/index.html. Licensed under the Apache License 2.0.

# Troubleshooting

As any distributed database does, sometimes Cassandra breaks and you
will have to troubleshoot what is going on. Generally speaking you can
debug Cassandra like any other distributed Java program, meaning that
you have to find which machines in your cluster are misbehaving and then
isolate the problem using logs and tools. Luckily Cassandra had a great
set of instrospection tools to help you.

These pages include a number of command examples demonstrating various
debugging and analysis techniques, mostly for Linux/Unix systems. If you
don’t have access to the machines running Cassandra, or are running on
Windows or another operating system you may not be able to use the exact
commands but there are likely equivalent tools you can use.

* [Finding nodes](finding_nodes.html)
* [Reading logs](reading_logs.html)
* [Using nodetool](use_nodetool.html)
* [Using tools](use_tools.html)
