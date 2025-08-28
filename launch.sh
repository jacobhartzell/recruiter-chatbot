#!/bin/bash

# Just a small script to launch streamlit from the command line while in Docker desktop.
streamlit run streamlit_app.py --server.enableCORS false --server.enableXsrfProtection false
