# Lab 5-2: Spring Data JPA with PostgreSQL

---

## Overview

This lab walks you through building a Spring Boot application with a full MVC stack backed by Spring Data JPA and a PostgreSQL database running in a Docker container. You will map Java entity classes to PostgreSQL tables, declare repository interfaces, wire them into a service layer, and expose the data through a REST controller. Along the way you will observe the JPA entity lifecycle in practice and learn where the framework helps you and where it can surprise you.

By the end of this lab you will have:

- Started a PostgreSQL database in Docker and created the schema by hand
- Created a Spring Boot project with JPA, PostgreSQL JDBC, and Web dependencies
- Mapped two related PostgreSQL tables to Java entity classes using JPA annotations
- Declared a repository interface and seen Spring Data generate the implementation at startup
- Written service methods with correct transaction boundaries
- Exposed CRUD endpoints through a REST controller
- Observed lazy loading, dirty checking, and the N+1 query problem directly in the VS Code Debug Console

---

## Background - What JPA Does and Does Not Do

Spring Data JPA sits on top of the Java Persistence API, which is implemented by Hibernate. When you annotate a class with `@Entity` and a field with `@Id`, you are telling Hibernate how to map that Java object to a database row. Hibernate then manages the lifecycle of that object inside a session: it knows when you read it, when you change it, and when to flush those changes to PostgreSQL.

Hibernate generates SQL on your behalf, and that SQL is not always what you would write by hand. Two behaviours in particular deserve attention before you start:

**Dirty checking** means Hibernate compares the state of every managed entity to its snapshot at load time when the transaction commits. If anything changed, it issues an UPDATE automatically. You do not need to call `save()` for an entity you loaded within the same transaction. Calling `save()` on an already-managed entity is harmless but redundant.

**Lazy loading** means Hibernate does not fetch a related entity from the database until your code actually accesses it. This is efficient when you do not need the related data, but it fires an additional SQL statement every time you do. If you load a list of 50 products and then access each product's category in a loop, you produce 51 queries. This is the N+1 problem. You will observe it in this lab and then fix it.

---

## The Domain

You will build a simple product catalog API for a fictional retail company. The schema has two tables: `categories` and `products`. A category has many products. A product belongs to exactly one category.

This is a realistic, representative domain. It is small enough to understand immediately and rich enough to demonstrate the important JPA behaviours: a parent-child relationship, lazy loading across the association, and a query that crosses both tables.

---

## Part 1 - Start PostgreSQL and Create the Schema

You will run PostgreSQL in a Docker container and create the two tables manually before wiring Spring Data JPA. This is the recommended approach in a professional environment: own your DDL, do not let Hibernate generate it in production.

### Step 1.1 - Start the PostgreSQL container

In a terminal:

```bash
docker run --name catalog-db \
  -e POSTGRES_PASSWORD=labpass123 \
  -e POSTGRES_DB=catalog \
  -p 5432:5432 \
  -d postgres:17-alpine
```

Read the flags:

| Flag | What it does |
|------|--------------|
| `--name catalog-db` | Names the container so you can refer to it by name later. |
| `-e POSTGRES_PASSWORD=labpass123` | Sets the password for the default `postgres` superuser. |
| `-e POSTGRES_DB=catalog` | Creates an initial database called `catalog` when the container first starts. |
| `-p 5432:5432` | Maps the container's PostgreSQL port to the same port on the host. |
| `-d` | Runs in the background. |
| `postgres:17-alpine` | A small (~90 MB) PostgreSQL 17 image. |

The first time you run this, Docker downloads the image. Subsequent starts are instant. Confirm the container is up:

```bash
docker ps
```

You should see a row with `catalog-db` and STATUS `Up X seconds`.

If you already have a PostgreSQL container or another process bound to port 5432 on your host, change the host-side port to something free (for example `-p 5433:5432`) and remember to use that port in the JDBC URL in Part 2.

### Step 1.2 - Connect to the database with psql

```bash
docker exec -it catalog-db psql -U postgres -d catalog
```

You should see the psql prompt:

```
psql (17.x)
Type "help" for help.

catalog=#
```

You are now connected as the `postgres` superuser to the `catalog` database. Everything you type from here until `\q` is a SQL statement (or a backslash meta-command).

### Step 1.3 - Create the categories table

```sql
CREATE TABLE categories (
  category_id   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name          VARCHAR(100) NOT NULL,
  description   VARCHAR(500),
  created_date  DATE DEFAULT CURRENT_DATE NOT NULL
);
```

Expected output:

```
CREATE TABLE
```

Three things worth noticing in this DDL:

1. **`BIGINT GENERATED ALWAYS AS IDENTITY`** is the SQL standard syntax for an auto-incrementing primary key (added in SQL:2003, supported by PostgreSQL since version 10). It is equivalent in behaviour to `BIGSERIAL` but uses standard syntax. The `ALWAYS` modifier means the database will reject any INSERT that tries to specify the ID explicitly; this protects against accidental data corruption and aligns cleanly with Hibernate's `@GeneratedValue(strategy = IDENTITY)`.

2. **`VARCHAR(n)`** is the standard variable-length string type. PostgreSQL also supports `TEXT` (unlimited length), and the two have identical performance characteristics in Postgres. The length limit on `VARCHAR(n)` is a constraint, not an optimization.

3. **`DATE DEFAULT CURRENT_DATE`** uses standard SQL functions; no Postgres-specific syntax.

### Step 1.4 - Create the products table

```sql
CREATE TABLE products (
  product_id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  category_id   BIGINT        NOT NULL,
  name          VARCHAR(200)  NOT NULL,
  sku           VARCHAR(50)   UNIQUE NOT NULL,
  price         NUMERIC(10,2) NOT NULL,
  stock_qty     INTEGER       DEFAULT 0 NOT NULL,
  active        BOOLEAN       DEFAULT TRUE NOT NULL,
  CONSTRAINT fk_prod_cat FOREIGN KEY (category_id)
    REFERENCES categories(category_id)
);
```

