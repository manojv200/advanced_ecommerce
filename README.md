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

#2. Create .env file

DB_NAME=e_commerce_db
DB_USER=root
DB_PASSWORD=root
DB_HOST=db
SECRET_KEY=django-insecure-ck%4l82+$2h&p8=nf)cd20%lr901vn&0mvw*)wwy=#szrno4lt
DEBUG=True

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
