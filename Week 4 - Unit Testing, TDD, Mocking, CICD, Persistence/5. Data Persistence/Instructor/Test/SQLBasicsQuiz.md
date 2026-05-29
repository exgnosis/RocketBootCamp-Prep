Multiple-Choice Questions on SQL Basics

- version 1.0

---

1 SQL stands for:
1. Sequential Query Language
2. **_Structured Query Language_**
3. Server Query Language
4. Standard Quantitative Logic
5. Do not know

---

2 The PRIMARY KEY constraint on a column ensures that the column's values are:
1. **_Unique and not null_**
2. Unique but may include one null
3. Sorted in ascending order
4. Indexed but may contain duplicates
5. Do not know

---

3 Adding a FOREIGN KEY constraint from `orders.customer_id` to `customers.customer_id` means that:
1. The customer_id column in orders becomes read-only and cannot be updated
2. Every customer must have at least one order
3. The orders table becomes a child table of customers and inherits its rows
4. **_Every value in orders.customer_id must correspond to a real customer_id in customers_**
5. Do not know

---

4 What does the following SQL statement do?

```sql
UPDATE customers SET city = 'Toronto';
```

1. Updates only the first row of the customers table
2. Raises an error because the WHERE clause is missing
3. **_Sets every customer's city to Toronto_**
4. Inserts a new row with city Toronto
5. Do not know

---

5 The RETURNING clause in an INSERT statement:
1. **_Returns the inserted row(s), including auto-generated column values_**
2. Tells PostgreSQL to roll back the insert on failure
3. Is required for the insert to be saved to disk
4. Renames the columns of the inserted row
5. Do not know

---

6 Which query correctly finds customers whose email is missing?
1. SELECT * FROM customers WHERE email = NULL;
2. SELECT * FROM customers WHERE email = '';
3. SELECT * FROM customers WHERE email <> '';
4. **_SELECT * FROM customers WHERE email IS NULL;_**
5. Do not know

---

7 Which products match the condition `WHERE name LIKE '%Cable%'`?
1. Products whose name is exactly "Cable"
2. **_Products whose name contains "Cable" anywhere_**
3. Products whose name starts with "Cable"
4. Products whose name has exactly 5 characters
5. Do not know

---

8 Which clause filters groups *after* aggregation has been performed?
1. WHERE
2. **_HAVING_**
3. GROUP BY
4. ORDER BY
5. Do not know

---

9 A LEFT JOIN between customers and orders (`customers LEFT JOIN orders`) returns:
1. Only customers who have placed at least one order
2. Only orders that have a matching customer
3. **_Every customer, plus their orders if any, with NULL in the order columns where no orders exist_**
4. Every order, plus its customer if any, with NULL in the customer columns where no customer exists
5. Do not know

---

10 To find products that have never been ordered (no rows in order_items), you can:
1. **_Use LEFT JOIN from products to order_items and filter with WHERE oi.order_id IS NULL_**
2. Use INNER JOIN and look for rows in the result
3. Use a CROSS JOIN with order_items
4. Use RIGHT JOIN with HAVING COUNT(*) = 0
5. Do not know

---
