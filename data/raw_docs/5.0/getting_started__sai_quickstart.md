---
title: "Storage-attached Indexing (SAI) Quickstart"
source_url: https://cassandra.apache.org/doc/5.0/cassandra/getting-started/sai-quickstart.html
cassandra_version: "5.0"
section: getting_started
retrieved: 2026-10-31
---

> Source: Apache Cassandra documentation, version 5.0, https://cassandra.apache.org/doc/5.0/cassandra/getting-started/sai-quickstart.html. Licensed under the Apache License 2.0.

# Storage-attached Indexing (SAI) Quickstart

To get started with Storage-Attached Indexing (SAI), we’ll do the following steps:

* Create a keyspace.
* Create a table.
* Create an [index using SAI](../reference/cql-commands/create-custom-index.html).
* Add data.
* Create and run a query using SAI.

The examples in this quickstart topic show SAI indexes with non-partition key columns.

## Create a keyspace

In `cqlsh`, define the `cycling` keyspace to try the commands in a test environment:

```
CREATE KEYSPACE IF NOT EXISTS cycling
   WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : '1' };
```

## Create a database table

Using `cqlsh` or the CQL Console, create a `cyclist_semi_pro` database [table](../reference/cql-commands/create-table.html) in the `cycling` keyspace or the keyspace name of your choice:

```
CREATE TABLE IF NOT EXISTS cycling.cyclist_semi_pro (
  id int,
  firstname text,
  lastname text,
  age int,
  affiliation text,
  country text,
  registration date,
  PRIMARY KEY (id));
```

## Create SAI indexes on the database table

To test a non-trivial query, you’ll need some SAI indexes.
Use [CREATE CUSTOM INDEX](../reference/cql-commands/create-custom-index.html) commands to create SAI indexes on a few non-primary-key columns in the `cyclist_semi_pro` table:

```
CREATE INDEX lastname_sai_idx ON cycling.cyclist_semi_pro (lastname)
USING 'sai'
WITH OPTIONS = {'case_sensitive': 'false', 'normalize': 'true', 'ascii': 'true'};

CREATE INDEX age_sai_idx ON cycling.cyclist_semi_pro (age)
USING 'sai';

CREATE INDEX country_sai_idx ON cycling.cyclist_semi_pro (country)
USING 'sai'
WITH OPTIONS = {'case_sensitive': 'false', 'normalize': 'true', 'ascii': 'true'};

CREATE INDEX registration_sai_idx ON cycling.cyclist_semi_pro (registration)
USING 'sai';
```

|  |  |
| --- | --- |
|  | Index names are unique per keyspace. You cannot use the same index name for two different indexes within a keyspace, regardless of which table they are on. |

Let’s take a look at the description of the table and its indexes:

* Query
* Result

```
DESCRIBE TABLE cycling.cyclist_semi_pro;
```

```
CREATE TABLE cycling.cyclist_semi_pro (
    id int PRIMARY KEY,
    affiliation text,
    age int,
    country text,
    firstname text,
    lastname text,
    registration date
) WITH additional_write_policy = '99PERCENTILE'
    AND bloom_filter_fp_chance = 0.01
    AND caching = {'keys': 'ALL', 'rows_per_partition': 'NONE'}
    AND comment = ''
    AND compaction = {'class': 'org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy', 'max_threshold': '32', 'min_threshold': '4'}
    AND compression = {'chunk_length_in_kb': '64', 'class': 'org.apache.cassandra.io.compress.LZ4Compressor'}
    AND crc_check_chance = 1.0
    AND default_time_to_live = 0
    AND gc_grace_seconds = 864000
    AND max_index_interval = 2048
    AND memtable_flush_period_in_ms = 0
    AND min_index_interval = 128
    AND nodesync = {'enabled': 'true', 'incremental': 'true'}
    AND read_repair = 'BLOCKING'
    AND speculative_retry = '99PERCENTILE';
CREATE INDEX registration_sai_idx ON cycling.cyclist_semi_pro (registration) USING 'sai';
CREATE INDEX country_sai_idx ON cycling.cyclist_semi_pro (country) USING 'sai' WITH OPTIONS = {'normalize': 'true', 'case_sensitive': 'false', 'ascii': 'true'};
CREATE INDEX age_sai_idx ON cycling.cyclist_semi_pro (age) USING 'sai';
CREATE INDEX lastname_sai_idx ON cycling.cyclist_semi_pro (lastname) USING 'sai' WITH OPTIONS = {'normalize': 'true', 'case_sensitive': 'false', 'ascii': 'true'};
```

## Add data to your table

Use CQLSH `INSERT` commands to add some data to the `cyclist_semi_pro` database table:

