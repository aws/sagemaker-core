# Contribution Guidelines for sagemaker-core

## Report Bugs/Feature Requests

We welcome you to use the GitHub issue tracker to report bugs or suggest features.

When filing an issue, please check [existing open](https://github.com/aws/sagemaker-core/issues) and [recently closed](https://github.com/aws/sagemaker-core/issues?q=is%3Aissue+is%3Aclosed) issues to make sure somebody else hasn't already
reported the issue. Please try to include as much information as you can. Details like these are incredibly useful:

* A reproducible test case or series of steps.
* The version of our code being used.
* Any modifications you've made relevant to the bug.

## Contribute via Pull Requests (PRs)

Contributions via pull requests are much appreciated.

Before sending us a pull request, please ensure that:

* You are working against the latest source on the *main* branch.
* You check the existing open and recently merged pull requests to make sure someone else hasn't already addressed the problem.
* You open an issue to discuss any significant work - we would hate for your time to be wasted.


### Pull Down the Code

1. If you do not already have one, create a GitHub account by following the prompts at [Join Github](https://github.com/join).
1. Create a fork of this repository on GitHub. You should end up with a fork at `https://github.com/<username>/sagemaker-python-sdk`.
   1. Follow the instructions at [Fork a Repo](https://help.github.com/en/articles/fork-a-repo) to fork a GitHub repository.
1. Clone your fork of the repository: `git clone https://github.com/<username>/sagemaker-core` where `<username>` is your github username.


## Setting up Personal Development Enviornment using Pyenv
* Set up prerequisites following guide here -  https://github.com/pyenv/pyenv/wiki#suggested-build-environment

* Install Pyenv
```
curl https://pyenv.run | bash
```

* Add the following to  ~/.zshrc to load Pyenv automatically
```
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init path)"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

* Install Python Version and setup virtual-env
```
pyenv install 3.10.14
pyenv virtualenv 3.10.14 py3.10.14
pyenv activate py3.10.14
```

* Install dependencies required for CodeGen and set PYTHONPATH
```
pip install ".[codegen]"
source .env
```

## Run Automated Code gen
* To generate all CodeGen code run the below
```
python src/sagemaker_core/tools/codegen.py
```

## Testing
* To check for regressions in existing flows, make sure to run: `pytest tst`. For new unit test coverage added make sure `pytest tst` validates them. 
```
pytest tst
```
* To run integrationt tests , use
```
pytest integ
```
* Use Pylint to detect errors and improve code quality. For code style errors use `black` to format the files.
```
black .
pylint **/*.py
```

## Building Distribution
* To build a distribution of SageMakerCore run below
```
pip install --upgrade build
python -m build
```

### Send a Pull Request

GitHub provides additional document on [Creating a Pull Request](https://help.github.com/articles/creating-a-pull-request/).

Please remember to:
* Use commit messages (and PR titles) that follow the guidelines under [Commit Your Change](#commit-your-change).
* Send us a pull request, answering any default questions in the pull request interface.
* Pay attention to any automated CI failures reported in the pull request, and stay involved in the conversation.

## Documentation 

The documentation for resource classes and shapes are generated automatically from boto's documentation .
If there is any documentation that is misleading please let us know so we can work with boto on it . 

The documentation that we follow for the code generation tools is the regular python doc strings outlining what the function does,
what each parameter represents and the return values.

## Code of Conduct

This project has adopted the [Amazon Open Source Code of Conduct](https://aws.github.io/code-of-conduct).
For more information see the [Code of Conduct FAQ](https://aws.github.io/code-of-conduct-faq) or contact
opensource-codeofconduct@amazon.com with any additional questions or comments.

## Security Issue Notifications

If you discover a potential security issue in this project we ask that you notify AWS/Amazon Security via our [vulnerability reporting page](http://aws.amazon.com/security/vulnerability-reporting/). Please do **not** create a public github issue.


## Licensing

See the [LICENSE](https://github.com/aws/sagemaker-core/blob/master/LICENSE) file for our project's licensing. We will ask you to confirm the licensing of your contribution.

We may ask you to sign a [Contributor License Agreement (CLA)](http://en.wikipedia.org/wiki/Contributor_License_Agreement) for larger changes.