Expected output:

```
CREATE TABLE
```

Two columns deserve a note:

- **`NUMERIC(10,2)`** is the standard SQL precise-decimal type, ideal for money. 10 total digits, 2 after the decimal point. PostgreSQL implements this with exact arithmetic (no binary floating-point), which is what you want for prices.
- **`BOOLEAN`** is a real first-class type in PostgreSQL. You can write `WHERE active = true` (or just `WHERE active`) and never have to remember which integer means "yes." Compare this to Oracle, which has no native boolean and uses `NUMBER(1)` with 1 and 0 by convention.

### Step 1.5 - Insert sample data

```sql
INSERT INTO categories (name, description) VALUES
  ('Electronics',     'Consumer electronics and accessories'),
  ('Office Supplies', 'Stationery, paper, and desk accessories'),
  ('Books',           'Technical and professional books');
```

Expected output:

```
INSERT 0 3
```

The `0` is a legacy field (it used to be the OID of the row in single-row inserts); ignore it. The `3` means three rows were inserted.

PostgreSQL auto-commits each statement when you are not inside an explicit transaction (`BEGIN ... COMMIT`), so no explicit `COMMIT;` is required after these inserts.

```sql
INSERT INTO products (category_id, name, sku, price, stock_qty) VALUES
  (1, 'Wireless Keyboard',                       'KBD-WL-001',  49.99, 120),
  (1, 'USB-C Hub 7-Port',                        'HUB-7C-002',  34.99,  85),
  (1, 'Monitor 27 Inch',                         'MON-27-003', 349.99,  22),
  (2, 'Ballpoint Pens 12-Pack',                  'PEN-BP-004',   6.99, 500),
  (2, 'Legal Pads 6-Pack',                       'PAD-LG-005',  12.49, 300),
  (3, 'Clean Code',                              'BK-CC-006',   39.99,  45),
  (3, 'Designing Data-Intensive Applications',   'BK-DD-007',   54.99,  30);
```

Expected output:

```
INSERT 0 7
```

Verify the data with a join:

```sql
SELECT p.name, p.sku, p.price, c.name AS category
FROM   products p
JOIN   categories c ON c.category_id = p.category_id
ORDER  BY c.name, p.name;
```

Expected output:

```
                 name                  |    sku     | price  |    category
---------------------------------------+------------+--------+-----------------
 Clean Code                            | BK-CC-006  |  39.99 | Books
 Designing Data-Intensive Applications | BK-DD-007  |  54.99 | Books
 Monitor 27 Inch                       | MON-27-003 | 349.99 | Electronics
 USB-C Hub 7-Port                      | HUB-7C-002 |  34.99 | Electronics
 Wireless Keyboard                     | KBD-WL-001 |  49.99 | Electronics
 Ballpoint Pens 12-Pack                | PEN-BP-004 |   6.99 | Office Supplies
 Legal Pads 6-Pack                     | PAD-LG-005 |  12.49 | Office Supplies
(7 rows)
```

You should see all seven products with their category names. If you do, the schema and seed are good.

Stay in psql for now; Step 2.2 will tell you when to exit.

---

## Part 2 - Create the Spring Boot Project

### Step 2.1 - Confirm VS Code extensions

This lab requires two VS Code extension packs. Open the Extensions view (`Ctrl+Shift+X`) and confirm each is installed and enabled. If any is missing, install it and reload VS Code when prompted.

| Extension | Publisher | Why this lab needs it |
|-----------|-----------|------------------------|
| Extension Pack for Java | Microsoft | Java language server, Maven integration, Run/Debug CodeLens above `main()` methods. |
| Spring Boot Extension Pack | VMware | Spring Boot dashboard, `application.yaml` IntelliSense, JPA query validation. |

The Extension Pack for Java is the standard requirement across this bootcamp's Java labs. If you have completed any earlier Java lab, it is already installed.

Part 8 of this lab exercises the REST endpoints using `curl` from the terminal. Confirm `curl` is available by running `curl --version` in a terminal. It is preinstalled on macOS and on most Linux distributions, and available out of the box in Windows 10/11 and in WSL.

### Step 2.2 - Generate the project from Spring Initializr

