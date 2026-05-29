# Lab 5-1: SQL Basics with PostgreSQL in Docker

## Overview

SQL (Structured Query Language) is the language used to talk to relational databases. The acronym has been around since the 1970s, and the basic syntax has remained surprisingly stable: a SELECT you write today would have been recognizable to a database engineer in 1985. That stability is one of SQL's quiet superpowers. The query language you learn for one database (PostgreSQL, MySQL, MariaDB, SQLite, SQL Server, Oracle, BigQuery, Snowflake) transfers to all the others with only minor dialect differences. Time spent learning SQL well pays back over a long career, regardless of which tools your company chooses.

This lab introduces the four building blocks of practical SQL: **DDL** (data definition: creating and altering tables), **DML** (data manipulation: inserting, updating, and deleting rows), **SELECT queries** (the workhorse for reading data), and **joins** (combining rows from multiple tables). You will work against a small e-commerce schema (`customers`, `products`, `orders`, `order_items`) running inside a PostgreSQL container started with Docker. Every query you run will produce a real result against real seed data, and you will compare your output against the expected output to verify your understanding.

The lab is therefore part **typing exercise** (build muscle memory for SQL syntax), part **observation exercise** (read query results critically and notice the structure), and part **diagnostic exercise** (when output does not match expectations, work out why).

**This lab is hands-on.** You type the SQL yourself; no AI assistance is needed or expected for the main exercises. The Copilot stretch in Part 8 invites you to compare your queries to ones Copilot generates from the same English problem statements.

---

## Learning Objectives

By the end of this lab, you will be able to:

1. Start a PostgreSQL database in a Docker container, connect to it with `psql`, and use the most common psql meta-commands (`\dt`, `\d`, `\q`).
2. Write DDL statements to create tables with primary keys, foreign keys, NOT NULL, and UNIQUE constraints.
3. Write DML statements (`INSERT`, `UPDATE`, `DELETE`) to add, modify, and remove rows.
4. Write `SELECT` queries using `WHERE` (with `=`, `<`, `>`, `AND`, `OR`, `IN`, `LIKE`, `BETWEEN`, `IS NULL`), `ORDER BY`, `LIMIT`, and `DISTINCT`.
5. Aggregate data with `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`, `GROUP BY`, and `HAVING`.
6. Combine data from multiple tables with `INNER JOIN` and `LEFT JOIN`, and explain when each is the right choice.
7. Use a LEFT JOIN with `WHERE ... IS NULL` to find rows in one table that have no match in another (the "anti-join" pattern).

---

## Part 1: Set Up the Workspace

### Step 1.1: Verify prerequisites

In a terminal:

```bash
docker --version
```

You should see Docker version 24.x or later. If Docker is not installed, see Lab 5-1 (Microservices) or install Docker Desktop from <https://docs.docker.com/get-docker/>.

You do not need PostgreSQL installed on your host machine. Everything runs inside the container.

### Step 1.2: Create the lab folder

```bash
mkdir -p ~/sql-lab
cd ~/sql-lab
```

### Step 1.3: Start the PostgreSQL container

```bash
docker run --name sql-lab \
  -e POSTGRES_PASSWORD=lab \
  -e POSTGRES_DB=sqllab \
  -p 5432:5432 \
  -d postgres:17-alpine
```

Read the flags:

| Flag | What it does |
|------|--------------|
| `--name sql-lab` | Names the container `sql-lab` so you can refer to it by name later. |
| `-e POSTGRES_PASSWORD=lab` | Sets the password for the default `postgres` superuser. The container refuses to start without this. |
| `-e POSTGRES_DB=sqllab` | Creates an initial database named `sqllab` when the container first starts. |
| `-p 5432:5432` | Maps the container's PostgreSQL port to the same port on the host. |
| `-d` | Runs the container in the background ("detached"). |
| `postgres:17-alpine` | The image to run. The alpine variant is smaller (~90 MB compressed) but functionally identical for everything in this lab. |

The first time you run this, Docker downloads the image (perhaps 30 seconds on a fast connection). Subsequent starts are instant.

### Step 1.4: Verify the container is running

```bash
docker ps
```

You should see a row with `sql-lab` in the NAMES column and a STATUS like `Up 10 seconds`. If the container is not listed, it crashed; run `docker logs sql-lab` to see why.

### Step 1.5: Connect to the database with psql

```bash
docker exec -it sql-lab psql -U postgres -d sqllab
```

You will see a psql prompt:

```
psql (17.x)
Type "help" for help.

sqllab=#
```

The `sqllab=#` prompt tells you the current database (`sqllab`) and that you are connected as a superuser (`#` rather than `>`). You are now talking directly to PostgreSQL.

Try one command to confirm everything works:

```sql
SELECT version();
```

Output:

```
                                                version
-------------------------------------------------------------------------------
 PostgreSQL 17.x on x86_64-pc-linux-musl, compiled by gcc ...
(1 row)
```

To exit psql, type `\q` and press Enter. To reconnect, run the same `docker exec` command from Step 1.5.

### Step 1.6: Learn the essential psql meta-commands

While inside psql, the commands starting with backslash are *meta-commands*: they are not SQL, but local commands for the psql client. Memorize these five:

| Command | What it does |
|---------|--------------|
| `\dt` | List all tables in the current database |
| `\d table_name` | Describe a specific table (columns, types, constraints, indexes) |
| `\l` | List all databases on the server |
| `\?` | Show all meta-commands |
| `\q` | Quit psql |

These exist because PostgreSQL's information about itself lives in system catalog tables that are tedious to query directly. The meta-commands are shortcuts for the queries you would otherwise have to write by hand.

### Step 1.7: Create a lab notebook

On your host machine (not inside psql; open a second terminal or first type `\q` to exit psql):

```bash
cd ~/sql-lab
touch notebook.md
```

Open `notebook.md` in your editor of choice. You will record observations as you work through the lab. Start it with:

```markdown
# SQL Basics Lab Notebook

## Part 2: Loading the seed data

## Part 3: DDL (CREATE, ALTER, DROP)

## Part 4: DML (INSERT, UPDATE, DELETE)

## Part 5: Basic SELECT queries

## Part 6: Aggregates and GROUP BY

## Part 7: Joins

## Part 8: Copilot stretch

## Part 9: Reflection
```

---

## Part 2: Load the Seed Data

The lab uses three pre-built tables (`products`, `orders`, `order_items`) plus a fourth table (`customers`) that you will create yourself in Part 3. The three pre-built tables are loaded from a `setup.sql` script.

