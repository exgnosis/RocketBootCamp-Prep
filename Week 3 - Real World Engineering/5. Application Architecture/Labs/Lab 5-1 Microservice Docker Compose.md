# Lab 5-1: Running a Microservice with Docker Compose

## Overview

A microservice is a single, narrowly-scoped application that talks to other applications over a network, rather than calling them as in-process functions or sharing a database. The microservice pattern reshapes how software is built in modern industry: a single business application is no longer one monolithic process running on one server, but a collection of small services running in separate containers, each maintained by a small team and each replaceable without redeploying the rest. Real production microservice fleets at large companies run thousands of services orchestrated by Kubernetes; the underlying ideas, however, are the same as for the two-container example in this lab.

You will run a small product-catalog microservice on your machine. The service is a Spring Boot application that exposes a REST API for creating, reading, updating, and deleting products. The data is stored in a MongoDB database that runs in a separate Docker container. The two containers are orchestrated by Docker Compose, which sets up a private network between them, maps the ports, and starts them in the correct order. You will read the source code to understand how the application is layered, start the system, exercise the REST API with `curl`, and observe how the layers communicate through HTTP.

The lab is therefore part **architecture reading exercise** (read the Java code to understand the layers before running anything), part **orchestration exercise** (drive Docker Compose to start, observe, and shut down a multi-container system), and part **API exploration exercise** (exercise each REST endpoint with `curl` and see what each one does to the data).

**This lab is hands-on.** You drive the commands yourself; no AI assistance is needed or expected for the main exercises. The Copilot stretch in Part 7 has you use Copilot to *read* the codebase rather than generate code, which is one of the most useful real-world AI-assisted-development skills.

---

## Learning Objectives

By the end of this lab, you will be able to:

1. Identify the four layers of a typical Spring Boot REST application (controller, service interface, service implementation, repository) and explain what each one is responsible for.
2. Read a `docker-compose.yml` file and identify the services it defines, the ports it exposes, and the network it creates.
3. Start and stop a multi-container application with `docker compose up` and `docker compose down`.
4. Inspect running containers with `docker compose ps` and read the columns of its output.
5. Exercise a REST API from the command line with `curl`, including setting headers (`-H`), specifying HTTP methods (`-X POST`, `-X PUT`, `-X DELETE`), and posting JSON bodies (`-d`).
6. Explain the dependency-inversion concept that lets the service swap from MongoDB to PostgreSQL by replacing one implementation class.
7. Use Copilot to read an unfamiliar codebase: ask it to map the dependencies, identify the architectural pattern, and reason about what would change to accommodate a different backing store.

---

## Part 1: Set Up the Workspace

### Step 1.1: Verify prerequisites

Three tools must be installed before you start:

```bash
git --version
docker --version
docker compose version
```

You should see version output for all three. `git` 2.x and `docker` 24.x or later are recommended. The `docker compose` (with a space) command is the Compose V2 plugin built into modern Docker Desktop and Docker Engine; the older `docker-compose` (with a hyphen) was Compose V1 and is no longer maintained. This lab uses V2.

If any of these are missing, install them now:

- **Docker** at <https://docs.docker.com/get-docker/>. Docker Desktop on macOS and Windows; the Docker Engine package on Linux. Compose V2 is included automatically.
- **Git** at <https://git-scm.com/downloads>. Usually already installed on macOS and Linux.

On Linux, make sure your user is in the `docker` group so you can run Docker commands without `sudo`:

```bash
sudo usermod -aG docker $USER
```

Log out and back in for the group change to take effect.

### Step 1.2: Clone the repository

```bash
git clone https://github.com/ExgnosisClasses/RocketDemo1.git
cd RocketDemo1
```

If the repository is private to your training organization and the clone fails with a permission error, ask your instructor for the correct URL or for the credentials your bootcamp account needs to access it.

After cloning, look at the contents:

```bash
ls -1
```

You should see a `docker-compose.yml` file, a `Dockerfile`, a `pom.xml` (Maven build file), a `src/` directory containing the Java source, and probably a `README.md`.

### Step 1.3: Open the project in VS Code

```bash
code .
```

