---
title: "Compaction overview"
source_url: https://cassandra.apache.org/doc/5.0/cassandra/managing/operating/compaction/overview.html
cassandra_version: "5.0"
section: operating
retrieved: 2026-10-31
---

> Source: Apache Cassandra documentation, version 5.0, https://cassandra.apache.org/doc/5.0/cassandra/managing/operating/compaction/overview.html. Licensed under the Apache License 2.0.

# Compaction overview

## What is compaction?

Data in Cassandra is created in [memtables](../../../architecture/storage-engine.html#memtables).
Once a memory threshold is reached, to free up memory again, the data is written to an [SSTable](../../../architecture/storage-engine.html#SSTables), an [immutable](/_/glossary.html#immutable) file residing on disk.

Because SSTables are immutable, when data is updated or deleted, the old data is not overwritten with inserts or updates, or removed from the SSTable.
Instead, a new SSTable is created with the updated data with a new timestamp, and the old SSTable is marked for deletion.
The piece of deleted data is known as a [tombstone](/_/glossary.html#tombstone).

Over time, Cassandra may write many versions of a row in different SSTables.
Each version may have a unique set of columns stored with a different timestamp.
As SSTables accumulate, the distribution of data can require accessing more and more SSTables to retrieve a complete row.

To keep the database healthy, Cassandra periodically merges SSTables and discards old data.
This process is called [compaction](/_/glossary.html#compaction).

## Why must compaction be run?

Since SSTables are consulted during read operations, it is important to keep the number of SSTables small.
Write operations will cause the number of SSTables to grow, so compaction is necessary.
Besides the issue of tombstones, data is deleted for other reasons, too, such as Time-To-Live (TTL) expiration of some data.
Deleting, updating, or expiring data are all valid triggers for compaction.

## What does compaction accomplish?

Two important factors accomplished by compaction are performance improvement and disk space reclamation.
If SSTables have duplicate data that must be read, read operations are slower.
Once tombstones and duplicates are removed, read operations are faster.
SSTables use disk space, and reducing the size of SSTables through compaction frees up disk space.

## How does compaction work?

Compaction works on a collection of SSTables.
From these SSTables, compaction collects all versions of each unique row and assembles one complete row, using the most up-to-date version (by timestamp) of each of the row’s columns.
The merge process is performant, because rows are sorted by partition key within each SSTable, and the merge process does not use random I/O.
The new versions of each row is written to a new SSTable.
The old versions, along with any rows that are ready for deletion, are left in the old SSTables, and are deleted as soon as pending reads are completed.

## Types of compaction

The concept of compaction is used for different kinds of operations in
Cassandra, the common thing about these operations is that they take one
or more SSTables, merges, and outputs new SSTables. The types of compactions are:

Minor compaction
:   A minor compaction triggered automatically in Cassandra for several actions:

    * When an SSTable is added to the node through flushing
    * When autocompaction is enabled after being disabled (`nodetool enableautocompaction`)
    * When compaction adds new SSTables
    * A check for new minor compactions every 5 minutes

Major compaction
:   A major compaction is triggered when a user executes a compaction over all SSTables on the node.

User defined compaction
:   Similar to a major compaction, a user-defined compaction executes when a user triggers a compaction on a given set of SSTables.

Scrub
:   A scrub triggers a compaction to try to fix any broken SSTables.
    This can actually remove valid data if that data is corrupted.
    If that happens you will need to run a full repair on the node.

UpgradeSSTables
:   A compaction occurs when you upgrade SSTables to the latest version.
    Run this after upgrading to a new major version.

Cleanup
:   Compaction executes to remove any ranges that a node no longer owns.
    This type of compaction is typically triggered on neighbouring nodes after a node has been bootstrapped, since the bootstrapping node will take ownership of some ranges from those nodes.

Secondary index rebuild
:   A compaction is triggered if the secondary indexes are rebuilt on a node.

Anticompaction
:   After repair, the ranges that were actually repaired are split out of the SSTables that existed when repair started. This type of compaction rewrites SSTables to accomplish this task.

Sub range compaction
:   It is possible to only compact a given sub range - this action is useful if you know a token that has been misbehaving - either gathering many updates or many deletes.
    The command `nodetool compact -st x -et y` will pick all SSTables containing the range between x and y and issue a compaction for those SSTables.
    For Size Tiered Compaction Strategy, this will most likely include all SSTables, but with Leveled Compaction Strategy, it can issue the compaction for a subset of the SSTables.
    With LCS the resulting SSTable will end up in L0.

## Strategies

Different compaction strategies are available to optimize for different workloads.
Picking the right compaction strategy for your workload will ensure the best performance for both querying and for compaction itself.

[`Unified Compaction Strategy (UCS)`](ucs.html)
:   UCS is a good choice for most workloads and is recommended for new workloads.
    This compaction strategy is designed to handle a wide variety of workloads.
    It is designed to be able to handle both immutable time-series data and workloads with lots of updates and deletes.
    It is also designed to be able to handle both spinning disks and SSDs.

[`Size Tiered Compaction Strategy (STCS)`](stcs.html)
:   STCS is the default compaction strategy, because it is useful as a fallback when other strategies don’t fit the workload.
    Most useful for not strictly time-series workloads with spinning disks, or when the I/O from `LCS` is too high.

[`Leveled Compaction Strategy (LCS)`](lcs.html)
:   Leveled Compaction Strategy (LCS) is optimized for read heavy workloads, or workloads with lots of updates and deletes.
    It is not a good choice for immutable time-series data.

[`Time Window Compaction Strategy (TWCS)`](twcs.html)
:   Time Window Compaction Strategy is designed for TTL’ed, mostly immutable time-series data.

## Tombstones

### What are tombstones?

Cassandra’s processes for deleting data are designed to improve performance, and to work with Cassandra’s built-in properties for data distribution and fault-tolerance.

Cassandra treats a deletion as an insertion, and inserts a time-stamped deletion marker called a tombstone.
The tombstones go through Cassandra’s write path, and are written to SSTables on one or more nodes.
The key feature difference of a tombstone is that it has a built-in expiration date/time.
At the end of its expiration period, the grace period, the tombstone is deleted as part of Cassandra’s normal compaction process.

|  |  |
| --- | --- |
|  | You can also mark a Cassandra row or column with a time-to-live (TTL) value. After this amount of time has ended, Cassandra marks the object with a tombstone, and handles it like other tombstoned objects. |

### Why tombstones?

The tombstone represents the deletion of an object, either a row or column value.
This approach is used instead of removing values because of the distributed nature of Cassandra.
Once an object is marked as a tombstone, queries will ignore all values that are time-stamped previous to the tombstone insertion.

### Zombies

In a multi-node cluster, Cassandra may store replicas of the same data on two or more nodes.
This helps prevent data loss, but it complicates the deletion process.
If a node receives a delete command for data it stores locally, the node tombstones the specified object and tries to pass the tombstone to other nodes containing replicas of that object.
But if one replica node is unresponsive at that time, it does not receive the tombstone immediately, so it still contains the pre-delete version of the object.
If the tombstoned object has already been deleted from the rest of the cluster before that node recovers, Cassandra treats the object on the recovered node as new data, and propagates it to the rest of the cluster.
This kind of deleted but persistent object is called a [zombie](/_/glossary.html#zombie).

### Grace period

To prevent the reappearance of zombies, Cassandra gives each tombstone a grace period.
The grace period for a tombstone is set with the table property `WITH gc_grace_seconds`.
Its default value is 864000 seconds (ten days), after which a tombstone expires and can be deleted during compaction.
Prior to the grace period expiring, Cassandra will retain a tombstone through compaction events.
Each table can have its own value for this property.

The purpose of the grace period is to give unresponsive nodes time to recover and process tombstones normally.
If a client writes a new update to the tombstoned object during the grace period, Cassandra overwrites the tombstone.
If a client sends a read for that object during the grace period, Cassandra disregards the tombstone and retrieves the object from other replicas if possible.

When an unresponsive node recovers, Cassandra uses hinted handoff to replay the database mutations the node missed while it was down.
Cassandra does not replay a mutation for a tombstoned object during its grace period.
But if the node does not recover until after the grace period ends, Cassandra may miss the deletion.

After the tombstone’s grace period ends, Cassandra deletes the tombstone during compaction.

### Deletion

After `gc_grace_seconds` has expired the tombstone may be removed (meaning there will no longer be any object that a certain piece of data was
deleted).
But one complication for deletion is that a tombstone can live in one SSTable and the data it marks for deletion in another, so a compaction must also remove both SSTables.
More precisely, drop an actual tombstone the:

* The tombstone must be older than `gc_grace_seconds`.
  Note that tombstones will not be removed until a compaction event even if `gc_grace_seconds` has elapsed.
* If partition X contains the tombstone, the SSTable containing the partition plus all SSTables containing data older than the tombstone containing X must be included in the same compaction.
  If all data in any SSTable containing partition X is newer than the tombstone, it can be ignored.
* If the option `only_purge_repaired_tombstones` is enabled, tombstones are only removed if the data has also been repaired.
  This process is described in the "Deletes with tombstones" sections.

If a node remains down or disconnected for longer than `gc_grace_seconds`, its deleted data will be repaired back to the other nodes and reappear in the cluster.
This is basically the same as in the "Deletes without Tombstones" section.

#### Deletes without tombstones

Imagine a three node cluster which has the value [A] replicated to every node:

```
[A], [A], [A]
```

If one of the nodes fails and our delete operation only removes existing values, we can end up with a cluster that looks like:

```
[], [], [A]
```

Then a repair operation would replace the value of [A] back onto the two nodes which are missing the value:

```
[A], [A], [A]
```

This would cause our data to be resurrected as a zombie even though it had been deleted.

#### Deletes with tombstones

Starting again with a three node cluster which has the value [A] replicated to every node:

```
[A], [A], [A]
```

If instead of removing data we add a tombstone object, so the single node failure situation will look like:

```
[A, Tombstone[A]], [A, Tombstone[A]], [A]
```

Now when we issue a repair the tombstone will be copied to the replica, rather than the deleted data being resurrected:

```
[A, Tombstone[A]], [A, Tombstone[A]], [A, Tombstone[A]]
```

Our repair operation will correctly put the state of the system to what we expect with the object [A] marked as deleted on all nodes.
This does mean we will end up accruing tombstones which will permanently accumulate disk space.
To avoid keeping tombstones forever, we set `gc_grace_seconds` for every table in Cassandra.

### Fully expired SSTables

If an SSTable contains only tombstones and it is guaranteed that SSTable is not shadowing data in any other SSTable, then the compaction can drop
that SSTable.
If you see SSTables with only tombstones (note that TTL’d data is considered tombstones once the time-to-live has expired), but it is not being dropped by compaction, it is likely that other SSTables contain older data.
There is a tool called `sstableexpiredblockers` that will list which SSTables are droppable and which are blocking them from being dropped.
With `TimeWindowCompactionStrategy` it is possible to remove the guarantee (not check for shadowing data) by enabling `unsafe_aggressive_sstable_expiration`.

## TTL

Data in Cassandra can have an additional property called time to live -
this is used to automatically drop data that has expired once the time
is reached. Once the TTL has expired the data is converted to a
tombstone which stays around for at least `gc_grace_seconds`. Note that
if you mix data with TTL and data without TTL (or just different length
of the TTL) Cassandra will have a hard time dropping the tombstones
created since the partition might span many SSTables and not all are
compacted at once.

## Repaired/unrepaired data

With incremental repairs Cassandra must keep track of what data is
repaired and what data is unrepaired. With anticompaction repaired data
is split out into repaired and unrepaired SSTables. To avoid mixing up
the data again separate compaction strategy instances are run on the two
sets of data, each instance only knowing about either the repaired or
the unrepaired SSTables. This means that if you only run incremental
repair once and then never again, you might have very old data in the
repaired SSTables that block compaction from dropping tombstones in the
unrepaired (probably newer) SSTables.

## Data directories

Since tombstones and data can live in different SSTables it is important
to realize that losing an SSTable might lead to data becoming live again
- the most common way of losing SSTables is to have a hard drive break
down. To avoid making data live tombstones and actual data are always in
the same data directory. This way, if a disk is lost, all versions of a
partition are lost and no data can get undeleted. To achieve this a
compaction strategy instance per data directory is run in addition to
the compaction strategy instances containing repaired/unrepaired data,
this means that if you have 4 data directories there will be 8
compaction strategy instances running. This has a few more benefits than
just avoiding data getting undeleted:

* It is possible to run more compactions in parallel - leveled
  compaction will have several totally separate levelings and each one can
  run compactions independently from the others.
* Users can backup and restore a single data directory.
* Note though that currently all data directories are considered equal,
  so if you have a tiny disk and a big disk backing two data directories,
  the big one will be limited the by the small one. One work around to
  this is to create more data directories backed by the big disk.

## Single SSTable tombstone compaction

When an SSTable is written a histogram with the tombstone expiry times
is created and this is used to try to find SSTables with very many
tombstones and run single SSTable compaction on that SSTable in hope of
being able to drop tombstones in that SSTable. Before starting this it
is also checked how likely it is that any tombstones will actually
be able to be dropped and how much this SSTable overlaps with other
SSTables. To avoid most of these checks the compaction option
`unchecked_tombstone_compaction` can be enabled.

## Common options

There is a number of common options for all the compaction strategies;

`enabled` (default: true)
:   Whether minor compactions should run. Note that you can have 'enabled': true as a compaction option and then do 'nodetool enableautocompaction' to start running compactions.

`tombstone_threshold` (default: 0.2)
:   How much of the SSTable should be tombstones for us to consider doing a single SSTable compaction of that SSTable.

`tombstone_compaction_interval` (default: 86400s (1 day))
:   Since it might not be possible to drop any tombstones when doing a single SSTable compaction we need to make sure that one SSTable is not constantly getting recompacted - this option states how often we should try for a given SSTable.

`log_all` (default: false)
:   New detailed compaction logging, see [below](#detailed-compaction-logging).

`unchecked_tombstone_compaction` (default: false)
:   The single SSTable compaction has quite strict checks for whether it should be started, this option disables those checks and for some use cases this might be needed.
    Note that this does not change anything for the actual compaction, tombstones are only dropped if it is safe to do so - it might just rewrite an SSTable without being able to drop any tombstones.

`only_purge_repaired_tombstones` (default: false)
:   Option to enable the extra safety of making sure that tombstones are only dropped if the data has been repaired.

`min_threshold` (default: 4)
:   Lower limit of number of SSTables before a compaction is triggered.
    Not used for `LeveledCompactionStrategy`.

`max_threshold` (default: 32)
:   Upper limit of number of SSTables before a compaction is triggered.
    Not used for `LeveledCompactionStrategy`.

Further, see the section on each strategy for specific additional options.

## Compaction nodetool commands

The `nodetool` utility provides a number of commands related to compaction:

`enableautocompaction`
:   Enable compaction.

`disableautocompaction`
:   Disable compaction.

`setcompactionthroughput`
:   How fast compaction should run at most - defaults to 64MiB/s.

`compactionstats`
:   Statistics about current and pending compactions.

`compactionhistory`
:   List details about the last compactions.

`setcompactionthreshold`
:   Set the min/max SSTable count for when to trigger compaction, defaults to 4/32.

## Switching the compaction strategy and options using JMX

It is possible to switch compaction strategies and its options on just a single node using JMX, this is a great way to experiment with settings without affecting the whole cluster.
The mbean is:

```
org.apache.cassandra.db:type=ColumnFamilies,keyspace=<keyspace_name>,columnfamily=<table_name>
```

and the attribute to change is `CompactionParameters` or `CompactionParametersJson` if you use jconsole or jmc. For example, the syntax for the json version is the same as you would use in an `ALTER TABLE <alter-table-statement>` statement:

```
{ 'class': 'LeveledCompactionStrategy', 'sstable_size_in_mb': 123, 'fanout_size': 10}
```

The setting is kept until someone executes an `ALTER TABLE <alter-table-statement>` that touches the compaction settings or restarts the node.

## More detailed compaction logging

Enable with the compaction option `log_all` and a more detailed compaction log file will be produced in your log directory.
