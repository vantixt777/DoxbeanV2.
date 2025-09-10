

# DoxbeanV2

![Image Alt](https://github.com/vantixt777/DoxbeanV2./blob/115b23a8b4825b9b98fef031529fd230cbf3d17e/Doxbean%20Tool.png)

![Image Alt](https://github.com/vantixt777/DoxbeanV2./blob/115b23a8b4825b9b98fef031529fd230cbf3d17e/doxbean%20Ip%20pinger.png)

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