The Explorer panel on the left should show the project tree. The files you will be reading in Part 2 live under `src/main/java/`. The exact package path depends on the project's group ID; expand the `src/main/java/` tree to find files named `ProductController.java`, `Product.java`, `ProductService.java`, and `ProductServiceImpl.java`.

### Step 1.4: Create a lab notebook

Create a file called `notebook.md` at the root of the project. Start it with:

```markdown
# Microservice Lab Notebook

## Part 2: Reading the architecture

## Part 3: Starting the service

## Part 4: Inspecting the running containers

## Part 5: Exercising the API

## Part 6: Stopping the service

## Part 7: Stretch (Copilot reads the architecture)

## Part 8: Reflection
```

Save it.

---

## Part 2: Read the Architecture Before You Run Anything

The standard Spring Boot REST application has four layers, each with one job. Before you start the application, read each layer's source code and answer for yourself: what is this layer responsible for, and what does it not know about?

### Step 2.1: The REST controller

Open `ProductController.java`. Read it carefully. You will see something like:

```java
@RestController
public class ProductController {

    @Autowired
    private ProductService productService;

    @GetMapping("/products")
    public ResponseEntity<List<Product>> getAllProduct(){
        return ResponseEntity.ok().body(productService.getAllProducts());
    }

    @GetMapping("/products/{id}")
    public ResponseEntity<Product> getProductById(@PathVariable Integer id){
        return ResponseEntity.ok().body(productService.getProductById(id));
    }

    @PostMapping("/products")
    public ResponseEntity<Product> createProduct(@RequestBody Product product){
        return ResponseEntity.ok().body(this.productService.createProduct(product));
    }

    @PutMapping("/products/{id}")
    public ResponseEntity<Product> updateProduct(@PathVariable Integer id, @RequestBody Product product){
        product.setId(id);
        return ResponseEntity.ok().body(this.productService.updateProduct(product));
    }

    @DeleteMapping("/products/{id}")
    public HttpStatus deleteProduct(@PathVariable Integer id){
        this.productService.deleteProductById(id);
        return HttpStatus.OK;
    }
}
```

Write in your notebook, in your own words:

1. What does `@RestController` do? (Hint: you saw it in Lab 6-1.)
2. For each HTTP verb (GET, POST, PUT, DELETE), what is the method's job?
3. The controller has a field `private ProductService productService`. What is the type of this field, and where is it defined?
4. What does the controller know about *how* products are stored? Look hard. Is there any mention of MongoDB? Any database driver? Any SQL?

The answer to the fourth question is "no." The controller knows that it can ask a `productService` to get, create, update, or delete products; it has no idea what that service does to fulfill those requests. This is the central design move of the architecture.

### Step 2.2: The model

Open `Product.java`. You will see something like:

```java
@Document(collection = "ProductDB")
public class Product {
    @Id
    private Integer id;

    @NotBlank
    @Indexed(unique = true)
    private String name;
    private String description;

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
}
```

Note the annotations:

- **`@Document(collection = "ProductDB")`** is from Spring Data MongoDB. It tells the framework to store instances of this class in a MongoDB collection named `ProductDB`.
- **`@Id`** marks the field that is the unique identifier for each document.
- **`@Indexed(unique = true)`** asks MongoDB to maintain an index on `name` and to refuse duplicate values.
- **`@NotBlank`** is a Bean Validation annotation; it asks Spring to reject requests where `name` is null or empty.

This class is the bridge between the application's Java world and the database's document world. Jackson uses it to serialize Java objects to JSON when responding to REST calls; Spring Data Mongo uses it to map between Java objects and Mongo documents when reading and writing the database.

### Step 2.3: The service interface

Open `ProductService.java`. You will see something like:

```java
public interface ProductService {
    Product createProduct(Product product);
    Product updateProduct(Product product);

    List<Product> getAllProducts();
    Product getProductById(Integer productId);
    void deleteProductById(Integer productId);
}
```

This is the contract the controller depends on. The interface names the five operations the application supports, but says nothing about how they are implemented. The controller, when it writes `productService.createProduct(...)`, is calling a method whose implementation is decided at runtime by Spring's dependency injection.

### Step 2.4: The service implementation

