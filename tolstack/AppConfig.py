class AppConfig:
    app_version = "0.6.0"
    file_format_version = "1.0"


if __name__ == "__main__":
    print(f"Application Version: {AppConfig.app_version}")
    print(f"File Format Version: {AppConfig.file_format_version}")
