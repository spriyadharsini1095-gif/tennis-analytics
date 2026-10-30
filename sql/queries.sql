--List every competition with its category name
select c1.competition_id,c1.competition_name,c2.category_name from competitions c1 
left join categories c2 on c1.category_id=c2.category_id;
--Count the competitions in each category
select c2.category_name,count(c1.competition_id) as total_competitions from competitions c1 
right join  categories c2 on c1.category_id=c2.category_id 
group by c2.category_name order by total_competitions desc;
--Find all competitions of type "doubles".
select competition_id,competition_name,parent_id,type,gender,level,category_id 
from competitions where type='doubles';
select * from competitions;
--List the competitions in a specific category, such as ITF Men.
select c1.competition_id,c1.competition_name,c1.type,c1.gender,c2.category_name
from competitions c1 join categories c2 on c1.category_id=c2.category_id
where c2.category_name='ITF Men' order by c1.competition_name;
--Show parent competitions and their sub-competitions (self-join on parent_id)
-- Q5: Show parent competitions and their sub-competitions (self-join on parent_id)
SELECT parent.competition_id   AS parent_id,
       parent.competition_name AS parent_competition,
       child.competition_id    AS sub_competition_id,
       child.competition_name  AS sub_competition
FROM competitions child
JOIN competitions parent ON child.parent_id = parent.competition_id
ORDER BY parent.competition_name, child.competition_name;
--Show how competition types are spread across categories.
-- Q6: Distribution of competition types by category
SELECT cat.category_name,
       comp.type,
       COUNT(*) AS total_competitions
FROM competitions comp
JOIN categories cat ON comp.category_id = cat.category_id
GROUP BY cat.category_name, comp.type
ORDER BY cat.category_name, total_competitions DESC;
--Top-level competitions (no parent)
select comp.competition_id,comp.competition_name,comp.type,comp.gender,cat.category_name
from competitions comp left join categories cat on comp.category_id=cat.category_id where 
comp.parent_id is null  order by cat.category_name,comp.competition_name;               
--List each venue with its complex name
select v.venue_id,v.venue_name,c.complex_name from venues v join complexes c 
on v.complex_id=c.complex_id order by c.complex_name,v.venue_name;
--Count the venues in each complex
select c.complex_name,count(v.venue_id) as total_venues from complexes c left join venues v
on c.complex_id=v.complex_id group by c.complex_name order by total_venues desc;
--Venues in a specific country (Chile)
select venue_id,venue_name,city_name,country_name from venues where country_name='Chile'
order by venue_name;
-- Each venue with its timezone
select venue_name,city_name,country_name,timezone from venues order by timezone,venue_name;
-- Complexes with more than one venue
select c.complex_name,count(v.venue_id)as total_venues from complexes c join venues v 
on c.complex_id=v.complex_id group by c.complex_name having count(v.venue_id)>1 order by total_venues desc;
--Venues by country
select country_name,count(*) as total_venues from venues group by country_name order by total_venues desc;
--All venues for a specific complex (Nacional)
select v.venue_name,v.city_name,v.country_name from venues v join complexes c on v.complex_id=c.complex_id
where c.complex_name='Nacional' order by v.venue_name;
-- All competitors with their rank and points
select c.name,c.country,r.rank,r.points from competitor_rankings r join competitors c on 
r.competitor_id=c.competitor_id order by r.rank;
----  Top 5 ranked competitors
select c.name,c.country,r.points,r.rank from competitor_rankings r join competitors c 
on r.competitor_id=c.competitor_id where r.rank<=5 order by r.rank;
---- Competitors with no rank movement (stable rank)
select c.name,c.country,r.points,r.rank from competitor_rankings r join competitors c on
r.competitor_id=c.competitor_id where r.movement =0 order by r.rank;
----Total ranking points of competitors from Croatia
select c.country,sum(r.points) as total_points from competitor_rankings r
join competitors c on r.competitor_id=c.competitor_id where c.country='Croatia'
group by c.country;
----Number of competitors per country
select country ,count(*) as total_competitors from competitors group by country 
----Competitor(s) with the highest points this week
select c.name,c.country,r.rank,r.points from competitor_rankings r join competitors c 
on r.competitor_id=c.competitor_id where r.points=(select max(points) from competitor_rankings);
