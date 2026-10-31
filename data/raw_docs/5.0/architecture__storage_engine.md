---
title: "Storage Engine"
source_url: https://cassandra.apache.org/doc/5.0/cassandra/architecture/storage-engine.html
cassandra_version: "5.0"
section: architecture
retrieved: 2026-10-31
---

> Source: Apache Cassandra documentation, version 5.0, https://cassandra.apache.org/doc/5.0/cassandra/architecture/storage-engine.html. Licensed under the Apache License 2.0.

# Storage Engine

The Cassandra storage engine is optimized for high performance, write-oriented workloads. The architecture is based on Log Structured Merge (LSM) trees, which utilize an append-only approach instead of the traditional relational database design with B-trees. This creates a write path free of read lookups and bottlenecks.

While the write path is highly optimized, it comes with tradeoffs in terms of read performance and write amplification. To enhance read operations, Cassandra uses Bloom filters when accessing data from stables. Bloom filters are remarkably efficient, leading to generally well-balanced performance for both reads and writes.

Compaction is a necessary background activity required by the âmergeâ phase of Log Structured Merge trees. Compaction creates write amplification when several small SSTables on disk are read, merged, updates and deletes processed, and a new SSTable is re-written. Every write of data in Cassandra is re-written multiple times, known as write amplification, and this adds background I/O to the database workload.

The core storage engine consists of memtables for in-memory data and immutable SSTables (Sorted String Tables) on disk. Data in SSTables is stored sorted to enable efficient merge sort during compaction. Additionally, a write-ahead log (WAL), referred to as the commit log, ensures resiliency for crash and transaction recovery.

The sequence of the steps in the write path:

* Logging data in the commit log
* Writing data to the memtable
* Flushing data from the memtable
* Storing data on disk in SSTables

## Logging writes to commit logs

When a write operation takes place, Cassandra records the data in a local append-only [cassandra.apache.org/](/)*/glossary.html#commit-log[commit log] on disk.
This action provides [configurable durability](../managing/configuration/cass_yaml_file.html) by logging every write made to a Cassandra node.
If an unexpected shutdown occurs, the commit log provides permanent durable writes of the data.
On startup, any mutations in the commit log will be applied to [cassandra.apache.org/](/)*/glossary.html#memtable[memtables].
The commit log is shared among tables.

