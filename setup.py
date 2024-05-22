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
        # Add your dependencies here (Include lower and upper bounds as applicable)
        'boto3>=1.34.0,<2.0.0',
        'pydantic>=2.7.0,<3.0.0',
        'PyYAML>=6.0, <7.0',
        'jsonschema<5.0.0',
        'platformdirs>=4.0.0, <5.0.0'
    ],
    extras_require={
        "codegen": [
            'black>=24.3.0, <25.0.0',
            'pandas>=2.2.0, <=2.2.2', 
            'pytest>=8.0.0, <9.0.0',
            'pylint>=3.0.0, <4.0.0'
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License 2.0',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
