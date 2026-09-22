CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL,
    signup_date DATE NOT NULL
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    price NUMERIC(12, 2) NOT NULL
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    order_date DATE NOT NULL,
    status VARCHAR(30) NOT NULL
);

CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(order_id),
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(12, 2) NOT NULL
);


INSERT INTO customers
    (customer_name, region, signup_date)
VALUES
    ('Aarav Sharma', 'North', '2025-01-15'),
    ('Priya Mehta', 'West', '2025-02-20'),
    ('Rahul Verma', 'South', '2025-03-10'),
    ('Sneha Kapoor', 'North', '2025-04-05'),
    ('Ananya Singh', 'East', '2025-05-18'),
    ('Rohan Gupta', 'West', '2025-06-22'),
    ('Kavya Nair', 'South', '2025-07-11'),
    ('Aditya Rao', 'East', '2025-08-30');


INSERT INTO products
    (product_name, category, price)
VALUES
    ('Laptop Pro', 'Electronics', 85000),
    ('Wireless Headphones', 'Electronics', 12000),
    ('Office Chair', 'Furniture', 18000),
    ('Standing Desk', 'Furniture', 30000),
    ('Mechanical Keyboard', 'Accessories', 7000),
    ('Monitor 27', 'Electronics', 25000);


INSERT INTO orders
    (customer_id, order_date, status)
VALUES
    (1, '2025-09-01', 'completed'),
    (2, '2025-09-03', 'completed'),
    (3, '2025-09-05', 'completed'),
    (4, '2025-09-08', 'completed'),
    (5, '2025-09-10', 'completed'),
    (6, '2025-09-12', 'completed'),
    (7, '2025-09-15', 'completed'),
    (8, '2025-09-18', 'completed'),
    (1, '2025-10-02', 'completed'),
    (2, '2025-10-05', 'completed'),
    (3, '2025-10-08', 'completed'),
    (4, '2025-10-11', 'completed'),
    (5, '2025-10-15', 'completed'),
    (6, '2025-10-20', 'completed'),
    (7, '2025-10-22', 'cancelled'),
    (8, '2025-10-25', 'completed');


INSERT INTO order_items
    (order_id, product_id, quantity, unit_price)
VALUES
    (1, 1, 1, 85000),
    (1, 5, 1, 7000),

    (2, 2, 2, 12000),

    (3, 3, 1, 18000),

    (4, 4, 1, 30000),

    (5, 6, 2, 25000),

    (6, 1, 1, 85000),

    (7, 5, 2, 7000),

    (8, 2, 1, 12000),

    (9, 1, 1, 85000),
    (9, 2, 1, 12000),

    (10, 3, 2, 18000),

    (11, 4, 1, 30000),

    (12, 6, 1, 25000),

    (13, 5, 3, 7000),

    (14, 2, 2, 12000),

    (15, 1, 1, 85000),

    (16, 4, 1, 30000);