"""Setup script for eastmoney_tool package."""

from setuptools import setup, find_packages

setup(
    name="eastmoney_tool",
    version="0.1.0",
    description="东方财富数据中心：机构类数据分析小工具",
    author="",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "pandas>=2.1.0",
        "pyarrow>=15.0.0",
        "streamlit>=1.32.0",
        "python-dateutil>=2.9.0.post0",
    ],
)