Open [https://start.spring.io](https://start.spring.io) and configure as follows:

| Setting | Value |
|---------|-------|
| Project | Maven |
| Language | Java |
| Spring Boot | Latest stable 3.x |
| Group | `com.example` |
| Artifact | `catalog` |
| Packaging | Jar |
| Java | 17 |

Also choose `yaml` for the configuration format.

Add the following dependencies:

- **Spring Web**
- **Spring Data JPA**
- **PostgreSQL Driver**
- **Spring Boot DevTools**
- **Validation**

Click **Generate** and unzip the archive into your workspace folder. In VS Code, open the project with **File > Open Folder** and select the unzipped `catalog` folder. When VS Code asks whether you trust the authors of the files in this folder, click **Yes, I trust the authors**.

The Java extension will start indexing the project and Maven will download dependencies. You will see "Java: Building..." and "Maven: importing..." progress messages in the status bar at the bottom of the window, and notification toasts in the bottom-right corner. Wait for these to complete before proceeding. The first import can take several minutes on a slow connection because Maven is downloading Spring Boot and Hibernate jars.

### Step 2.3 - Configure the datasource

Open `src/main/resources/application.yaml` and add the following. If you mapped the container to a different host port in Step 1.1, change the `5432` in the URL accordingly.

```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/catalog
    username: postgres
    password: labpass123
    driver-class-name: org.postgresql.Driver

  jpa:
    database-platform: org.hibernate.dialect.PostgreSQLDialect
    hibernate:
      ddl-auto: validate
    show-sql: true
    properties:
      hibernate:
        format_sql: true
```

Two settings here warrant explanation:

`ddl-auto: validate` tells Hibernate to compare its entity model against the actual database tables at startup. If the mapping does not match the schema, the application refuses to start and reports which column or table is missing. It never creates or drops anything. This is the appropriate setting when you own your DDL.

`show-sql: true` and `format_sql: true` together print every SQL statement Hibernate sends to PostgreSQL to the VS Code Debug Console. Keep these on throughout the lab. You will use the output to understand what Hibernate is actually doing.

### Step 2.4 - Create the package structure

In the Explorer panel on the left, right-click `src/main/java/com/example/catalog` and create these sub-packages:

```
com.example.catalog
├── controller
├── dto
├── entity
├── repository
└── service
```

---

## Part 3 - Map the Entity Classes

> Note:
> There are a number of TO NOTE comments in the provided code. These are *not* places to add code; all the code is already there. The purpose of the TO NOTE markers is to direct your attention to important JPA annotations and behaviours. Read the comment, understand the concept, then review the code that follows. Explanations for almost all of the TO NOTE markers are in the solutions file.

### Step 3.1 - Create the Category entity

Create `Category.java` in the `entity` package:

```java
package com.example.catalog.entity;

import jakarta.persistence.*;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "categories")
public class Category {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "category_id")
    private Long categoryId;

    @Column(name = "name", nullable = false, length = 100)
    private String name;

    @Column(name = "description", length = 500)
    private String description;

    @Column(name = "created_date")
    private LocalDate createdDate;

    // TO NOTE 14: The @PrePersist lifecycle callback below.
    //
    // The database column `created_date` is declared NOT NULL with DEFAULT CURRENT_DATE.
    // You might expect that omitting `createdDate` in Java code would let the database default
    // fire. It does not. Hibernate generates an INSERT that lists every entity column and
    // binds the Java field value, which for a freshly-constructed Category is NULL. PostgreSQL
    // then rejects the INSERT because an explicit NULL overrides the column DEFAULT.
    //
    // The fix is the @PrePersist callback below, which JPA invokes just before the INSERT
    // is sent to the database. It populates `createdDate` if the caller did not set one.
    // This pattern (automatically setting an audit field at persist time) is one of the most
    // common uses of JPA lifecycle callbacks in production code.
    @PrePersist
    protected void onCreate() {
        if (createdDate == null) {
            createdDate = LocalDate.now();
        }
    }

    // TO NOTE 1: Add the @OneToMany mapping to the products field below.
    // Use mappedBy = "category" (this refers to the field name on Product, not the column name).
    // Use FetchType.LAZY -- this is the default but declare it explicitly so the intent is clear.
    // Use cascade = CascadeType.ALL so saving a Category also saves its Products.
    @OneToMany(mappedBy = "category", fetch = FetchType.LAZY, cascade = CascadeType.ALL)
    private List<Product> products = new ArrayList<>();

    // Constructors

    public Category() {}

    public Category(String name, String description) {
        this.name = name;
        this.description = description;
    }

    // Getters and setters

    public Long getCategoryId() { return categoryId; }
    public void setCategoryId(Long categoryId) { this.categoryId = categoryId; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public LocalDate getCreatedDate() { return createdDate; }
    public void setCreatedDate(LocalDate createdDate) { this.createdDate = createdDate; }

    public List<Product> getProducts() { return products; }
    public void setProducts(List<Product> products) { this.products = products; }
}
```

### Step 3.2 - Create the Product entity

Create `Product.java` in the `entity` package:

```java
package com.example.catalog.entity;

import jakarta.persistence.*;
import java.math.BigDecimal;

@Entity
@Table(name = "products")
public class Product {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "product_id")
    private Long productId;

    // TO NOTE 2: Add the @ManyToOne mapping for the category field.
    // Use fetch = FetchType.LAZY.
    // Add @JoinColumn(name = "category_id", nullable = false).
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category_id", nullable = false)
    private Category category;

    @Column(name = "name", nullable = false, length = 200)
    private String name;

    @Column(name = "sku", unique = true, nullable = false, length = 50)
    private String sku;

    @Column(name = "price", nullable = false, precision = 10, scale = 2)
    private BigDecimal price;

    @Column(name = "stock_qty", nullable = false)
    private Integer stockQty = 0;

    @Column(name = "active", nullable = false)
    private Boolean active = true;

    // Constructors

    public Product() {}

    public Product(Category category, String name, String sku, BigDecimal price) {
        this.category = category;
        this.name = name;
        this.sku = sku;
        this.price = price;
    }

    // Getters and setters

    public Long getProductId() { return productId; }
    public void setProductId(Long productId) { this.productId = productId; }

    public Category getCategory() { return category; }
    public void setCategory(Category category) { this.category = category; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getSku() { return sku; }
    public void setSku(String sku) { this.sku = sku; }

    public BigDecimal getPrice() { return price; }
    public void setPrice(BigDecimal price) { this.price = price; }

    public Integer getStockQty() { return stockQty; }
    public void setStockQty(Integer stockQty) { this.stockQty = stockQty; }

    public Boolean getActive() { return active; }
    public void setActive(Boolean active) { this.active = active; }
}
```

### Step 3.3 - Start the application and read the startup log

Open `CatalogApplication.java`. Above the `public static void main` method, the Java extension renders two clickable text links: **Run | Debug**. Click **Run**. The application starts in the Debug Console pane at the bottom of the window (open it with **View > Debug Console** if it is not already visible). Watch the output carefully.

Because `ddl-auto=validate`, Hibernate will:

1. Query PostgreSQL's catalog tables to read the actual column definitions of `categories` and `products`
2. Compare those definitions against the fields on your entity classes
3. Either start cleanly or throw a `SchemaManagementException` if something does not match

A successful start looks like this in the console (the exact SQL will vary):

```
HibernateJpaVendorAdapter - Hibernate ORM core version ...
SchemaValidator - Validated schema for table [categories]
SchemaValidator - Validated schema for table [products]
Started CatalogApplication in X.XXX seconds
```

If you see a `SchemaManagementException`, the most common cause is a column name mismatch between your `@Column(name = ...)` annotation and the actual PostgreSQL column name. Compare the error message to the DDL from Step 1.3 and correct the annotation.

> **A note on case sensitivity.** PostgreSQL folds unquoted identifiers to lowercase by default. The DDL `CREATE TABLE categories` creates a table named `categories` (lowercase). Your `@Table(name = "categories")` annotation matches because Hibernate sends the name as you wrote it, which Postgres folds to lowercase to match. If you ever quote an identifier in DDL (`CREATE TABLE "Categories"`), Postgres preserves the case and you have to match it exactly in the annotation. Don't quote identifiers unless you genuinely need to.

---

## Part 4 - Declare the Repositories

### Step 4.1 - Create the CategoryRepository

Create `CategoryRepository.java` in the `repository` package:

```java
package com.example.catalog.repository;

import com.example.catalog.entity.Category;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface CategoryRepository extends JpaRepository<Category, Long> {

    // TO NOTE 3: Add a derived query method that finds a Category by its name field.
    // The method signature should be:
    //   Optional<Category> findByName(String name);
    // Spring Data will parse "findByName" and generate:
    //   SELECT c FROM Category c WHERE c.name = :name
    Optional<Category> findByName(String name);

    // TO NOTE 4: Add a native query that returns all categories ordered by name.
    // Use @Query(value = "...", nativeQuery = true).
    // Native queries use PostgreSQL SQL syntax and column names, not Java field names.
    @Query(value = "SELECT * FROM categories ORDER BY name ASC", nativeQuery = true)
    List<Category> findAllOrderedByName();
}
```

### Step 4.2 - Create the ProductRepository

Create `ProductRepository.java` in the `repository` package:

```java
package com.example.catalog.repository;

import com.example.catalog.entity.Product;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {

    // Derived query: Spring Data generates WHERE sku = :sku from the method name
    Optional<Product> findBySku(String sku);

    // Derived query with two conditions: WHERE active = :active AND category.categoryId = :categoryId
    List<Product> findByActiveAndCategoryCategoryId(Boolean active, Long categoryId);

    // Derived query with a price range: WHERE price BETWEEN :min AND :max
    List<Product> findByPriceBetween(BigDecimal min, BigDecimal max);

    // TO NOTE 5: Add a JPQL query that fetches products and eagerly joins their category
    // in a single SQL statement. This prevents the N+1 problem when you later need
    // category data alongside the product.
    //
    // JPQL operates on Java class and field names, not table and column names.
    // The query is:
    //   SELECT p FROM Product p JOIN FETCH p.category WHERE p.active = true
    //
    // Use @Query("...") without nativeQuery = true.
    @Query("SELECT p FROM Product p JOIN FETCH p.category WHERE p.active = true")
    List<Product> findAllActiveWithCategory();

    // TO NOTE 6: Add a native PostgreSQL SQL query that returns the top 5 most expensive
    // active products. The FETCH FIRST syntax used here is standard SQL:2008,
    // supported by PostgreSQL natively.
    // Mark it with @Query(value = "...", nativeQuery = true).
    @Query(value = """
            SELECT * FROM products
            WHERE  active = true
            ORDER  BY price DESC
            FETCH  FIRST 5 ROWS ONLY
            """, nativeQuery = true)
    List<Product> findTop5MostExpensive();
}
```

---

## Part 5 - Define the DTOs

Returning JPA entity objects directly from a REST controller is a common anti-pattern. The entity's field set is driven by the database schema, not by what the API consumer needs. Exposing entities also risks accidentally serializing lazy-loaded associations, which triggers additional queries or throws a `LazyInitializationException` after the session closes.

Use dedicated DTO (Data Transfer Object) classes for responses.

### Step 5.1 - Create CategoryDto

Create `CategoryDto.java` in the `dto` package:

```java
package com.example.catalog.dto;

public class CategoryDto {

    private Long categoryId;
    private String name;
    private String description;

    // Constructor used by the service layer to map from the entity
    public CategoryDto(Long categoryId, String name, String description) {
        this.categoryId = categoryId;
        this.name = name;
        this.description = description;
    }

    public Long getCategoryId() { return categoryId; }
    public String getName() { return name; }
    public String getDescription() { return description; }
}
```

### Step 5.2 - Create ProductDto

Create `ProductDto.java` in the `dto` package:

```java
package com.example.catalog.dto;

import java.math.BigDecimal;

public class ProductDto {

    private Long productId;
    private String name;
    private String sku;
    private BigDecimal price;
    private Integer stockQty;
    private Boolean active;
    private String categoryName;  // flattened from the Category association

    public ProductDto(Long productId, String name, String sku,
                      BigDecimal price, Integer stockQty,
                      Boolean active, String categoryName) {
        this.productId = productId;
        this.name = name;
        this.sku = sku;
        this.price = price;
        this.stockQty = stockQty;
        this.active = active;
        this.categoryName = categoryName;
    }

    public Long getProductId() { return productId; }
    public String getName() { return name; }
    public String getSku() { return sku; }
    public BigDecimal getPrice() { return price; }
    public Integer getStockQty() { return stockQty; }
    public Boolean getActive() { return active; }
    public String getCategoryName() { return categoryName; }
}
```

### Step 5.3 - Create ProductCreateRequest

Create `ProductCreateRequest.java` in the `dto` package. This is the inbound request body for creating a new product.

```java
package com.example.catalog.dto;

import jakarta.validation.constraints.*;
import java.math.BigDecimal;

public class ProductCreateRequest {

    @NotNull
    private Long categoryId;

    @NotBlank
    @Size(max = 200)
    private String name;

    @NotBlank
    @Size(max = 50)
    private String sku;

    @NotNull
    @DecimalMin(value = "0.01")
    private BigDecimal price;

    @NotNull
    @Min(0)
    private Integer stockQty;

    public Long getCategoryId() { return categoryId; }
    public void setCategoryId(Long categoryId) { this.categoryId = categoryId; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getSku() { return sku; }
    public void setSku(String sku) { this.sku = sku; }

    public BigDecimal getPrice() { return price; }
    public void setPrice(BigDecimal price) { this.price = price; }

    public Integer getStockQty() { return stockQty; }
    public void setStockQty(Integer stockQty) { this.stockQty = stockQty; }
}
```

---

## Part 6 - Implement the Service Layer

### Step 6.1 - Create ProductService

Create `ProductService.java` in the `service` package. This is where the transaction boundaries live.

```java
package com.example.catalog.service;

import com.example.catalog.dto.ProductCreateRequest;
import com.example.catalog.dto.ProductDto;
import com.example.catalog.entity.Category;
import com.example.catalog.entity.Product;
import com.example.catalog.repository.CategoryRepository;
import com.example.catalog.repository.ProductRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.NoSuchElementException;

@Service
public class ProductService {

    private final ProductRepository productRepository;
    private final CategoryRepository categoryRepository;

    public ProductService(ProductRepository productRepository,
                          CategoryRepository categoryRepository) {
        this.productRepository = productRepository;
        this.categoryRepository = categoryRepository;
    }

    // Read-only transaction: JPA skips dirty checking, PostgreSQL can optimise locking
    @Transactional(readOnly = true)
    public List<ProductDto> findAllActive() {
        // TO NOTE 7: Call productRepository.findAllActiveWithCategory() to fetch active
        // products with their category in a single JOIN FETCH query.
        // Map each Product to a ProductDto using the private toDto() method below.
        // Return the mapped list.
        return productRepository.findAllActiveWithCategory()
                .stream()
                .map(this::toDto)
                .toList();
    }

    @Transactional(readOnly = true)
    public ProductDto findById(Long id) {
        // TO NOTE 8: Use productRepository.findById(id).
        // If the Optional is empty, throw new NoSuchElementException("Product not found: " + id).
        // Otherwise map and return the ProductDto.
        return productRepository.findById(id)
                .map(this::toDto)
                .orElseThrow(() -> new NoSuchElementException("Product not found: " + id));
    }

    @Transactional
    public ProductDto create(ProductCreateRequest request) {
        // TO NOTE 9: Load the Category from categoryRepository.findById(request.getCategoryId()).
        // If absent, throw NoSuchElementException("Category not found: " + request.getCategoryId()).
        //
        // Construct a new Product entity:
        //   product.setCategory(category);
        //   product.setName(request.getName());
        //   product.setSku(request.getSku());
        //   product.setPrice(request.getPrice());
        //   product.setStockQty(request.getStockQty());
        //
        // Call productRepository.save(product) and return the mapped DTO.
        //
        // Note: the product is new (not yet managed), so save() is required here.
        // After the first save(), the entity becomes managed for the rest of this transaction.
        Category category = categoryRepository.findById(request.getCategoryId())
                .orElseThrow(() -> new NoSuchElementException(
                        "Category not found: " + request.getCategoryId()));

        Product product = new Product();
        product.setCategory(category);
        product.setName(request.getName());
        product.setSku(request.getSku());
        product.setPrice(request.getPrice());
        product.setStockQty(request.getStockQty());

        Product saved = productRepository.save(product);
        return toDto(saved);
    }

    @Transactional
    public ProductDto adjustStock(Long id, int delta) {
        // TO NOTE 10: Load the product by ID (throw NoSuchElementException if absent).
        //
        // Update the stock quantity:
        //   product.setStockQty(product.getStockQty() + delta);
        //
        // DO NOT call productRepository.save().
        //
        // Because the product is now a MANAGED entity inside this @Transactional method,
        // Hibernate's dirty checking will detect the field change automatically and issue
        // an UPDATE when the transaction commits. You do not need an explicit save() call.
        //
        // Notice the `System.out.println` line below, just before the return:
        //   System.out.println("No explicit save() called -- dirty checking handles the UPDATE");
        // Run the endpoint and verify the UPDATE appears in the Debug Console anyway.
        Product product = productRepository.findById(id)
                .orElseThrow(() -> new NoSuchElementException("Product not found: " + id));

        product.setStockQty(product.getStockQty() + delta);

        System.out.println("No explicit save() called -- dirty checking handles the UPDATE");
        return toDto(product);
    }

    @Transactional
    public void deactivate(Long id) {
        Product product = productRepository.findById(id)
                .orElseThrow(() -> new NoSuchElementException("Product not found: " + id));
        product.setActive(false);
        // Again: no save() needed. Dirty checking will issue the UPDATE.
    }

    // Private mapping helper. Accesses product.getCategory().getName(),
    // which is safe here because this method is always called inside
    // an open transaction (the caller's @Transactional boundary).
    private ProductDto toDto(Product product) {
        return new ProductDto(
                product.getProductId(),
                product.getName(),
                product.getSku(),
                product.getPrice(),
                product.getStockQty(),
                product.getActive(),
                product.getCategory().getName()   // triggers lazy load if not already fetched
        );
    }
}
```

### Step 6.2 - Create CategoryService

Create `CategoryService.java` in the `service` package:

```java
package com.example.catalog.service;

import com.example.catalog.dto.CategoryDto;
import com.example.catalog.entity.Category;
import com.example.catalog.repository.CategoryRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.NoSuchElementException;

@Service
public class CategoryService {

    private final CategoryRepository categoryRepository;

    public CategoryService(CategoryRepository categoryRepository) {
        this.categoryRepository = categoryRepository;
    }

    @Transactional(readOnly = true)
    public List<CategoryDto> findAll() {
        return categoryRepository.findAllOrderedByName()
                .stream()
                .map(this::toDto)
                .toList();
    }

    @Transactional(readOnly = true)
    public CategoryDto findById(Long id) {
        return categoryRepository.findById(id)
                .map(this::toDto)
                .orElseThrow(() -> new NoSuchElementException("Category not found: " + id));
    }

    @Transactional
    public CategoryDto create(String name, String description) {
        // TO NOTE 11: Check whether a category with this name already exists
        // using categoryRepository.findByName(name).
        // If present, throw new IllegalArgumentException("Category already exists: " + name).
        // Otherwise construct a new Category entity, call categoryRepository.save(), and return the DTO.
        categoryRepository.findByName(name).ifPresent(existing -> {
            throw new IllegalArgumentException("Category already exists: " + name);
        });

        Category category = new Category(name, description);
        Category saved = categoryRepository.save(category);
        return toDto(saved);
    }

    private CategoryDto toDto(Category category) {
        return new CategoryDto(
                category.getCategoryId(),
                category.getName(),
                category.getDescription()
        );
    }
}
```

---

## Part 7 - Implement the Controllers

### Step 7.1 - Create ProductController

Create `ProductController.java` in the `controller` package:

```java
package com.example.catalog.controller;

import com.example.catalog.dto.ProductCreateRequest;
import com.example.catalog.dto.ProductDto;
import com.example.catalog.service.ProductService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;

@RestController
@RequestMapping("/api/v1/products")
public class ProductController {

    private final ProductService productService;

    public ProductController(ProductService productService) {
        this.productService = productService;
    }

    @GetMapping
    public List<ProductDto> getAll() {
        return productService.findAllActive();
    }

    @GetMapping("/{id}")
    public ResponseEntity<ProductDto> getById(@PathVariable Long id) {
        try {
            return ResponseEntity.ok(productService.findById(id));
        } catch (NoSuchElementException e) {
            return ResponseEntity.notFound().build();
        }
    }

    @PostMapping
    public ResponseEntity<ProductDto> create(@Valid @RequestBody ProductCreateRequest request) {
        try {
            ProductDto created = productService.create(request);
            return ResponseEntity.status(HttpStatus.CREATED).body(created);
        } catch (NoSuchElementException e) {
            return ResponseEntity.badRequest().build();
        }
    }

    // TO NOTE 12: Implement the PATCH /api/v1/products/{id}/stock endpoint.
    // It should read a "delta" integer from the request body (use Map<String, Integer>).
    // Call productService.adjustStock(id, delta) and return 200 OK with the updated DTO.
    // Return 404 if the product is not found.
    @PatchMapping("/{id}/stock")
    public ResponseEntity<ProductDto> adjustStock(@PathVariable Long id,
                                                  @RequestBody Map<String, Integer> body) {
        try {
            int delta = body.getOrDefault("delta", 0);
            return ResponseEntity.ok(productService.adjustStock(id, delta));
        } catch (NoSuchElementException e) {
            return ResponseEntity.notFound().build();
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deactivate(@PathVariable Long id) {
        try {
            productService.deactivate(id);
            return ResponseEntity.noContent().build();
        } catch (NoSuchElementException e) {
            return ResponseEntity.notFound().build();
        }
    }
}
```

### Step 7.2 - Create CategoryController

Create `CategoryController.java` in the `controller` package:

```java
package com.example.catalog.controller;

import com.example.catalog.dto.CategoryDto;
import com.example.catalog.service.CategoryService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;

@RestController
@RequestMapping("/api/v1/categories")
public class CategoryController {

    private final CategoryService categoryService;

    public CategoryController(CategoryService categoryService) {
        this.categoryService = categoryService;
    }

    @GetMapping
    public List<CategoryDto> getAll() {
        return categoryService.findAll();
    }

    @GetMapping("/{id}")
    public ResponseEntity<CategoryDto> getById(@PathVariable Long id) {
        try {
            return ResponseEntity.ok(categoryService.findById(id));
        } catch (NoSuchElementException e) {
            return ResponseEntity.notFound().build();
        }
    }

    // TO NOTE 13: Implement POST /api/v1/categories.
    // Read "name" and "description" from the request body (use Map<String, String>).
    // Call categoryService.create(name, description).
    // Return 201 CREATED with the CategoryDto body.
    // Return 400 BAD REQUEST if an IllegalArgumentException is thrown (duplicate name).
    @PostMapping
    public ResponseEntity<CategoryDto> create(@RequestBody Map<String, String> body) {
        try {
            String name = body.get("name");
            String description = body.get("description");
            CategoryDto created = categoryService.create(name, description);
            return ResponseEntity.status(HttpStatus.CREATED).body(created);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        }
    }
}
```

---

## Part 8 - Test the Application

### Step 8.1 - Start the application and read the SQL log

If the application is not still running from Step 3.3, click the **Run** link above `main()` in `CatalogApplication.java`. You will see Hibernate's validation queries in the Debug Console, followed by the Spring Boot startup banner.

Once started, confirm it is listening: open `http://localhost:8080/api/v1/categories` in a browser. You should see a JSON array of the three categories inserted in Part 1.

### Step 8.2 - Exercise the endpoints with curl

You will exercise each REST endpoint from a terminal using `curl`. Keep your editor with the Spring Boot logs visible (the Debug Console) on one side of the screen and a terminal open on the other. After each `curl` command, switch to the Debug Console to read the SQL that Hibernate emitted.

Every command below includes the `-i` flag, which prints the HTTP status line and response headers before the body. This lets you see the difference between 200 OK, 201 Created, 204 No Content, and 4xx error responses. The response body comes after a blank line.

If you would like prettier JSON output, pipe the response through `jq` (install with `apt install jq`, `brew install jq`, or equivalent). Otherwise the raw JSON is readable enough for this lab.

Run each command in order. Read the response in the terminal, then switch to the Debug Console to see the SQL.

**List all categories** (ordered by name; uses the native query in `CategoryRepository`):

```bash
curl -i http://localhost:8080/api/v1/categories
```

**Get a single category**:

```bash
curl -i http://localhost:8080/api/v1/categories/1
```

**List all active products** (uses the `JOIN FETCH` query; one SQL statement):

```bash
curl -i http://localhost:8080/api/v1/products
```

**Get a single product**:

```bash
curl -i http://localhost:8080/api/v1/products/1
```

**Create a new product** (expect `201 Created`):

```bash
curl -i -X POST http://localhost:8080/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{
    "categoryId": 1,
    "name": "Mechanical Keyboard TKL",
    "sku": "KBD-MK-008",
    "price": 89.99,
    "stockQty": 60
  }'
```

**Adjust stock** (positive or negative delta; expect `200 OK`):

```bash
curl -i -X PATCH http://localhost:8080/api/v1/products/1/stock \
  -H "Content-Type: application/json" \
  -d '{"delta": -5}'
```

**Deactivate a product** (soft delete; expect `204 No Content`, empty body):

```bash
curl -i -X DELETE http://localhost:8080/api/v1/products/7
```

**Create a duplicate category** (triggers the duplicate-name check; expect `400 Bad Request`):

```bash
curl -i -X POST http://localhost:8080/api/v1/categories \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Electronics",
    "description": "Duplicate attempt"
  }'
```

**Create a new category successfully** (expect `201 Created`):

```bash
curl -i -X POST http://localhost:8080/api/v1/categories \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Peripherals",
    "description": "Keyboards, mice, and monitors"
  }'
```

### Step 8.3 - Observe the SQL that Hibernate generates

Run the **List all active products** curl command and switch to the Debug Console. You should see exactly one SELECT statement, including a JOIN, because `findAllActiveWithCategory()` uses `JOIN FETCH`:

```sql
SELECT p1_0.product_id,
       p1_0.active,
       c1_0.category_id,
       c1_0.created_date,
       c1_0.description,
       c1_0.name,
       p1_0.name,
       p1_0.price,
       p1_0.sku,
       p1_0.stock_qty
FROM   products p1_0
JOIN   categories c1_0 ON c1_0.category_id = p1_0.category_id
WHERE  p1_0.active = true
```

One query. All seven products. All category names. This is what you want.

> **A note on the WHERE clause.** Hibernate generates `WHERE p1_0.active = true` because the `active` column is a real `BOOLEAN` in PostgreSQL. If you were running against a database without native boolean support (such as Oracle, which uses `NUMBER(1)`), Hibernate would generate `WHERE active = 1` instead. The Java code does not change; the dialect handles the translation.

### Step 8.4 - Run the stock adjustment and observe dirty checking

Run the **Adjust stock** curl command. In the Debug Console you will see your `System.out.println` message followed by an UPDATE that Hibernate issued even though your code never called `save()`:

```sql
update products
set    active=?,
       category_id=?,
       name=?,
       price=?,
       sku=?,
       stock_qty=?
where  product_id=?
```

Hibernate detected that `stockQty` changed between when the entity was loaded and when the transaction committed. It generated the UPDATE automatically. This is dirty checking in action.

Notice that Hibernate updates *every* column in the entity, not just `stock_qty`. This is the default Hibernate behaviour and is usually what you want (it makes UPDATE statement caching more effective). If you need to update only changed columns, add `@DynamicUpdate` to the entity class; this is rarely worth it in practice.

---

## (Challenge) Part 9 - Observe and Fix the N+1 Problem

This part demonstrates the most common JPA performance mistake and shows you how to diagnose and correct it.

### Step 9.1 - Create a broken endpoint that triggers N+1

Add the following method to `ProductRepository`:

```java
// This method does NOT use JOIN FETCH -- it returns products without their category
List<Product> findByActiveTrue();
```

Add the following method to `ProductService`:

```java
@Transactional(readOnly = true)
public List<ProductDto> findAllActiveNPlusOne() {
    // WARNING: this method demonstrates the N+1 problem.
    // It loads products without their category, then accesses
    // product.getCategory() in toDto(), which fires one additional
    // SELECT per product.
    return productRepository.findByActiveTrue()
            .stream()
            .map(this::toDto)
            .toList();
}
```

Add the following endpoint to `ProductController`:

```java
@GetMapping("/n-plus-one-demo")
public List<ProductDto> nPlusOneDemo() {
    return productService.findAllActiveNPlusOne();
}
```

### Step 9.2 - Run the broken endpoint and count the queries

Run the new endpoint with curl:

```bash
curl -i http://localhost:8080/api/v1/products/n-plus-one-demo
```

Switch to the Debug Console and count the SELECT statements. With seven active products you will see:

- 1 SELECT to load all products (no category join)
- Several additional SELECTs to load each distinct category when `toDto()` accesses `product.getCategory().getName()`

The number of additional queries depends on how many distinct categories are referenced. In this lab, with seven products spanning three categories, Hibernate fires roughly four queries total (one for the product list, three for the three categories, because Hibernate caches each category within the session after the first lookup). With a thousand products spanning a thousand categories, you would see 1001 queries.

Either way, the lesson is the same: a method that *looks* like it does one query is actually doing many, and the count scales with the data, not with the code.

### Step 9.3 - Understand why this happens

When Hibernate loads a product from the database with lazy loading on the category association, it does not fetch the category row. Instead it installs a proxy object in the `category` field. That proxy looks like a real `Category` to your Java code, but it has no data. The first time your code calls any method on the proxy (such as `getName()`), Hibernate fires a SELECT to load the real category from PostgreSQL.

Because `toDto()` calls `product.getCategory().getName()` for every product in the list, and each product has its own proxy pointing at potentially a different category, Hibernate fires a SELECT for each distinct category it has not already loaded in this session.

### Step 9.4 - Confirm the fix

The `findAllActiveWithCategory()` method in `ProductRepository` already contains the fix: `JOIN FETCH p.category`. Run the original `/api/v1/products` endpoint again and confirm you still see exactly one query. The `findByActiveTrue()` method and its N+1 path are left in place for comparison.

---

## Part 10 - Tear Down

When you are done with the lab, stop the application (click the red stop button in the floating debug toolbar at the top of the editor, or press `Ctrl+C` if the app is running in a terminal pane) and stop the container:

```bash
docker stop catalog-db
docker rm catalog-db
```

The container is gone. The data stored inside it is also gone. The image (`postgres:17-alpine`) remains on your machine so the next `docker run` starts in seconds.

If you want the database to persist across container restarts (so you do not have to recreate the schema next session), use a Docker volume:

```bash
docker run --name catalog-db \
  -e POSTGRES_PASSWORD=labpass123 \
  -e POSTGRES_DB=catalog \
  -p 5432:5432 \
  -v catalog-data:/var/lib/postgresql/data \
  -d postgres:17-alpine
```

The `-v catalog-data:/var/lib/postgresql/data` flag mounts a named volume to PostgreSQL's data directory. When you stop and remove the container, the volume persists. The next `docker run` (with the same `-v`) reuses the same data.

---

## Checkpoints

Answer these in writing or discuss with your instructor before closing the lab.

1. In `adjustStock()` you changed `stockQty` and did not call `save()`. The UPDATE still executed. Explain exactly when Hibernate detects the change and when it sends the UPDATE to PostgreSQL.

2. The `@Transactional(readOnly = true)` annotation is on several service methods. It does two things: it tells the Spring transaction manager to open a read-only transaction, and it gives Hibernate permission to skip dirty checking entirely. Why is skipping dirty checking a meaningful performance improvement in a method that returns a large list?

3. `findAllActiveWithCategory()` uses JPQL with `JOIN FETCH`. `findTop5MostExpensive()` uses a native SQL query. Give one reason you would choose native SQL over JPQL for a specific query in a PostgreSQL application.

4. The `toDto()` helper method accesses `product.getCategory().getName()`. This is safe in the service methods here because they are all `@Transactional`. What would happen if `toDto()` were called from inside the controller, after the service transaction had already closed? What exception would you see and why?

5. `ProductRepository` extends `JpaRepository<Product, Long>`. The `Long` type parameter is the type of the primary key. What would happen at application startup if you used `Integer` instead of `Long` while the PostgreSQL column was defined as `BIGINT GENERATED ALWAYS AS IDENTITY`?

---

## Challenge Exercises

Complete these independently. No solution is provided.

### Challenge 1 - Price range search endpoint

Add a GET endpoint at `/api/v1/products/search` that accepts `minPrice` and `maxPrice` as query parameters and returns the matching products. Use the existing `findByPriceBetween` derived query in the repository. Handle missing or invalid parameters gracefully.

### Challenge 2 - Products by category

Add a GET endpoint at `/api/v1/categories/{id}/products` that returns all active products in the given category. Use the derived query `findByActiveAndCategoryCategoryId` in `ProductRepository`. Return 404 if the category does not exist.

### Challenge 3 - Bidirectional traversal

The `Category` entity has a `List<Product>` field mapped with `@OneToMany`. Add a GET endpoint at `/api/v1/categories/{id}/summary` that returns the category name and the count of active products in it. Implement this without writing a new query: load the category with its products list and count in Java. Then consider what the implications are for a category with 50,000 products, and describe a better approach using `@Query`.

### Challenge 4 - Observe the entity lifecycle states

Add a `@PostConstruct` method to a new `@Component` class that:

1. Uses the `EntityManager` directly (inject via `@PersistenceContext`) to find a product by ID
2. Prints "Entity state: MANAGED"
3. Calls `entityManager.detach(product)`
4. Prints "Entity state: DETACHED"
5. Modifies a field on the detached product and calls `entityManager.merge(product)`
6. Prints "Entity state: MANAGED (after merge)"

Read the Hibernate SQL output at startup. This exercise makes the entity lifecycle states from the lecture slides concrete.

---

## Lab Summary

In this lab you:

- Ran PostgreSQL in a Docker container and created tables with primary keys using `GENERATED ALWAYS AS IDENTITY` and a foreign key constraint
- Mapped those tables to JPA entity classes using `@Entity`, `@Table`, `@Id`, `@GeneratedValue`, `@Column`, `@ManyToOne`, and `@OneToMany`
- Declared repository interfaces and observed Spring Data generate proxy implementations at startup
- Used derived query methods (`findBySku`, `findByPriceBetween`) and both JPQL and native queries via `@Query`
- Observed Hibernate's dirty checking issue an UPDATE without an explicit `save()` call
- Observed the N+1 query problem by loading lazy associations in a loop and fixed it with `JOIN FETCH`
- Placed `@Transactional` boundaries in the service layer and explained why they belong there rather than in the repository or controller

---

*End of Lab 5-2*
