CREATE TABLE "User" (
    id serial PRIMARY KEY,
    role VARCHAR(32) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    login VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE "Order_Pick_Up_Point" (
    id serial PRIMARY KEY,
    full_address VARCHAR(255) NOT NULL UNIQUE
);
CREATE TABLE "Goods" (
    id serial PRIMARY KEY,
    article VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    unit_of_measurement VARCHAR(10) NOT NULL,
    price NUMERIC(12, 2) NOT NULL,
    provider VARCHAR(100),
    manufacturer VARCHAR(100),
    category VARCHAR(100),
    discount NUMERIC(5, 2),
    count INTEGER NOT NULL DEFAULT 0,
    description text,
    image VARCHAR(255)
);
CREATE TABLE "Order" (
    id serial PRIMARY KEY,
    user_id INTEGER REFERENCES "User"(id) ON DELETE
    SET NULL,
        pick_up_point_id INTEGER REFERENCES "Order_Pick_Up_Point"(id) ON DELETE
    SET NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        delivered_at TIMESTAMP,
        recipient_code VARCHAR(50),
        status VARCHAR(50)
);
-- Таблица для связи "многие ко многим" между Order и Goods
CREATE TABLE "Order_Items" (
    id serial PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES "Order"(id) ON DELETE CASCADE,
    goods_id INTEGER NOT NULL REFERENCES "Goods"(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    UNIQUE(order_id, goods_id)
);