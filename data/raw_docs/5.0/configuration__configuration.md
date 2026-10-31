---
title: "Liberating cassandra.yaml Parameters' Names from Their Units"
source_url: https://cassandra.apache.org/doc/5.0/cassandra/managing/configuration/configuration.html
cassandra_version: "5.0"
section: configuration
retrieved: 2026-10-31
---

> Source: Apache Cassandra documentation, version 5.0, https://cassandra.apache.org/doc/5.0/cassandra/managing/configuration/configuration.html. Licensed under the Apache License 2.0.

# Liberating cassandra.yaml Parameters' Names from Their Units

## Objective

Three big things happened as part of [CASSANDRA-15234](https://issues.apache.org/jira/browse/CASSANDRA-15234):

1) Renaming of parameters in `cassandra.yaml` to follow the form `noun_verb`.

2) Liberating `cassandra.yaml` parameters from their units (DataStorage, DataRate and Duration) and introducing temporary smallest accepted unit per parameter (only for DataStorage and Duration ones)

3) Backward compatibility framework to support the old names and lack of units support until at least the next major release.

## Renamed Parameters

The community has decided to allow operators to specify units for Cassandra parameters of types duration, data storage, and data rate.
All parameters which had a particular unit (most of the time added as a suffix to their name) can be now set by using the format [value][unit]. The unit suffix has been removed from their names.
Supported units:

| Parameter Type | Units Supported |
| --- | --- |
| Duration | d, h, m, s, ms, us, Âµs, ns |
| Data Storage | B, KiB, MiB, GiB |
| Data Rate | B/s, MiB/s, KiB/s |

**Example**:

Old name and value format:

```
permissions_update_interval_ms: 0
```

New name and possible value formats:

```
permissions_update_interval: 0ms
permissions_update_interval: 0s
permissions_update_interval: 0d
permissions_update_interval: 0us
permissions_update_interval: 0Âµs
```

