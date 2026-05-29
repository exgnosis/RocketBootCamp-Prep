-- catalog_setup.sql
-- Schema and seed data for Lab 5-2 (Spring Data JPA with PostgreSQL).
-- Can be loaded into a fresh database with:
--   docker exec -i catalog-db psql -U postgres -d catalog < catalog_setup.sql

DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS categories;

CREATE TABLE categories (
  category_id   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name          VARCHAR(100) NOT NULL,
  description   VARCHAR(500),
  created_date  DATE DEFAULT CURRENT_DATE NOT NULL
);

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

INSERT INTO categories (name, description) VALUES
  ('Electronics',     'Consumer electronics and accessories'),
  ('Office Supplies', 'Stationery, paper, and desk accessories'),
  ('Books',           'Technical and professional books');

INSERT INTO products (category_id, name, sku, price, stock_qty) VALUES
  (1, 'Wireless Keyboard',                       'KBD-WL-001',  49.99, 120),
  (1, 'USB-C Hub 7-Port',                        'HUB-7C-002',  34.99,  85),
  (1, 'Monitor 27 Inch',                         'MON-27-003', 349.99,  22),
  (2, 'Ballpoint Pens 12-Pack',                  'PEN-BP-004',   6.99, 500),
  (2, 'Legal Pads 6-Pack',                       'PAD-LG-005',  12.49, 300),
  (3, 'Clean Code',                              'BK-CC-006',   39.99,  45),
  (3, 'Designing Data-Intensive Applications',   'BK-DD-007',   54.99,  30);
