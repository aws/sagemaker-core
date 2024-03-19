from setuptools import setup, find_packages

setup(
    name='sagemaker-core',
    version='0.1.0',
    description='An python package for sagemaker core functionalities',
    author='AWS',
    author_email='sagemaker-interests@amazon.com',
    url='https://github.com/mohanasudhan/sagemaker-code-gen',
    packages=find_packages(),
    install_requires=[
        # Add your dependencies here
        'boto3>=1.34.0,<=2.0.0',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License 2.0',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
