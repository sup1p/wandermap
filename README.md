# WanderMap Backend -
website: https://wandermap-front-phi.vercel.app/

## PROJECT OVERVIEW
WanderMap is a backend service where users after registration can see the map, add and manage their travel history. Trips are displayed from oldest to newest and in the map, with photo previews, and users can control profile visibility by setting their access policy (e.g., public or "honored-only" access). 

---

## INSTRUCTIONS

### 🛠 Clone the Project
```bash
git clone https://github.com/your-username/wandermap-backend.git
cd wandermap-backend
```

###  Create `.env` File
Add the required environment variables. All environment-specific values are read using `os.getenv` in `settings.py`.

###  Install Dependencies
```bash
pip install -r requirements.txt
```

###  Apply Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### ▶ Run Development Server
```bash
python manage.py runserver
```

---

## DEVELOPMENT PROCESS
- **Understanding the Task**: I began with a deep analysis of the technical requirements, as understanding the problem is 50% of the solution.
- **Tech Stack Selection**: Initially considered Java + Spring, but switched to Django REST Framework due to time constraints and better familiarity.
- **Database**: Chose PostgreSQL for its simplicity and reliability. Hosted it using **Supabase**.
- **Model Design**: Designed models with future scalability and clear relationships in mind.
- **Features Implemented**:
  - Registration and JWT-based login with **SimpleJWT**
  - CRUD operations for trips
  - Image upload system with external **Supabase S3** bucket
  - Public and private profile access with hashed token links
  - Integration with **Nominatim API** for place autocomplete

---

## UNIQUE METHODOLOGY
- I created a detailed daily schedule leading up to the deadline, planning tasks by hour as in a real-world job environment.
- Images are **not** stored in the database. Only URLs are saved, while the actual files are uploaded to **Supabase S3**.

---

## COMPROMISES
- Chose **Railway** for deployment due to its simplicity and quick setup.
- Used **Supabase** for database hosting to avoid time-consuming AWS configuration.
- Paused my initial long-term development roadmap to focus on a university hackathon, where our team placed second.

---

## WHY THIS STACK?
- **Django + DRF**: Known for rapid MVP development with high productivity.
- **PostgreSQL**: Reliable and easy-to-use relational database.
- **Supabase S3 + Railway**: Lightweight deployment and media storage without extra DevOps complexity.
