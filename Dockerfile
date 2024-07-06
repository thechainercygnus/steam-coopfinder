FROM python:3.12.4
RUN mkdir /usr/src/app
WORKDIR /usr/src/app
RUN mkdir log
RUN mkdir out
COPY requirements.txt .
COPY ./steam_coopfinder /usr/src/app/steam_coopfinder
RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt
CMD ["python", "-m", "steam_coopfinder"]