Open `ProductServiceImpl.java`. You will see something like:

```java
@Service
@Transactional
public class ProductServiceImpl implements ProductService {

    @Autowired
    private ProductRepository productRepository;

    @Override
    public Product createProduct(Product product) {
        return productRepository.save(product);
    }

    @Override
    public Product updateProduct(Product product) {
        Optional<Product> productDb = this.productRepository.findById(product.getId());
        if (productDb.isPresent()) {
            Product productUpdate = productDb.get();
            productUpdate.setName(product.getName());
            productUpdate.setDescription(product.getDescription());
            productRepository.save(productUpdate);
            return productUpdate;
        } else {
            throw new ResourceNotFoundException("Product not found with id : " + product.getId());
        }
    }

    // ... other methods ...
}
```

This is where the controller's abstract requests turn into database calls. The `ProductRepository` field is itself a Spring Data interface (you will not find a `ProductRepositoryImpl`; Spring Data generates the implementation at runtime).

> **A note on `@Transactional` and MongoDB.** The original example marks the service `@Transactional`. MongoDB does support transactions starting from version 4.0, but only when running as a replica set, not in single-node mode. The Docker Compose setup in this lab runs Mongo as a single standalone node, so the `@Transactional` annotation has no effect at runtime. This is a small but real wart in many tutorial codebases; the annotation is harmless but not doing what the reader might assume.

### Step 2.5: The repository

Search the source tree for `ProductRepository.java`. You will find a small file like:

```java
public interface ProductRepository extends MongoRepository<Product, Integer> {
}
```

That is the whole file. The interface extends `MongoRepository<Product, Integer>` and inherits dozens of methods (`save`, `findById`, `findAll`, `deleteById`, and many more) that Spring Data implements automatically at runtime based on the parameterization. There is no Java code that explicitly opens a connection to Mongo, runs a query, or maps results to objects; the framework does all of that.

### Step 2.6: Put it together

In your notebook, sketch the layers as a diagram. The dependency arrows go *downward* (each layer depends only on the layer below it):

```
HTTP request
    |
    v
+--------------------------+
|  ProductController       |   knows: ProductService interface
|  (REST + JSON)           |
+--------------------------+
    |
    v
+--------------------------+
|  ProductService          |   defines: the operations
|  (interface)             |
+--------------------------+
    ^
    | implements
    |
+--------------------------+
|  ProductServiceImpl      |   knows: ProductRepository interface
|  (business logic)        |
+--------------------------+
    |
    v
+--------------------------+
|  ProductRepository       |   defines: the persistence operations
|  (interface)             |       (provided by Spring Data Mongo)
+--------------------------+
    |
    v
+--------------------------+
|  MongoDB                 |   storage
+--------------------------+
```

Notice that the controller depends on `ProductService` (the interface), not on `ProductServiceImpl` (the implementation). Similarly, the implementation depends on `ProductRepository` (the interface), not on any concrete database driver. This is **dependency inversion**: high-level code depends on abstractions, not on concrete details.

The practical consequence: if you wanted to swap MongoDB for PostgreSQL, you would:

1. Add the PostgreSQL JDBC driver and Spring Data JPA to `pom.xml`.
2. Create a `ProductRepository` that extends `JpaRepository<Product, Integer>` instead of `MongoRepository`.
3. Adjust the `Product` class's annotations from MongoDB-specific (`@Document`, `@Id` from `org.springframework.data.annotation`) to JPA-specific (`@Entity`, `@Id` from `jakarta.persistence`).
4. Update `docker-compose.yml` to start a PostgreSQL container instead of MongoDB and adjust environment variables.

The controller, the service interface, and the business logic in the service implementation would not change. That is the value of the abstraction.

---

## Part 3: Start the Service

### Step 3.1: Read the docker-compose.yml file

Open `docker-compose.yml`. Compose files declare services (one block per container), the network they share, and how they are wired together. A typical structure for this lab:

```yaml
services:
  mongo_db:
    image: mongo
    container_name: mongoDB
    ports:
      - "27017:27017"
    # ...

  productservice:
    build: .
    container_name: product-service-app
    ports:
      - "8080:8080"
    depends_on:
      - mongo_db
    # ...
```

