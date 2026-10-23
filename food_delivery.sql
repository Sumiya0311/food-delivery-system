CREATE DATABASE food_delivery_db;
SHOW DATABASES;
USE food_delivery_db;
SHOW TABLES;


SELECT *
FROM delivery_partners
WHERE user_id = 5;


INSERT INTO delivery_partners
    (user_id, vehicle_number, vehicle_type, is_online, is_available, total_earnings)
VALUES
    (4, 'AP39DL4567', 'Bike', 0, 0, 0.00);


SELECT id, order_id, partner_id, status, expires_at
FROM delivery_offers
WHERE order_id = 6;
SELECT NOW() AS database_time;


UPDATE delivery_offers
SET status = 'Expired'
WHERE id = 2
  AND status = 'Pending';
  


SELECT id, order_number, delivery_otp, status
FROM orders
WHERE id = 6;
SELECT id, order_number, delivery_otp, status
FROM orders
WHERE id = 7;
SELECT id, order_number, delivery_otp, status
FROM orders
WHERE id = 5;