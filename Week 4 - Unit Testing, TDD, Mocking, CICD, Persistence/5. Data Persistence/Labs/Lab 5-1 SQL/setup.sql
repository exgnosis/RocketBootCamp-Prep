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
