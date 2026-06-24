-- Seed data for Supply Chain Risk Optimization Platform
-- Password for all users is: admin123 (hashed using bcrypt)

-- 1. Insert Users
INSERT INTO users (name, email, password, role) VALUES
('Sarah Jenkins (Admin)', 'admin@platform.com', '$2b$12$vFvVR8nlwU5.SbzUcmGe5eKH87uwi2GvUY.5oTXX69CcZycqc.Bpu', 'Admin'),
('David Miller (Procurement)', 'procurement@platform.com', '$2b$12$vFvVR8nlwU5.SbzUcmGe5eKH87uwi2GvUY.5oTXX69CcZycqc.Bpu', 'Procurement Manager'),
('Elena Rostova (Project)', 'project@platform.com', '$2b$12$vFvVR8nlwU5.SbzUcmGe5eKH87uwi2GvUY.5oTXX69CcZycqc.Bpu', 'Project Manager');

-- 2. Insert Suppliers
INSERT INTO suppliers (id, name, supplier_type, risk_score, performance_rating) VALUES
(1, 'Apex Steel Solutions', 'Preferred  Framework', 18, 4.8),
(2, 'London Merchant Goods', 'Approved  Regional', 35, 4.2),
(3, 'Midlands MEP Cable Co.', 'Preferred  Framework', 12, 4.9),
(4, 'Ready-Mix Concrete Ltd', 'Approved  Regional', 28, 4.4),
(5, 'Wales Drywall Merchants', 'Approved  Regional', 42, 3.9),
(6, 'Highland Timber Partners', 'Preferred  Framework', 22, 4.6),
(7, 'Global MEP Plant Systems', 'Preferred  Framework', 15, 4.7),
(8, 'Precast Concrete Specialists', 'Spot / Non-Framework', 75, 3.1),
(9, 'Metro Facades & Glazing', 'Spot / Non-Framework', 82, 2.8),
(10, 'Rapid Scaffolding Supply', 'Spot / Non-Framework', 65, 3.4);

-- 3. Insert Materials
INSERT INTO materials (id, material_name, category, unit_cost) VALUES
(1, 'Structural Steel Beams', 'Structural Steel & Metalwork', 450.00),
(2, 'General Drywall Panels', 'Drywall & Finishes', 12.50),
(3, 'Heavy Duty Copper Cable', 'MEP  Cable & Containment', 85.00),
(4, 'High Strength Ready-Mix C40', 'Ready-Mix & Aggregates', 120.00),
(5, 'Premium Softwood Timber Joists', 'Timber & Engineered Wood', 45.00),
(6, 'Industrial HVAC Unit (15kW)', 'MEP  Plant & Equipment', 4500.00),
(7, 'Precast Concrete Stairs', 'Precast & Specialist Concrete', 1500.00),
(8, 'Double-Glazed Facade Panels', 'Facades & Glazing', 650.00),
(9, 'Scaffold Poles & Couplers', 'Scaffolding & Temporary Works', 8.50),
(10, 'Merchant Cement & Aggregates', 'General Merchanted Goods', 15.00);

-- 4. Insert Orders
-- Order 1: High risk delivery (delayed prediction)
INSERT INTO orders (id, supplier_id, material_id, quantity, order_date, delivery_date, risk_score, risk_level, prediction_probability) VALUES
(1, 9, 8, 120, '2026-05-10', '2026-06-15', 82, 'HIGH', 0.82),
-- Order 2: Low risk delivery
(2, 1, 1, 50, '2026-05-12', '2026-06-20', 18, 'LOW', 0.18),
-- Order 3: Medium risk delivery
(3, 8, 7, 30, '2026-05-15', '2026-06-18', 58, 'MEDIUM', 0.58),
-- Order 4: High risk delivery
(4, 10, 9, 500, '2026-05-20', '2026-06-10', 74, 'HIGH', 0.74),
-- Order 5: Low risk delivery
(5, 3, 3, 200, '2026-05-22', '2026-06-25', 12, 'LOW', 0.12),
-- Order 6: Low risk delivery
(6, 6, 5, 150, '2026-05-25', '2026-06-30', 25, 'LOW', 0.25),
-- Order 7: Medium risk delivery
(7, 2, 10, 1000, '2026-05-28', '2026-06-12', 45, 'MEDIUM', 0.45);

-- 5. Insert Predictions
INSERT INTO predictions (order_id, probability, expected_delay_days, prediction_timestamp) VALUES
(1, 0.82, 6, '2026-05-11 09:00:00'),
(2, 0.18, 0, '2026-05-13 10:15:00'),
(3, 0.58, 3, '2026-05-16 11:30:00'),
(4, 0.74, 5, '2026-05-21 14:20:00'),
(5, 0.12, 0, '2026-05-23 16:45:00'),
(6, 0.25, 1, '2026-05-26 08:30:00'),
(7, 0.45, 2, '2026-05-29 13:10:00');

-- 6. Insert Alerts
INSERT INTO alerts (order_id, alert_type, message, created_at) VALUES
(1, 'CRITICAL', 'Delivery of Double-Glazed Facade Panels from Metro Facades & Glazing has a 82% probability of delay. Expected delay: 6 days. This item is on the project critical path.', '2026-05-11 09:05:00'),
(4, 'CRITICAL', 'Delivery of Scaffold Poles & Couplers from Rapid Scaffolding Supply has a 74% probability of delay. Expected delay: 5 days.', '2026-05-21 14:25:00'),
(3, 'WARNING', 'Delivery of Precast Concrete Stairs from Precast Concrete Specialists has a 58% probability of delay. Expected delay: 3 days.', '2026-05-16 11:35:00');
