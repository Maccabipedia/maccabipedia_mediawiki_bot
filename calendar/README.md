# Maccabipedia Calendar
Maccabipedia's Calendar is a small python program to scrap data about games schedule from [Maccabi Tel Aviv Official Site](maccabi-tlv.co.il), parse it and display the games as events in Google Calendar.


<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Twitter Follow][follow-shield]][follow-url]

<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About the Project](#about-the-project)
  * [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Contributing](#contributing)
* [Contact](#contact)



<!-- ABOUT THE PROJECT -->
## About The Project

We wanted to have a calender for for Maccabi games, but without manual updating.
So we decided to scrap the data from the official site and automate the proccess as much as possible.

### Built With
* Python
* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
* [googleapiclient](https://github.com/googleapis/google-api-python-client)


<!-- GETTING STARTED -->
## Getting Started

1. Have a Google account with Google Developer Console

### Prerequisites

* Python >= 3.8

### Installation

1. Clone the repo

2. Create .env file, insert your calendar id and save it in repo directory:
```env
calendar_id = 'your_calendar_id'
```

3. Create OAuth 2.0 Client Credentials for your user at [Google Developer Console](https://console.developers.google.com/a)

4. Download the credentials & save them as 'credentials.json'

5. Install Python packages
```python
pip install 
```

6. run main.py


<!-- CONTRIBUTING -->
## Contributing

Pull requests are welcome.

For major changes, please open an issue first to discuss what you would like to change.

Best to talk with us first!



<!-- LICENSE
## License

Distributed under the MIT License. See `LICENSE` for more information.
 -->



<!-- CONTACT -->
## Contact

Maccabipedia - [@maccabipedia](https://twitter.com/maccabipedia) - maccabipedia@gmail.com

[Shlomixg](https://github.com/Shlomixg)

Project Link: [https://github.com/Maccabipedia/MaccabipediaCalendar](https://github.com/Maccabipedia/MaccabipediaCalendar)



<!-- MARKDOWN LINKS & IMAGES -->
[contributors-shield]: https://img.shields.io/github/contributors/Maccabipedia/MaccabipediaCalendar.svg?style=flat-square
[contributors-url]: https://github.com/Maccabipedia/MaccabipediaCalendar/graphs/contributors
[follow-shield]: https://img.shields.io/twitter/follow/maccabipedia?color=%23ffdd00&style=flat-square
[follow-url]: https://twitter.com/intent/follow?screen_name=maccabipedia
