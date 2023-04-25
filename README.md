# WATCHER

<p align="center">
  <img width="300" height="300" src="assets/ninja.png">
</p>

<p align="center">
    <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/pycti?color=%2327AE60&style=plastic">
    <img alt="GitHub" src="https://img.shields.io/github/license/mkdemir/opencti-watcher?color=%2334495E&style=plastic">

</p>

Watcher is a solution that integrates with security products using IoC (Indicator of Consensus) information gathered through the OpenCTI platform. This integration makes it possible to detect and respond to threats faster.

## Table of contents

* [Features](#features)
* [Setup](#setup)
* [Usage](#usage)
* [Contributing](#contributing)
* [License](#license)

## Features

* Integrates with security products
* Uses IoC information gathered through OpenCTI

## Setup

1. Install and configure OpenCTI
    * For more information on OpenCTI installation, please refer to their documentation.
2. Clone the Watcher repository:
    * git clone [https://github.com/mkdemir/opencti-watcher.git](https://github.com/mkdemir/opencti-watcher.git)
3. Install dependencies:
    * Windows - Powershell: To install OpenCTI on Windows using PowerShell, run the following command
    `.\setup_powershell.ps1 -PythonVersion "3.11" -EnvName "venv" -RequirementsFile ".\requirements.txt"`
        -PythonVersion specifies the Python version to install.
        -EnvName specifies the name of the virtual environment to create.
        -RequirementsFile specifies the path to the requirements file containing the dependencies.
    * Linux/Unix - shell script: To install OpenCTI on Linux/Unix using the shell script, run the following command
    `./setup_linux.sh`

## Usage

1. Navigate to the `opencti-watcher/src/` directory in your terminal.
2. Run the command `../venv/bin/python3 main.py` to start the script.
3. When prompted, enter the **URL** and **API** key of your OpenCTI server.
4. The script will start running and sending IoC information to your OpenCTI server.
5. When the script finishes, it will stop running.
6. You can find the files containing IoC information under the **data/data_log/** folder.

**Note:** Make sure to have a running OpenCTI instance and API key available before running the script.

## Contributing

1. Fork this repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Make your changes and commit them (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Create a new Pull Request

## License

This project is licensed under the **MIT License** - see the **[LICENSE](https://github.com/mkdemir/opencti-watcher/blob/main/LICENSE)** file for details.
