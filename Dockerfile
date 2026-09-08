FROM python:3.12-slim

WORKDIR /app

COPY requirements-docker.txt .

RUN pip install --no-cache-dir -r requirements-docker.txt

COPY src ./src

ENV PYTHONPATH=/app/src

CMD ["python", "-c", "from air_quality_intelligence.service import AirQualityService; service = AirQualityService(); print(service.get_city_analysis('Nandyal'))"]