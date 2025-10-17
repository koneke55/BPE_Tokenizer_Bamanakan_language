from setuptools import setup, find_packages

setup(
    name="bambara-bpe-tokenizer",
    version="1.0.0",
    author="Sambou Kone",
    author_email="samboukone99@gmail.com",
    description="A simple Byte Pair Encoding (BPE) tokenizer for Bamanakan",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Topic :: Text Processing :: Linguistic"
    ],
)