Read each block in your file and write in your notebook:

1. What are the two services named?
2. What is each service's container name (the name you will see in `docker compose ps`)?
3. What ports are exposed on the host for each service?
4. Does the file declare which service must start first? (Look for `depends_on`.)

The `mongo_db` service uses a public image (`image: mongo`) downloaded from Docker Hub. The `productservice` uses `build: .`, which tells Compose to build a local image from the `Dockerfile` in the current directory.

> **A note on the `version:` line.** Older Compose files start with a line like `version: '3.8'`. Compose V2 ignores this attribute and prints a warning: `WARN[0000] the attribute 'version' is obsolete, it will be ignored, please remove it to avoid potential confusion`. You will see this warning on every command; it is harmless. If you want to silence it, delete the `version:` line from `docker-compose.yml`.

### Step 3.2: Start the system

```bash
docker compose up
```

The first time you run this, Docker:

1. Downloads the `mongo` image from Docker Hub (a few hundred MB).
2. Builds the Spring Boot image locally. This includes downloading Maven dependencies into the image, which is the slow part. Expect 5 to 15 minutes the first time.
3. Creates a private network and starts both containers on it.

Subsequent runs reuse the cached images and start in a few seconds.

Watch the logs as the containers start. The MongoDB container is ready when you see:

```
mongoDB | ... Waiting for connections on port 27017
```

The Spring Boot container is ready when you see something like:

```
product-service-app | ... Tomcat started on port 8080 (http) with context path '/'
product-service-app | ... Started ProductServiceApplication in X.YYY seconds
```

Leave this terminal running. The output is the live log of both services; you will see new log lines whenever you exercise the API in Part 5. Open a second terminal for the rest of the lab.

---

## Part 4: Inspect the Running Containers

### Step 4.1: List the containers

In the second terminal:

```bash
cd RocketDemo1   # navigate to the same project directory
docker compose ps
```

Expected output (the `WARN[0000]` line will appear and can be ignored):

```
NAME                  IMAGE             COMMAND                  SERVICE          CREATED         STATUS         PORTS
mongoDB               mongo             "docker-entrypoint.s..."  mongo_db         36 seconds ago  Up 35 seconds  0.0.0.0:27017->27017/tcp
product-service-app   product-service   "java -jar target/sp..."  productservice   36 seconds ago  Up 35 seconds  0.0.0.0:8080->8080/tcp
```

Read each column:

- **NAME**: the container's friendly name (set by `container_name:` in compose).
- **IMAGE**: the Docker image the container is running. `mongo` is from Docker Hub; `product-service` was built locally.
- **COMMAND**: the entry point that runs inside the container. The MongoDB container runs its built-in `docker-entrypoint.sh`. The Spring Boot container runs `java -jar target/spring-boot-application.jar` (truncated to fit).
- **SERVICE**: the service name from the compose file.
- **STATUS**: `Up X seconds` means the container is running and has been for that long.
- **PORTS**: the port mappings. `0.0.0.0:8080->8080/tcp` means "anything connecting to `localhost:8080` on the host is forwarded to port 8080 inside the container."

If the STATUS shows `Restarting` or `Exited`, something has gone wrong; see the Troubleshooting section.

### Step 4.2: Check Docker's view of the world

```bash
docker ps
```

This is the lower-level command; it lists *all* running containers, not just the ones managed by this Compose project. The output should include the same two containers, plus any others you might have running.

```bash
docker network ls
```

You should see an entry named `rocketdemo1_default` (or whatever the project directory is called, followed by `_default`). That is the private network Compose created for the two containers to talk to each other. The Spring Boot app connects to MongoDB via the network name `mongo_db` (the service name), not via `localhost`; Docker's internal DNS resolves the service name to the container's private IP on this network.

---

## Part 5: Exercise the API

The service is running. Time to call it.

### Step 5.1: Confirm the database is empty

```bash
curl "http://localhost:8080/products"
```

Expected output:

```
[]
```

An empty JSON array. The collection exists but has no documents.

### Step 5.2: Add a product (POST)

```bash
curl -X POST http://localhost:8080/products/ \
     -H "Content-Type: application/json" \
     -d '{ "id": 1, "name": "Mobile", "description": "Samsung Mobile." }'
```

