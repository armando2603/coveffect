# coveffect
Coveffect is a project that aim to automatically extract informations from covid-related articles.
In particular what we want to extract from each paper a table containing the list of variants/mutation and their corresponding effects
![Alt text](/screenshot.png?raw=true "Title")
- An instance of the system is available at this link: http://geco.deib.polimi.it/coveffect/#/

## Requirements

- Install the last version of Docker
- Install docker-compose

## Installation
- clone the coveffect repository
- download the model checkpoint using gdown:
```bash
gdown 1VOF7NCqgM5pFaJcexhXjvp-OsLkza5lz
```
- or download it at the following link <a href="https://drive.google.com/file/d/1VOF7NCqgM5pFaJcexhXjvp-OsLkza5lz/view?usp=sharing" target="_blank">drive</a>
- unzip the folder model_0 in the coveffect/backend/api/checkpoints/ folder

## System Usage
### To start the application run in the main folder:
```bash
docker-compose up
```
### open the browser at the following link
- http://localhost:8080/#/

## How to use the model to extract information from a list of abstract
- create a python enviroment and install the backend/requirements.txt 
- run the batch_prediction.ipynb notebook
