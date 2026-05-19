# Lab 6-1: Building a REST Service with Spring Boot

## Overview

REST (Representational State Transfer) is the architectural style that powers most of the modern web. Coined by Roy Fielding in his 2000 doctoral dissertation, it describes a small set of constraints (statelessness, uniform interface, addressability, hypertext-driven state changes) that, when followed, produce web APIs that scale and compose well. By 2010 it had displaced SOAP as the default style for new web services; today, almost every public web API you have ever used (GitHub, Stripe, Twilio, OpenWeather, Spotify) follows REST conventions, at least loosely.

Spring Boot is the most popular Java framework for building REST services. It bundles Spring Framework's web stack with sensible defaults, an embedded Tomcat server, and a "starter" dependency system that hides most of the configuration. A REST endpoint that returns JSON, listens on port 8080, validates incoming parameters, and serializes objects to JSON requires three things in Spring Boot: a class with `@RestController` on top, a method with `@GetMapping("/path")` on it, and an immutable data type as the return value. That is the entire lab.

In this lab you will use Spring Initializr (the official project generator at `start.spring.io`) to create a fresh Spring Boot project, add a small data type called `Greeting`, and add a controller class with one endpoint at `/greeting`. The endpoint will accept an optional `name` query parameter and return a JSON object with two fields: an `id` (a counter that increments on each request, so you can see that Spring is calling your endpoint with shared state) and a `content` field (the greeting itself, defaulting to "Hello, World!" if no name was provided).

