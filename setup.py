from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sogood-nutritional-analysis",
    version="1.0.0",
    author="SoGood Team",
    description="Analyse nutritionnelle des produits alimentaires",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.10",
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "cassandra-driver==3.28.0",
        "cqlengine==0.21.0",
        "pydantic==2.5.0",
        "pandas==2.1.3",
        "numpy==1.25.2",
        "scikit-learn==1.3.2",
    ],
) 