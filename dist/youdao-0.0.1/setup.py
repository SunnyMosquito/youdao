from setuptools import setup, find_packages
import os
import sys
setup(
    name="youdao",
    version="0.0.1",
    author="zhiwen",
    author_email="191329761@qq.com",
    description="youdao translate",
    long_description=open("README.md").read(),
    license="MIT",
    url="https://github.com/SunnyMosquito/youdao",
    packages=['youdao'],
    data_files=[('youdao',['youdao/search.png','youdao/setting.png','youdao/youdao.png'])],
    # package_data={'package': ['search.png', 'setting.png', 'youdao.png']},
    install_requires=[
        "PyQt5",
    ],
    classifiers=[
        "Topic :: Text Processing :: Indexing",
        "Programming Language :: Python :: 3",
    ],
    entry_points={
        'console_scripts': [
            'youdao = youdao.youdao:main'
        ]
    }
)
