# coveffect (frontend)

virus mutation effects extraction

## Build the docker
```bash
docker build -t coveffect-frontend .
```

## Install the dependencies
```bash
docker run --rm -it -v "/$(pwd)/:/usr/src/app/" -p 61111:8080 coveffect-frontend:latest npm install
```

### Start the app in development mode (hot-code reloading, error reporting, etc.)
```bash
docker run --rm -it -v "/$(pwd)/:/usr/src/app/" -p 61111:8080 coveffect-frontend:latest quasar dev
```

### Build the app for production
```bash
TODO
```
