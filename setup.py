from setuptools import setup, find_packages

setup(
    name="sogood-backend",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "sqlalchemy==2.0.23",
        "psycopg2-binary==2.9.9",
        "pydantic==2.5.0",
        "pydantic-settings==2.1.0",
        "pandas==2.1.3",
        "python-dotenv==1.0.0",
    ],
) 