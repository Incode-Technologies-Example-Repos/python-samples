<img src="https://incode.com/wp-content/uploads/2022/12/cropped-favicon.jpg?w=96" alt="Incode Logo" title="Incode Developer Sample | Python" align="right" height="96" width="96"/>

# Incode Python Samples

Python samples for Incode API products:

* [Onboarding API][onboarding_api]

* [Conference API][conference_api]

* [Login API][login_api]

* [Validations API][validations_api]

* [Government Validation API][government_api]

Samples include Web Hook Implementations for:
* Creating an session and access token for web and mobile clients
* Creating onboarding URL links
* A basic Web Hook implementation for accessing onboarding results

[incode]: https://incode.com/
[onboarding_api]: https://docs.incode.com/docs/omni-api/api/onboarding
[conference_api]: https://docs.incode.com/docs/omni-api/api/conference
[login_api]: https://docs.incode.com/docs/omni-api/api/login
[government_api]: https://docs.incode.com/docs/omni-api/api/government-validation
[validations_api]: https://docs.incode.com/docs/omni-api/api/api-validations
[webhooks_api]: https://docs.incode.com/docs/omni-api/api/web-hooks


## Incode Samples

To browse ready to use code samples check [Incode Samples](https://github.com/Incode-Technologies-Example-Repos/python-samples).

## Setup

### Prerequisites

#### Conda

1. Install Anaconda

* Windows Anaconda Install - [here][win_conda]
* MacOS Anaconda Install - [here][mac_conda]

1. Create conda environment:

        cd <repo root directory>
        conda env create -f dependencies.yml
        conda env update --prefix ./env --file dependencies.yml  --prune

2. Clone this repository:

        git clone https://github.com/Incode-Technologies-Example-Repos/python-samples.


#### Pip

1. Install [python][python_install]

2. For each dependency listed in the dependencies .yml file run the [pip install][pip_commands] command

[python_install]: https://www.python.org/downloads/
[win_conda]: https://docs.anaconda.com/free/anaconda/install/windows/
[mac_conda]: https://docs.anaconda.com/free/anaconda/install/mac-os/
[pip_commands]: https://docs.anaconda.com/free/anaconda/install/mac-os/

## How to run a sample

### Notebook sample (.ipynb)

1. Start Jupyter Nodebook App

2. Browse to the sample directory

3. Open the <sample.ipynb> file

### Command sample

1. Run the following command

        python sample.py
