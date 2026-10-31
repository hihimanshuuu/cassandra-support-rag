---
title: "Nodetool"
source_url: https://cassandra.apache.org/doc/5.0/cassandra/managing/tools/nodetool/nodetool.html
cassandra_version: "5.0"
section: tools
retrieved: 2026-10-31
---

> Source: Apache Cassandra documentation, version 5.0, https://cassandra.apache.org/doc/5.0/cassandra/managing/tools/nodetool/nodetool.html. Licensed under the Apache License 2.0.

# Nodetool

## Usage

```
usage: nodetool [(-pwf <passwordFilePath> | --password-file <passwordFilePath>)]
        [(-p <port> | --port <port>)] [(-pp | --print-port)]
        [(-h <host> | --host <host>)] [(-u <username> | --username <username>)]
        [(-pw <password> | --password <password>)] <command> [<args>]
```

The most commonly used nodetool commands are:

[assassinate](assassinate.html) - Forcefully remove a dead node without re-replicating any data. Use as a last resort if you cannot removenode

[autorepairstatus](autorepairstatus.html) - Print autorepair status

[bootstrap](bootstrap.html) - Monitor/manage node’s bootstrap process

[checktokenmetadata](checktokenmetadata.html) -
[compares](#cassandra:managing/tools/nodetool/compares.adoc) - the Gossip endpointState and TokenMetadata cache; printing any mismatches found

[cidrfilteringstats](cidrfilteringstats.html) - Print statistics on CIDR filtering

[cleanup](cleanup.html) - Triggers the immediate cleanup of keys no longer belonging to a node. By default, clean all keyspaces

[clearsnapshot](clearsnapshot.html) - Remove the snapshot with the given name from the given keyspaces

[clientstats](clientstats.html) - Print information about connected clients

[compact](compact.html) - Force a (major) compaction on one or more tables or user-defined compaction on given SSTables

[compactionhistory](compactionhistory.html) - Print history of compaction

[compactionstats](compactionstats.html) - Print statistics on compactions

[datapaths](datapaths.html) - Print all directories where data of tables are stored

[decommission](decommission.html) - Decommission the **node I am connecting to**

[describecluster](describecluster.html) - Print the name, snitch, partitioner and schema version of a cluster

[describering](describering.html) - Shows the token ranges info of a given keyspace

[disableauditlog](disableauditlog.html) - Disable the audit log

[disableautocompaction](disableautocompaction.html) - Disable autocompaction for the given keyspace and table

[disablebackup](disablebackup.html) - Disable incremental backup

[disablebinary](disablebinary.html) - Disable native transport (binary protocol)

[disablefullquerylog](disablefullquerylog.html) - Disable the full query log

[disablegossip](disablegossip.html) - Disable gossip (effectively marking the node down)

[disablehandoff](disablehandoff.html) - Disable storing hinted handoffs

[disablehintsfordc](disablehintsfordc.html) - Disable hints for a data center

[disableoldprotocolversions](disableoldprotocolversions.html) - Disable old protocol versions

[drain](drain.html) - Drain the node (stop accepting writes and flush all tables)

[dropcidrgroup](dropcidrgroup.html) - Drop an existing cidr group

[enableauditlog](enableauditlog.html) - Enable the audit log

[enableautocompaction](enableautocompaction.html) - Enable autocompaction for the given keyspace and table

[enablebackup](enablebackup.html) - Enable incremental backup

[enablebinary](enablebinary.html) - Reenable native transport (binary protocol)

[enablefullquerylog](enablefullquerylog.html) - Enable full query logging, defaults for the options are configured in cassandra.yaml

[enablegossip](enablegossip.html) - Reenable gossip

[enablehandoff](enablehandoff.html) - Reenable future hints storing on the current node

[enablehintsfordc](enablehintsfordc.html) - Enable hints for a data center that was previsouly disabled

[enableoldprotocolversions](enableoldprotocolversions.html) - Enable old protocol versions

[failuredetector](failuredetector.html) - Shows the failure detector information for the cluster

[flush](flush.html) - Flush one or more tables

[forcecompact](forcecompact.html) - Force a (major) compaction on a table

[garbagecollect](garbagecollect.html) - Remove deleted data from one or more tables

[gcstats](gcstats.html) - Print GC Statistics

[getauditlog](getauditlog.html) - Print configuration of audit log if enabled, otherwise the configuration reflected in cassandra.yaml

[getauthcacheconfig](getauthcacheconfig.html) - Get configuration of Auth cache

[getautorepairconfig](getautorepairconfig.html) - Print autorepair configurations

[getbatchlogreplaythrottle](getbatchlogreplaythrottle.html) - Print batchlog replay throttle in KB/s. This is reduced proportionally to the number of nodes in the cluster.

[getcidrgroupsofip](getcidrgroupsofip.html) - Print CIDR groups associated with given IP

[getcolumnindexsize](getcolumnindexsize.html) - Print the granularity of the collation index of rows within a partition in KiB

[getcompactionthreshold](getcompactionthreshold.html) - Print min and max compaction thresholds for a given table

[getcompactionthroughput](getcompactionthroughput.html) - Print the MiB/s throughput cap for compaction in the system as a rounded number

[getconcurrency](getconcurrency.html) - Get maximum concurrency for processing stages

[getconcurrentcompactors](getconcurrentcompactors.html) - Get the number of concurrent compactors in the system.

[getconcurrentviewbuilders](getconcurrentviewbuilders.html) - Get the number of concurrent view builders in the system

[getdefaultrf](getdefaultrf.html) - Gets default keyspace replication factor.

[getendpoints](getendpoints.html) - Print the end points that owns the key

[getfullquerylog](getfullquerylog.html) - Print configuration of fql if enabled, otherwise the configuration reflected in cassandra.yaml

[getguardrailsconfig](getguardrailsconfig.html) - Print runtime configuration of guardrails.

[getinterdcstreamthroughput](getinterdcstreamthroughput.html) - Print the throughput cap for inter-datacenter streaming and entire SSTable inter-datacenter streaming in the systemin rounded megabits. For precise number, please, use option -d

[getlogginglevels](getlogginglevels.html) - Get the runtime logging levels

[getmaxhintwindow](getmaxhintwindow.html) - Print the max hint window in ms

[getseeds](getseeds.html) - Get the currently in use seed node IP list excluding the node IP

[getsnapshotthrottle](getsnapshotthrottle.html) - Print the snapshot\_links\_per\_second throttle for snapshot/clearsnapshot

[getsstables](getsstables.html) - Print the sstable filenames that own the key

[getstreamthroughput](getstreamthroughput.html) - Print the throughput cap for streaming and entire SSTable streaming in the system in rounded megabits. For precise number, please, use option -d

[gettimeout](gettimeout.html) - Print the timeout of the given type in ms

[gettraceprobability](gettraceprobability.html) - Print the current trace probability value

[gossipinfo](gossipinfo.html) - Shows the gossip information for the cluster

[help](help.html) - Display help information

[import](import.html) - Import new SSTables to the system

[info](info.html) - Print node information (uptime, load, …​)

[invalidatecidrpermissionscache](invalidatecidrpermissionscache.html) - Invalidate the cidr permissions cache

[invalidatecountercache](invalidatecountercache.html) - Invalidate the counter cache

[invalidatecredentialscache](invalidatecredentialscache.html) - Invalidate the credentials cache

[invalidatejmxpermissionscache](invalidatejmxpermissionscache.html) - Invalidate the JMX permissions cache

[invalidatekeycache](invalidatekeycache.html) - Invalidate the key cache

[invalidatenetworkpermissionscache](invalidatenetworkpermissionscache.html) - Invalidate the network permissions cache

[invalidatepermissionscache](invalidatepermissionscache.html) - Invalidate the permissions cache

[invalidaterolescache](invalidaterolescache.html) - Invalidate the roles cache

[invalidaterowcache](invalidaterowcache.html) - Invalidate the row cache

[join](join.html) - Join the ring

[listcidrgroups](listcidrgroups.html) - List existing cidr groups

[listpendinghints](listpendinghints.html) - Print all pending hints that this node has

[listsnapshots](listsnapshots.html) - Lists all the snapshots along with the size on disk and true size. True size is the total size of all SSTables which are not backed up to disk. Size on disk is total size of the snapshot on disk. Total TrueDiskSpaceUsed does not make any SSTable deduplication.

[move](move.html) - Move node on the token ring to a new token

[netstats](netstats.html) - Print network information on provided host (connecting node by default)

[pausehandoff](pausehandoff.html) - Pause hints delivery process

[profileload](profileload.html) - Low footprint profiling of activity for a period of time

[proxyhistograms](proxyhistograms.html) - Print statistic histograms for network operations

[rangekeysample](rangekeysample.html) - Shows the sampled keys held across all keyspaces

[rebuild](rebuild.html) - Rebuild data by streaming from other nodes (similarly to bootstrap)

[rebuild\_index](rebuild_index.html) - A full rebuild of native secondary indexes for a given table

[recompress\_sstables](recompress_sstables.html) - Rewrite sstables (for the requested tables) that have compression configuration different from the current

[refresh](refresh.html) - Load newly placed SSTables to the system without restart

[refreshsizeestimates](refreshsizeestimates.html) - Refresh system.size\_estimates

[reloadcidrgroupscache](reloadcidrgroupscache.html) - Reload CIDR groups cache with latest entries in cidr\_groups table, when CIDR authorizer is enabled

[reloadlocalschema](reloadlocalschema.html) - Reload local node schema from system tables

[reloadseeds](reloadseeds.html) - Reload the seed node list from the seed node provider

[reloadssl](reloadssl.html) - Signals Cassandra to reload SSL certificates

[reloadtriggers](reloadtriggers.html) - Reload trigger classes

[relocatesstables](relocatesstables.html) - Relocates sstables to the correct disk

[removenode](removenode.html) - Show status of current node removal, force completion of pending removal or remove provided ID

[repair](repair.html) - Repair one or more tables

[repair\_admin](repair_admin.html) -
[list](#cassandra:managing/tools/nodetool/list.adoc) - and fail incremental repair sessions

[replaybatchlog](replaybatchlog.html) - Kick off batchlog replay and wait for finish

[resetfullquerylog](resetfullquerylog.html) - Stop the full query log and clean files in the configured full query log directory from cassandra.yaml as well as JMX

[resetlocalschema](resetlocalschema.html) - Reset node’s local schema and resync

[resumehandoff](resumehandoff.html) - Resume hints delivery process

[ring](ring.html) - Print information about the token ring

[scrub](scrub.html) - Scrub (rebuild sstables for) one or more tables

[setauthcacheconfig](setauthcacheconfig.html) - Set configuration for Auth cache

[setautorepairconfig](setautorepairconfig.html) -
[sets](#cassandra:managing/tools/nodetool/sets.adoc) - the autorepair configuration

[setbatchlogreplaythrottle](setbatchlogreplaythrottle.html) - Set batchlog replay throttle in KB per second, or 0 to disable throttling. This will be reduced proportionally to the number of nodes in the cluster.

[setcachecapacity](setcachecapacity.html) - Set global key, row, and counter cache capacities (in MB units)

[setcachekeystosave](setcachekeystosave.html) - Set number of keys saved by each cache for faster post-restart warmup. 0 to disable

[setcolumnindexsize](setcolumnindexsize.html) - Set the granularity of the collation index of rows within a partition in KiB

[setcompactionthreshold](setcompactionthreshold.html) - Set min and max compaction thresholds for a given table

[setcompactionthroughput](setcompactionthroughput.html) - Set the MiB/s throughput cap for compaction in the system, or 0 to disable throttling

[setconcurrency](setconcurrency.html) - Set maximum concurrency for processing stage

[setconcurrentcompactors](setconcurrentcompactors.html) - Set number of concurrent compactors in the system.

[setconcurrentviewbuilders](setconcurrentviewbuilders.html) - Set the number of concurrent view builders in the system

[setdefaultrf](setdefaultrf.html) - Sets default keyspace replication factor.

[setguardrailsconfig](setguardrailsconfig.html) - Modify runtime configuration of guardrails.

[sethintedhandoffthrottlekb](sethintedhandoffthrottlekb.html) - Set hinted handoff throttle in KiB per second, per delivery thread.

[setinterdcstreamthroughput](setinterdcstreamthroughput.html) - Set the throughput cap for inter-datacenter streaming and entire SSTable inter-datacenter streaming in the system, or 0 to disable throttling

[setlogginglevel](setlogginglevel.html) - Set the log level threshold for a given component or class. Will reset to the initial configuration if called with no parameters.

[setmaxhintwindow](setmaxhintwindow.html) - Set the specified max hint window in ms

[setsnapshotthrottle](setsnapshotthrottle.html) - Set the snapshot\_links\_per\_second cap for snapshot and clearsnapshot throttling

[setstreamthroughput](setstreamthroughput.html) - Set throughput cap for streaming and entire SSTable streaming in the system, or 0 to disable throttling

[settimeout](settimeout.html) - Set the specified timeout in ms, or 0 to disable timeout

[settraceprobability](settraceprobability.html) - Sets the probability for tracing any given request to value. 0 disables, 1 enables for all requests, 0 is the default

[sjk](sjk.html) - Run commands of 'Swiss Java Knife'. Run 'nodetool sjk --help' for more information.

[snapshot](snapshot.html) - Take a snapshot of specified keyspaces or a snapshot of the specified table

[sstablerepairedset](sstablerepairedset.html) - Set the repaired state of SSTables for given keyspace/tables

[status](status.html) - Print cluster information (state, load, IDs, …​)

[statusautocompaction](statusautocompaction.html) -
[status](status.html) - of autocompaction of the given keyspace and table

[statusbackup](statusbackup.html) - Status of incremental backup

[statusbinary](statusbinary.html) - Status of native transport (binary protocol)

[statusgossip](statusgossip.html) - Status of gossip

[statushandoff](statushandoff.html) - Status of storing future hints on the current node

[stop](stop.html) - Stop compaction

[stopdaemon](stopdaemon.html) - Stop cassandra daemon

[tablehistograms](tablehistograms.html) - Print statistic histograms for a given table

[tablestats](tablestats.html) - Print statistics on tables

[toppartitions](toppartitions.html) - Sample and print the most active partitions

[tpstats](tpstats.html) - Print usage statistics of thread pools

[truncatehints](truncatehints.html) - Truncate all hints on the local node, or truncate hints for the endpoint(s) specified.

[updatecidrgroup](updatecidrgroup.html) - Insert/Update a cidr group

[upgradesstables](upgradesstables.html) - Rewrite sstables (for the requested tables) that are not on the current version (thus upgrading them to said current version)

[verify](verify.html) - Verify (check data checksum for) one or more tables

[version](version.html) - Print cassandra version

[viewbuildstatus](viewbuildstatus.html) - Show progress of a materialized view build

See 'nodetool help <command>' for more information on a specific command.
