# muteffstage (frontend)

virus mutation effects extraction

## Build the docker
```bash
docker build -t muteffstage-frontend .
```

## Install the dependencies
```bash
docker run --rm -it -v "/$(pwd)/:/usr/src/app/" -p 61111:8080 muteffstage-frontend:latest npm install
```

### Start the app in development mode (hot-code reloading, error reporting, etc.)
```bash
docker run --rm -it -v "/$(pwd)/:/usr/src/app/" -p 61111:8080 muteffstage-frontend:latest quasar dev -m ssr
```

### Build the app for production
```bash
TODO
```
