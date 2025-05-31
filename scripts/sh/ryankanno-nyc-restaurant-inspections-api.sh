curl -X POST -H "Accept: application/json" -d "name=Japanese" http://localhost:8080/restaurants/by_name
curl -X POST -H "Accept: application/json" -d "cuisine=Japanese" http://localhost:8080/restaurants/by_cuisine
curl -X GET -H "Accept: application/json" http://localhost:8080/restaurants/10
# curl -X GET "http://localhost:8080/"