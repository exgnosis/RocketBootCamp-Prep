Multiple-Choice Questions on Data Persistence

- 9/15 version 1.0

---

1 Which of the following is the external model of data?
1. How the data is organized internally in storage
2. Logical schema of the project
3. Relational model implementation
4. **_Users’ view of the data in their context_**
5. Do not know

---

2 Why is loose coupling important in persistence design?
1. It improves speed of SQL queries
2. It reduces redundancy in user interfaces
3. It removes the need for schemas
4. It prevents client code from breaking when the storage mechanism changes
5. Do not know

---

3 In JPA, an entity represents:
1. **_A domain object mapped to some persistence storage artifact_**
2. A client object that makes requests of persistent storage
3. A table in a relational database
4. None of the above
5. Do not know

---

4 In microservices, ideally each service has:
1. No dependency on any data persistence
2. **_Its own data repository_**
3. A schema registry
4. An anti-corruption layer
5. Do not know

---

5 The segmentation problem in microservices arises because:
1. Microservices share UI code
2. APIs are might have different schema for an entity
3. ORM mappings are missing database vendor support
4. **_Multiple copies of the same data exist_**
5. Do not know

---

6 What was the drawback of using JDBC directly in Java applications?
1. **_It produced tightly coupled brittle code_**
2. It required expensive hardware
3. It only worked with NoSQL databases
4. It did not support SQL
5. Do not know

---

7 Which technique improves scalability by separating read and write operations in databases?
1. Schema registry
2. CAP balancing
3. Normalization
4. **_CQRS (Command Query Responsibility Segregation)_**
5. Do not know

---

8 In the ANSI-SPARC model, which level ensures data independence between users and the internal schema?
1. **_Conceptual view_**
2. External view
3. Implementation view
4. Physical view
5. Do not know

---

9 What is the role of an anti-corruption layer?
1. Encrypts schema data
2. **_Translates data between contexts when no schema registry exists_**
3. Prevents unauthorized access to data
4. None of the above
5. Do not know

---

10 In microservices, persistence is often managed through:
1. The client tier
2. XML configuration files
3. Data pipelines
4. **_A backing service that handles CRUD for domain objects_**
5. Do not know

---