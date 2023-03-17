Nuxt/Flask/NGINX boilerplate
============================

Useful to quickly get started on building Flask apps with modern frontend practices.

Installation
------------

1. Clone this repository: `git clone https://github.com/Cheaterman/fluxt && cd fluxt`
1. Install uwsgi - example for Debian: `apt install uwsgi`
1. Start the database server: `docker-compose up -d db`
1. Create the backend virtualenv and activate it: `cd backend && python3 -mvenv env && source env/bin/activate`
1. Install backend runtime & test dependencies: `pip install -r requirements.txt -r requirements-test.txt`
1. Run database migrations: `flask db upgrade`
1. Run the development server: `cd .. && ./start_devserver.sh`
1. In a few seconds, the example chat app should be available at http://localhost:8080/ (if you're getting 502 Bad Gateway, be patient and try again :-) )