The work in [CASSANDRA-15234](https://issues.apache.org/jira/browse/CASSANDRA-15234) was already quite big, so we decided
to introduce the notion of the smallest allowed unit per parameter for duration and data storage parameters. What does this mean?
Cassandra’s internals still use the old units for parameters. If, for example, seconds are used internally, but you want
to add a value in nanoseconds in `cassandra.yaml`, you will get a configuration exception that contains the following information:

```
Accepted units: seconds, minutes, hours, days.
```

Why was this needed?
Because we can run into precision issues. The full solution to the problem is to convert internally all parametersâ values
to be manipulated with the smallest supported by Cassandra unit. A series of tickets to assess and maybe migrate to the smallest unit
our parameters (incrementally, post [CASSANDRA-15234](https://issues.apache.org/jira/browse/CASSANDRA-15234)) will be opened in the future.

| Old Name | New Name | The Smallest Supported Unit |
| --- | --- | --- |
| permissions\_validity\_in\_ms | permissions\_validity | ms |
| permissions\_update\_interval\_in\_ms | permissions\_update\_interval | ms |
| roles\_validity\_in\_ms | roles\_validity | ms |
| roles\_update\_interval\_in\_ms | roles\_update\_interval | ms |
| credentials\_validity\_in\_ms | credentials\_validity | ms |
| credentials\_update\_interval\_in\_ms | credentials\_update\_interval | ms |
| max\_hint\_window\_in\_ms | max\_hint\_window | ms |
| native\_transport\_idle\_timeout\_in\_ms | native\_transport\_idle\_timeout | ms |
| request\_timeout\_in\_ms | request\_timeout | ms |
| read\_request\_timeout\_in\_ms | read\_request\_timeout | ms |
| range\_request\_timeout\_in\_ms | range\_request\_timeout | ms |
| write\_request\_timeout\_in\_ms | write\_request\_timeout | ms |
| counter\_write\_request\_timeout\_in\_ms | counter\_write\_request\_timeout | ms |
| cas\_contention\_timeout\_in\_ms | cas\_contention\_timeout | ms |
| truncate\_request\_timeout\_in\_ms | truncate\_request\_timeout | ms |
| streaming\_keep\_alive\_period\_in\_secs | streaming\_keep\_alive\_period | s |
| cross\_node\_timeout | internode\_timeout | - |
| slow\_query\_log\_timeout\_in\_ms | slow\_query\_log\_timeout | ms |
| memtable\_heap\_space\_in\_mb | memtable\_heap\_space | MiB |
| memtable\_offheap\_space\_in\_mb | memtable\_offheap\_space | MiB |
| repair\_session\_space\_in\_mb | repair\_session\_space | MiB |
| internode\_max\_message\_size\_in\_bytes | internode\_max\_message\_size | B |
| internode\_send\_buff\_size\_in\_bytes | internode\_socket\_send\_buffer\_size | B |
| internode\_socket\_send\_buffer\_size\_in\_bytes | internode\_socket\_send\_buffer\_size | B |
| internode\_socket\_receive\_buffer\_size\_in\_bytes | internode\_socket\_receive\_buffer\_size | B |
| internode\_recv\_buff\_size\_in\_bytes | internode\_socket\_receive\_buffer\_size | B |
| internode\_application\_send\_queue\_capacity\_in\_bytes | internode\_application\_send\_queue\_capacity | B |
| internode\_application\_send\_queue\_reserve\_endpoint\_capacity\_in\_bytes | internode\_application\_send\_queue\_reserve\_endpoint\_capacity | B |
| internode\_application\_send\_queue\_reserve\_global\_capacity\_in\_bytes | internode\_application\_send\_queue\_reserve\_global\_capacity | B |
| internode\_application\_receive\_queue\_capacity\_in\_bytes | internode\_application\_receive\_queue\_capacity | B |
| internode\_application\_receive\_queue\_reserve\_endpoint\_capacity\_in\_bytes | internode\_application\_receive\_queue\_reserve\_endpoint\_capacity | B |
| internode\_application\_receive\_queue\_reserve\_global\_capacity\_in\_bytes | internode\_application\_receive\_queue\_reserve\_global\_capacity | B |
| internode\_tcp\_connect\_timeout\_in\_ms | internode\_tcp\_connect\_timeout | ms |
| internode\_tcp\_user\_timeout\_in\_ms | internode\_tcp\_user\_timeout | ms |
| internode\_streaming\_tcp\_user\_timeout\_in\_ms | internode\_streaming\_tcp\_user\_timeout | ms |
| native\_transport\_max\_frame\_size\_in\_mb | native\_transport\_max\_frame\_size | MiB |
| max\_value\_size\_in\_mb | max\_value\_size | MiB |
| column\_index\_size\_in\_kb | column\_index\_size | KiB |
| column\_index\_cache\_size\_in\_kb | column\_index\_cache\_size | KiB |
| batch\_size\_warn\_threshold\_in\_kb | batch\_size\_warn\_threshold | KiB |
| batch\_size\_fail\_threshold\_in\_kb | batch\_size\_fail\_threshold | KiB |
| compaction\_throughput\_mb\_per\_sec | compaction\_throughput | MiB/s |
| compaction\_large\_partition\_warning\_threshold\_mb | compaction\_large\_partition\_warning\_threshold | MiB |
| min\_free\_space\_per\_drive\_in\_mb | min\_free\_space\_per\_drive | MiB |
| stream\_throughput\_outbound\_megabits\_per\_sec | stream\_throughput\_outbound | MiB/s |
| inter\_dc\_stream\_throughput\_outbound\_megabits\_per\_sec | inter\_dc\_stream\_throughput\_outbound | MiB/s |
| commitlog\_total\_space\_in\_mb | commitlog\_total\_space | MiB |
| commitlog\_sync\_group\_window\_in\_ms | commitlog\_sync\_group\_window | ms |
| commitlog\_sync\_period\_in\_ms | commitlog\_sync\_period | ms |
| commitlog\_segment\_size\_in\_mb | commitlog\_segment\_size | MiB |
| periodic\_commitlog\_sync\_lag\_block\_in\_ms | periodic\_commitlog\_sync\_lag\_block | ms |
| max\_mutation\_size\_in\_kb | max\_mutation\_size | KiB |
| cdc\_total\_space\_in\_mb | cdc\_total\_space | MiB |
| cdc\_free\_space\_check\_interval\_ms | cdc\_free\_space\_check\_interval | ms |
| dynamic\_snitch\_update\_interval\_in\_ms | dynamic\_snitch\_update\_interval | ms |
| dynamic\_snitch\_reset\_interval\_in\_ms | dynamic\_snitch\_reset\_interval | ms |
| hinted\_handoff\_throttle\_in\_kb | hinted\_handoff\_throttle | KiB |
| batchlog\_replay\_throttle\_in\_kb | batchlog\_replay\_throttle | KiB |
| hints\_flush\_period\_in\_ms | hints\_flush\_period | ms |
| max\_hints\_file\_size\_in\_mb | max\_hints\_file\_size | MiB |
| trickle\_fsync\_interval\_in\_kb | trickle\_fsync\_interval | KiB |
| sstable\_preemptive\_open\_interval\_in\_mb | sstable\_preemptive\_open\_interval | MiB |
| key\_cache\_size\_in\_mb | key\_cache\_size | MiB |
| row\_cache\_size\_in\_mb | row\_cache\_size | MiB |
| counter\_cache\_size\_in\_mb | counter\_cache\_size | MiB |
| networking\_cache\_size\_in\_mb | networking\_cache\_size | MiB |
| file\_cache\_size\_in\_mb | file\_cache\_size | MiB |
| index\_summary\_capacity\_in\_mb | index\_summary\_capacity | MiB |
| index\_summary\_resize\_interval\_in\_minutes | index\_summary\_resize\_interval | m |
| gc\_log\_threshold\_in\_ms | gc\_log\_threshold | ms |
| gc\_warn\_threshold\_in\_ms | gc\_warn\_threshold | ms |
| tracetype\_query\_ttl | trace\_type\_query\_ttl | s |
| tracetype\_repair\_ttl | trace\_type\_repair\_ttl | s |
| prepared\_statements\_cache\_size\_mb | prepared\_statements\_cache\_size | MiB |
| enable\_user\_defined\_functions | user\_defined\_functions\_enabled | - |
| enable\_scripted\_user\_defined\_functions | scripted\_user\_defined\_functions\_enabled | - |
| enable\_materialized\_views | materialized\_views\_enabled | - |
| enable\_transient\_replication | transient\_replication\_enabled | - |
| enable\_sasi\_indexes | sasi\_indexes\_enabled | - |
| enable\_drop\_compact\_storage | drop\_compact\_storage\_enabled | - |
| enable\_user\_defined\_functions\_threads | user\_defined\_functions\_threads\_enabled | - |
| enable\_legacy\_ssl\_storage\_port | legacy\_ssl\_storage\_port\_enabled | - |
| user\_defined\_function\_fail\_timeout | user\_defined\_functions\_fail\_timeout | ms |
| user\_defined\_function\_warn\_timeout | user\_defined\_functions\_warn\_timeout | ms |
| cache\_load\_timeout\_seconds | cache\_load\_timeout | s |

Another TO DO is to add JMX methods supporting the new format. However, we may abandon this if virtual tables support
configuration changes in the near future.

**Notes for Cassandra Developers**:

* Most of our parameters are already moved to the new framework as part of [CASSANDRA-15234](https://issues.apache.org/jira/browse/CASSANDRA-15234).
  `@Replaces` is the annotation to be used when you make changes to any configuration parameters in `Config` class and `cassandra.yaml`, and you want to add backward
  compatibility with previous Cassandra versions. `Converters` class enumerates the different methods used for backward compatibility.
  `IDENTITY` is the one used for name change only. For more information about the other Converters, please, check the JavaDoc in the class.
  For backward compatibility virtual table `Settings` contains both the old and the new
  parameters with the old and the new value format. Only exception at the moment are the following three parameters: `key_cache_save_period`,
  `row_cache_save_period` and `counter_cache_save_period` which appear only once with the new value format.
  The old names and value format still can be used at least until the next major release. Deprecation warning is emitted on startup.
  If the parameter is of type duration, data rate or data storage, its value should be accompanied by a unit when new name is used.
* Please follow the new format `noun_verb` when adding new configuration parameters.
* Please consider adding any new parameters with the lowest supported by Cassandra unit when possible. Our new types also
  support long and integer upper bound, depending on your needs. All options for configuration parameters' types are nested
  classes in our three main abstract classes - `DurationSpec`, `DataStorageSpec`, `DataRateSpec`.
* If for some reason you consider the smallest unit for a new parameter shouldnât be the one that is supported as such in
  Cassandra, you can use the rest of the nested classes in `DurationSpec`, `DataStorageSpec`. The smallest allowed unit is
  the one we use internally for the property, so we don’t have to do conversions to bigger units which will lead to precision
  problems. This is a problem only with `DurationSpec` and `DataStorageSpec`. `DataRateSpec` is handled internally in double.
* New parameters should be added as non-negative numbers. For parameters where you would have set -1 to disable in the past, you might
  want to consider a separate flag parameter or null value. In case you use the null value, please, ensure that any default value
  introduced in the DatabaseDescriptor to handle it is also duplicated in any related setters.
* Parameters of type data storage, duration and data rate cannot be set to Long.MAX\_VALUE (former parameters of long type)
  and Integer.MAX\_VALUE (former parameters of int type). That numbers are used during conversion between units to prevent
  an overflow from happening.
* Any time you add @Replaces with a name change, we need to add an entry in this [Python dictionary in CCM](https://github.com/riptano/ccm/blob/808b6ca13526785b0fddfe1ead2383c060c4b8b6/ccmlib/common.py#L62) to support the same backward compatibility as SnakeYAML.

Please follow the instructions in requirements.txt in the DTest repo how to retag CCM after committing any changes.
You might want to test also with tagging in your repo to ensure that there will be no surprise after retagging the official CCM.
Please be sure to run a full CI after any changes as CCM affects a few of our testing suites.

* Some configuration parameters are not announced in cassandra.yaml, but they are presented in the Config class for advanced users.
  Those also should be using the new framework and naming conventions.
* As we have backward compatibility, we didnât have to rework all python DTests to set config in the new format, and we exercise
  the backward compatibility while testing. Please consider adding any new tests using the new names and value format though.
* In-JVM upgrade tests do not support per-version configuration at the moment, so we have to keep the old names and value format.
  Currently, if we try to use the new config for a newer version, that will be silently ignored and default config will be used.
* SnakeYAML supports overloading of parameters. This means that if you add a configuration parameter more than once in your `cassandra.yaml` -
  the latest occasion will be the one to load in Config during Cassandra startup. In order to make upgrades as less disruptive as possible,
  we continue supporting that behavior also with adding old and new names of a parameter into `cassandra.yaml`.
* Please ensure that any JMX setters/getters update the Config class properties and not some local copies. Settings Virtual Table
  reports the configuration loaded at any time from the Config class.

**Example**:

If you add the following to `cassandra.yaml`:

```
hinted_handoff_enabled: true
enabled_hinted_handolff: false
```

you will get loaded in `Config`:

```
hinted_handoff_enabled: false
```

[CASSANDRA-17379](https://issues.apache.org/jira/browse/CASSANDRA-17379) was opened to improve the user experience and deprecate the overloading.
By default, we refuse starting Cassandra with a config containing both old and new config keys for the same parameter. Start
Cassandra with `-Dcassandra.allow_new_old_config_keys=true` to override. For historical reasons duplicate config keys
in `cassandra.yaml` are allowed by default, start Cassandra with `-Dcassandra.allow_duplicate_config_keys=false` to disallow this.
Please note that `key_cache_save_period`, `row_cache_save_period`, `counter_cache_save_period` will be affected only by `-Dcassandra.allow_duplicate_config_keys`.
