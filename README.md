# Topsoe Web Scraper

This project contains a web scraper for Topsoe.com that creates a structured content repository of the website's content in markdown format.

## Project Setup

### Prerequisites
- Python 3.x installed on your system
- Terminal/Command Prompt access

### First-Time Setup

1. Open Terminal/Command Prompt
2. Navigate to the project directory:
   ```
   cd path/to/topsoe_scraper
   ```

3. Create a virtual environment:
   ```
   python3 -m venv venv
   ```

4. Activate the virtual environment:
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```
   - On Windows:
     ```
     venv\Scripts\activate
     ```

5. Install required packages:
   ```
   pip install requests beautifulsoup4 markdown
   ```

### Returning to the Project

When coming back to work on the project:

1. Navigate to the project directory:
   ```
   cd path/to/topsoe_scraper
   ```

2. Activate the virtual environment:
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```
   - On Windows:
     ```
     venv\Scripts\activate
     ```

3. You're ready to run the scraper!

### Running the Scraper

With the virtual environment activated: 
```
python topsoe_scraper.py
```