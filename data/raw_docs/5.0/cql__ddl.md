---
title: "Data Definition"
source_url: https://cassandra.apache.org/doc/5.0/cassandra/developing/cql/ddl.html
cassandra_version: "5.0"
section: cql
retrieved: 2026-10-31
---

> Source: Apache Cassandra documentation, version 5.0, https://cassandra.apache.org/doc/5.0/cassandra/developing/cql/ddl.html. Licensed under the Apache License 2.0.

# Data Definition

CQL stores data in *tables*, whose schema defines the layout of the
data in the table. Tables are located in *keyspaces*.
A keyspace defines options that apply to all the keyspace’s tables.
The [replication strategy](#replication-strategy)
is an important keyspace option, as is the replication factor.
A good general rule is one keyspace per application.
It is common for a cluster to define only one keyspace for an active application.

This section describes the statements used to create, modify, and remove
those keyspace and tables.

## Common definitions

The names of the keyspaces and tables are defined by the following
grammar:

```
keyspace_name::= name
table_name::= [keyspace_name '.' ] name
name::= unquoted_name | quoted_name
unquoted_name::= re('[a-zA-Z_0-9]\{1, 48}')
quoted_name::= '"' unquoted_name '"'
```

Both keyspace and table name should be comprised of only alphanumeric
or underscore characters and cannot be empty.
Keyspace name is limited in size to 48 characters, while
table name is limited in size to 222 characters
(those limits exist mostly to avoid filenames (which may include the
keyspace and table name) to go over the limits of certain file systems).
By default, keyspace and table names are case-insensitive (`myTable` is
equivalent to `mytable`) but case sensitivity can be forced by using
double-quotes (`"myTable"` is different from `mytable`).

Further, a table is always part of a keyspace and a table name can be
provided fully-qualified by the keyspace it is part of. If is is not
fully-qualified, the table is assumed to be in the *current* keyspace
(see [USE](#use-statement) statement).

Further, the valid names for columns are defined as:

```
column_name::= identifier
```

We also define the notion of statement options for use in the following
section:

```
options::= option ( AND option )*
option::= identifier '=' ( identifier
	| constant
	| map_literal )
```

## CREATE KEYSPACE

A keyspace is created with a `CREATE KEYSPACE` statement:

```
create_keyspace_statement::= CREATE KEYSPACE [ IF NOT EXISTS ] keyspace_name
	WITH options
```

For example:

```
CREATE KEYSPACE excelsior
   WITH replication = {'class': 'SimpleStrategy', 'replication_factor' : 3};

CREATE KEYSPACE excalibur
   WITH replication = {'class': 'NetworkTopologyStrategy', 'DC1' : 1, 'DC2' : 3}
   AND durable_writes = false;
```

Attempting to create a keyspace that already exists will return an error
unless the `IF NOT EXISTS` option is used. If it is used, the statement
will be a no-op if the keyspace already exists.

The supported `options` are:

| name | kind | mandatory | default | description |
| --- | --- | --- | --- | --- |
| `replication` | *map* | yes | n/a | The replication strategy and options to use for the keyspace (see details below). |
| `durable_writes` | *simple* | no | true | Whether to use the commit log for updates on this keyspace (disable this option at your own risk!). |

The `replication` property is mandatory and must contain the `'class'` sub-option that defines the desired
[replication strategy](#replication-strategy) class.
The rest of the sub-options depend on which replication strategy is used.
By default, Cassandra supports the following `'class'` values:

### `SimpleStrategy`

A simple strategy that defines a replication factor for data to be
spread across the entire cluster. This is generally not a wise choice
for production, as it does not respect datacenter layouts and can
lead to wildly varying query latency. For production, use
`NetworkTopologyStrategy`. `SimpleStrategy` supports a single
mandatory argument:

| sub-option | type | since | description |
| --- | --- | --- | --- |
| `'replication_factor'` | int | all | The number of replicas to store per range |

### `NetworkTopologyStrategy`

A production-ready replication strategy that sets the
replication factor independently for each data-center. The rest of the
sub-options are key-value pairs, with a key set to a data-center name and
its value set to the associated replication factor. Options:

| sub-option | type | description | `'<datacenter>'` |
| --- | --- | --- | --- |
| int | The number of replicas to store per range in the provided datacenter. | `'replication_factor'` | int |

When later altering keyspaces and changing the `replication_factor`,
auto-expansion will only *add* new datacenters for safety, it will not
alter existing datacenters or remove any, even if they are no longer in
the cluster. If you want to remove datacenters while setting the
`replication_factor`, explicitly zero out the datacenter you want to
have zero replicas.

An example of auto-expanding datacenters with two datacenters: `DC1` and
`DC2`:

```
CREATE KEYSPACE excalibur
    WITH replication = {'class': 'NetworkTopologyStrategy', 'replication_factor' : 3};

DESCRIBE KEYSPACE excalibur;
```

will result in:

```
CREATE KEYSPACE excalibur WITH replication = {'class': 'NetworkTopologyStrategy', 'DC1': '3', 'DC2': '3'} AND durable_writes = true;
```

An example of auto-expanding and overriding a datacenter:

```
CREATE KEYSPACE excalibur
   WITH replication = {'class': 'NetworkTopologyStrategy', 'replication_factor' : 3, 'DC2': 2};

DESCRIBE KEYSPACE excalibur;
```

will result in:

```
CREATE KEYSPACE excalibur WITH replication = {'class': 'NetworkTopologyStrategy', 'DC1': '3', 'DC2': '2'} AND durable_writes = true;
```

An example that excludes a datacenter while using `replication_factor`:

```
CREATE KEYSPACE excalibur
   WITH replication = {'class': 'NetworkTopologyStrategy', 'replication_factor' : 3, 'DC2': 0};

DESCRIBE KEYSPACE excalibur;
```

will result in:

```
CREATE KEYSPACE excalibur WITH replication = {'class': 'NetworkTopologyStrategy', 'DC1': '3'} AND durable_writes = true;
```

If [transient replication](../../managing/operating/transientreplication.html) has been enabled, transient replicas can be
configured for both `SimpleStrategy` and `NetworkTopologyStrategy` by
defining replication factors in the format
`'<total_replicas>/<transient_replicas>'`

For instance, this keyspace will have 3 replicas in DC1, 1 of which is
transient, and 5 replicas in DC2, 2 of which are transient:

```
CREATE KEYSPACE some_keyspace
   WITH replication = {'class': 'NetworkTopologyStrategy', 'DC1' : '3/1', 'DC2' : '5/2'};
```

## USE

The `USE` statement changes the *current* keyspace to the specified keyspace.
A number of objects in CQL are bound to a keyspace (tables, user-defined types, functions, etc.) and the
current keyspace is the default keyspace used when those objects are
referred to in a query without a fully-qualified name (without a prefixed keyspace name).
A `USE` statement specifies the keyspace to use as an argument:

```
use_statement::= USE keyspace_name
```

Using CQL:

```
USE excelsior;
```

## ALTER KEYSPACE

An `ALTER KEYSPACE` statement modifies the options of a keyspace:

```
alter_keyspace_statement::= ALTER KEYSPACE [ IF EXISTS ] keyspace_name
	WITH options
```

For example:

```
ALTER KEYSPACE excelsior
    WITH replication = {'class': 'SimpleStrategy', 'replication_factor' : 4};
```

If the keyspace does not exist, the statement will return an error, unless `IF EXISTS` is used in which case the operation is a no-op.
The supported options are the same as for [creating a keyspace](#create-keyspace-statement).

## DROP KEYSPACE

Dropping a keyspace is done with the `DROP KEYSPACE` statement:

```
drop_keyspace_statement::= DROP KEYSPACE [ IF EXISTS ] keyspace_name
```

For example:

```
DROP KEYSPACE excelsior;
```

Dropping a keyspace results in the immediate, irreversible removal of
that keyspace, including all the tables, user-defined types, user-defined functions, and
all the data contained in those tables.

If the keyspace does not exists, the statement will return an error,
unless `IF EXISTS` is used in which case the operation is a no-op.

## CREATE TABLE

Creating a new table uses the `CREATE TABLE` statement:

```
create_table_statement::= CREATE TABLE [ IF NOT EXISTS ] table_name '('
	column_definition  ( ',' column_definition )*
	[ ',' PRIMARY KEY '(' primary_key ')' ]
	 ')' [ WITH table_options ]
column_definition::= column_name cql_type [ STATIC ] [ column_mask ] [ PRIMARY KEY]
column_mask::= MASKED WITH ( DEFAULT | function_name '(' term ( ',' term )* ')' )
primary_key::= partition_key [ ',' clustering_columns ]
partition_key::= column_name  | '(' column_name ( ',' column_name )* ')'
clustering_columns::= column_name ( ',' column_name )*
table_options::= COMPACT STORAGE [ AND table_options ]
	| CLUSTERING ORDER BY '(' clustering_order ')'
	[ AND table_options ]  | options
clustering_order::= column_name (ASC | DESC) ( ',' column_name (ASC | DESC) )*
```

For example, here are some CQL statements to create tables:

```
CREATE TABLE monkey_species (
    species text PRIMARY KEY,
    common_name text,
    population varint,
    average_size int
) WITH comment='Important biological records';

CREATE TABLE timeline (
    userid uuid,
    posted_month int,
    posted_time uuid,
    body text,
    posted_by text,
    PRIMARY KEY (userid, posted_month, posted_time)
) WITH compaction = { 'class' : 'LeveledCompactionStrategy' };

CREATE TABLE loads (
    machine inet,
    cpu int,
    mtime timeuuid,
    load float,
    PRIMARY KEY ((machine, cpu), mtime)
) WITH CLUSTERING ORDER BY (mtime DESC);
```

A CQL table has a name and is composed of a set of *rows*.
Creating a table amounts to defining which [columns](#column-definition) each rows will have,
which of those columns comprise the [primary key](#primary-key), as well as defined
[options](#create-table-options) for the table.

Attempting to create an already existing table will return an error
unless the `IF NOT EXISTS` directive is used. If it is used, the
statement will be a no-op if the table already exists.

### Column definitions

Every row in a CQL table will have the predefined columns defined at table creation.
Columns can be added later using an [alter statement](#alter-table-statement).

A `column_definition` is comprised of the name of the column and its [type](#data-type),
restricting the values that are accepted for that column. Additionally, a column definition can have the
following modifiers:

* `STATIC`: declares the column as a [static column](#static-column)
* `PRIMARY KEY`: declares the column as the sole component of the [primary key](#primary-key) of the table

#### Static columns

Some columns can be declared as `STATIC` in a table definition. A column
that is static will be âsharedâ by all the rows belonging to the same
partition (having the same [partition key](#partition-key)).

For example:

* Code
* Results

```
CREATE TABLE t (
    pk int,
    t int,
    v text,
    s text static,
    PRIMARY KEY (pk, t)
);
INSERT INTO t (pk, t, v, s) VALUES (0, 0, 'val0', 'static0');
INSERT INTO t (pk, t, v, s) VALUES (0, 1, 'val1', 'static1');
SELECT * FROM t;
```

```
   pk | t | v      | s
  ----+---+--------+-----------
   0  | 0 | 'val0' | 'static1'
   0  | 1 | 'val1' | 'static1'
```

As can be seen, the `s` value is the same (`static1`) for both of the
rows in the partition (the partition key being `pk`, and both
rows are in the same partition): the second insertion overrides the
value for `s`.

The use of static columns has the following restrictions:

* A table without clustering columns cannot have static columns.
  In a table without clustering columns, every partition has only one row, and
  so every column is inherently static)
* Only non-primary key columns can be static.

### The Primary key

Within a table, a row is uniquely identified by its `PRIMARY KEY`, and
hence all tables **must** define a single PRIMARY KEY.
A `PRIMARY KEY` is composed of one or more of the defined columns in the table.
Syntactically, the primary key is defined with the phrase `PRIMARY KEY`
followed by a comma-separated list of the column names within parenthesis.
If the primary key has only one column, you can alternatively add the `PRIMARY KEY` phrase to
that column in the table definition.
The order of the columns in the primary key definition defines the partition key and
clustering columns.

A CQL primary key is composed of two parts:

[partition key](#partition-key)
:   * It is the first component of the primary key definition.
      It can be a single column or, using an additional set of parenthesis, can be multiple columns.
      A table must have at least one partition key, the smallest possible table definition is:

      ```
      CREATE TABLE t (k text PRIMARY KEY);
      ```

[clustering columns](#clustering-columns)
:   * The columns are the columns that follow the partition key in the primary key definition.
      The order of those columns define the *clustering order*.

Some examples of primary key definition are:

* `PRIMARY KEY (a)`: `a` is the single partition key and there are no clustering columns
* `PRIMARY KEY (a, b, c)` : `a` is the single partition key and `b` and `c` are the clustering columns
* `PRIMARY KEY ((a, b), c)` : `a` and `b` compose the *composite* partition key and `c` is the clustering column

|  |  |
| --- | --- |
|  | The primary key uniquely identifies a row in the table, as described above. A consequence of this uniqueness is that if another row is inserted using the same primary key, then an `UPSERT` occurs and an existing row with the same primary key is replaced. Columns that are not part of the primary key cannot define uniqueness. |

#### Partition key

Within a table, CQL defines the notion of a *partition* that defines the location of data within a Cassandra cluster.
A partition is the set of rows that share the same value for their partition key.

Note that if the partition key is composed of multiple columns, then rows belong to the same partition
when they have the same values for all those partition key columns.
A hash is computed from the partition key columns and that hash value defines the partition location.
So, for instance, given the following table definition and content:

```
CREATE TABLE t (
    a int,
    b int,
    c int,
    d int,
    PRIMARY KEY ((a, b), c, d)
);
INSERT INTO t (a, b, c, d) VALUES (0,0,0,0);
INSERT INTO t (a, b, c, d) VALUES (0,0,1,1);
INSERT INTO t (a, b, c, d) VALUES (0,1,2,2);
INSERT INTO t (a, b, c, d) VALUES (0,1,3,3);
INSERT INTO t (a, b, c, d) VALUES (1,1,4,4);
SELECT * FROM t;
```

will result in

```
 a | b | c | d
---+---+---+---
 0 | 0 | 0 | 0 	(1)
 0 | 0 | 1 | 1
 0 | 1 | 2 | 2	(2)
 0 | 1 | 3 | 3
 1 | 1 | 4 | 4  (3)

(5 rows)
```

|  |  |
| --- | --- |
| **1** | Rows 1 and 2 are in the same partition, because both columns `a` and `b` are zero. |
| **2** | Rows 3 and 4 are in the same partition, but a different one, because column `a` is zero and column `b` is 1 in both rows. |
| **3** | Row 5 is in a third partition by itself, because both columns `a` and `b` are 1. |

Note that a table always has a partition key, and that if the table has
no `clustering columns`, then every partition of that table has a single row.
because the partition key, compound or otherwise, identifies a single location.

The most important property of partition is that all the rows belonging
to the same partition are guaranteed to be stored on the same set of
replica nodes.
In other words, the partition key of a table defines which rows will be localized on the same
node in the cluster.
The localization of data is important to the efficient retrieval of data, requiring the Cassandra coordinator
to contact as few nodes as possible.
However, there is a flip-side to this guarantee, and all rows sharing a partition key will be stored on the same
node, creating a hotspot for both reading and writing.
While selecting a primary key that groups table rows assists batch updates and can ensure that the updates are
*atomic* and done in *isolation*, the partitions must be sized "just right, not too big nor too small".

Data modeling that considers the querying patterns and assigns primary keys based on the queries will have the lowest
latency in fetching data.

#### Clustering columns

The clustering columns of a table define the clustering order for the partition of that table.
For a given `partition`, all rows are ordered by that clustering order. Clustering columns also add uniqueness to
a row in a table.

For instance, given:

```
CREATE TABLE t2 (
    a int,
    b int,
    c int,
    d int,
    PRIMARY KEY (a, b, c)
);
INSERT INTO t2 (a, b, c, d) VALUES (0,0,0,0);
INSERT INTO t2 (a, b, c, d) VALUES (0,0,1,1);
INSERT INTO t2 (a, b, c, d) VALUES (0,1,2,2);
INSERT INTO t2 (a, b, c, d) VALUES (0,1,3,3);
INSERT INTO t2 (a, b, c, d) VALUES (1,1,4,4);
SELECT * FROM t2;
```

will result in

```
 a | b | c | d
---+---+---+---
 1 | 1 | 4 | 4	(1)
 0 | 0 | 0 | 0
 0 | 0 | 1 | 1
 0 | 1 | 2 | 2
 0 | 1 | 3 | 3

(5 rows)
```

|  |  |
| --- | --- |
| **1** | Row 1 is in one partition, and Rows 2-5 are in a different one. The display order is also different. |

Looking more closely at the four rows in the same partition, the `b` clustering column defines the order in which those rows
are displayed.
Whereas the partition key of the table groups rows on the same node, the clustering columns control
how those rows are stored on the node.

That sorting allows the very efficient retrieval of a range of rows within a partition:

```
SELECT * FROM t2 WHERE a = 0 AND b > 0 and b <= 3;
```

will result in

```
 a | b | c | d
---+---+---+---
 0 | 1 | 2 | 2
 0 | 1 | 3 | 3

(2 rows)
```

### Table options

A CQL table has a number of options that can be set at creation (and,
for most of them, altered later). These options are specified after the
`WITH` keyword.

One important option that cannot be changed after creation, `CLUSTERING ORDER BY`, influences how queries can be done against the table. It is worth discussing in more detail here.

#### Clustering order

The clustering order of a table is defined by the clustering columns.
By default, the clustering order is ascending for the clustering column’s data types.
For example, integers order from 1, 2, …​ n, while text orders from A to Z.

The `CLUSTERING ORDER BY` table option uses a comma-separated list of the
clustering columns, each set for either `ASC` (for *ascending* order) or `DESC` (for \_descending order).
The default is ascending for all clustering columns if the `CLUSTERING ORDER BY` option is not set.

This option is basically a hint for the storage engine that changes the order in which it stores the row.
Beware of the consequences of setting this option:

* It changes the default ascending order of results when queried with a `SELECT` statement with no `ORDER BY` clause.
* It limits how the `ORDER BY` clause is used in `SELECT` statements on that table.
  Results can only be ordered with either the original clustering order or the reverse clustering order.
  Suppose you create a table with two clustering columns `a` and `b`, defined `WITH CLUSTERING ORDER BY (a DESC, b ASC)`.
  Queries on the table can use `ORDER BY (a DESC, b ASC)` or `ORDER BY (a ASC, b DESC)`.
  Mixed order, such as `ORDER BY (a ASC, b ASC)` or `ORDER BY (a DESC, b DESC)` will not return expected order.
* It has a performance impact on queries. Queries in reverse clustering order are slower than the default ascending order.
  If you plan to query mostly in descending order, declare the clustering order in the table schema using `WITH CLUSTERING ORDER BY ()`.
  This optimization is common for time series, to retrieve the data from newest to oldest.

#### Other table options

A table supports the following options:

| option | kind | default | description |
| --- | --- | --- | --- |
| `comment` | *simple* | none | A free-form, human-readable comment |
| [`speculative_retry`](#spec_retry) | *simple* | 99PERCENTILE | Speculative retry options |
| `cdc` | *boolean* | false | Create a Change Data Capture (CDC) log on the table |
| `additional_write_policy` | *simple* | 99PERCENTILE | Same as `speculative_retry` |
| `gc_grace_seconds` | *simple* | 864000 | Time to wait before garbage collecting tombstones (deletion markers) |
| `bloom_filter_fp_chance` | *simple* | 0.00075 | The target probability of false positive of the sstable bloom filters. Said bloom filters will be sized to provide the provided probability, thus lowering this value impacts the size of bloom filters in-memory and on-disk. |
| `default_time_to_live` | *simple* | 0 | Default expiration time (âTTLâ) in seconds for a table |
| `compaction` | *map* | *see below* | [Compaction options](../../managing/operating/compaction/index.html#cql-compaction-options) |
| `compression` | *map* | *see below* | [Compression options](#cassandra:managing/operating/compression/index.adoc#cql-compression-options) |
| `caching` | *map* | *see below* | Caching options |
| `memtable_flush_period_in_ms` | *simple* | 0 | Time (in ms) before Cassandra flushes memtables to disk |
| `read_repair` | *simple* | BLOCKING | Sets read repair behavior (see below) |

##### Speculative retry options

By default, Cassandra read coordinators only query as many replicas as
necessary to satisfy consistency levels: one for consistency level
`ONE`, a quorum for `QUORUM`, and so on. `speculative_retry` determines
when coordinators may query additional replicas, a useful action when
replicas are slow or unresponsive. Speculative retries reduce the latency.
The speculative\_retry option configures rapid read protection, where a coordinator sends more
requests than needed to satisfy the consistency level.

|  |  |
| --- | --- |
|  | Frequently reading from additional replicas can hurt cluster performance. When in doubt, keep the default `99PERCENTILE`. |

Pre-Cassandra 4.0 speculative retry policy takes a single string as a parameter:

* `NONE`
* `ALWAYS`
* `99PERCENTILE` (PERCENTILE)
* `50MS` (CUSTOM)

An example of setting speculative retry sets a custom value:

```
ALTER TABLE users WITH speculative_retry = '10ms';
```

This example uses a percentile for the setting:

```
ALTER TABLE users WITH speculative_retry = '99PERCENTILE';
```

A percentile setting can backfire. If a single host becomes unavailable, it can
force up the percentiles. A value of `p99` will not speculate as intended because the
value at the specified percentile has increased too much. If the consistency level is set to `ALL`, all
replicas are queried regardless of the speculative retry setting.

Cassandra 4.0 supports case-insensitivity for speculative retry values ([CASSANDRA-14293](https://issues.apache.org/jira/browse/CASSANDRA-14293)). For example, assigning the value as `none`, `None`, or `NONE` has the same effect.

Additionally, the following values are added:

| Format | Example | Description |
| --- | --- | --- |
| `XPERCENTILE` | 90.5PERCENTILE | Coordinators record average per-table response times for all replicas. If a replica takes longer than `X` percent of this table’s average response time, the coordinator queries an additional replica. `X` must be between 0 and 100. |
| `XP` | 90.5P | Same as `XPERCENTILE` |
| `Yms` | 25ms | If a replica takes more than `Y` milliseconds to respond, the coordinator queries an additional replica. |
| `MIN(XPERCENTILE,YMS)` | MIN(99PERCENTILE,35MS) | A hybrid policy that uses either the specified percentile or fixed milliseconds depending on which value is lower at the time of calculation. Parameters are `XPERCENTILE`, `XP`, or `Yms`. This setting helps protect against a single slow instance. |
| `MAX(XPERCENTILE,YMS)` `ALWAYS` `NEVER` | MAX(90.5P,25ms) | A hybrid policy that uses either the specified percentile or fixed milliseconds depending on which value is higher at the time of calculation. |

Cassandra 4.0 adds support for hybrid `MIN()` and `MAX()` speculative retry policies, with a mix and match of either `MIN(), MAX()`, `MIN(), MIN()`, or `MAX(), MAX()` ([CASSANDRA-14293](https://issues.apache.org/jira/browse/CASSANDRA-14293)).
The hybrid mode will still speculate if the normal `p99` for the table is < 50ms, the minimum value.
But if the `p99` level goes higher than the maximum value, then that value can be used.
In a hybrid value, one value must be a fixed time (ms) value and the other a percentile value.

To illustrate variations, the following examples are all valid:

```
min(99percentile,50ms)
max(99p,50MS)
MAX(99P,50ms)
MIN(99.9PERCENTILE,50ms)
max(90percentile,100MS)
MAX(100.0PERCENTILE,60ms)
```

The `additional_write_policy` setting specifies the threshold at which a cheap
quorum write will be upgraded to include transient replicas.

##### Compaction options

The `compaction` options must minimally define the `'class'` sub-option,
to specify the compaction strategy class to use.
The supported classes are:

* `'SizeTieredCompactionStrategy'`, [STCS](../../managing/operating/compaction/stcs.html#stcs) (Default)
* `'LeveledCompactionStrategy'`, [LCS](../../managing/operating/compaction/lcs.html#lcs)
* `'TimeWindowCompactionStrategy'`, [TWCS](../../managing/operating/compaction/twcs.html#twcs)

If a custom strategies is required, specify the full class name as a [string constant](definitions.html#constants).

All default strategies support a number of [common options](../../managing/operating/compaction/index.html#compaction-options), as well as options specific to the strategy chosen. See the section corresponding to your strategy for details: [STCS](../../managing/operating/compaction/stcs.html#stcs_options), [LCS](../../managing/operating/compaction/lcs.html#lcs_options), [TWCS](../../managing/operating/compaction/twcs.html#twcs_options).

##### Compression options

The `compression` options define if and how the SSTables of the table
are compressed. Compression is configured on a per-table basis as an
optional argument to `CREATE TABLE` or `ALTER TABLE`. The following
sub-options are available:

| Option | Default | Description |
| --- | --- | --- |
| `class` | LZ4Compressor | The compression algorithm to use. Default compressor are: LZ4Compressor, SnappyCompressor, DeflateCompressor and ZstdCompressor. Use `'enabled' : false` to disable compression. Custom compressor can be provided by specifying the full class name as a [string constant](definitions.html#constants). |
| `enabled` | true | Enable/disable sstable compression. If the `enabled` option is set to `false`, no other options must be specified. |
| `chunk_length_in_kb` | 64 | On disk SSTables are compressed by block (to allow random reads). This option defines the size (in KB) of said block. See [note](#chunk_note) for further information. |
| `compression_level` | 3 | Compression level. Only applicable for `ZstdCompressor`. Accepts values between `-131072` and `22`. |

|  |  |
| --- | --- |
|  | Bigger values may improve the compression rate, but will increase the minimum size of data to be read from disk for a read. The default value is an optimal value for compressing tables. Chunk length must be a power of 2 when computing the chunk number from an uncompressed file offset. Block size may be adjusted based on read/write access patterns such as:  * How much data is typically requested at once * Average size of rows in the table |

For instance, to create a table with LZ4Compressor and a `chunk_length_in_kb` of 4 KB:

```
CREATE TABLE simple (
   id int,
   key text,
   value text,
   PRIMARY KEY (key, value)
) WITH compression = {'class': 'LZ4Compressor', 'chunk_length_in_kb': 4};
```

##### Caching options

Caching optimizes the use of cache memory of a table. The cached data is
weighed by size and access frequency.
The `caching` options can configure both the `key cache` and the `row cache` for the table.
The following sub-options are available:

| Option | Default | Description |
| --- | --- | --- |
| `keys` | ALL | Whether to cache keys (key cache) for this table. Valid values are: `ALL` and `NONE`. |
| `rows_per_partition` | NONE | The amount of rows to cache per partition (row cache). If an integer `n` is specified, the first `n` queried rows of a partition will be cached. Valid values are: `ALL`, to cache all rows of a queried partition, or `NONE` to disable row caching. |

For instance, to create a table with both a key cache and 10 rows cached per partition:

```
CREATE TABLE simple (
id int,
key text,
value text,
PRIMARY KEY (key, value)
) WITH caching = {'keys': 'ALL', 'rows_per_partition': 10};
```

##### Read Repair options

The `read_repair` options configure the read repair behavior, tuning for various performance and consistency behaviors.

The values are:

| Option | Default | Description |
| --- | --- | --- |
| `BLOCKING` | yes | If a read repair is triggered, the read blocks writes sent to other replicas until the consistency level is reached by the writes. |
| `NONE` | no | If set, the coordinator reconciles any differences between replicas, but doesn’t attempt to repair them. |

Two consistency properties are affected by read repair behavior.

* Monotonic quorum reads: Monotonic quorum reads
  prevents reads from appearing to go back in time in some circumstances.
  When monotonic quorum reads are not provided and a write fails to reach
  a quorum of replicas, the read values may be visible in one read, and then disappear
  in a subsequent read. `BLOCKING` provides this behavior.
* Write atomicity: Write atomicity prevents reads
  from returning partially-applied writes. Cassandra attempts to provide
  partition-level write atomicity, but since only the data covered by a
  SELECT statement is repaired by a read repair, read repair can break
  write atomicity when data is read at a more granular level than it is
  written. For example, read repair can break write atomicity if you write
  multiple rows to a clustered partition in a batch, but then select a
  single row by specifying the clustering column in a SELECT statement.
  `NONE` provides this behavior.

##### Other considerations:

* Adding new columns (see `ALTER TABLE` below) is a constant time
  operation. Thus, there is no need to anticipate future usage while initially creating a table.

## ALTER TABLE

Altering an existing table uses the `ALTER TABLE` statement:

```
alter_table_statement::= ALTER TABLE [ IF EXISTS ] table_name alter_table_instruction
alter_table_instruction::= ADD [ IF NOT EXISTS ] column_definition ( ',' column_definition)*
	| DROP [ IF EXISTS ] column_name ( ',' column_name )*
	| RENAME [ IF EXISTS ] column_name to column_name (AND column_name to column_name)*
	| ALTER [ IF EXISTS ] column_name ( column_mask | DROP MASKED )
	| WITH options
column_definition::= column_name cql_type [ column_mask]
column_mask::= MASKED WITH ( DEFAULT | function_name '(' term ( ',' term )* ')' )
```

If the table does not exist, the statement will return an error, unless `IF EXISTS` is used in which case the operation is a no-op.

For example:

```
ALTER TABLE addamsFamily ADD gravesite varchar;
ALTER TABLE addamsFamily
   WITH comment = 'A most excellent and useful table';
```

The `ALTER TABLE` statement can:

* `ADD` a new column to a table. The primary key of a table cannot ever be altered.
  A new column, thus, cannot be part of the primary key.
  Adding a column is a constant-time operation based on the amount of data in the table.
  If the new column already exists, the statement will return an error, unless `IF NOT EXISTS` is used in which case the operation is a no-op.
* `DROP` a column from a table. This command drops both the column and all
  its content. Be aware that, while the column becomes immediately
  unavailable, its content are removed lazily during compaction. Because of this lazy removal,
  the command is a constant-time operation based on the amount of data in the table.
  Also, it is important to know that once a column is dropped, a column with the same name can be re-added,
  unless the dropped column was a non-frozen column like a collection.
  If the dropped column does not already exist, the statement will return an error, unless `IF EXISTS` is used in which case the operation is a no-op.

|  |  |
| --- | --- |
|  | Warning  Dropping a column assumes that the timestamps used for the value of this column are "real" timestamp in microseconds. Using "real" timestamps in microseconds is the default is and is **strongly** recommended but as Cassandra allows the client to provide any timestamp on any table, it is theoretically possible to use another convention. Please be aware that if you do so, dropping a column will not correctly execute. |

* `RENAME` a primary key column of a table. Non primary key columns cannot be renamed.
  Furthermore, renaming a column to another name which already exists isn’t allowed.
  It’s important to keep in mind that renamed columns shouldn’t have dependent seconday indexes.
  If the renamed column does not already exist, the statement will return an error, unless `IF EXISTS` is used in which case the operation is a no-op.
* Use `WITH` to change a table option. The [supported options](#create-table-options)
  are the same as those used when creating a table, with the exception of `CLUSTERING ORDER`.
  However, setting any `compaction` sub-options will erase **ALL** previous `compaction` options, so you need to re-specify
  all the sub-options you wish to keep. The same is true for `compression` sub-options.

## DROP TABLE

Dropping a table uses the `DROP TABLE` statement:

```
drop_table_statement::= DROP TABLE [ IF EXISTS ] table_name
```

Dropping a table results in the immediate, irreversible removal of the
table, including all data it contains.

If the table does not exist, the statement will return an error, unless
`IF EXISTS` is used, when the operation is a no-op.

## TRUNCATE TABLE

A table can be truncated using the `TRUNCATE` statement:

```
truncate_statement::= TRUNCATE [ TABLE ] table_name
```

`TRUNCATE TABLE foo` is the preferred syntax for consistency with other DDL
statements.
However, tables are the only object that can be truncated currently, and the `TABLE` keyword can be omitted.

Truncating a table permanently removes all existing data from the table, but without removing the table itself.