### Step 2.1: Create the setup script

In your host terminal, in the `~/sql-lab` directory, create `setup.sql` with the following content:

```sql
-- setup.sql: pre-built schema and data for parts 5-7 of the lab.
-- The customers table is NOT created here. You will create it yourself
-- in Part 3, and the foreign key linking orders to customers is added
-- in Part 4 after customer data exists.

DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;

CREATE TABLE products (
    product_id   SERIAL PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    category     VARCHAR(50)  NOT NULL,
    price        NUMERIC(10, 2) NOT NULL,
    in_stock     INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE orders (
    order_id     SERIAL PRIMARY KEY,
    customer_id  INTEGER NOT NULL,
    order_date   DATE NOT NULL
);

CREATE TABLE order_items (
    order_id     INTEGER NOT NULL REFERENCES orders(order_id),
    product_id   INTEGER NOT NULL REFERENCES products(product_id),
    quantity     INTEGER NOT NULL,
    PRIMARY KEY (order_id, product_id)
);

INSERT INTO products (name, category, price, in_stock) VALUES
('Wireless Mouse',      'Electronics',  25.99,  50),
('Mechanical Keyboard', 'Electronics',  89.99,  20),
('USB-C Cable',         'Electronics',   9.99, 200),
('Notebook',            'Stationery',    4.50, 100),
('Pen Pack',            'Stationery',    6.99,  75),
('Desk Lamp',           'Furniture',    45.00,  15),
('Office Chair',        'Furniture',   189.00,   8),
('Coffee Mug',          'Kitchen',      12.50,  60),
('Water Bottle',        'Kitchen',      18.00,  40),
('Headphones',          'Electronics',  79.00,   0);

INSERT INTO orders (customer_id, order_date) VALUES
(1, '2025-03-01'),
(1, '2025-04-15'),
(2, '2025-03-05'),
(3, '2025-03-12'),
(3, '2025-04-22'),
(4, '2025-04-01'),
(5, '2025-04-08'),
(6, '2025-05-10'),
(7, '2025-05-12'),
(2, '2025-05-20');

INSERT INTO order_items (order_id, product_id, quantity) VALUES
(1, 1, 2), (1, 3, 3),
(2, 8, 1), (2, 4, 5),
(3, 2, 1), (3, 6, 1),
(4, 5, 2), (4, 4, 3), (4, 3, 1),
(5, 7, 1),
(6, 1, 1), (6, 2, 1), (6, 3, 2),
(7, 9, 2),
(8, 8, 4), (8, 5, 1),
(9, 6, 1), (9, 9, 1),
(10, 1, 1), (10, 2, 1), (10, 8, 2);
```

Save the file.

### Step 2.2: Load the script into the container

```bash
docker exec -i sql-lab psql -U postgres -d sqllab < setup.sql
```

The `-i` flag (rather than `-it`) lets you pipe the file's contents into psql as standard input. Expected output:

```
DROP TABLE
DROP TABLE
DROP TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
INSERT 0 10
INSERT 0 10
INSERT 0 21
```

Each line confirms one statement executed. On the very first run (when the tables do not yet exist), each `DROP TABLE` is preceded by a `NOTICE: table "..." does not exist, skipping` line; that is harmless and shows that `DROP TABLE IF EXISTS` is doing its job.

### Step 2.3: Verify the seed loaded correctly

Reconnect to psql:

```bash
docker exec -it sql-lab psql -U postgres -d sqllab
```

Inside psql:

```sql
\dt
```

Expected output:

```
            List of relations
 Schema |    Name     | Type  |  Owner
--------+-------------+-------+----------
 public | order_items | table | postgres
 public | orders      | table | postgres
 public | products    | table | postgres
(3 rows)
```

Three tables are present. The fourth (`customers`) does not exist yet; you will create it in Part 3.

Run a quick sanity-check query:

```sql
SELECT COUNT(*) FROM products;
```

Expected:

```
 count
-------
    10
(1 row)
```

If you see 10, the data loaded correctly.

---

## Part 3: DDL (Data Definition Language)

DDL statements create and modify the structure of tables. The three you will use most are `CREATE TABLE`, `ALTER TABLE`, and `DROP TABLE`. In this part you will create the `customers` table (which was deliberately left out of `setup.sql`). The `ALTER TABLE` example is in Part 4, after the customers table has data: altering a table is more interesting once there are rows to interact with the change.

### Step 3.1: Create the customers table

In psql:

```sql
CREATE TABLE customers (
    customer_id  SERIAL PRIMARY KEY,
    first_name   VARCHAR(50) NOT NULL,
    last_name    VARCHAR(50) NOT NULL,
    email        VARCHAR(100) UNIQUE,
    city         VARCHAR(50),
    signup_date  DATE NOT NULL
);
```

Expected output:

```
CREATE TABLE
```

That one terse line is PostgreSQL's confirmation that the statement succeeded. Notice the constraints on each column:

| Constraint | What it means |
|------------|---------------|
| `SERIAL PRIMARY KEY` | Auto-incrementing integer, unique, not null. The primary key uniquely identifies each row. |
| `NOT NULL` | This column cannot be empty. Trying to insert a row without it produces an error. |
| `UNIQUE` | No two rows may have the same value in this column. |
| (no constraint) | This column may be NULL or duplicated freely. |

### Step 3.2: Verify the table structure

```sql
\d customers
```

Expected output:

```
                                          Table "public.customers"
   Column    |          Type          | Collation | Nullable |                    Default
-------------+------------------------+-----------+----------+------------------------------------------------
 customer_id | integer                |           | not null | nextval('customers_customer_id_seq'::regclass)
 first_name  | character varying(50)  |           | not null |
 last_name   | character varying(50)  |           | not null |
 email       | character varying(100) |           |          |
 city        | character varying(50)  |           |          |
 signup_date | date                   |           | not null |
Indexes:
    "customers_pkey" PRIMARY KEY, btree (customer_id)
    "customers_email_key" UNIQUE CONSTRAINT, btree (email)
```

Two things to notice:

1. The `customer_id` column has a default of `nextval('customers_customer_id_seq'::regclass)`. PostgreSQL's `SERIAL` type silently creates a sequence (a counter that generates new IDs); the default for the column is "the next value from that counter." When you `INSERT` without specifying `customer_id`, the sequence supplies one.
2. Two indexes were created automatically: one for the primary key (`customers_pkey`) and one for the unique constraint on `email` (`customers_email_key`). Indexes make lookups by these columns fast.

### Step 3.3: Notice what DROP TABLE looks like