Expected output:

```json
{"id":1,"name":"Mobile","description":"Samsung Mobile."}
```

The server echoed back the same product. The `Content-Type: application/json` header tells Spring's `@RequestBody` mechanism to use Jackson to parse the body. The `-d '...'` flag supplies the body content.

> **A note on the ID's type.** If you send `"id": "1"` (a string in quotes) instead of `"id": 1` (a number), Jackson will coerce the string to an Integer on input. The output will always be `"id":1` (a number) because the Java field is `Integer`. This is the kind of small JSON-vs-Java mismatch you should know exists; in production code you would tighten the contract by rejecting type mismatches.

### Step 5.3: Add two more

```bash
curl -X POST http://localhost:8080/products/ \
     -H "Content-Type: application/json" \
     -d '{ "id": 2, "name": "Apple", "description": "IPhone 14" }'

curl -X POST http://localhost:8080/products/ \
     -H "Content-Type: application/json" \
     -d '{ "id": 3, "name": "Blackberry", "description": "legacy" }'
```

Each call returns the created product. Now list them all:

```bash
curl "http://localhost:8080/products"
```

Expected output (the order may vary; MongoDB does not guarantee insertion order without an explicit sort):

```json
[{"id":1,"name":"Mobile","description":"Samsung Mobile."},{"id":2,"name":"Apple","description":"IPhone 14"},{"id":3,"name":"Blackberry","description":"legacy"}]
```

### Step 5.4: Get one by ID (GET)

```bash
curl "http://localhost:8080/products/2"
```

Expected output:

```json
{"id":2,"name":"Apple","description":"IPhone 14"}
```

### Step 5.5: Update a product (PUT)

```bash
curl -X PUT http://localhost:8080/products/2 \
     -H "Content-Type: application/json" \
     -d '{ "id": 2, "name": "Apple", "description": "IPhone 16" }'
```

Expected output:

```json
{"id":2,"name":"Apple","description":"IPhone 16"}
```

The description has changed from `IPhone 14` to `IPhone 16`. Confirm with a GET:

```bash
curl "http://localhost:8080/products/2"
```

### Step 5.6: Delete a product (DELETE)

```bash
curl -X DELETE http://localhost:8080/products/2
```

Expected output (the controller returns `HttpStatus.OK`, which serializes as a 200 status with no body, but the HTTP status text is included):

```
OK
```

Confirm the product is gone:

```bash
curl "http://localhost:8080/products"
```

The list should contain only the two remaining products (Mobile and Blackberry).

### Step 5.7: Trigger an error

What happens when you ask for a product that does not exist?

```bash
curl "http://localhost:8080/products/999"
```

You will see an error response, probably with a 500 status code and a JSON body containing a stack trace or a Spring error description. Look back at `ProductServiceImpl.getProductById`; if it throws a `ResourceNotFoundException` and the application has not configured a `@RestControllerAdvice` to translate that to a 404, you get a 500. This is exactly the kind of behavior that Lab 3-1's "no stack traces in error responses" property would address; a production version of this service would have a global exception handler.

Note in your notebook what error response you got. Is it appropriate for a public API? What would change it?

---

## Part 6: Stop the Service

### Step 6.1: Bring it all down

In the second terminal (the one not running `docker compose up`):

```bash
docker compose down
```

Expected output:

```
[+] Running 3/3
 ✔ Container product-service-app  Removed     0.3s
 ✔ Container mongoDB              Removed     0.3s
 ✔ Network rocketdemo1_default    Removed     0.1s
```

Both containers and the private network are removed. The images (the built artifacts) are not deleted; they remain in your local Docker cache so the next `docker compose up` is faster.

### Step 6.2: Confirm everything is gone

```bash
docker compose ps
```

Expected output:

```
NAME      IMAGE     COMMAND   SERVICE   CREATED   STATUS    PORTS
```

The table is empty.

### Step 6.3: A note about data

When you `docker compose down`, the MongoDB container is removed. The data MongoDB was storing was inside that container by default. After `down`, the products you created are gone.

