

Dependencies install steps:

1.
```
poetry env use python3.12
```
2. 
```
poetry install
```

Run steps:

to run use docker-compose.*.yaml


project structure:
```
root/
│
├── libs/
│    └─ [lib_name]
│         ├── src/
│         └─ pyproject.toml
│
├── services/
│    └── [service_name]
│         ├── src/
│         ├── Dockerfile
│         └─ pyproject.toml
│
├── env/
│    └── [.env.*]
│
├── docker/
│    └─ [docker-compose.*.yml]
│
└─ pyproject.toml
```