You will not actually drop anything (you need the table for the rest of the lab), but knowing the syntax is part of DDL fluency:

```sql
-- Don't run this. It is shown for syntax only.
-- DROP TABLE customers;
```

`DROP TABLE` is irrecoverable. There is no undo. In a real codebase, dropping a table is a major operation that should be reviewed carefully. The lab's exercises will never ask you to drop anything important.

---

## Part 4: DML (Data Manipulation Language)

DML statements add, modify, and remove rows. The three you will use most are `INSERT`, `UPDATE`, and `DELETE`.

### Step 4.1: Insert customers (multi-row INSERT)

In psql:

```sql
INSERT INTO customers (first_name, last_name, email, city, signup_date) VALUES
('Alice',   'Anderson', 'alice@example.com', 'Toronto',   '2025-01-15'),
('Bob',     'Brown',    'bob@example.com',   'Vancouver', '2025-02-03'),
('Carol',   'Chen',     'carol@example.com', 'Toronto',   '2025-02-20'),
('David',   'Davis',    'david@example.com', 'Montreal',  '2025-03-10'),
('Eve',     'Evans',    NULL,                'Toronto',   '2025-03-22'),
('Frank',   'Foster',   'frank@example.com', 'Calgary',   '2025-04-05'),
('Grace',   'Garcia',   'grace@example.com', 'Vancouver', '2025-04-18'),
('Henry',   'Hughes',   'henry@example.com', 'Ottawa',    '2025-05-01');
```

Expected output:

```
INSERT 0 8
```

Eight rows inserted. The `0` is a legacy field (it used to be the OID of the inserted row in single-row inserts); ignore it.

Several details worth noticing in the INSERT:

- `customer_id` is not in the column list. PostgreSQL fills it automatically from the SERIAL sequence (1, 2, 3, ...).
- Eve's email is `NULL` (not `'NULL'`). Without quotes, `NULL` is the SQL keyword for the absence of a value. With quotes, it would be the literal four-character string "NULL", which is not what we want.
- The whole multi-row INSERT is a single statement. PostgreSQL processes it atomically: if any row fails (e.g., a duplicate email), none of the rows are inserted.

### Step 4.2: Insert a single row with RETURNING

```sql
INSERT INTO customers (first_name, last_name, email, city, signup_date)
VALUES ('Ivy', 'Iverson', 'ivy@example.com', 'Edmonton', '2025-05-15')
RETURNING *;
```

Expected output:

```
 customer_id | first_name | last_name |      email      |   city   | signup_date
-------------+------------+-----------+-----------------+----------+-------------
           9 | Ivy        | Iverson   | ivy@example.com | Edmonton | 2025-05-15
(1 row)

INSERT 0 1
```

The `RETURNING *` clause is a PostgreSQL extension to standard SQL that returns the inserted row(s). It is useful when you need the auto-generated `customer_id` for subsequent operations. Note that Ivy got `customer_id = 9` (the next sequence value after the eight rows from Step 4.1).

### Step 4.3: Update a row

Ivy has just moved from Edmonton to Calgary. Update her record:

```sql
UPDATE customers SET city = 'Calgary' WHERE customer_id = 9;
```

Expected output:

```
UPDATE 1
```

One row was updated. The `WHERE` clause is critical: without it, the UPDATE would change *every* customer's city to Calgary. This is one of the most expensive mistakes a SQL beginner can make, and it has destroyed real databases in real companies. Always write the `WHERE` clause first, run a `SELECT` with the same condition to confirm the affected rows look right, and only then turn the SELECT into an UPDATE.

Verify:

```sql
SELECT first_name, last_name, city FROM customers WHERE customer_id = 9;
```

Expected:

```
 first_name | last_name |  city
------------+-----------+---------
 Ivy        | Iverson   | Calgary
(1 row)
```

### Step 4.4: Update with an expression

Bump the price of every product in the Electronics category by 10%:

```sql
UPDATE products SET price = price * 1.10 WHERE category = 'Electronics';
```

Expected output:

```
UPDATE 4
```

Four electronics products had their prices raised. Verify:

```sql
SELECT name, price FROM products WHERE category = 'Electronics' ORDER BY name;
```

Expected:

```
        name         | price
---------------------+--------
 Headphones          |  86.90
 Mechanical Keyboard |  98.99
 USB-C Cable         |  10.99
 Wireless Mouse      |  28.59
(4 rows)
```

Now revert the change so the rest of the lab uses the canonical seed data:

```sql
UPDATE products SET price = ROUND(price / 1.10, 2) WHERE category = 'Electronics';
```

Verify the revert:

```sql
SELECT name, price FROM products WHERE category = 'Electronics' ORDER BY name;
```

Expected:

```
        name         | price
---------------------+-------
 Headphones          | 79.00
 Mechanical Keyboard | 89.99
 USB-C Cable         |  9.99
 Wireless Mouse      | 25.99
(4 rows)
```

> **A note on rounding.** `ROUND(price / 1.10, 2)` divides by 1.10 (undoing the 10% increase) and rounds to 2 decimal places. Without `ROUND`, the result would be a long decimal because `99 / 110` does not have an exact representation. Decimal precision in SQL is a deeper topic than this lab can cover; for now, treat `ROUND(x, 2)` as the standard way to format money values.

### Step 4.5: Delete a row

Ivy never actually made a purchase; remove her from the customers table:

```sql
DELETE FROM customers WHERE customer_id = 9;
```

Expected output:

```
DELETE 1
```

One row deleted. Just as with UPDATE, the `WHERE` clause is critical: `DELETE FROM customers;` with no WHERE would empty the entire table. Always run a SELECT with the same condition first.

Verify Ivy is gone:

```sql
SELECT COUNT(*) FROM customers;
```

Expected:

```
 count
-------
     8
(1 row)
```

Back to 8 customers, the canonical seed state.

### Step 4.6: Add a foreign key with ALTER TABLE

You now have customers in `customers` and orders in `orders` that reference them by `customer_id`. The link between these two tables is implicit at this point: nothing in the database enforces that every `orders.customer_id` actually corresponds to a real customer. Add a foreign-key constraint to make the link explicit:

```sql
ALTER TABLE orders
    ADD CONSTRAINT orders_customer_fk
    FOREIGN KEY (customer_id)
    REFERENCES customers(customer_id);
```

Expected output:

```
ALTER TABLE
```

The foreign key tells PostgreSQL that every value in `orders.customer_id` must correspond to a real `customer_id` in `customers`. After this point:

- You cannot insert an order for a customer that does not exist.
- You cannot delete a customer who has orders (without first dealing with those orders).
- PostgreSQL also validates the existing rows: if any current order had a `customer_id` that did not exist in `customers`, the `ALTER TABLE` would fail with a foreign-key violation. This is why we added the constraint *after* inserting the customers, not before.

Verify the constraint is in place:

```sql
\d orders
```

You should now see a "Foreign-key constraints" section in the output:

```
Foreign-key constraints:
    "orders_customer_fk" FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
```

> **Why the foreign key is added now, not in Part 3.** Foreign keys link two tables, so they cannot exist until both tables exist with consistent data. In a real project this comes up constantly: you create the tables in one migration, populate them, and add the relationships in a later migration once the data is clean. The lab is teaching you the realistic pattern, not the "all DDL first, all DML second" textbook pattern.

---

## Part 5: Basic SELECT Queries

The `SELECT` statement is the workhorse of SQL. Almost every interaction with a database is a SELECT.

### Step 5.1: SELECT everything

```sql
SELECT * FROM customers;
```

Expected output:

```
 customer_id | first_name | last_name |       email       |   city    | signup_date
-------------+------------+-----------+-------------------+-----------+-------------
           1 | Alice      | Anderson  | alice@example.com | Toronto   | 2025-01-15
           2 | Bob        | Brown     | bob@example.com   | Vancouver | 2025-02-03
           3 | Carol      | Chen      | carol@example.com | Toronto   | 2025-02-20
           4 | David      | Davis     | david@example.com | Montreal  | 2025-03-10
           5 | Eve        | Evans     |                   | Toronto   | 2025-03-22
           6 | Frank      | Foster    | frank@example.com | Calgary   | 2025-04-05
           7 | Grace      | Garcia    | grace@example.com | Vancouver | 2025-04-18
           8 | Henry      | Hughes    | henry@example.com | Ottawa    | 2025-05-01
(8 rows)
```

Notice Eve's email column is blank: that is how psql displays NULL by default. In the next section you will see how to query for it explicitly.

> **A note on `SELECT *`.** `*` means "all columns." It is fine for interactive exploration but considered poor practice in production code because (a) adding a column to the table changes what the query returns, breaking callers that expect a specific column order, and (b) you usually do not actually need every column. Real applications spell out the columns they need.

### Step 5.2: SELECT specific columns

```sql
SELECT first_name, last_name, city FROM customers;
```

Expected output:

```
 first_name | last_name |   city
------------+-----------+-----------
 Alice      | Anderson  | Toronto
 Bob        | Brown     | Vancouver
 Carol      | Chen      | Toronto
 David      | Davis     | Montreal
 Eve        | Evans     | Toronto
 Frank      | Foster    | Calgary
 Grace      | Garcia    | Vancouver
 Henry      | Hughes    | Ottawa
(8 rows)
```

Three columns, in the order listed. Try reordering them (`SELECT city, last_name, first_name FROM customers;`) and note that the output column order follows the SELECT list, not the table's column order.

### Step 5.3: Filter with WHERE

Find all customers in Toronto:

```sql
SELECT * FROM customers WHERE city = 'Toronto';
```

Expected output:

```
 customer_id | first_name | last_name |       email       |  city   | signup_date
-------------+------------+-----------+-------------------+---------+-------------
           1 | Alice      | Anderson  | alice@example.com | Toronto | 2025-01-15
           3 | Carol      | Chen      | carol@example.com | Toronto | 2025-02-20
           5 | Eve        | Evans     |                   | Toronto | 2025-03-22
(3 rows)
```

Three Toronto customers. Note that string literals use single quotes (`'Toronto'`), not double quotes. Double quotes in SQL mean "this is an identifier"; if you wrote `"Toronto"`, PostgreSQL would look for a column called Toronto.

### Step 5.4: Combine conditions with AND, OR

Toronto customers who signed up after February 1:

```sql
SELECT first_name, last_name, signup_date
FROM customers
WHERE city = 'Toronto' AND signup_date > '2025-02-01';
```

Expected output:

```
 first_name | last_name | signup_date
------------+-----------+-------------
 Carol      | Chen      | 2025-02-20
 Eve        | Evans     | 2025-03-22
(2 rows)
```

`AND` requires both conditions to be true; `OR` requires either. When mixing them, use parentheses to make precedence explicit: `WHERE (a OR b) AND c` is different from `WHERE a OR (b AND c)`.

### Step 5.5: Match a list with IN

Customers in Toronto OR Vancouver:

```sql
SELECT first_name, last_name, city
FROM customers
WHERE city IN ('Toronto', 'Vancouver');
```

Expected output:

```
 first_name | last_name |   city
------------+-----------+-----------
 Alice      | Anderson  | Toronto
 Bob        | Brown     | Vancouver
 Carol      | Chen      | Toronto
 Eve        | Evans     | Toronto
 Grace      | Garcia    | Vancouver
(5 rows)
```

`IN (...)` is equivalent to `city = 'Toronto' OR city = 'Vancouver'` but much shorter, especially for longer lists.

### Step 5.6: Find NULLs with IS NULL

Find customers who have no email recorded:

```sql
SELECT first_name, last_name FROM customers WHERE email IS NULL;
```

Expected output:

```
 first_name | last_name
------------+-----------
 Eve        | Evans
(1 row)
```

> **A trap to know about.** `WHERE email = NULL` does NOT work. `NULL` in SQL means "unknown," and `unknown = anything` is itself unknown (not true and not false), so the row is excluded. Always use `IS NULL` and `IS NOT NULL` for null checks. This is one of the most common SQL beginner mistakes.

### Step 5.7: Pattern matching with LIKE

Find products whose name contains "Cable":

```sql
SELECT name, price FROM products WHERE name LIKE '%Cable%';
```

Expected output:

```
    name     | price
-------------+-------
 USB-C Cable |  9.99
(1 row)
```

The `%` wildcard matches any string (including empty). `_` (underscore) matches exactly one character. `LIKE` is case-sensitive in PostgreSQL; `ILIKE` is the case-insensitive variant.

### Step 5.8: Range filtering with BETWEEN

Find products priced between $10 and $50:

```sql
SELECT name, price FROM products WHERE price BETWEEN 10 AND 50 ORDER BY price;
```

Expected output:

```
      name      | price
----------------+-------
 Coffee Mug     | 12.50
 Water Bottle   | 18.00
 Wireless Mouse | 25.99
 Desk Lamp      | 45.00
(4 rows)
```

`BETWEEN x AND y` is inclusive on both ends; it is equivalent to `price >= 10 AND price <= 50`.