All mutations are write-optimized on storage in commit log segments, reducing the number of seeks needed to write to disk.
Commit log segments are limited by the [`commitlog_segment_size`](../managing/configuration/cass_yaml_file.html#commitlog_segment_size) option.
Once the defined size is reached, a new commit log segment is created.
Commit log segments can be archived, deleted, or recycled once all the data is flushed to
[SSTables](/_/glossary.html#sstable).
Commit log segments are truncated when Cassandra has written data older than a certain point to the SSTables.
Running [`nodetool drain`](../managing/tools/nodetool/drain.html) before stopping Cassandra will write everything in the memtables
to SSTables and remove the need to sync with the commit logs on startup.

* [`commitlog_segment_size`](../managing/configuration/cass_yaml_file.html#commitlog_segment_size ): The default size is 32MiB, which is almost always fine, but if you are archiving commitlog segments (see commitlog\_archiving.properties), then you probably want a finer granularity of archiving; 8 or 16 MiB is reasonable.
  `commitlog_segment_size` also determines the default value of [`max_mutation_size`](../managing/configuration/cass_yaml_file.html#max_mutation_size) in `cassandra.yaml`. By default, `max_mutation_size` is a half the size of `commitlog_segment_size`.

|  |  |
| --- | --- |
|  | If `max_mutation_size` is set explicitly then `commitlog_segment_size` must be set to at least twice the size of `max_mutation_size`. |

* [`commitlog_sync`](../managing/configuration/cass_yaml_file.html#commitlog_sync): may be either *periodic* or *batch*.

  + `batch`: In batch mode, Cassandra won’t acknowledge writes until the commit log has been fsynced to disk.
  + `periodic`: In periodic mode, writes are immediately acknowledged, and the commit log is simply synced every "commitlog\_sync\_period" milliseconds.

    - `commitlog_sync_period`: Time to wait between "periodic" fsyncs
      *Default Value:* 10000ms

*Default Value:* periodic

|  |  |
| --- | --- |
|  | In the event of an unexpected shutdown, Cassandra can lose up to the sync period or more if the sync is delayed. If using `batch` mode, it is recommended to store commit logs in a separate, dedicated device. |

* [`commitlog_directory`](../managing/configuration/cass_yaml_file.html#commitlog_directory): This option is commented out by default.
  When running on magnetic HDD, this should be a separate spindle than the data directories.
  If not set, the default directory is `$CASSANDRA_HOME/data/commitlog`.

*Default Value:* `/var/lib/cassandra/commitlog`

* [`commitlog_compression`](../managing/configuration/cass_yaml_file.html#commitlog_compression): Compression to apply to the commitlog.
  If omitted, the commit log will be written uncompressed.
  LZ4, Snappy,Deflate and Zstd compressors are supported.

*Default Value:*

```
#   - class_name: LZ4Compressor
#     parameters:
```

* [`commitlog_total_space`](../managing/configuration/cass_yaml_file.html#commitlog_total_space): Total space to use for commit logs on disk.
  This option is commented out by default.
  If space gets above this value, Cassandra will flush every dirty table in the oldest segment and remove it.
  So a small total commit log space will tend to cause more flush activity on less-active tables.
  The default value is the smallest between 8192 and 1/4 of the total space of the commitlog volume.

*Default Value:* 8192MiB

## Memtables

When Cassandra accepts new write requests, it saves the data in two places: an in-memory write-back cache called a memtable and the CommitLog.
The memtable buffers writes and allows serving reads without accessing the disk, while the CommitLog ensures durability by appending new mutations.
Typically, there is one active memtable per table, acting as a cache for data partitions that Cassandra accesses by key.

Depending on the [`memtable_allocation_type`](../managing/configuration/cass_yaml_file.html#memtable_allocation_type), memtables can be stored entirely on-heap or partially off-heap.
If Cassandra crashes before flushing the memtable, it can restore acknowledged writes by replaying the commitLog.

The memtable stores writes in sorted order until reaching a configurable limit.
When the limit is reached, memtables are flushed onto disk and become immutable [SSTables](#sstables).
Flushing can be triggered in several ways:

* The memory usage of the memtables exceeds the configured threshold (see [`memtable_cleanup_threshold`](../managing/configuration/cass_yaml_file.html#memtable_cleanup_threshold))
* The `commit log` approaches its maximum size, and forces memtable flushes in order to allow commit log segments to be freed.

When a triggering event occurs, the memtable is put in a queue that is flushed to disk.
Flushing writes the data to disk, in the memtable-sorted order.
A partition index is also created on the disk that maps the tokens to a location on disk.

The queue can be configured with either the [`memtable_heap_space`](../managing/configuration/cass_yaml_file.html#memtable_heap_space) or [`memtable_offheap_space`](../managing/configuration/cass_yaml_file.html#memtable_offheap_space) setting in the `cassandra.yaml` file.
If the data to be flushed exceeds the `memtable_cleanup_threshold`, Cassandra blocks writes until the next flush succeeds.
You can manually flush a table using [`nodetool flush`](../managing/tools/nodetool/flush.html) or `nodetool drain` (flushes memtables without listening for connections to other nodes).
To reduce the commit log replay time, the recommended best practice is to flush the memtable before you restart the nodes.
If a node stops working, replaying the commit log restores writes to the memtable that were there before it stopped.

Data in the commit log is purged after its corresponding data in the memtable is flushed to an SSTable on disk.

## SSTables

[SSTables](/_/glossary.html#sstable) are the immutable data files that Cassandra uses for persisting data on disk.
SSTables are maintained per table.
SSTables are immutable, and never written to again after the memtable is flushed.
Thus, a partition is typically stored across multiple SSTable files, as data is added or modified.

Each SSTable consists of multiple components stored in separate files:

`Data.db`
:   The actual data, i.e. the contents of rows.

`Partitions.db`
:   The partition index file maps unique prefixes of decorated partition keys to data file locations, or, in the case of wide partitions indexed in the row index file, to locations in the row index file.

`Rows.db`
:   The row index file only contains entries for partitions that contain more than one row and are bigger than one index block.
    For all such partitions, it stores a copy of the partition key, a partition header, and an index of row block separators, which map each row key into the first block where any content with equal or higher row key can be found.

`Index.db`
:   An index from partition keys to positions in the `Data.db` file.
    For wide partitions, this may also include an index to rows within a partition.

`Summary.db`
:   A sampling of (by default) every 128th entry in the `Index.db` file.

`Filter.db`
:   A Bloom Filter of the partition keys in the SSTable.

`CompressionInfo.db`
:   Metadata about the offsets and lengths of compression chunks in the `Data.db` file.

`Statistics.db`
:   Stores metadata about the SSTable, including information about timestamps, tombstones, clustering keys, compaction, repair, compression, TTLs, and more.

`Digest.crc32`
:   A CRC-32 digest of the `Data.db` file.

`TOC.txt`
:   A plain text list of the component files for the SSTable.

`SAI*.db`
:   Index information for Storage-Attached indexes.
    Only present if SAI is enabled for the table.

|  |  |
| --- | --- |
|  | Note that the `Index.db` file type is replaced by `Partitions.db` and `Rows.db`. This change is a consequence of the inclusion of Big Trie indexes in Cassandra [CEP-25](https://cwiki.apache.org/confluence/display/CASSANDRA/CEP-25%3A+Trie-indexed+SSTable+format). |

Within the `Data.db` file, rows are organized by partition.
These partitions are sorted in token order (i.e. by a hash of the partition key when the default partitioner, `Murmur3Partition`, is used).
Within a partition, rows are stored in the order of their clustering keys.

SSTables can be optionally compressed using block-based compression.

As SSTables are flushed to disk from `memtables` or are streamed from other nodes, Cassandra triggers compactions which combine multiple SSTables into one.
Once the new SSTable has been written, the old SSTables can be removed.

## SSTable Versions

From [BigFormat#BigVersion](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/io/sstable/format/big/BigFormat.java#L338).

The version numbers, to date are:

### Version 0

* b (0.7.0): added version to SSTable filenames
* c (0.7.0): bloom filter component computes hashes over raw key bytes
  instead of strings
* d (0.7.0): row size in data component becomes a long instead of int
* e (0.7.0): stores undecorated keys in data and index components
* f (0.7.0): switched bloom filter implementations in data component
* g (0.8): tracks flushed-at context in metadata component

### Version 1

* h (1.0): tracks max client timestamp in metadata component
* hb (1.0.3): records compression ration in metadata component
* hc (1.0.4): records partitioner in metadata component
* hd (1.0.10): includes row tombstones in maxtimestamp
* he (1.1.3): includes ancestors generation in metadata component
* hf (1.1.6): marker that replay position corresponds to 1.1.5+
  millis-based id (see CASSANDRA-4782)
* ia (1.2.0):

  + column indexes are promoted to the index file
  + records estimated histogram of deletion times in tombstones
  + bloom filter (keys and columns) upgraded to Murmur3
* ib (1.2.1): tracks min client timestamp in metadata component
* ic (1.2.5): omits per-row bloom filter of column names

### Version 2

* ja (2.0.0):

  + super columns are serialized as composites (note that there is no
    real format change, this is mostly a marker to know if we should expect
    super columns or not. We do need a major version bump however, because
    we should not allow streaming of super columns into this new format)
  + tracks max local deletiontime in SSTable metadata
  + records bloom\_filter\_fp\_chance in metadata component
  + remove data size and column count from data file (CASSANDRA-4180)
  + tracks max/min column values (according to comparator)
* jb (2.0.1):

  + switch from crc32 to adler32 for compression checksums
  + checksum the compressed data
* ka (2.1.0):

  + new Statistics.db file format
  + index summaries can be down sampled and the sampling level is
    persisted
  + switch uncompressed checksums to adler32
  + tracks presence of legacy (local and remote) counter shards
* la (2.2.0): new file name format
* lb (2.2.7): commit log lower bound included

### Version 3

* ma (3.0.0):

  + swap bf hash order
  + store rows natively
* mb (3.0.7, 3.7): commit log lower bound included
* mc (3.0.8, 3.9): commit log intervals included
* md (3.0.18, 3.11.4): corrected SSTable min/max clustering
* me (3.0.25, 3.11.11): added hostId of the node from which the SSTable originated

### Version 4

* na (4.0-rc1): uncompressed chunks, pending repair session, isTransient, checksummed SSTable metadata file, new Bloom filter format
* nb (4.0.0): originating host id

### Version 5

* oa (5.0): improved min/max, partition level deletion presence marker, key range (CASSANDRA-18134)

  + Long deletionTime to prevent TTL overflow
  + token space coverage

## Trie-indexed Based SSTable Versions (BTI)

Cassandra 5.0 introduced new SSTable formats BTI for Trie-indexed SSTables.
To use the BTI formats configure it `cassandra.yaml` like

```
sstable:
  selected_format: bti
```

Versions come from [BtiFormat#BtiVersion](https://github.com/apache/cassandra/blob/f16fb6765b8a3ff8f49accf61c908791520c0d6e/src/java/org/apache/cassandra/io/sstable/format/bti/BtiFormat.java#L302).

For implementation docs see [BtiFormat.md](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/io/sstable/format/bti/BtiFormat.md).

### Version 5

* da (5.0): initial version of the BTI format

### Example Code

The following example is useful for finding all SSTables that do not
match the "ib" SSTable version

```
find /var/lib/cassandra/data/ -type f | grep -v -- -ib- | grep -v "/snapshots"
```
