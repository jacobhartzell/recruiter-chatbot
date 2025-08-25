# app/Dockerfile

FROM python:3.13-slim


RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

# RUN git clone https://github.com/streamlit/streamlit-example.git .

# RUN --mount=type=bind 

# RUN pip3 install -r requirements.txt


WORKDIR /workspaces/recruiter-chatbot

#RUN pwd && ls

#RUN touch HERE.txt

#RUN uv pip install --system -r requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# ENTRYPOINT ["streamlit", "run", "streamlit_app.py"]

# ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]