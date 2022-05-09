# coveffect (backend)

virus mutation effects extraction

### Suggested installation for annoy on Windows 10
Without installing all Visual Studio 2015
[How to install annoy in python windows environment](https://www.programmersought.com/article/95834605670/)

## Build the docker
```bash
docker build -t coveffect-backend .
```

### Start the app in development mode (hot-code reloading, error reporting, etc.)
```bash
docker run -d -v "/$(pwd)/:/workspace/" -p 61113:5003 -it --rm coveffect-backend:latest flask run -p 5003 -h 0.0.0.0
```

### Build the app for production
```bash
TODO
```
