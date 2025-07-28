# Broken Link Checker (BLC)

A web-based tool that automatically scans websites for broken links. The BLC crawls through a provided URL and checks the status of all links based on user-defined filters, returning clear results for each link's status.

## Features

- **Automated Link Detection**: Scans web pages and identifies all links
- **Customizable Filters**: Set user-defined criteria for which links to check
- **Clear Status Reporting**: Returns one of three statuses for each link:
  - `OK` - Link is working properly
  - `BROKEN` - Link is inaccessible or returns an error
  - `SKIP` - Link was excluded based on your filters
- **Web Interface**: Easy-to-use browser-based interface
- **Docker Support**: Quick deployment with containerization

## Getting Started

### Prerequisites

Choose one of the following:
- Python 3.x installed on your system
- Docker and Docker Compose installed

### Installation & Usage

#### Method 1: Direct Python Execution

1. Clone this repository:
   ```bash
   git clone [repository-url]
   cd [repository-name]
   ```

2. Install dependencies (if requirements.txt exists):
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

4. Open your browser and navigate to `http://localhost:5000`

#### Method 2: Docker (Recommended)

1. Clone this repository:
   ```bash
   git clone [repository-url]
   cd [repository-name]
   ```

2. Build and run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

3. Open your browser and navigate to `http://localhost:5000`

## Demo

Watch this demonstration video to see the BLC in action and learn how to use all its features:

[**View Demo Video**](https://www.loom.com/share/63926f8d1e2f41ff8d1a58724bc40d0d?sid=4552f85c-bc2e-4c7f-9919-8a26d3855ae2)

## How It Works

1. Enter a URL you want to scan
2. Configure your filtering preferences
3. The BLC will crawl the page and extract all links
4. Each link is tested and categorized as OK, BROKEN, or SKIP
5. View comprehensive results in the web interface

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the [MIT License](LICENSE.md).