To make the data persist across restarts, the Compose file would declare a *volume* mounted to MongoDB's data directory:

```yaml
mongo_db:
  image: mongo
  volumes:
    - mongo_data:/data/db

volumes:
  mongo_data:
```

The named volume `mongo_data` is managed by Docker and survives container deletion. This is a real production concern; the lab's intentionally-ephemeral setup is fine for a tutorial but would not be acceptable for anything real.

---

## Part 7: Stretch: Have Copilot Explain the Architecture

In Part 2 you read the four layers and worked out the architecture for yourself. The reflection at the end of the lab will ask you to compare that experience to using Copilot for the same task. Copilot is good at reading codebases it has not seen before; in real work, this is one of the highest-value AI-assisted-development skills, because most engineering time is spent reading existing code, not writing new code.

### Step 7.1: Open Copilot Chat

In VS Code with the project open, open the Chat view with `Ctrl+Alt+I` (or `Cmd+Alt+I` on macOS). Select **Ask** mode and **Claude Sonnet 4.6** in the model picker. If Claude Sonnet 4.6 is not available, **Auto** is an acceptable fallback (see Lab 1-1 for full availability notes).

### Step 7.2: First prompt - identify the architecture

Attach the four key files to the chat using the paperclip icon or `#`:

- `ProductController.java`
- `ProductService.java`
- `ProductServiceImpl.java`
- `Product.java`

Send this prompt:

```
Read these four files. Describe the architectural pattern this application
uses, name each layer's responsibility in one sentence, and draw the
dependency relationships between them as ASCII art.
```

Compare Copilot's answer to the diagram you drew in Step 2.6. In your notebook:

1. Did Copilot identify the layered architecture and name the pattern (layered architecture, three-tier, MVC, hexagonal architecture, dependency inversion)? Was its naming the same as yours, or different?
2. Did its dependency diagram match yours? Were the arrows pointing the same direction?
3. Did Copilot mention anything you missed? (For example, the `@Transactional` annotation, the role of `@Autowired`, or anything about the test setup if there is any.)

### Step 7.3: Second prompt - reason about the swap

Without starting a new chat (keep the same files attached), send:

```
What would need to change to swap MongoDB for PostgreSQL? Specifically:

1. Which files would need to change?
2. Which annotations on the Product class would change?
3. Which interface would the repository extend instead of MongoRepository?
4. What new dependencies would be needed in pom.xml?
5. Would the ProductController need to change? Why or why not?
```

This question tests whether Copilot understands the *abstraction*, not just the syntax. The right answer to question 5 is "no, the controller would not need to change" because the controller depends on `ProductService` (the interface), which is database-agnostic. If Copilot gets this right, it has correctly identified the seam in the design.

In your notebook:

1. Did Copilot correctly identify question 5's answer?
2. Were the items in its list of file changes the same as what you would have predicted?
3. Did Copilot mention anything you had not considered (test changes, configuration property differences, transaction behavior differences between Mongo and Postgres)?

### Step 7.4: The takeaway

Copilot can read a small codebase and identify its architecture quite well; this is a different kind of task from generating new code, and the failure modes are different. For architecture-explanation tasks, the typical pattern is:

- **Strengths**: Copilot quickly picks up structural patterns (layered architecture, dependency injection, repository pattern) and uses the right vocabulary. It can identify the seam in a design when explicitly asked.
- **Weaknesses**: It sometimes invents details ("the project also has a `ProductDTO` class" when there is no such class) and treats minor or stale annotations as significant. Verify before quoting.

The right division of labor for a real architecture review is: read the code yourself first, then ask Copilot to confirm or extend your understanding. Skipping the first step risks accepting a plausible-sounding answer without the calibration to know if it is right.

---

## Part 8: Reflection

Answer in your notebook. These are open-ended; spend at least ten minutes.

1. **The layered architecture.** This lab's application has four layers. In your own words, what is the cost (in lines of code, files, runtime overhead) of having four layers instead of one? What is the benefit? At what scale does the benefit start to outweigh the cost?

2. **Dependency inversion.** The argument in Step 2.6 is that the controller does not know about MongoDB, so swapping in PostgreSQL is a local change. This is the *theoretical* benefit; in practice, swaps rarely happen. Is the abstraction still worth the cost if it never gets exercised? What is the practical value of the abstraction even without a swap?

