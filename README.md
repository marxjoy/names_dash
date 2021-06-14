# Names popularity Dashboard
Dashboard with data on first names given in Poland in the 21st century. 

Demo:
[http://18.198.22.122/](http://18.198.22.122/)

Data source:
[https://dane.gov.pl/pl/dataset/219,imiona-nadawane-dzieciom-w-polsce](https://dane.gov.pl/pl/dataset/219,imiona-nadawane-dzieciom-w-polsce)

## Technologies used: 
* plotly / dash
* docker
* postgresql database
* pandas 

## Setup
Create .env file with DB credentials data:
```
SQL_HOST=xxx
SQL_PASSWORD=xxx
SQL_USER=xxx
SQL_DATABASE=xxx
```

Run containers:
```
bash run_docker.sh
```
