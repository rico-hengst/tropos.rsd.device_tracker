

<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url] [![License][license.shield]][license-url]




<!-- PROJECT LOGO -->
<br />
<div align="centerv" style="margin-bottom: 7ex;">
    <img src="static/images/logbook_logo2_pink.png" alt="Logo" height="100">
</div>


<!-- ABOUT THE PROJECT -->
## About The Project
[![Python][python.org]][python-url] [![Flask][flask.python]][flask-url] [![Bootstrap][Bootstrap.com]][Bootstrap-url] [![JQuery][JQuery.com]][JQuery-url]


Device tracker is the name of a Python Flask App that provide some services to track the location history of mobile research devices.

Assumption:

* devices are "mobile" and change their position (earth surface) from time to time




<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

### Installation


1. Clone the repo

   ```sh
   git clone https://github.com:rico-hengst/tropos.rsd.device_tracker.git
   ```
2. Install Python env and packages

   ```sh
   conda create --name myenv --file environment.yml
   ```

### Config

* default config file: config/dv.config
* you can use the file as it is or create another one somewhere else
    * make sure that the content and structure is based on the default config
* when starting the application, the config file will be exported as tmp ENV variable (DV_ENV)


### Usage: Start the application

* local test server

    ```sh
    export DV_ENV=../config/dv.config; flask --debug --app dv_app.py run --host 0.0.0.0 --port 5555
    ```
* via unicorn




### Usage: Import

tbd

<p align="right">(<a href="#readme-top">back to top</a>)</p>




### Authors

* AK
* RH [![ORCID iD](https://img.shields.io/badge/-ORCID-A6CE39?logo=orcid&logoColor=white)](https://orcid.org/0000-0001-8994-5868)




### Copyright and license [![GNU V3][license.shield]][license-url]
This application is free software, licensed under GNU v3.0. 

## Details

### Data structure

The data are stored in json format.
An API is provided to access the data, see later on.

* Each record of the data has a key with the unique keyname of the device.

```json
{
  "device_keyname": {
    "calibration": [],
    "history": [],
    "metadata": {  }
  }
}
```

* The device record consists of three parts.
    * The metadata part contains several common info to the device. The structure of the metadata part is defined at [config/schema_device.json](config/schema_device.json).
    * The history part contains a list of location information where the instrument took the measurements. The structure of the history record is defined at [config/schema_history.json](config/schema_history.json).
    * The calibration part contains a list of already realized calibrations of the device. The structure of the calibration record is defined at [config/schema_calibration.json](config/schema_calibration.json).
* Example

```json
{
    "ms-21_sn445566a": {
        "metadata": {
            "class": [
                "radiation",
                "pygeometer"
            ],
            "created": "2026-08-10T06:55:35Z",
            "description": "",
            "device_manufacturer": {
                "address": "EKO Instruments Europe B.V. Lulofsstraat 55, Unit 28 2521 AL, Den Haag Netherlands",
                "contact": "",
                "name": "EKO"
            },
            "device_model": {
                "description": "Research-grade, accurate, and robust, the MS-21 measures longwave downwelling radiation and longwave net radiation in a wide spectral band and delivers superior stability independent of the sensors\u2019 operating temperature.",
                "name": "MS-21",
                "pid": "",
                "purchased": "2022-01-01T12:00:00Z",
                "serial": {
                    "ManufactSN#2026100816384512#": "2345IIO88"
                }
            },
            "is_platform": false,
            "name": "MS-21_SN445566a",
            "owner": {
                "address": "",
                "contact": "x@tropos.de",
                "inv": {
                  "TINV#2026100816384517#": "2026001",
                  "TINV2#2026100816384519#": "20889H"
                },
                "name": "TROPOS"
            }
        },
        "calibration": [
            {
                "calibration_coefficient_uncertainties": [
                  0.007,
                  1.3,
                  0.005
                ],
                "calibration_coefficients": [
                  0.11992,
                  -22.3,
                  0.3
                ],
                "calibration_equation": "calibrated irradiance = voltage*calibration_factor",
                "certificate_id": "S25000039900-EX25",
                "certificate_issuance_date": "2023-07-03T12:12:12Z",
                "description": "",
                "performed_at": "DWD",
                "performed_by": "Ak Hein",
                "performed_period_dates": [
                  "2023-07-03T12:12:12Z",
                  "2023-07-13T12:12:12Z"
                ],
                "performed_repeats": 1,
                "record_created_date": "2024-08-03T12:12:12Z",
                "temperature_correction_coefficients": [
                  5.6111e-06,
                  -0.000129,
                  -6.0915e-05
                ],
                "temperature_correction_equation": "BTC: U/U0= a*T^2+b*T+c",
                "used_method": "ISO9846 continuos sun-and-shade method",
                "used_reference": "",
                "uuid": "d3r1234214tz4z3z23z5z3zr",
                "valid_period_dates": [
                  "2023-08-03T00:12:12Z",
                  "2024-08-03T12:12:12Z"
                ]
            },
            {
                ...
            }
        ],
        "history": [
            {
                "created": "2026-08-10T07:03:54Z",
                "location": {
                  "country": "Cabo Verde",
                  "is_mobile": false,
                  "lat": 16.878,
                  "lon": -24.995,
                  "name": "Mindelo"
                },
                "platform": [
                  "TARO"
                ],
                "startdate": "2023-09-24T12:12:12Z",
                "stopdate": "2023-12-01T00:12:12Z",
                "uuid": "a66bd642-9489-11f1-ac24-cc2f71a772c7"
            },
            {
                "created": "2026-08-10T07:03:54Z",
                "location": {
                  "country": "Germany",
                  "is_mobile": false,
                  "lat": 51.525507,
                  "lon": 12.927753,
                  "name": "Melpitz"
                },
                "platform": [
                  "TARO"
                ],
                "startdate": "2024-01-24T12:12:12Z",
                "stopdate": "2024-12-01T00:12:12Z",
                "uuid": "a66bd6ec-9489-11f1-ac24-cc2f71a772c7"
            },
            {
                ...
            }
        ]
    }, 
    "Device_2" : {
        ...
    }
}
```





<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/rico-hengst/tropos.rsd.device_tracker?color=pink
[contributors-url]: https://github.com/rico-hengst/tropos.rsd.device_tracker/graphs/contributors?
[license.shield]: https://img.shields.io/badge/license-GNU/GPLv3-pink
[license-url]: https://www.gnu.org/licenses/gpl-3.0.de.html
[Bootstrap.com]: https://img.shields.io/badge/-Bootstrap_5-7952B3?style=flat&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?logo=jQuery&logoColor=white
[JQuery-url]: https://jquery.com 
[python.org]: https://img.shields.io/badge/python-%3E=3.11-blue?logo=python
[python-url]: https://www.python.org/
[flask.python]: https://img.shields.io/badge/Python-flask-blue
[flask-url]: https://github.com/pallets/flask