```
INSERT INTO cycling.cyclist_semi_pro (id, firstname, lastname, age, affiliation, country, registration) VALUES (1, 'Carlos', 'Perotti', 22, 'Recco Club', 'ITA', '2020-01-12');
INSERT INTO cycling.cyclist_semi_pro (id, firstname, lastname, age, affiliation, country, registration) VALUES (2, 'Giovani', 'Pasi', 19, 'Venezia VelocitÃ ', 'ITA', '2016-05-15');
INSERT INTO cycling.cyclist_semi_pro (id, firstname, lastname, age, affiliation, country, registration) VALUES (3, 'Frances', 'Giardello', 24, 'Menaggio Campioni', 'ITA', '2018-07-29');
INSERT INTO cycling.cyclist_semi_pro (id, firstname, lastname, age, affiliation, country, registration) VALUES (4, 'Mark', 'Pastore', 19, 'Portofino Ciclisti', 'ITA', '2017-06-16');
INSERT INTO cycling.cyclist_semi_pro (id, firstname, lastname, age, affiliation, country, registration) VALUES (5, 'Irene', 'Cantona', 24, 'Como VelocitÃ ', 'ITA', '2012-07-22');
INSERT INTO cycling.cyclist_semi_pro (id, firstname, lastname, age, affiliation, country, registration) VALUES (6, 'Hugo', 'Herrera', 23, 'Bellagio Ciclisti', 'ITA', '2004-02-12');
INSERT INTO cycling.cyclist_semi_pro (id, firstname, lastname, age, affiliation, country, registration) VALUES (7, 'Marcel', 'Silva', 21, 'Paris Cyclistes', 'FRA', '2018-04-28');
INSERT INTO cycling.cyclist_semi_pro (id, firstname, lastname, age, affiliation, country, registration) VALUES (8, 'Theo', 'Bernat', 19, 'Nice Cavaliers', 'FRA', '2007-05-15');
INSERT INTO cycling.cyclist_semi_pro (id, firstname, lastname, age, affiliation, country, registration) VALUES (9, 'Richie', 'Draxler', 24, 'Normandy Club', 'FRA', '2011-02-26');
INSERT INTO cycling.cyclist_semi_pro (id, firstname, lastname, age, affiliation, country, registration) VALUES (10, 'Agnes', 'Cavani', 22, 'Chamonix Hauteurs', 'FRA', '2020-01-02');
INSERT INTO cycling.cyclist_semi_pro (id, firstname, lastname, age, affiliation, country, registration) VALUES (11, 'Pablo', 'Verratti', 19, 'Chamonix Hauteurs', 'FRA', '2006-05-15');
INSERT INTO cycling.cyclist_semi_pro (id, firstname, lastname, age, affiliation, country, registration) VALUES (12, 'Charles', 'Eppinger', 24, 'Chamonix Hauteurs', 'FRA', '2018-07-29');
INSERT INTO cycling.cyclist_semi_pro (id, firstname, lastname, age, affiliation, country, registration) VALUES (13, 'Stanley', 'Trout', 30, 'Bolder Boulder', 'USA', '2016-02-12');
INSERT INTO cycling.cyclist_semi_pro (id, firstname, lastname, age, affiliation, country, registration) VALUES (14, 'Juan', 'Perez', 31, 'Rutgers Alumni Riders', 'USA', '2017-06-16');
INSERT INTO cycling.cyclist_semi_pro (id, firstname, lastname, age, affiliation, country, registration) VALUES (15, 'Thomas', 'Fulton', 27, 'Exeter Academy', 'USA', '2012-12-15');
INSERT INTO cycling.cyclist_semi_pro (id, firstname, lastname, age, affiliation, country, registration) VALUES (16, 'Jenny', 'Hamler', 28, 'CU Alums Crankworkz', 'USA', '2012-07-22');
INSERT INTO cycling.cyclist_semi_pro (id, firstname, lastname, age, affiliation, country, registration) VALUES (17, 'Alice', 'McCaffrey', 26, 'Pennan Power', 'GBR', '2020-02-12');
INSERT INTO cycling.cyclist_semi_pro (id, firstname, lastname, age, affiliation, country, registration) VALUES (18, 'Nicholas', 'Burrow', 26, 'Aberdeen Association', 'GBR', '2016-02-12');
INSERT INTO cycling.cyclist_semi_pro (id, firstname, lastname, age, affiliation, country, registration) VALUES (19, 'Tyler', 'Higgins', 24, 'Highclere Agents', 'GBR', '2019-07-31');
INSERT INTO cycling.cyclist_semi_pro (id, firstname, lastname, age, affiliation, country, registration) VALUES (20, 'Leslie', 'Boyd', 18, 'London Cyclists', 'GBR', '2012-12-15');
```

