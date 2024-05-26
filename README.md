# File Manager

File Manager is a streamlit application designed to manage and analyze files within a directory structure. Built with Python, Docker, Streamlit, and Echarts, this app offers a user-friendly interface to visualize file statistics and interactively filter file content.

## Features

### Home Page
- **Directory Statistics**: Visual representation of the number of files and the total size of files in each directory.
- **Interactive Charts**: Utilize Echarts to display dynamic and interactive charts for better data visualization.

### File Page
- **File Selection**: Users can easily navigate and select files using a tree component.
- **Dynamic Filtering**: Apply filters dynamically to the selected dataset, allowing users to tailor the data view to their needs.
- **Export Filtered Data**: After applying filters, users can export the refined dataset for further use.

## Technology Stack

- **Python**: The core programming language used for the app.
- **Docker**: Containerization to ensure consistent and portable deployments.
- **Streamlit**: Framework used to create the web interface and interactive components.
- **Echarts**: Library for creating interactive charts and data visualizations.

## Installation

To get started with File Manager, follow these steps:

1. **Clone the Repository**:
    ```bash
    git clone repo_name
    cd FileManager
    ```

2. **Build the Docker Image**:
    ```bash
    docker build compose build
    ```

3. **Run the Docker Container**:
    ```bash
    docker compose up 
    ```

4. **Access the Application**:
    Open your browser and navigate to `http://localhost:8501` to start using the File Manager app.

## Usage

### Home Page

- **View Directory Statistics**: Upon accessing the home page, you will see charts displaying the number of files and their sizes within each directory. These statistics help you quickly understand the structure and storage distribution in your file system.

### File Page

- **Select a File**: Use the tree component to browse through the directories and select a file you want to analyze.
- **Apply Filters**: Once a file is selected, apply various filters to the dataset. The filters can be adjusted dynamically to refine the data view as needed.
- **Export Data**: After filtering the dataset, export the filtered data for further analysis or reporting.

