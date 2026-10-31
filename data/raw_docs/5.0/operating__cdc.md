---
title: "Change Data Capture"
source_url: https://cassandra.apache.org/doc/5.0/cassandra/managing/operating/cdc.html
cassandra_version: "5.0"
section: operating
retrieved: 2026-10-31
---

> Source: Apache Cassandra documentation, version 5.0, https://cassandra.apache.org/doc/5.0/cassandra/managing/operating/cdc.html. Licensed under the Apache License 2.0.

# Change Data Capture

## Overview

Change data capture (CDC) provides a mechanism to flag specific tables
for archival as well as rejecting writes to those tables once a
configurable size-on-disk for the CDC log is reached. An operator can
enable CDC on a table by setting the table property `cdc=true` (either
when [`creating the table`](../../developing/cql/ddl.html#create-table) or
[`altering it`](../../developing/cql/ddl.html#alter-table)). Upon CommitLogSegment creation,
a hard-link to the segment is created in the directory specified in
`cassandra.yaml`. On segment fsync to disk, if CDC data is present
anywhere in the segment a <segment\_name>\_cdc.idx file is also created
with the integer offset of how much data in the original segment is
persisted to disk. Upon final segment flush, a second line with the
human-readable word "COMPLETED" will be added to the \_cdc.idx file
indicating that Cassandra has completed all processing on the file.

We use an index file rather than just encouraging clients to parse
the log realtime off a memory mapped handle as data can be reflected in
a kernel buffer that is not yet persisted to disk. Parsing only up to
the listed offset in the \_cdc.idx file will ensure that you only parse
CDC data for data that is durable.

Please note that in rare chances, e.g. slow disk, it is possible for the
consumer to read an empty value from the \_cdc.idx file because update is
achieved with first truncating the file then write to the file. In such
case, the consumer should retry read the index file.

A threshold of total disk space allowed is specified in the yaml at
which time newly allocated CommitLogSegments will not allow CDC data
until a consumer parses and removes files from the specified cdc\_raw
directory.

## Configuration

### Enabling or disabling CDC on a table

CDC is enable or disable through the cdc table property,
for instance:

```
CREATE TABLE foo (a int, b text, PRIMARY KEY(a)) WITH cdc=true;

ALTER TABLE foo WITH cdc=true;

ALTER TABLE foo WITH cdc=false;
```

### cassandra.yaml parameters

The following cassandra.yaml options are available for CDC:

`cdc_enabled` (default: false)
:   Enable or disable CDC operations node-wide.

`cdc_raw_directory` (default: `$CASSANDRA_HOME/data/cdc_raw`)
:   Destination for CommitLogSegments to be moved after all corresponding
    memtables are flushed.

`cdc_total_space`: (default: min of 4096MiB and 1/8th volume space)
:   Calculated as sum of all active CommitLogSegments that permit CDC  
    all flushed CDC segments in `cdc_raw_directory`.

`cdc_free_space_check_interval` (default: 250ms)
:   When at capacity, we limit the frequency with which we re-calculate
    the space taken up by `cdc_raw_directory` to prevent burning CPU
    cycles unnecessarily. Default is to check 4 times per second.

## Reading CommitLogSegments

Use a
[CommitLogReader.java](https://github.com/apache/cassandra/blob/e31e216234c6b57a531cae607e0355666007deb2/src/java/org/apache/cassandra/db/commitlog/CommitLogReader.java).
Usage is
[fairly
straightforward](https://github.com/apache/cassandra/blob/e31e216234c6b57a531cae607e0355666007deb2/src/java/org/apache/cassandra/db/commitlog/CommitLogReplayer.java#L132-L140) with a
[variety
of signatures](https://github.com/apache/cassandra/blob/e31e216234c6b57a531cae607e0355666007deb2/src/java/org/apache/cassandra/db/commitlog/CommitLogReader.java#L71-L103) available for use. In order to handle mutations read from
disk, implement
[CommitLogReadHandler](https://github.com/apache/cassandra/blob/e31e216234c6b57a531cae607e0355666007deb2/src/java/org/apache/cassandra/db/commitlog/CommitLogReadHandler.java).

## Warnings

**Do not enable CDC without some kind of consumption process in-place.**

If CDC is enabled on a node and then on a table, the
`cdc_free_space_in_mb` will fill up and then writes to CDC-enabled
tables will be rejected unless some consumption process is in place.

## Further Reading

* Change Data Capture ( [CASSANDRA-8844 JIRA ticket](https://issues.apache.org/jira/browse/CASSANDRA-8844) )
* Improve determinism of CDC data availability ( [CASSANDRA-12148 JIRA ticket](https://issues.apache.org/jira/browse/CASSANDRA-12148) )