3. **REST verbs and CRUD.** Each HTTP verb maps to a CRUD operation: POST=create, GET=read, PUT=update, DELETE=delete. The lab also uses PUT for updating a specific product (`/products/{id}`). What does PATCH do, and why is it sometimes preferred over PUT for partial updates? What would the controller method look like?

4. **The two-container system.** This lab runs one application container and one database container. Real microservice fleets often have one container per process *type*, but multiple replicas of each. What would change if you ran three replicas of the application container against one MongoDB? What would the docker-compose file need to add, and what problems would the application now have (sessions, sticky state, sequence IDs) that it does not have with one replica?

5. **Operational concerns.** Walk through what would need to be added to make this lab's setup production-ready. At minimum: persistent volumes for the database, environment-variable configuration for credentials, health-check endpoints on the service, log aggregation, and TLS for the API. Pick three of these and describe what each one solves and approximately what it would cost to implement.

6. **AI-assisted comprehension.** Compare your experience in Part 2 (reading the code yourself) to Part 7 (asking Copilot). Which was faster? Which produced a deeper understanding? Was the faster path also the better path? When would you reverse the order (Copilot first, then your own reading)?

7. **The next iteration.** Imagine your team uses this microservice as the starting point for a "products" service in a real application. List three changes you would make to the code before considering it production-ready, and three changes you would make to the operational setup (Docker Compose, deployment).

---

## Reference: The Four Layers in One Picture

```
+-------------------------------------------------------+
|  Layer 1: REST controller                             |
|  ProductController                                    |
|  - Maps HTTP requests to method calls                 |
|  - Knows: ProductService (interface)                  |
|  - Does NOT know: MongoDB, JSON, persistence          |
+-------------------------------------------------------+
                          |
                          v
+-------------------------------------------------------+
|  Layer 2: Service contract                            |
|  ProductService (interface)                           |
|  - Names the operations the application supports      |
|  - Says nothing about how they are implemented        |
+-------------------------------------------------------+
                          ^
                          | implements
                          |
+-------------------------------------------------------+
|  Layer 3: Service implementation                      |
|  ProductServiceImpl                                   |
|  - Business logic (validation, orchestration)         |
|  - Knows: ProductRepository (interface)               |
|  - Does NOT know: MongoDB driver internals            |
+-------------------------------------------------------+
                          |
                          v
+-------------------------------------------------------+
|  Layer 4: Repository                                  |
|  ProductRepository extends MongoRepository            |
|  - Auto-generated by Spring Data Mongo                |
|  - Translates Java method calls to Mongo operations   |
+-------------------------------------------------------+
                          |
                          v
                  +---------------+
                  |   MongoDB     |
                  |  (container)  |
                  +---------------+
```

Each layer depends only on the layer immediately below it, and on the *interface* form of that layer, not the concrete implementation. The dotted line (between the interface and its implementation, written here as the ^ implements arrow) is the seam where the design can be reconfigured.

---

## Reference: The Compose V2 Command Cheat Sheet

| Command | What it does |
|---------|--------------|
| `docker compose up` | Build (if needed) and start all services. Stays in the foreground showing logs. |
| `docker compose up -d` | Start in detached mode (background). Use `docker compose logs -f` to follow logs. |
| `docker compose down` | Stop and remove all containers and networks. |
| `docker compose down -v` | Same, but also remove volumes (data is destroyed). |
| `docker compose ps` | List running services in the current compose project. |
| `docker compose logs` | Show all service logs. |
| `docker compose logs -f service` | Follow a specific service's logs. |
| `docker compose exec service bash` | Open a shell inside a running container. |
| `docker compose build` | Rebuild images defined in the compose file. |
| `docker compose pull` | Pull the latest version of images defined in the compose file. |
| `docker compose restart` | Restart all services (or a named one). |

---

## Reference: The Curl Flags You Used