Adding data in this quickstart topic shows simple `INSERT` commands.
To load databases with many rows, consider using [DataStax Bulk Loader for Apache Cassandra](https://docs.datastax.com/en/dsbulk/doc/index.html).

## Try out CQL queries

Use the CQLSH `SELECT` command to submit queries.

|  |  |
| --- | --- |
|  | The supported query operators for tables with SAI indexes: \* Numerics: `=`, `<`, `>`, `⇐`, `>=`, `AND` \* Strings: `=`, `CONTAINS`, `CONTAINS KEY`, `AND` \* Strings or Numerics: `LIKE` |

Find a specific semi-pro cyclist:

* Query
* Result

```
SELECT * FROM cycling.cyclist_semi_pro WHERE lastname = 'Eppinger';
```

```
 id | affiliation       | age | country | firstname | lastname | registration
----+-------------------+-----+---------+-----------+----------+--------------
 12 | Chamonix Hauteurs |  24 |     FRA |   Charles | Eppinger |   2018-07-29

(1 rows)
```

Find semi-pro cyclists whose age is less than or equal to 23:

* Query
* Result

```
SELECT * FROM cycling.cyclist_semi_pro WHERE age <= 23;
```

```
 id | affiliation        | age | country | firstname | lastname | registration
----+--------------------+-----+---------+-----------+----------+--------------
 10 |  Chamonix Hauteurs |  22 |     FRA |     Agnes |   Cavani |   2020-01-02
 11 |  Chamonix Hauteurs |  19 |     FRA |     Pablo | Verratti |   2006-05-15
  1 |         Recco Club |  22 |     ITA |    Carlos |  Perotti |   2020-01-12
  8 |     Nice Cavaliers |  19 |     FRA |      Theo |   Bernat |   2007-05-15
  2 |   Venezia VelocitÃ  |  19 |     ITA |   Giovani |     Pasi |   2016-05-15
  4 | Portofino Ciclisti |  19 |     ITA |      Mark |  Pastore |   2017-06-16
 20 |    London Cyclists |  18 |     GBR |    Leslie |     Boyd |   2012-12-15
  7 |    Paris Cyclistes |  21 |     FRA |    Marcel |    Silva |   2018-04-28
  6 |  Bellagio Ciclisti |  23 |     ITA |      Hugo |  Herrera |   2004-02-12

(9 rows)
```

Find semi-pro cyclists from Great Britain:

* Query
* Result

```
SELECT * FROM cycling.cyclist_semi_pro WHERE country = 'GBR';
```

```
 id | affiliation          | age | country | firstname | lastname  | registration
----+----------------------+-----+---------+-----------+-----------+--------------
 19 |     Highclere Agents |  24 |     GBR |     Tyler |   Higgins |   2019-07-31
 18 | Aberdeen Association |  26 |     GBR |  Nicholas |    Burrow |   2016-02-12
 20 |      London Cyclists |  18 |     GBR |    Leslie |      Boyd |   2012-12-15
 17 |         Pennan Power |  26 |     GBR |     Alice | McCaffrey |   2020-02-12

(4 rows)
```

Find semi-pro cyclists who registered between a given date range:

* Query
* Result

```
SELECT * FROM cycling.cyclist_semi_pro WHERE registration > '2010-01-01' AND registration < '2015-12-31' LIMIT 10;
```

```
 id | affiliation         | age | country | firstname | lastname | registration
----+---------------------+-----+---------+-----------+----------+--------------
  5 |       Como VelocitÃ  |  24 |     ITA |     Irene |  Cantona |   2012-07-22
 16 | CU Alums Crankworkz |  28 |     USA |     Jenny |   Hamler |   2012-07-22
 15 |      Exeter Academy |  27 |     USA |    Thomas |   Fulton |   2012-12-15
 20 |     London Cyclists |  18 |     GBR |    Leslie |     Boyd |   2012-12-15
  9 |       Normandy Club |  24 |     FRA |    Richie |  Draxler |   2011-02-26

(5 rows)
```

|  |  |
| --- | --- |
|  | For query examples with `CONTAINS` clauses that take advantage of SAI collection maps, lists, and sets, be sure to see [SAI collection map examples with keys, values, and entries](../developing/cql/indexing/sai/collections.html). |

## Removing an SAI index

To remove an SAI index, use `DROP INDEX`.

Example:

```
DROP INDEX IF EXISTS cycling.age_sai_idx;
```

## Resources

[SAI overview](../developing/cql/indexing/sai/sai-overview.html)
