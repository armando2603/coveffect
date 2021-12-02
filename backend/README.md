# muteffstage (backend)

virus mutation effects extraction

## Build the docker
```bash
docker build -t muteffstage-backend .
```

### Start the app in development mode (hot-code reloading, error reporting, etc.)
```bash
docker run -d -v "/$(pwd)/:/workspace/" -p 5000:5003 -it --rm muteffstage-backend:latest flask run -p 5003 -h 0.0.0.0
```

### Build the app for production
```bash
TODO
```