| Flag | What it does |
|------|--------------|
| (none) | Default verb is GET. |
| `-X METHOD` | Override the HTTP method (`POST`, `PUT`, `DELETE`, `PATCH`). |
| `-H "Header: value"` | Add a request header. Repeat for multiple headers. |
| `-d '...'` | Add a request body. Implies `-X POST` if no `-X` is given. |
| `-d @file.json` | Use the contents of a file as the body. |
| `-i` | Include response headers in the output (useful for debugging). |
| `-v` | Verbose: show request and response headers, plus the body. |
| `-s` | Silent: do not show progress meter or error messages. |
| `-o file` | Write output to a file instead of stdout. |

For exploring an unfamiliar API, `-i` is almost always worth adding so you can see the status code and content-type.

---

## Troubleshooting

**`docker: command not found` or `docker compose: command not found`.**
Docker is not installed or not on your `PATH`. See Step 1.1; install Docker Desktop (macOS/Windows) or Docker Engine (Linux). On Linux, also confirm your user is in the `docker` group.

**`Cannot connect to the Docker daemon`.**
The Docker service is not running. On macOS/Windows, start Docker Desktop. On Linux, run `sudo systemctl start docker`.

**`Bind for 0.0.0.0:8080 failed: port is already allocated`.**
Another process on your machine is using port 8080. Either stop that process, or change the host-side port in `docker-compose.yml`: `"8081:8080"` would map host port 8081 to container port 8080, and you would call the API at `http://localhost:8081/products`.

**The `productservice` container exits immediately with a stack trace mentioning MongoDB.**
The Spring Boot app started before MongoDB was ready, and its initial connection attempt failed. The `depends_on:` directive in compose ensures container start order but does not wait for the service inside to be ready. Either restart the productservice (`docker compose restart productservice`) or add a health-check-based wait condition to the compose file.

**`curl: (52) Empty reply from server` on a POST.**
The service is running but is rejecting the request. Check the `docker compose up` terminal for an error log; often the cause is a JSON parse error (mismatched braces, wrong type for `id`) or a validation failure (`name` was blank).

**Maven downloads take forever the first time.**
This is expected. Maven downloads all transitive dependencies on first build. Subsequent builds use the local Maven cache inside the image. On a slow connection, the first `docker compose up` can take 10 to 20 minutes.

**The `WARN[0000] ... the attribute 'version' is obsolete` warning appears on every command.**
This is harmless; the old `version:` field in compose files is no longer used by Compose V2. To silence it, delete the `version: '3.x'` line at the top of `docker-compose.yml`.

**`curl` returns a 500 status with a long Spring Boot error page on `GET /products/999`.**
The service does not have a global exception handler, so unhandled exceptions reach the default error response. See Step 5.7. A production service would add `@RestControllerAdvice` to translate exceptions to clean HTTP responses (404 for not-found, 400 for bad-input, 500 only for genuinely unexpected errors).

**Copilot in Part 7 mentions a class that does not exist in the project.**
Copilot occasionally invents plausible-sounding details. Verify each claim against the source before trusting it. If Copilot mentions `ProductDTO` or `ProductMapper`, search the project (`Ctrl+Shift+F`) for the class name. If it does not exist, the answer is invented; mark this in your notebook.

---

## Further Reading

- **Spring Boot reference documentation** at <https://docs.spring.io/spring-boot/index.html>. The canonical reference. Sections on REST, data access, and Spring Data MongoDB cover most of the technologies in this lab.
- **Docker Compose specification** at <https://docs.docker.com/compose/compose-file/>. The current reference for compose-file syntax, including which fields are required, optional, or deprecated.
- **Microservices.io** at <https://microservices.io/>. Chris Richardson's pattern catalog. The Layered Architecture pattern (this lab's design) is one of many discussed.
- **Building Microservices, 2nd edition** (Sam Newman). The standard book-length introduction to microservice architecture. Chapters 1-5 cover the foundational ideas; later chapters cover operational concerns.
- **Spring Data MongoDB documentation** at <https://docs.spring.io/spring-data/mongodb/reference/>. Specifically the "Repositories" chapter, which explains how Spring Data generates the `ProductRepository` implementation at runtime.
- **MongoDB documentation** at <https://www.mongodb.com/docs/>. The official reference. The "CRUD Operations" tutorial covers what the `MongoRepository` calls do under the hood.
