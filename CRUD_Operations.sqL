USE food_waste_management;

-- CREATE

INSERT INTO food_listings
(Food_ID, Food_Name, Quantity, Expiry_Date,
 Provider_ID, Provider_Type, Location,
 Food_Type, Meal_Type)
VALUES
(2001, 'Rice', 25, '2025-12-31',
 343, 'Grocery Store', 'Test City',
 'Vegetarian', 'Lunch');


-- READ
SELECT *
FROM food_listings
WHERE Food_ID = 2001;

-- UPDATE
UPDATE food_listings
SET Quantity = 50
WHERE Food_ID = 2001;


-- DELETE
DELETE FROM food_listings
WHERE Food_ID = 2001;