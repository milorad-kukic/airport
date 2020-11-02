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

# Crate admin user

In order to login to admin console, you need to create an admin user with following command:

    docker-compose run --rm python sh -c "python manage.py createsuperuser"

You can now open the admin section in your browser at `http://127.0.0.1:8000/admin` and login with a user that you just created.

# Make API calls

*Note: Check Simulator section*

When we start the app, there are no aircrafts in the system. When new aircraft communicates with an airport, it needs to send it's type, previous state and intent like following:

    curl --header "Content-Type: application/json" --request POST --data '{"public_key": "{public_key_content}", "type": "AIRLINER", "state": "PARKED", "intent": "TAKE_OFF" }' http://localhost:8000/api/NC9574/intent/

After initial communication, aircraft can send data just by providing call sign:

    curl --header "Content-Type: application/json" --request POST --data '{"public_key": "{public_key_content}", "state": "AIRBORNE" }' http://localhost:8000/api/NC9574/intent/

# Simulator

You can visit `http://localhost:8000/simulator/` and see API in action without forming these call manually. Intent was to give you a good insight of what calls were sent and how it affects the state of the app.

In order to have best experience, you can open two browser windows side by side. In one you open an admin console at `http://127.0.0.1:8000/admin` and in other open a simulator at `http://localhost:8000/simulator/`. In simulator you need to provide a public key which is required by the API. Do it by copying a content of the public key into appropriate field.

**When you start the simulation, all aircraft data and logs data will be deleted !!!**

By executing next step you will perform an action described bellow "EXECUTE NEXT STEP" button. State change log will appear in admin console which check for new logs every 10 seconds.

Enjoy!

[build-status-image]: https://travis-ci.com/milorad-kukic/airport.svg?branch=master
[travis]: https://travis-ci.com/milorad-kukic/airport?branch=master
                                     