### Step 5.9: Sort with ORDER BY

The three most expensive products:

```sql
SELECT name, price FROM products ORDER BY price DESC LIMIT 3;
```

Expected output:

```
        name         | price
---------------------+--------
 Office Chair        | 189.00
 Mechanical Keyboard |  89.99
 Headphones          |  79.00
(3 rows)
```

`ORDER BY price DESC` sorts highest to lowest. `ASC` is ascending (the default). `LIMIT 3` truncates to the first three rows.

### Step 5.10: Eliminate duplicates with DISTINCT

List the distinct product categories:

```sql
SELECT DISTINCT category FROM products ORDER BY category;
```

Expected output:

```
  category
-------------
 Electronics
 Furniture
 Kitchen
 Stationery
(4 rows)
```

Without `DISTINCT`, the query would return ten rows (one per product, with duplicate category values). `DISTINCT` collapses identical rows into one.

---

## Part 6: Aggregates and GROUP BY

Aggregate functions reduce a set of values to a single value. The five most common are `COUNT`, `SUM`, `AVG`, `MIN`, and `MAX`.

### Step 6.1: Simple aggregates

How many products are there in total?

```sql
SELECT COUNT(*) FROM products;
```

Expected:

```
 count
-------
    10
(1 row)
```

How many electronics products are there?

```sql
SELECT COUNT(*) FROM products WHERE category = 'Electronics';
```

Expected:

```
 count
-------
     4
(1 row)
```

What is the average, minimum, and maximum price?

```sql
SELECT
    ROUND(AVG(price), 2) AS avg_price,
    MIN(price) AS min_price,
    MAX(price) AS max_price
FROM products;
```

Expected:

```
 avg_price | min_price | max_price
-----------+-----------+-----------
     48.10 |      4.50 |    189.00
(1 row)
```

Three things worth noticing:

