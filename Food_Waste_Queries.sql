USE food_waste_management;

-- Question 1:
-- How many food providers are there in each city?

SELECT City,
       COUNT(*) AS Providers_Count
FROM providers
GROUP BY City
ORDER BY Providers_Count DESC
LIMIT 10;

-- Query 2: How many food receivers are there in each city?
SELECT City,
       COUNT(*) AS Receivers_Count
FROM receivers
GROUP BY City
ORDER BY Receivers_Count DESC
LIMIT 10;

-- Query 3: Which type of food provider contributes the most food?

SELECT Provider_Type,
       SUM(Quantity) AS Total_Food_Quantity
FROM food_listings
GROUP BY Provider_Type
ORDER BY Total_Food_Quantity DESC;

-- Query 4:What is the contact information of food providers in a specific city?
SELECT Provider_ID,
       Name,
       Contact,
       City
FROM providers
WHERE City = 'South Christopherborough';

-- Query 5: Which receivers have claimed the most food?
SELECT
    r.Receiver_ID,
    r.Name,
    COUNT(c.Claim_ID) AS Total_Claims
FROM receivers r
JOIN claims c
    ON r.Receiver_ID = c.Receiver_ID
GROUP BY r.Receiver_ID, r.Name
ORDER BY Total_Claims DESC
LIMIT 10;

-- Query 6: What is the total quantity of food available from all providers?
SELECT
    SUM(Quantity) AS Total_Food_Available
FROM food_listings;

-- Query 7: Which city has the highest number of food listings?
SELECT
    Location,
    COUNT(*) AS Food_Listings_Count
FROM food_listings
GROUP BY Location
ORDER BY Food_Listings_Count DESC
LIMIT 10;

-- Query 8: What are the most commonly available food types?
SELECT
    Food_Type,
    COUNT(*) AS Available_Count
FROM food_listings
GROUP BY Food_Type
ORDER BY Available_Count DESC;

-- Query 9: How many food claims have been made for each food item?
SELECT
    f.Food_ID,
    f.Food_Name,
    COUNT(c.Claim_ID) AS Total_Claims
FROM food_listings f
LEFT JOIN claims c
    ON f.Food_ID = c.Food_ID
GROUP BY f.Food_ID, f.Food_Name
ORDER BY Total_Claims DESC
LIMIT 10;

-- Query 10: Which provider has had the highest number of successful food claims?
SELECT
    p.Provider_ID,
    p.Name,
    COUNT(c.Claim_ID) AS Successful_Claims
FROM providers p
JOIN food_listings f
    ON p.Provider_ID = f.Provider_ID
JOIN claims c
    ON f.Food_ID = c.Food_ID
WHERE c.Status = 'Completed'
GROUP BY p.Provider_ID, p.Name
ORDER BY Successful_Claims DESC
LIMIT 10;

-- Query 11:What percentage of food claims are Completed vs Pending vs Cancelled?
SELECT
    Status,
    COUNT(*) AS Total_Claims,
    ROUND(
        COUNT(*) * 100.0 /
        (SELECT COUNT(*) FROM claims),
        2
    ) AS Percentage
FROM claims
GROUP BY Status
ORDER BY Percentage DESC;

-- Query 12:What is the average quantity of food claimed per receiver?
SELECT
    r.Receiver_ID,
    r.Name,
    ROUND(AVG(f.Quantity), 2) AS Avg_Quantity_Claimed
FROM receivers r
JOIN claims c
    ON r.Receiver_ID = c.Receiver_ID
JOIN food_listings f
    ON c.Food_ID = f.Food_ID
GROUP BY r.Receiver_ID, r.Name
ORDER BY Avg_Quantity_Claimed DESC
LIMIT 10;

-- Query 13: Which meal type (Breakfast, Lunch, Dinner, Snacks) is claimed the most?
SELECT
    f.Meal_Type,
    COUNT(c.Claim_ID) AS Total_Claims
FROM food_listings f
JOIN claims c
    ON f.Food_ID = c.Food_ID
GROUP BY f.Meal_Type
ORDER BY Total_Claims DESC;

-- Query 14: What is the total quantity of food donated by each provider?
SELECT
    p.Provider_ID,
    p.Name,
    SUM(f.Quantity) AS Total_Donated
FROM providers p
JOIN food_listings f
    ON p.Provider_ID = f.Provider_ID
GROUP BY p.Provider_ID, p.Name
ORDER BY Total_Donated DESC
LIMIT 10;

-- Query 15: Which cities have the highest demand based on completed food claims?
SELECT
    r.City,
    COUNT(c.Claim_ID) AS Completed_Claims
FROM receivers r
JOIN claims c
    ON r.Receiver_ID = c.Receiver_ID
WHERE c.Status = 'Completed'
GROUP BY r.City
ORDER BY Completed_Claims DESC
LIMIT 10;