The lab is short. The reflection at the end (when does the framework's magic help you, when does it hide things you need to know, and how the conventions of REST itself constrain your design) is where the real conceptual content lives.

**This lab is hands-on.** You write the code yourself; no AI assistance is needed or expected.

**Estimated time:** 30 to 45 minutes
**Difficulty:** Beginner

**Prerequisites:**

- A Java Development Kit (JDK), version 17 or later, installed and on your PATH (`java --version` should print 17.x, 21.x, or higher). Java 21 is the recommended version.
- VS Code (or another editor; the lab assumes VS Code).
- An internet connection (Spring Initializr is a web service; Maven Wrapper will download dependencies on first run).
- Either `curl` on the command line, or a web browser, for testing the endpoint.

You do **not** need Maven installed separately. The project Spring Initializr generates ships with the Maven Wrapper (`./mvnw` on macOS/Linux, `mvnw.cmd` on Windows), which downloads the correct Maven version on first use.

---

## Learning Objectives

By the end of this lab, you will be able to:

1. Generate a Spring Boot project using Spring Initializr and explain what each of the generated files does.
2. Define a controller class using `@RestController` and map an HTTP GET request to a Java method using `@GetMapping`.
3. Bind a query-string parameter to a method argument with `@RequestParam`, including providing a default value.
4. Return a plain Java object from a controller method and rely on Spring's automatic JSON serialization (via Jackson) to send it to the client.
5. Run a Spring Boot application using the Maven Wrapper (`./mvnw spring-boot:run`) and test it using `curl` or a browser.
6. Recognize the resource-and-identity convention of REST (every response has an `id`) and explain why that matters in a real API.

---

## Part 1: Generate the Starter Project

Spring Initializr is a web-hosted project generator. You fill in a short form, click Generate, download a zip, and you have a working Spring Boot project skeleton with the right files in the right places. It is the standard way to start a new Spring Boot project.

### Step 1.1: Open Spring Initializr

In a browser, go to <https://start.spring.io>.

You will see a form with several sections. Fill it in as follows:

| Field | Value |
|-------|-------|
| Project | **Maven** |
| Language | **Java** |
| Spring Boot | The default (the most recent stable release; **4.0.x** is current as of mid-2026) |
| Group | `com.example` |
| Artifact | `greeting` |
| Name | `greeting` |
| Description | `Demo project for REST` (or leave the default) |
| Package name | `com.example.greeting` (this is generated from Group and Artifact; leave as-is) |
| Packaging | **Jar** |
| Java | **21** |

For dependencies, click **Add Dependencies** (or `Ctrl+B`), search for `Spring Web`, and click it to add it. Only one dependency is needed.

> **Why these choices?** Maven is the default Java build system that Spring is most commonly taught with. Java 21 is an LTS release with several more years of vendor support. `com.example.greeting` is a conventional Java package name (all lowercase). The Jar packaging option produces a self-contained executable jar; the alternative (`War`) would require an external servlet container, which Spring Boot no longer needs because it ships with an embedded Tomcat. The Spring Web dependency brings in everything for HTTP: Tomcat, Spring MVC, Jackson (for JSON), and the validation API.

### Step 1.2: Generate and download

Click **Generate**. A file called `greeting.zip` downloads.

Unzip the file. You will get a folder called `greeting/` containing the project. Move it somewhere convenient (your home directory, your projects folder, anywhere you can find it later).

### Step 1.3: Open the project in VS Code

If you have the `code` command available, in a terminal:

```bash
cd path/to/greeting
code .
```

Otherwise, open VS Code and use **File > Open Folder...** to open the `greeting/` directory. Click **Yes, I trust the authors** if prompted.

The Explorer panel on the left should show:

```
greeting/
├── .gitignore
├── HELP.md
├── mvnw
├── mvnw.cmd
├── pom.xml
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/
│   │   │       └── example/
│   │   │           └── greeting/
│   │   │               └── GreetingApplication.java
│   │   └── resources/
│   │       ├── application.properties
│   │       ├── static/
│   │       └── templates/
│   └── test/
│       └── java/
│           └── com/
│               └── example/
│                   └── greeting/
│                       └── GreetingApplicationTests.java
```

The key files to know:

- **`pom.xml`**: the Maven build descriptor. It declares the Spring Boot version, the Java version, and the one dependency (Spring Web).
- **`mvnw` and `mvnw.cmd`**: the Maven Wrapper scripts. Use these instead of a system-wide `mvn` command. They download the correct Maven version automatically on first use.
- **`GreetingApplication.java`**: the main application class. Has `@SpringBootApplication` on top and a `main` method that calls `SpringApplication.run`. You do not need to edit this file.
- **`application.properties`**: configuration. Empty by default. Settings like the HTTP port go here.

### Step 1.4: Run the generated project to confirm it works

In the VS Code integrated terminal (**View > Terminal** or `` Ctrl+` ``), run:

On macOS/Linux:

```bash
./mvnw spring-boot:run
```

On Windows (PowerShell or Command Prompt):

```cmd
mvnw spring-boot:run
```

The first run will take a minute or two as Maven downloads Spring Boot and its dependencies. Subsequent runs are much faster (a few seconds).

When the application is ready, you will see something like the following near the end of the output:

```
 :: Spring Boot ::                (v4.0.x)

...
... Tomcat initialized with port 8080 (http)
... Tomcat started on port 8080 (http) with context path '/'
... Started GreetingApplication in 1.2 seconds (process running for 1.4)
```

The application is now running and listening on port 8080. It does not yet have any endpoints, so visiting `http://localhost:8080` in a browser will show a "Whitelabel Error Page" (Spring Boot's default 404 page). That is expected; you will add the endpoint in the next two parts.

**Stop the application** by pressing `Ctrl+C` in the terminal.

### Step 1.5: Create a lab notebook

Create a file `notebook.md` in the project folder. You will record your analyses and observations as you go:

```markdown
# REST Lab Notebook

## Part 2: The model class

## Part 3: The controller

## Part 4: Verification

## Part 5: Stretch (URL change)

## Part 6: Reflection
```

Save it.

---

## Part 2: Create the Model Class

A "model" in REST terminology is a representation of a resource. In this lab the resource is a greeting; every greeting has two properties (an `id` and a `content` string), and every greeting is immutable once created. That is a textbook use case for a Java **record**, which was added in Java 16 specifically for this kind of data type.

A record gives you private final fields, a canonical constructor, accessor methods (named after the components, with parens: `id()` and `content()`), and sensible `equals`, `hashCode`, and `toString` implementations, all generated by the compiler. Jackson (the JSON serialization library Spring Boot uses) has supported records natively since Jackson 2.12, so a record serializes to clean JSON with no extra annotations.

### Step 2.1: Create the file

In the Explorer panel, right-click on the `src/main/java/com/example/greeting/` folder and choose **New File...**. Name it `Greeting.java`.

### Step 2.2: Add the record

Paste the following into the file:

```java
package com.example.greeting;

public record Greeting(long id, String content) {
}
```

That is the entire file. Save it (`Ctrl+S`).

> **Why a record instead of a class?** The original lab in this series defined `Greeting` as a class with two private final fields, a constructor, two getters, and no `equals`/`hashCode`/`toString`. That is 15 lines of code that the record above expresses in 1. The record is also strictly safer: it is immutable by construction, you cannot accidentally add a setter, and Jackson serializes it exactly the same way as the old class form. For any DTO (Data Transfer Object) that is just data and accessors, a record is the idiomatic Java choice as of Java 16.

The record's two components, `id` and `content`, are what will be serialized to JSON. The JSON Jackson produces will look like:

```json
{ "id": 1, "content": "Hello, World!" }
```

No additional annotations are needed.

---

## Part 3: Create the REST Controller

A **controller** in Spring MVC is a class that handles incoming HTTP requests. The `@RestController` annotation tells Spring two things at once: this class handles requests (Spring should register it in the dispatch table), and every method's return value should be serialized directly to the response body (rather than being interpreted as a view name to render).

### Step 3.1: Create the file

In the Explorer panel, right-click on the `src/main/java/com/example/greeting/` folder and choose **New File...**. Name it `GreetingController.java`.

### Step 3.2: Add the controller code

Paste the following into the file:

```java
package com.example.greeting;

import java.util.concurrent.atomic.AtomicLong;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class GreetingController {

    private static final String TEMPLATE = "Hello, %s!";
    private final AtomicLong counter = new AtomicLong();

    @GetMapping("/greeting")
    public Greeting greeting(
            @RequestParam(value = "name", defaultValue = "World") String name) {
        return new Greeting(counter.incrementAndGet(), TEMPLATE.formatted(name));
    }
}
```

Save the file.

Read it carefully. Every line is doing one specific thing:

- **`@RestController`**: marks this class as a REST controller. Spring scans the classpath at startup and registers any class with this annotation.
- **`TEMPLATE`**: a `private static final` string constant. The order of modifiers (`private static final`, in that order) is the convention recommended by the JLS and used in the JDK. Constants are conventionally `UPPER_SNAKE_CASE` in Java.
- **`counter`**: an instance field. `AtomicLong` is thread-safe; multiple HTTP requests from different clients may call `greeting` concurrently, and `AtomicLong.incrementAndGet()` guarantees each request gets a distinct id without races. (A plain `long` field with a `++` would have a race condition under concurrent requests.)
- **`@GetMapping("/greeting")`**: maps HTTP `GET /greeting` to this method. There are also `@PostMapping`, `@PutMapping`, `@DeleteMapping`, and `@PatchMapping` for the other HTTP verbs.
- **`@RequestParam(value = "name", defaultValue = "World")`**: binds the `name` query-string parameter to the `name` method argument. If the client did not supply `?name=...`, the argument defaults to `"World"`. Because there is a default value, the parameter is automatically optional.
- **`TEMPLATE.formatted(name)`**: equivalent to `String.format(TEMPLATE, name)`, but more readable. Added in Java 15.
- **`new Greeting(...)`**: constructs a new record on each call. The id is a fresh integer; the content is the formatted template.

### Step 3.3: Run the application

In the terminal, run:

```bash
./mvnw spring-boot:run
```

Wait for the `Started GreetingApplication in ...` line. The application is now serving the `/greeting` endpoint.

> **A note about modifier order.** Java permits `final static` and `static final` interchangeably (and similarly `private final static`, `private static final`, etc.), but the *Java Language Specification* recommends the order **access, then non-access**, with `static` before `final`. Most linters and the JDK's own source code follow this. Mixing orders compiles but reads as sloppy in code review.

---

## Part 4: Test the Endpoint

The application is running. Time to call it.

Open a second terminal in VS Code (split it or use `` Ctrl+Shift+` ``). The first terminal is still running the Spring Boot application; do not close it.

### Step 4.1: Default greeting (no name)

In the second terminal:

```bash
curl http://localhost:8080/greeting
```

Expected output:

```json
{"id":1,"content":"Hello, World!"}
```

If you do not have `curl`, open <http://localhost:8080/greeting> in your browser. You will see the same JSON, possibly with line breaks added by your browser's JSON formatter.

### Step 4.2: With a name parameter

```bash
curl 'http://localhost:8080/greeting?name=Spring'
```

(The single quotes around the URL are not strictly required here, but they protect against `?` or `&` being interpreted by your shell, which becomes important when you have more than one parameter.)

Expected output:

```json
{"id":2,"content":"Hello, Spring!"}
```

Note two things:

1. The `id` is now `2`. Each request increments the counter; the counter is shared across all requests because the `GreetingController` is a singleton (this is Spring's default bean scope).
2. The `content` is now `"Hello, Spring!"` instead of `"Hello, World!"`. The `name=Spring` query parameter overrode the default.

### Step 4.3: Repeat the default to see the counter keep going

```bash
curl http://localhost:8080/greeting
```

Expected output:

```json
{"id":3,"content":"Hello, World!"}
```

The `id` is now `3`. The counter is not reset when you switch from `?name=Spring` back to no parameter. The same controller instance is handling every request.

> **Why does this matter?** The counter is the proof that Spring is running the controller as a long-lived singleton. If you stopped the application (`Ctrl+C`) and started it again, the counter would reset to 1, because the singleton would be reconstructed. This is the difference between **request scope** (a new instance per request, would always start from 1) and **singleton scope** (one instance for the lifetime of the application, which is Spring's default). The reflection at the end of the lab returns to this.

### Step 4.4: Try a path that does not exist

```bash
curl http://localhost:8080/
```

Expected output (the Whitelabel Error Page, rendered as HTML):

```html
<!DOCTYPE html><html lang="en"><head>...</head><body><h1>Whitelabel Error Page</h1>...</body></html>
```

Or, with the `Accept` header that browsers send by default, the same HTML page rendered.

The `/` path has no `@GetMapping` for it, so Spring returns 404. The "Whitelabel Error Page" is Spring Boot's default 404 / 500 / error page; you would customize or replace it for a production app.

Stop the application with `Ctrl+C` in the first terminal before moving on.

---

## Part 5: Verify Against the Expected Output

Let's do a clean end-to-end run to make sure everything works together. Start the application:

```bash
./mvnw spring-boot:run
```

Run all four requests in the second terminal and confirm the output matches exactly:

| Request | Expected response |
|---------|-------------------|
| `curl http://localhost:8080/greeting` | `{"id":1,"content":"Hello, World!"}` |
| `curl 'http://localhost:8080/greeting?name=Spring'` | `{"id":2,"content":"Hello, Spring!"}` |
| `curl 'http://localhost:8080/greeting?name=Java'` | `{"id":3,"content":"Hello, Java!"}` |
| `curl http://localhost:8080/greeting` | `{"id":4,"content":"Hello, World!"}` |

If your output does not match, work through the troubleshooting section below.

### If your output differs

1. **`Connection refused`.** The application is not running, or it is running on a different port. Check the first terminal for the "Started GreetingApplication" line; if you see it, the app is up. If you see the prompt back, the app exited.

2. **`{"timestamp":"...","status":404,"error":"Not Found","path":"/greeting"}`.** The `/greeting` endpoint is not mapped. The most common cause is forgetting `@RestController` on the class, or putting `@GetMapping("/greeting/")` (with a trailing slash) and then hitting `/greeting`. Open `GreetingController.java` and check both.

3. **`{"id":0,...}`.** Your `counter.incrementAndGet()` call is `counter.get()` instead; the counter never advances. Fix the method name.

4. **`{"id":1,"content":"Hello,World!"}` (no space).** Your template is `"Hello,%s!"` (no space after the comma). Add the space.

5. **`{"content":"Hello, World!","id":1}` (different field order).** Jackson generally serializes record components in declaration order, but JSON object key order is not significant. Most clients do not care. If you need a guaranteed order, you can annotate the record with `@JsonPropertyOrder({"id", "content"})`, but for this lab the natural order is fine.

6. **The response body is the entire `Greeting` toString rather than JSON.** You used `@Controller` instead of `@RestController`. The first treats return values as view names; the second serializes them as the response body.

Stop the application before continuing.

---

## Part 6: Stretch: Change the URL

The `@GetMapping("/greeting")` annotation is the only thing tying the method to the URL. Change it to anything else, restart, and the URL changes.

### Step 6.1: Change the mapping

In `GreetingController.java`, change:

```java
@GetMapping("/greeting")
```

to:

```java
@GetMapping("/howdy")
```

Save the file. Restart the application (`Ctrl+C` to stop, then `./mvnw spring-boot:run`).

### Step 6.2: Test the new URL

```bash
curl http://localhost:8080/howdy
```

Expected output:

```json
{"id":1,"content":"Hello, World!"}
```

The old URL is now a 404:

```bash
curl http://localhost:8080/greeting
```

Returns the Whitelabel error page.

> **Hot reload.** As you change the controller, you have to restart the application. Spring Boot DevTools can do an automatic restart on file change; you would add `spring-boot-devtools` as a dependency in `pom.xml` to enable it. This is outside the scope of this lab, but worth knowing for any serious Spring Boot work.

Change the mapping back to `/greeting` for consistency, restart, and stop the application before reflecting.

---

## Part 7: Reflection

Answer in your notebook. These are open-ended; spend at least 10 minutes.

1. **The framework's magic.** You wrote 3 lines of code in `Greeting.java` and 14 lines in `GreetingController.java`. Spring Boot did the rest: started an HTTP server, parsed the URL, looked up the matching `@GetMapping`, extracted the query parameter, called your method, serialized the result to JSON, and sent the response. List two things this saved you from writing yourself. Then name one situation where the framework would *hide* something you would later need to know.

2. **Singleton state.** The `counter` field is shared across all requests because the controller is a singleton. Is that the right choice for a counter that represents "how many requests has this app received"? What about for a more meaningful counter, like "how many users are logged in" or "how many database connections are open"? When does shared mutable state in a controller become a problem?

3. **REST conventions.** The `Greeting` resource has an `id` field even though our application does not store anything in a database. Why is this a REST convention? Look at any public REST API (GitHub's, Stripe's, the Slack API): every resource has an id. What property of REST does the id support? (Hint: addressability.)

4. **The query parameter vs the path parameter.** This lab used `?name=Spring` as a query parameter. An alternative would be a path variable: `GET /greeting/Spring`. The annotation for that is `@PathVariable` instead of `@RequestParam`. When is each one appropriate? (Hint: think about what is *identifying* a resource versus what is *filtering* a collection.)

5. **What is missing for production?** This lab's REST service works but is not production-ready. List three things you would want to add before deploying it publicly. (Hints: input validation, rate limiting, authentication, logging, OpenAPI documentation, health checks.)

6. **JSON serialization with records.** This lab used a record. Jackson serialized it without any annotations. What would change about the JSON if a future Java version added a new "credit_card_number" component to the record? What design principle does that suggest about API stability?

---

## Reference: How `@RestController` Works

The `@RestController` annotation is shorthand for `@Controller` + `@ResponseBody`. It is what tells Spring to do all of the following for you:

| Step | What happens |
|------|--------------|
| 1 | At startup, Spring scans the classpath for any class with `@Controller` or `@RestController` (transitively). It registers each one as a Spring bean. |
| 2 | For each `@GetMapping` (or `@PostMapping`, etc.) method in the controller, Spring registers a route in its request-dispatching table. |
| 3 | When an HTTP request arrives, Spring matches the URL and HTTP method to a registered route. |
| 4 | Spring extracts the method arguments from the request: `@RequestParam` reads query parameters, `@PathVariable` reads path segments, `@RequestBody` reads the JSON body and deserializes it, and so on. |
| 5 | Spring calls your method with those arguments. |
| 6 | Because of the `@ResponseBody` part of `@RestController`, Spring takes the return value and asks an `HttpMessageConverter` (Jackson for JSON by default) to serialize it. |
| 7 | Spring writes the serialized result to the response body, sets `Content-Type: application/json`, and returns 200 OK. |

A plain `@Controller` (without the `Rest` prefix) does step 6 differently: it interprets the return value as the name of a view template (Thymeleaf, JSP, etc.) to render. This is for traditional server-side-rendered web applications. For JSON APIs, `@RestController` is what you want.

---

## Reference: The Mapping Annotations

Spring's HTTP method annotations are shorthands for `@RequestMapping` with the HTTP method specified.

| Annotation | HTTP method | Typical use |
|------------|-------------|-------------|
| `@GetMapping` | GET | Read a resource. Safe and idempotent. |
| `@PostMapping` | POST | Create a new resource. Not idempotent (repeating creates duplicates). |
| `@PutMapping` | PUT | Replace a resource. Idempotent (repeating leaves the same end state). |
| `@PatchMapping` | PATCH | Partially update a resource. Idempotent in most designs. |
| `@DeleteMapping` | DELETE | Delete a resource. Idempotent. |

A well-designed REST API uses each HTTP method for its conventional purpose. Mixing them up (using GET to create things, for example) breaks caching, retry logic, and tooling that assumes the conventions hold.

---

## Reference: The `@RequestParam` Attributes

| Attribute | Effect |
|-----------|--------|
| `value` (or `name`) | The name of the query parameter to bind. Defaults to the Java parameter name if compiled with `-parameters`. |
| `defaultValue` | A default if the parameter is absent. Setting this implicitly makes the parameter optional. |
| `required` | Whether the parameter must be present. Defaults to `true` unless `defaultValue` is set. |

If `required = true` and the parameter is missing with no `defaultValue`, Spring returns a 400 Bad Request response automatically. This is one of the small things the framework does for you that would be tedious to write by hand.

---

## Reference: The Project's Files

| File | Purpose |
|------|---------|
| `pom.xml` | Maven build descriptor. Declares the Spring Boot parent, the Java version, and dependencies. |
| `mvnw`, `mvnw.cmd` | Maven Wrapper. Downloads and runs Maven without requiring a system install. |
| `src/main/java/.../GreetingApplication.java` | The entry point. Has `@SpringBootApplication` and a `main` method. Do not edit. |
| `src/main/java/.../Greeting.java` | The model record. You wrote this in Part 2. |
| `src/main/java/.../GreetingController.java` | The REST controller. You wrote this in Part 3. |
| `src/main/resources/application.properties` | Configuration. Empty by default. Settings like `server.port=9090` would go here. |
| `src/test/java/.../GreetingApplicationTests.java` | A generated empty smoke test. Not used in this lab. |

---

## Troubleshooting

**`./mvnw: Permission denied`.**
On macOS or Linux, the Maven Wrapper script needs to be executable. Run `chmod +x mvnw` in the project root.

**`./mvnw: command not found`.**
You are in the wrong directory. The `mvnw` script lives in the project root (where `pom.xml` is). `cd` there first. The `./` prefix is required because the current directory is not on your `PATH` by default.

**The first `./mvnw` run takes forever.**
The first run downloads Maven itself (one-time, about 10 MB) and then all Spring Boot dependencies (about 40 MB). On a fast connection this takes 30 seconds to a minute. Later runs only check for updates (a few seconds).

**Port 8080 is already in use.**
Some other process is on port 8080. Either stop that process, or change Spring Boot's port: add `server.port=9090` to `application.properties` and restart. Then use `http://localhost:9090/greeting` instead.

**`error: package org.springframework.web.bind.annotation does not exist`.**
You forgot Spring Web as a dependency, or the dependency download failed. Check `pom.xml` for `spring-boot-starter-web`. If missing, regenerate the project on `start.spring.io` with Spring Web added, or add the dependency manually:

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```

Then rerun `./mvnw spring-boot:run`.

**`org.springframework.beans.factory.UnsatisfiedDependencyException`.**
Usually a typo in an `@Autowired` constructor or a missing bean. For this lab there is no `@Autowired`; if you see this, you have probably accidentally added an unsatisfiable constructor argument to the controller. Compare your code to the example in Step 3.2.

**The Whitelabel Error Page is the wrong type (XML, not JSON, etc.).**
The Whitelabel page is content-negotiated; what you see depends on the `Accept` header. Browsers send `Accept: text/html`, so you get HTML. `curl` does not set an `Accept` header by default, so you get whatever Spring Boot's default content type is. Add `-H 'Accept: application/json'` to a `curl` call to get the JSON variant.

**`./mvnw spring-boot:run` exits immediately with no error.**
Usually a JDK version mismatch. The project requires Java 17 or later, but if your `JAVA_HOME` points at an older JDK, the build will fail silently in some configurations. Run `./mvnw -v` to see which Java the wrapper is using; if it is not 17 or later, set `JAVA_HOME` to a newer JDK.

**Application starts but the `/greeting` URL still returns 404.**
The controller class is not being picked up by Spring's component scan. The most common cause is putting `GreetingController.java` in a package that is not under `com.example.greeting`. The `@SpringBootApplication` annotation scans the package it lives in and all subpackages. Move the controller back under `com.example.greeting`.

---

## Further Reading

- **Spring Boot reference documentation** at <https://docs.spring.io/spring-boot/index.html>. The canonical reference. Long but searchable.
- **Spring's official "Building a RESTful Web Service" guide** at <https://spring.io/guides/gs/rest-service>. The official guide that this lab is loosely based on. Worth comparing against; you will recognize most of the code.
- **Roy Fielding's dissertation, "Architectural Styles and the Design of Network-based Software Architectures"** (2000), Chapter 5: "Representational State Transfer (REST)". The original definition. Short, readable, surprisingly philosophical.
- **REST API Design Rulebook** (Mark Massé). A practical book on what URLs should look like, what HTTP methods to use when, and how to design error responses.
- **Jackson Databind documentation** at <https://github.com/FasterXML/jackson-databind>. The JSON library Spring Boot uses by default. Useful when you need to customize how a particular field is serialized.
- **Spring Initializr documentation** at <https://docs.spring.io/initializr/docs/current/reference/html/>. Everything Spring Initializr can do, including the command-line interface and the API.