1. **The `AS` keyword renames a column** in the output. Without `AS`, the column header would be the literal expression `round` (PostgreSQL's default name for the result of a function call).
2. **`ROUND(AVG(price), 2)` rounds to two decimal places.** Without `ROUND`, `AVG` returns a number with 16 decimal places of precision (try it). The extra precision is correct mathematically but ugly to read.
3. **`COUNT(*)` versus `COUNT(column)`.** `COUNT(*)` counts all rows. `COUNT(email)` counts only rows where `email IS NOT NULL`. Try `SELECT COUNT(*), COUNT(email) FROM customers;` and note the difference.

### Step 6.2: Group by a column

Count products per category:

```sql
SELECT category, COUNT(*) FROM products GROUP BY category ORDER BY category;
```

Expected:

```
  category   | count
-------------+-------
 Electronics |     4
 Furniture   |     2
 Kitchen     |     2
 Stationery  |     2
(4 rows)
```

`GROUP BY` partitions the rows by the named column, then runs the aggregate (`COUNT`) within each partition. The result has one row per distinct category.

### Step 6.3: Multiple aggregates per group

Combine multiple aggregates in one query:

```sql
SELECT
    category,
    ROUND(AVG(price), 2) AS avg_price,
    COUNT(*) AS product_count
FROM products
GROUP BY category
ORDER BY category;
```

Expected:

```
  category   | avg_price | product_count
-------------+-----------+---------------
 Electronics |     51.24 |             4
 Furniture   |    117.00 |             2
 Kitchen     |     15.25 |             2
 Stationery  |      5.75 |             2
(4 rows)
```

### Step 6.4: Filter groups with HAVING

Categories whose average price exceeds $20:

```sql
SELECT
    category,
    ROUND(AVG(price), 2) AS avg_price
FROM products
GROUP BY category
HAVING AVG(price) > 20
ORDER BY category;
```

Expected:

```
  category   | avg_price
-------------+-----------
 Electronics |     51.24
 Furniture   |    117.00
(2 rows)
```

> **WHERE versus HAVING.** `WHERE` filters individual rows *before* grouping. `HAVING` filters groups *after* grouping. You cannot write `WHERE AVG(price) > 20` because at the time WHERE is evaluated, the groups do not exist yet. The order of clauses is fixed: `FROM ... WHERE ... GROUP BY ... HAVING ... ORDER BY ... LIMIT ...`, and that order reflects the order of operations.

---

## Part 7: Joins

A join combines rows from two or more tables based on a related column. The two you need to know first are `INNER JOIN` (only rows with matches in both tables) and `LEFT JOIN` (all rows from the left table, plus matches from the right where they exist).

### Step 7.1: INNER JOIN: orders with customer names

The `orders` table has a `customer_id` but no customer name. To see who placed each order, join `orders` to `customers`:

```sql
SELECT
    o.order_id,
    c.first_name,
    c.last_name,
    o.order_date
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
ORDER BY o.order_id;
```

Expected output:

```
 order_id | first_name | last_name | order_date
----------+------------+-----------+------------
        1 | Alice      | Anderson  | 2025-03-01
        2 | Alice      | Anderson  | 2025-04-15
        3 | Bob        | Brown     | 2025-03-05
        4 | Carol      | Chen      | 2025-03-12
        5 | Carol      | Chen      | 2025-04-22
        6 | David      | Davis     | 2025-04-01
        7 | Eve        | Evans     | 2025-04-08
        8 | Frank      | Foster    | 2025-05-10
        9 | Grace      | Garcia    | 2025-05-12
       10 | Bob        | Brown     | 2025-05-20
(10 rows)
```

Anatomy of this query:

- **`FROM orders o`**: the left-side table. `o` is a *table alias*: a shorthand you can use everywhere in the query in place of `orders`.
- **`INNER JOIN customers c`**: the right-side table, aliased to `c`.
- **`ON o.customer_id = c.customer_id`**: the join condition. For each row in `orders`, find rows in `customers` where the customer IDs match.
- The result has one row per match. Notice Alice appears twice (orders 1 and 2) and Bob appears twice (orders 3 and 10) because each placed two orders.

The keyword `INNER` is optional; `JOIN` by itself means `INNER JOIN`. The following query is identical:

```sql
SELECT o.order_id, c.first_name, c.last_name, o.order_date
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE c.city = 'Toronto'
ORDER BY o.order_id;
```

Expected:

```
 order_id | first_name | last_name | order_date
----------+------------+-----------+------------
        1 | Alice      | Anderson  | 2025-03-01
        2 | Alice      | Anderson  | 2025-04-15
        4 | Carol      | Chen      | 2025-03-12
        5 | Carol      | Chen      | 2025-04-22
        7 | Eve        | Evans     | 2025-04-08
(5 rows)
```

Five orders, all placed by Toronto-based customers.

### Step 7.2: LEFT JOIN: every customer, with their orders if any

`INNER JOIN` shows only customers who have orders. To list *every* customer alongside their orders (including customers with no orders), use `LEFT JOIN`:

```sql
SELECT
    c.first_name,
    c.last_name,
    o.order_id,
    o.order_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
ORDER BY c.customer_id, o.order_id;
```

Expected output:

```
 first_name | last_name | order_id | order_date
------------+-----------+----------+------------
 Alice      | Anderson  |        1 | 2025-03-01
 Alice      | Anderson  |        2 | 2025-04-15
 Bob        | Brown     |        3 | 2025-03-05
 Bob        | Brown     |       10 | 2025-05-20
 Carol      | Chen      |        4 | 2025-03-12
 Carol      | Chen      |        5 | 2025-04-22
 David      | Davis     |        6 | 2025-04-01
 Eve        | Evans     |        7 | 2025-04-08
 Frank      | Foster    |        8 | 2025-05-10
 Grace      | Garcia    |        9 | 2025-05-12
 Henry      | Hughes    |          |
(11 rows)
```

Look at the last row: Henry has no orders, but he is in the result anyway, with NULL values for the columns from the orders table. This is the LEFT JOIN promise: every row from the left table appears in the result, with NULLs where the right table has no match. If you had used `INNER JOIN`, Henry would not have appeared at all.

> **When LEFT vs INNER matters.** Use INNER JOIN when you only want rows that have a match in both tables (e.g., "list every order with its customer name"). Use LEFT JOIN when you want every row from the primary table, even ones with no match (e.g., "list every customer and their orders if they have any"). For most analytical questions, LEFT JOIN is the safer default because you do not silently drop rows.

### Step 7.3: Three-way join: orders, items, products

The order details (which products were in each order) live in the `order_items` table. To see them with product names and prices, join three tables:

```sql
SELECT
    o.order_id,
    c.first_name,
    p.name,
    oi.quantity,
    p.price,
    (oi.quantity * p.price) AS line_total
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
ORDER BY o.order_id, p.name;
```

Expected output (first 10 rows of 21):

```
 order_id | first_name |        name         | quantity | price  | line_total
----------+------------+---------------------+----------+--------+------------
        1 | Alice      | USB-C Cable         |        3 |   9.99 |      29.97
        1 | Alice      | Wireless Mouse      |        2 |  25.99 |      51.98
        2 | Alice      | Coffee Mug          |        1 |  12.50 |      12.50
        2 | Alice      | Notebook            |        5 |   4.50 |      22.50
        3 | Bob        | Desk Lamp           |        1 |  45.00 |      45.00
        3 | Bob        | Mechanical Keyboard |        1 |  89.99 |      89.99
        4 | Carol      | Notebook            |        3 |   4.50 |      13.50
        4 | Carol      | Pen Pack            |        2 |   6.99 |      13.98
        4 | Carol      | USB-C Cable         |        1 |   9.99 |       9.99
        5 | Carol      | Office Chair        |        1 | 189.00 |     189.00
...
(21 rows)
```

Each row is one product line in one order. The expression `oi.quantity * p.price` is computed per row and named `line_total`. This three-way join is the heart of a thousand real e-commerce reports.

### Step 7.4: JOIN + GROUP BY: order totals

Now compute one row per order, showing the total amount spent:

```sql
SELECT
    o.order_id,
    c.first_name,
    c.last_name,
    ROUND(SUM(oi.quantity * p.price), 2) AS order_total
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
GROUP BY o.order_id, c.first_name, c.last_name
ORDER BY o.order_id;
```

Expected output:

```
 order_id | first_name | last_name | order_total
----------+------------+-----------+-------------
        1 | Alice      | Anderson  |       81.95
        2 | Alice      | Anderson  |       35.00
        3 | Bob        | Brown     |      134.99
        4 | Carol      | Chen      |       37.47
        5 | Carol      | Chen      |      189.00
        6 | David      | Davis     |      135.96
        7 | Eve        | Evans     |       36.00
        8 | Frank      | Foster    |       56.99
        9 | Grace      | Garcia    |       63.00
       10 | Bob        | Brown     |      140.98
(10 rows)
```

Notice that every column in the SELECT list either appears in the GROUP BY clause (`o.order_id`, `c.first_name`, `c.last_name`) or is wrapped in an aggregate function (`SUM`). This is a hard rule of GROUP BY: every selected column must be either grouped or aggregated. Forgetting this is the most common GROUP BY error.

### Step 7.5: Customer lifetime spend

Combine LEFT JOIN with GROUP BY to compute every customer's total spending, including customers with zero orders:

```sql
SELECT
    c.first_name,
    c.last_name,
    COUNT(DISTINCT o.order_id) AS num_orders,
    COALESCE(ROUND(SUM(oi.quantity * p.price), 2), 0) AS total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
LEFT JOIN order_items oi ON o.order_id = oi.order_id
LEFT JOIN products p ON oi.product_id = p.product_id
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY total_spent DESC;
```

Expected output:

```
 first_name | last_name | num_orders | total_spent
------------+-----------+------------+-------------
 Bob        | Brown     |          2 |      275.97
 Carol      | Chen      |          2 |      226.47
 David      | Davis     |          1 |      135.96
 Alice      | Anderson  |          2 |      116.95
 Grace      | Garcia    |          1 |       63.00
 Frank      | Foster    |          1 |       56.99
 Eve        | Evans     |          1 |       36.00
 Henry      | Hughes    |          0 |           0
(8 rows)
```

A few details:

- **`COUNT(DISTINCT o.order_id)`** counts unique orders. Without `DISTINCT`, the count would be the number of join rows (one per line item), not orders.
- **`COALESCE(..., 0)`** replaces NULL with 0. Henry has no orders, so the SUM would be NULL without COALESCE; we want it to display as 0.
- **Henry appears in the result** because of the LEFT JOIN. With INNER JOIN, he would have been dropped.

### Step 7.6: The anti-join: find products that have never been ordered

Use LEFT JOIN combined with `WHERE ... IS NULL` to find products with no matching rows in `order_items`:

```sql
SELECT p.name, p.category
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
WHERE oi.order_id IS NULL;
```

Expected output:

```
    name    |  category
------------+-------------
 Headphones | Electronics
(1 row)
```

The pattern is worth memorizing:

1. LEFT JOIN to the table where you want to look for missing matches.
2. WHERE the joined column IS NULL.

The result is "every row in the left table that has no match in the right table." This is called an *anti-join*, and it answers a very common kind of business question: "Which products have never sold?" "Which customers have never placed an order?" "Which invoices have not been paid?"

---

## Part 8: Stretch: Compare Your Queries to Copilot's

### Step 8.1: Open Copilot Chat

This step is best done in VS Code. Open the project folder (`~/sql-lab`) in VS Code, then open the Chat view with `Ctrl+Alt+I` (or `Cmd+Alt+I` on macOS). Select **Ask** mode and **Claude Sonnet 4.6** in the model picker. If Claude Sonnet 4.6 is not available, **Auto** is an acceptable fallback (see Lab 1-1 for full availability notes).

### Step 8.2: Provide context

Attach `setup.sql` to the chat using the paperclip icon or `#`. Also send this prompt as the first message so Copilot knows what's in your database:

```
I have a PostgreSQL database with the schema in the attached setup.sql,
plus a customers table with these columns: customer_id, first_name,
last_name, email, city, signup_date. I will ask you to write SQL queries
against this schema. Respond with just the SQL, no explanation.
```

### Step 8.3: Ask Copilot for each query you wrote

Pick three of the queries you wrote yourself (one simple, one with GROUP BY, one with a JOIN) and ask Copilot for each one in plain English. Examples:

- "List the average price per product category."
- "Show every customer along with the number of orders they have placed and the total amount they have spent."
- "Find products that have never been ordered."

For each one, run Copilot's query in psql and compare its output to yours.

In your notebook, write for each query:

1. Did Copilot produce the same query you wrote? Different syntax, same meaning?
2. Did it produce the same result?
3. If different: was Copilot's version better, worse, or just different style?

### Step 8.4: Push on an edge case

Try this prompt:

```
Write a query that lists every customer's name along with their most
recent order date, or NULL if they have never placed an order.
```

This is a slightly harder query (it involves an aggregate plus a LEFT JOIN). In your notebook:

1. Did Copilot's query handle the "never placed an order" case correctly?
2. Did it use LEFT JOIN, or did it accidentally exclude Henry?
3. Run the query. Does Henry appear in the result with a NULL `order_date`?

For reference, a correct query looks like:

```sql
SELECT
    c.first_name,
    c.last_name,
    MAX(o.order_date) AS most_recent_order
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY most_recent_order DESC NULLS LAST;
```

### Step 8.5: The takeaway

Copilot is generally very good at SQL of this complexity. The kinds of mistakes to watch for are:

- **Forgetting LEFT JOIN** when the question implies "even if there are no matches." This is the most common error.
- **Forgetting DISTINCT** in `COUNT(DISTINCT ...)` when counting through a join.
- **Mixing up `WHERE` and `HAVING`**, especially for filters that involve aggregates.
- **Inventing column names** that do not exist in your schema. Always verify against `\d table_name`.

The right workflow for using Copilot on real database work is: ask Copilot for a query, run it, and check the result against your understanding of the question. If the result feels off, ask Copilot to explain its query line by line; this often surfaces the assumption that was wrong.

---

## Part 9: Reflection

Answer in your notebook. These are open-ended; spend at least ten minutes.

1. **The shape of SQL.** SQL is a declarative language: you describe *what* you want, not *how* to get it. Pick one query you wrote (e.g., the customer lifetime spend query from Step 7.5) and write a few sentences describing what the query says in plain English. Now imagine writing the same logic in Python with explicit loops. Which version is shorter? Which is clearer? In what situations would you choose one over the other?

2. **LEFT JOIN vs INNER JOIN.** Step 7.5 used a LEFT JOIN to make sure Henry (a customer with no orders) appeared in the result with a total of $0. If the query had used INNER JOIN, Henry would have silently dropped out. In production code, would you rather have a query that silently drops rows or a query that surfaces them with NULL values? Why?

3. **NULL semantics.** SQL's three-valued logic (TRUE, FALSE, UNKNOWN) is one of its sharpest edges. The query `WHERE email = NULL` returns no rows even when there are rows with NULL emails. Why does this happen? When would you actually want this behavior?

4. **DDL vs DML.** This lab treated DDL and DML separately. In a real production deployment, who runs DDL (CREATE, ALTER, DROP) statements, and who runs DML (INSERT, UPDATE, DELETE)? Are they the same people? The same processes? What is the cost of mixing them up?

5. **The destructive operations.** `DROP TABLE`, `DELETE` without WHERE, `UPDATE` without WHERE, `TRUNCATE`. Each one can destroy data in milliseconds. What practices (technical and procedural) would you adopt in a real team to protect against accidents?

6. **What is missing?** This lab's schema is intentionally tiny. List three things you would want to add before deploying this schema in a real e-commerce application. (Hints: think about who can see the data, what happens when a customer changes their email, how prices change over time.)

7. **AI as a SQL partner.** Based on Part 8, what is the right division of labor between you and Copilot for SQL work? Where does Copilot accelerate you, and where does it create risk?

---

## Part 10: Tear Down

When you are done with the lab, stop and remove the container:

```bash
docker stop sql-lab
docker rm sql-lab
```

The container is gone; the data is gone. The image is still on your machine (so the next `docker run postgres:17-alpine` is fast). To remove the image too:

```bash
docker rmi postgres:17-alpine
```

If you want to keep the data across container restarts, use a Docker volume:

```bash
docker run --name sql-lab \
  -e POSTGRES_PASSWORD=lab \
  -e POSTGRES_DB=sqllab \
  -p 5432:5432 \
  -v sql-lab-data:/var/lib/postgresql/data \
  -d postgres:17-alpine
```

The `-v sql-lab-data:/var/lib/postgresql/data` flag mounts a named volume to PostgreSQL's data directory. When you stop and remove the container, the volume persists. The next `docker run` (with the same `-v`) reuses the same data.

---

## Reference: The SQL Clauses in Execution Order

Every SELECT query has clauses in this written order:

```
SELECT     columns
FROM       table
[JOIN]     other_table ON condition
WHERE      row_filter
GROUP BY   group_columns
HAVING     group_filter
ORDER BY   sort_columns
LIMIT      n
```

But they execute in a different order:

```
1. FROM / JOIN     (build the working set of rows)
2. WHERE           (filter rows)
3. GROUP BY        (collapse rows into groups)
4. HAVING          (filter groups)
5. SELECT          (compute the output columns)
6. DISTINCT        (eliminate duplicates)
7. ORDER BY        (sort the result)
8. LIMIT           (truncate the result)
```

Understanding this order explains why:

- You cannot use a column alias from SELECT in the WHERE clause (the alias does not exist yet at WHERE time).
- You can use a column alias in ORDER BY (because ORDER BY runs after SELECT).
- WHERE cannot use aggregate functions like `SUM` (the aggregates do not exist until GROUP BY runs).
- HAVING can use aggregate functions (it runs after GROUP BY).

---

## Reference: The Join Types

| Type | Returns | When to use |
|------|---------|-------------|
| `INNER JOIN` (or just `JOIN`) | Only rows with a match in both tables | "Show me orders with their customer info." Both sides must exist. |
| `LEFT JOIN` (or `LEFT OUTER JOIN`) | Every row from the left table, plus matches from the right (NULL where no match) | "Show me every customer and their orders, if any." |
| `RIGHT JOIN` (or `RIGHT OUTER JOIN`) | Mirror of LEFT JOIN. Every row from the right table, plus matches from the left | Almost never used; rewrite as LEFT JOIN with the tables swapped. |
| `FULL OUTER JOIN` | Every row from both tables, with NULLs where there is no match on the other side | Rare. Useful for reconciliation reports (e.g., "show me every customer in either system A or system B, matching them up where possible"). |
| `CROSS JOIN` | Every combination of every row in both tables (Cartesian product) | Rare; usually a bug if it happens by accident. Useful for generating combinations. |

This lab covered INNER and LEFT. The others are real and worth knowing about, but you can complete most analytical work with INNER and LEFT alone.

---

## Reference: psql Quick Reference

| Command | What it does |
|---------|--------------|
| `\l` | List all databases |
| `\c dbname` | Connect to a different database |
| `\dt` | List tables in the current database |
| `\d table_name` | Describe a table (columns, types, constraints, indexes) |
| `\df` | List functions |
| `\dn` | List schemas |
| `\du` | List users |
| `\timing` | Toggle showing query execution time |
| `\x` | Toggle expanded display (one column per row, useful for wide tables) |
| `\e` | Open the previous query in your editor |
| `\h SQL_KEYWORD` | Show help for a SQL statement (e.g., `\h SELECT`) |
| `\?` | Show all meta-commands |
| `\q` | Quit psql |

---

## Reference: Common SQL Idioms

Patterns you will see and use repeatedly:

| Pattern | Idiom |
|---------|-------|
| Count distinct values | `COUNT(DISTINCT column)` |
| Replace NULL with a default | `COALESCE(column, 0)` |
| Conditional column | `CASE WHEN x > 0 THEN 'positive' ELSE 'non-positive' END` |
| Find duplicates | `GROUP BY column HAVING COUNT(*) > 1` |
| Find missing rows (anti-join) | `LEFT JOIN ... WHERE other.id IS NULL` |
| Top N per group | More complex; uses window functions, beyond this lab. |
| Date arithmetic | `WHERE signup_date >= CURRENT_DATE - INTERVAL '30 days'` |

---

## Troubleshooting

**`docker: Cannot connect to the Docker daemon`.**
Docker is installed but not running. On macOS/Windows, start Docker Desktop. On Linux, run `sudo systemctl start docker`.

**`Bind for 0.0.0.0:5432 failed: port is already allocated`.**
Another process is using port 5432. Either you have another PostgreSQL running (stop it with `sudo systemctl stop postgresql` on Linux, or quit the conflicting Docker container), or change the host port in the docker run command: `-p 5433:5432` maps the container's 5432 to host 5433, and you would connect with `docker exec -it sql-lab psql -U postgres -d sqllab` (the in-container port is still 5432).

**`psql: error: connection to server ... failed: FATAL: role "postgres" does not exist`.**
You connected as the wrong user. Make sure your `docker exec` includes `-U postgres`.

**`ERROR: duplicate key value violates unique constraint "customers_email_key"`.**
You tried to insert a row with an email that already exists in the table. Either change the email value or delete the existing row first. This is the UNIQUE constraint doing its job.

**`ERROR: insert or update on table "orders" violates foreign key constraint "orders_customer_fk"`.**
You tried to insert an order whose `customer_id` does not exist in the `customers` table. Either insert the customer first or use a different customer_id.

**`ERROR: column "x" must appear in the GROUP BY clause or be used in an aggregate function`.**
This is the GROUP BY rule: every selected column must be either grouped or aggregated. Add the missing column to GROUP BY, or wrap it in an aggregate function like MAX or MIN.

**The query runs but returns 0 rows when you expected results.**
Check three things: (a) Are you in the right database? `SELECT current_database();`. (b) Did the seed actually load? `SELECT COUNT(*) FROM customers;`. (c) Is your WHERE clause too restrictive? Try removing it and adding it back one condition at a time.

**A query takes a long time and seems hung.**
For the data in this lab, no query should take more than a fraction of a second. If something hangs, you may have an open transaction blocking it. Press Ctrl+C in psql to cancel the query. To see what is happening: `SELECT * FROM pg_stat_activity;`.

**You typed something wrong and psql shows `sqllab-#` instead of `sqllab=#`.**
psql is waiting for you to finish a multi-line statement (the dash indicates an unclosed quote or unmatched parenthesis). Type a `;` and press Enter to try to finish it, or press Ctrl+C to abandon the partial query.

**You exited psql but the container is still running.**
That is fine; the container is the database server, psql is just the client. Reconnect with `docker exec -it sql-lab psql -U postgres -d sqllab`.

---

## Further Reading

- **PostgreSQL official documentation** at <https://www.postgresql.org/docs/current/>. The canonical reference. Chapters 4 (SQL syntax), 5 (data definition), 6 (data manipulation), and 7 (queries) cover everything in this lab in more depth.
- **PostgreSQL Tutorial** at <https://www.postgresqltutorial.com/>. A free, well-organized tutorial site with worked examples.
- **The official Postgres Docker image** at <https://hub.docker.com/_/postgres>. Authoritative reference for all the environment variables and configuration options the image supports.
- **CS50's Introduction to Databases with SQL** at <https://cs50.harvard.edu/sql/>. A free, Creative Commons-licensed full course on SQL, broken into seven manageable weeks. Recommended as the next step after this lab.
- **SQL Notes for Professionals** (GoalKicker) at <https://books.goalkicker.com/SQLBook/>. A free 166-page reference book organized by topic. Useful as a desk reference for syntax lookups.
- **Use the Index, Luke!** by Markus Winand at <https://use-the-index-luke.com/>. The free online book on database indexing. Not relevant to a basics lab, but the next thing to read when your queries start getting slow.
