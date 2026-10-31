---
title: "Overview"
source_url: https://cassandra.apache.org/doc/5.0/cassandra/architecture/overview.html
cassandra_version: "5.0"
section: architecture
retrieved: 2026-10-31
---

> Source: Apache Cassandra documentation, version 5.0, https://cassandra.apache.org/doc/5.0/cassandra/architecture/overview.html. Licensed under the Apache License 2.0.

# Overview

Apache Cassandra is an open-source, distributed NoSQL database.
It implements a partitioned wide-column storage model with eventually consistent semantics.

Cassandra was initially designed at [Facebook](https://www.cs.cornell.edu/projects/ladis2009/papers/lakshman-ladis2009.pdf) using a staged event-driven architecture ([SEDA](http://www.sosp.org/2001/papers/welsh.pdf)).
This initial design implemented a combination of Amazon’s [Dynamo](https://www.cs.cornell.edu/courses/cs5414/2017fa/papers/dynamo.pdf) distributed storage and replication techniques and Google’s [Bigtable](https://static.googleusercontent.com/media/research.google.com/en//archive/bigtable-osdi06.pdf) data and storage engine model.
Dynamo and Bigtable were both developed to meet emerging requirements for scalable, reliable and highly available storage systems, but each had areas that could be improved.

Apache Cassandra was designed as a best-in-class combination of both systems to meet emerging large scale, both in data footprint and query volume, storage requirements.
As applications began to require full global replication and always available low-latency reads and writes, a new kind of database model was required to meet these new requirements.
Relational database systems at that time struggled to meet the requirements.

Apache Cassandra was designed to meet these challenges with the following design objectives in mind:

* Full multi-primary database replication
* Global availability at low latency
* Scaling out on commodity hardware
* Linear throughput increase with each additional processor
* Online load balancing and cluster growth
* Partitioned key-oriented queries
* Flexible schema

## Features

Cassandra provides the Cassandra Query Language ([CQL](../developing/cql/ddl.html)), an SQL-like
language, to create, modify, and delete database schema, as well as access data.
CQL allows users to organize data within a cluster of Cassandra nodes using:

* Keyspace: Specifies the replication strategy for a dataset across different datacenters.
  Replication refers to the number of copies stored within a cluster.
  Keyspaces serve as containers for tables.
* Table: Tables are composed of rows and columns.
  Columns define the typed schema for a single datum in a table.
  Tables are partitioned based on the columns provided in the partition key.
  Cassandra tables can flexibly add new columns to tables with zero downtime.
* Partition: Defines the mandatory part of the primary key all rows in
  Cassandra must have to identify the node in a cluster where the row is stored.
  All performant queries supply the partition key in the query.
* Row: Contains a collection of columns identified by a unique primary
  key made up of the partition key and optionally additional clustering
  keys.
* Column: A single datum with a type which belongs to a row.

CQL supports numerous advanced features over a partitioned dataset such
as:

* Collection types including sets, maps, and lists
* User-defined types, tuples, functions and aggregates
* Storage-attached indexing (SAI) for secondary indexes
* Local secondary indexes (2i)
* User-defined types, functions and aggregates
* Single-partition lightweight transactions with atomic compare and set
  semantics
* (Experimental) materialized views

Cassandra explicitly chooses not to implement operations that require
cross-partition coordination as they are typically slow and hard to
provide highly available global semantics.
For example, Cassandra does not support:

* Cross-partition transactions
* Distributed joins
* Foreign keys or referential integrity.

## Operating

Apache Cassandra configuration settings are configured in the `cassandra.yaml` file that can be edited by hand or with the aid of configuration management tools.
Some settings can be manipulated live using an online interface, but others require a restart of the database
to take effect.

Cassandra provides tools for managing a cluster.
The `nodetool` command interacts with Cassandra’s live control interface, allowing runtime
manipulation of many settings from `cassandra.yaml`.
The `auditlogviewer` is used to view the audit logs.
The `fqltool` is used to view, replay and compare full query logs.

In addition, Cassandra supports out of the box atomic snapshot functionality, which presents a point in time (PIT) snapshot of Cassandra’s data for easy integration with many backup tools.
Cassandra also supports incremental backups where data can be backed up as it is written.
