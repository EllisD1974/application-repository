# Application Repository

A **centralized repository service** for storing, versioning, and distributing applications.  
This project provides a **Dockerized API** that allows teams and organizations to register applications, keep track of different versions, and make them easily accessible from a single location.

---

## 🚀 Features

- 📦 **Application management** – register and organize applications in a structured repository  
- 🔖 **Version tracking** – manage multiple versions of the same application  
- 🐳 **Docker Compose support** – spin up the full stack with a single command  
- 🔑 **Access control (planned)** – restrict downloads to authorized users  
- 📂 **Centralized access** – one place for teams to find and fetch applications  

---

## 📋 Requirements

- [Docker](https://www.docker.com/get-started) (20.x or newer recommended)  
- [Docker Compose](https://docs.docker.com/compose/) v2 or newer  

---

## 🛠️ Setup & Run

### 1. Clone the repository

```bash
git clone https://github.com/EllisD1974/application-repository.git
cd application-repository
```


### 2. Start the application with docker-compose
```bash
docker-compose up -d
```

### 3. Stop the application
```bash
docker-compose down
```


The API will now be available at:
👉 http://localhost:8000


## 📖 Usage

### List all applications
```bash
curl http://localhost:8000/applications
```

### Upload an application/new version

```bash
curl -X POST http://localhost:8000/upload \
  -H "Content-Type: application/json" \
  -d '{
    "name": "MyApp",
    "version": "1.0.0",
    "url": "http://example.com/MyApp/1.0.0/myapp.exe"
  }'
```

### Download an application
```bash
curl -O http://localhost:8000/download-app/MyApp/1.0.0
```


## 🧩 Roadmap
- [ ] Support S3 or local storage
- [ ] Add option for back up checks to allow searching storage if not found in database
- [ ] Add authentication & authorization
- [ ] Provide a python module for API interaction
- [ ] Implement database persistence for metadata
- [ ] Enable S3 / cloud storage backends
- [ ] Add automated CI/CD deployment


## 👤 Maintainer
EllisD1974

**GitHub:** @EllisD1974
