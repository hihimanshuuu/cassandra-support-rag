---
title: "Size Tiered Compaction Strategy (STCS)"
source_url: https://cassandra.apache.org/doc/5.0/cassandra/managing/operating/compaction/stcs.html
cassandra_version: "5.0"
section: operating
retrieved: 2026-10-31
---

> Source: Apache Cassandra documentation, version 5.0, https://cassandra.apache.org/doc/5.0/cassandra/managing/operating/compaction/stcs.html. Licensed under the Apache License 2.0.

# Size Tiered Compaction Strategy (STCS)

|  |  |
| --- | --- |
|  | The Unified Compaction Strategy (UCS) is the recommended compaction strategy for most workloads starting with {cass-50}. If you are creating new tables, use this strategy. |

The `SizeTieredCompactionStrategy (STCS)` is recommended for write-intensive workloads, and is the legacy recommended compaction strategy.
It is the default compaction strategy if no other strategy is specified.

STCS initiates compaction when Cassandra has accumulated a set number (default: 4) of similar-sized SSTables.
STCS merges these SSTables into one larger SSTable.
As these larger SSTables accumulate, STCS merges them into even larger SSTables.
At any given time, several SSTables of varying sizes are present.

While STCS works well to compact a write-intensive workload, it makes reads slower because the merge-by-size process does not group data by rows.
This fact makes it more likely that versions of a particular row may be spread over many SSTables.
Also, STCS does not evict deleted data predictably, because its trigger for compaction is SSTable size.
However, SSTables may not grow quickly enough to merge and evict old data regularly.

Most STCS compactions are minor compactions, which merge a few SSTables into one.
In contrast, when executing a major compaction with STCS, two SSTables per data directory, one for repaired data and one for unrepaired data, will exist during the compaction.
As the largest SSTables grow in size, the amount of disk space needed for both the new and old SSTables simultaneously during STCS compaction can outstrip a typical amount of disk space on a node.
This phenomenon is known as space amplification, the problem of growing SSTable size, and the issue of outgrowing a cluster’s ability to do compaction.
Major compactions are not recommended for STCS.

STCS depends on the calculation of the average size of SSTables to determine which SSTables to merge.
This process is called bucketing.
The following options are used to calculate the bucket into which an SSTable will be grouped, based on that average size.
The bucketing process groups SSTables based on their size differing from the average size by either 50% or 150% more than the average size.
Another way to state this calculation is that the bucketing process groups SSTables with a size within [average-size Ã bucket\_low] and [average-size Ã bucket\_high].

|  |  |
| --- | --- |
|  | The `SizeTieredCompactionStrategy` is the default compaction strategy. Any other compaction strategy must be defined in the `cassandra.yaml` file. |

## STCS options

SizeTieredCompactionStrategy (STCS) options are set per table using table options.
The `min_threshold` option of a table is the main value that triggers a minor compaction.
Minor compactions do not involve all the tables in a keyspace.

| Subproperty | Description |
| --- | --- |
| enabled | Enables background compaction. Default value: true |
| tombstone\_compaction\_interval | The minimum number of seconds after which an SSTable is created before Cassandra considers the SSTable for tombstone compaction. An SSTable is eligible for tombstone compaction if the table exceeds the `tombstone_threshold` ratio. Default value: 86400 |
| tombstone\_threshold | The ratio of garbage-collectable tombstones to all contained columns. If the ratio exceeds this limit, Cassandra starts compaction on that table alone, to purge the tombstones. Default value: 0.2 |
| unchecked\_tombstone\_compaction | If set to `true`, allows Cassandra to run tombstone compaction without pre-checking which tables are eligible for this operation. Even without this pre-check, Cassandra checks an SSTable to make sure it is safe to drop tombstones. Default value: false |
| log\_all | Activates advanced logging for the entire cluster. Default value: false |
| max\_threshold | The maximum number of SSTables to allow in a minor compaction. Default value: 32 |
| min\_threshold | The minimum number of SSTables to trigger a minor compaction. Default value: 4 |
| bucket\_high | An SSTable is added to a bucket if its size is less than 150% of the average size of that bucket. For example, if the SSTable size is 13 MB, and the bucket average size is 10 MB, then the SSTable will be added to that bucket and the new average size will be computed for that bucket. Default value: 1.5 |
| bucket\_low | An SSTable is added to a bucket if the SSTable size is greater than 50% of the average size of that bucket. For example, if the SSTable size is 6 MB, and the bucket average size is 10 MB, then the SSTable will be added to that bucket and the new average size will be computed for that bucket. Default value: 0.5 |
| min\_sstable\_size | SSTables smaller than this value will be grouped into one bucket where the average size is less than this setting. Default value: 50MB |
| only\_purge\_repaired\_tombstones | If set to `true`, allows purging tombstones only from repaired SSTables. The purpose is to prevent data from resurrecting if repair is not run within `gc_grace_seconds`. If you do not run repair for a long time, Cassandra keeps all tombstones â this may cause problems. Default value: false |
