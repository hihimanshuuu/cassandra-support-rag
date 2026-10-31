---
title: "commitlog-archiving.properties file"
source_url: https://cassandra.apache.org/doc/5.0/cassandra/managing/configuration/cass_cl_archive_file.html
cassandra_version: "5.0"
section: configuration
retrieved: 2026-10-31
---

> Source: Apache Cassandra documentation, version 5.0, https://cassandra.apache.org/doc/5.0/cassandra/managing/configuration/cass_cl_archive_file.html. Licensed under the Apache License 2.0.

# commitlog-archiving.properties file

The `commitlog-archiving.properties` configuration file can optionally
set commands that are executed when archiving or restoring a commitlog
segment.

## Options

### `archive_command`

One command can be inserted with `%path`
and `%name` arguments. `%path` is the fully qualified path of the commitlog
segment to archive. `%name` is the filename of the commitlog. `STDOUT`,
`STDIN`, or multiple commands cannot be executed. If multiple commands are
required, add a pointer to a script in this option.

**Example:** archive\_command=/bin/ln %path /backup/%name

**Default value:** blank

### `restore_command`

One command can be inserted with `%from`
and `%to` arguments. `%from` is the fully qualified path to an archived
commitlog segment using the specified restore directories. `%to` defines
the directory to the live commitlog location.

**Example:** restore\_command=/bin/cp -f %from %to

**Default value:** blank

### `restore_directories`

Defines the directory to scan the recovery files into.

**Example:** restore\_directories=/path/to/restore\_dir\_location

**Default value:** blank

### `restore_point_in_time`

Restore mutations created up
to and including this timestamp in GMT in the format
`yyyy:MM:dd HH:mm:ss`. Recovery will continue through the segment when
the first client-supplied timestamp greater than this time is
encountered, but only mutations less than or equal to this timestamp
will be applied.

**Example:** restore\_point\_in\_time=2020:04:31 20:43:12

**Default value:** blank

### `precision`

Precision of the timestamp used
in the inserts. Choice is generally MILLISECONDS or MICROSECONDS

**Example:** precision=MICROSECONDS

**Default value:** MICROSECONDS
