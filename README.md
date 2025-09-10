

# DoxbeanV2

![Image Alt](https://github.com/vantixt777/doxbean/blob/82b0a26fe25ed30b3d55949627ed6aa135e21e4d/doxbean%20tool.png)


`DoxbeanV2.py` is a **Python application** with a graphical user interface built using **PyQt5**.
It combines network-related features with a modern GUI design.

## Features

* **PyQt5 interface** with a dark theme and customizable input fields
* **Main window** with log output, progress bar, and control buttons
* **Proxy support**: fetch and validate proxy lists from multiple APIs
* **Multithreading**:

  * `QThread` for background tasks
  * `concurrent.futures` for parallel execution
* **Integrated ping tool** (accessible via the menu bar)
* **Configurable modes** (different timeout and delay presets)

## Requirements

* Python 3.9+
* Dependencies:

  ```bash
  pip install -r requirements.txt
  ```

  (PyQt5, requests)

## Run

```bash
python DoxbeanV2.py
```


