curl -i -X POST -d "name=Japanese" http://localhost:8080/restaurants/by_name
echo
echo ---
curl -i -X POST -d "cuisine=Japanese" http://localhost:8080/restaurants/by_cuisine
echo
echo ---
curl -i -X GET http://localhost:8080/restaurants/10 
echo
echo ---