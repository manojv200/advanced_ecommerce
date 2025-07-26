#
This is a Django backend for an e-commerce app using:

- PostgreSQL for database
- Redis For Caching
- REST Api with JWT Auth
- Docker Compose for setup

---

#How to Run

#1. Clone the project

git clone https://github.com/manojv200/advanced_ecommerce.git

cd advanced_ecommerce


#3. Start All Services

docker compose up --build -d


#4. Create admin user

docker compose exec web python manage.py createsuperuser

📌 URLs
Django: http://localhost:8000

Api_urls_postman_doc_link:https://drive.google.com/file/d/12sXqmNVVOshk3Vxh2TEajaQSfteaMm8M/view?usp=sharing 

#Tech Stack
Django + PostgreSQL

DRF(REST)

Redis

Docker Compose
