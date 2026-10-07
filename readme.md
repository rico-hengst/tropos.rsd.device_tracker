

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
  <a href="https://github.com/othneildrew/Best-README-Template">
    <img src="static/images/logbook_logo2_pink.svg" alt="Logo" height="100">
  </a>

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
