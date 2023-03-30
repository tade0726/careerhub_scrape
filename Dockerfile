FROM continuumio/anaconda3:latest
COPY environment.yml .
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y make

RUN conda update -n base -c defaults conda
RUN conda env create -f environment.yml
RUN echo "conda activate web_spider" >> ~/.bashrc

ENV PATH /opt/conda/envs/web_spider/bin:$PATH

WORKDIR /app
EXPOSE 8888
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
