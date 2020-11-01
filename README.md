# Next-Generation Airport Operations

[![build-status-image]][travis]

**REST API for automation of airport operations**

This is an exercise project

---

# Software Stack

Following tools are used for this application:

* Django
* django rest framework
* Postgresql
* Celery
* Redis

# Running the app

Make sure that you have installed **Docker** and **docker-compose**.

Clone this repo and move into it in terminal:

    git clone http://github.com/milorad-kukic/airport
   
    cd airport

Run the application by typing:

    docker-compose up -d

You can now open the Application in your browser at `http://127.0.0.1:8000/` and you can start issuing API calls.



[build-status-image]: https://travis-ci.com/milorad-kukic/airport.svg?branch=master
[travis]: https://travis-ci.com/milorad-kukic/airport?branch=master
                                     
