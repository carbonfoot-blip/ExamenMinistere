FROM python:3.11-slim
WORKDIR /app
RUN pip install fastapi uvicorn
COPY backend/main.py ./backend/main.py
COPY backend/examples ./backend/examples
RUN mkdir -p ./backend/static
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]