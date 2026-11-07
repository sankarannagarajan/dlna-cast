import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.clock import Clock
import upnpclient
from yt_dlp import YoutubeDL
import sys

class DLNACasterGUI(BoxLayout):
    def __init__(self, **kwargs):
        super(DLNACasterGUI, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15

        # 1. Device Info Header
        self.add_widget(Label(
            text="Target Device: http://192.168.1.2:49565/description.xml", 
            size_hint_y=None, 
            height=40
        ))

        # 2. Status Label (Displays what the backend is doing)
        self.status_label = Label(
            text="Status: Ready. Enter a YouTube URL below.",
            size_hint_y=None,
            height=40,
            bold=True
        )
        self.add_widget(self.status_label)

        # 3. YouTube URL Text Input Field
        self.url_input = TextInput(
            text='',
            hint_text='Paste YouTube video URL here...',
            multiline=False,
            size_hint_y=None,
            height=50
        )
        self.add_widget(self.url_input)

        # 4. Horizontal Control Row for Buttons
        # This layout hosts all 4 control actions side-by-side
        control_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint_y=None,
            height=60
        )

        # Cast Trigger Button
        self.cast_btn = Button(
            text='Cast Video',
            background_color=(0.1, 0.6, 0.8, 1) # Custom blue color
        )
        self.cast_btn.bind(on_press=self.start_casting_process)
        control_layout.add_widget(self.cast_btn)

        # Pause Button
        self.pause_btn = Button(
            text='Pause',
            background_color=(0.8, 0.6, 0.1, 1) # Dark yellow/Orange
        )
        self.pause_btn.bind(on_press=lambda instance: self.trigger_dlna_command('Pause'))
        control_layout.add_widget(self.pause_btn)

        # Resume Button
        self.resume_btn = Button(
            text='Resume',
            background_color=(0.1, 0.8, 0.3, 1) # Green
        )
        self.resume_btn.bind(on_press=lambda instance: self.trigger_dlna_command('Play'))
        control_layout.add_widget(self.resume_btn)

        # Stop Button
        self.stop_btn = Button(
            text='Stop',
            background_color=(0.8, 0.1, 0.2, 1) # Red
        )
        self.stop_btn.bind(on_press=lambda instance: self.trigger_dlna_command('Stop'))
        control_layout.add_widget(self.stop_btn)

        self.add_widget(control_layout)

    def start_casting_process(self, instance):
        youtube_url = self.url_input.text.strip()
        if not youtube_url:
            self.status_label.text = "Status: Error - URL input field is empty!"
            return

        # Disable button and update text so user knows it's working
        self.cast_btn.disabled = True
        self.status_label.text = "Status: Extracting YouTube formats..."

        # Dispatch the core network work onto a separate thread to prevent UI freezing
        threading.Thread(target=self.bg_cast_worker, args=(youtube_url,), daemon=True).start()

    def bg_cast_worker(self, youtube_url):
        try:
            # Connect to your dedicated DLNA device profile
            uri = 'http://192.168.1.2:49565/description.xml'
            d = upnpclient.Device(uri)

            # Create a completely silent logger class to stop internal write bugs
            class SilentLogger:
                def debug(self, msg): pass
                def info(self, msg): pass
                def warning(self, msg): pass
                def error(self, msg): pass

            # Updated parameter configurations to prevent timeouts and bypass blocks
            ydl_opts = {
                'format': '22/18/best[ext=mp4]/best',
                'quiet': True,
                'no_warnings': True,
                'logger': SilentLogger(),
                
                # Network Timeout Optimization
                'socket_timeout': 10,       # Max seconds to wait for a network socket
                'retries': 3,               # Max retry attempts before stopping
                
                # Human Emulation Headers to bypass connection dropping
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                },
                'js_runtimes': {
                    'node': {}
                },
                'extractor_args': {
                    'youtube': {
                        'player_client': ['ios', 'android'],
                    }
                }
            }

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                
            formats = info.get('formats', [])
            play_uri = None

            # Match target progressive profile configurations
            for f in formats:
                if f.get('format_id') in ['94', '18']:
                    play_uri = f['url']
                    break

            # Fallback optimization if specific target itags missing
            if not play_uri:
                play_uri = info.get('url')

            if not play_uri:
                raise Exception("Compatible progressive format not found")

            # Update status message inside safe main Kivy loop
            self.update_status_ui("Transmitting media payload to device...")

            # Execute standard UPnP media transport injection commands
            d.AVTransport.SetAVTransportURI(InstanceID=0, CurrentURI=play_uri, CurrentURIMetaData='')
            d.AVTransport.Play(InstanceID=0, Speed="1")

            self.update_status_ui("Status: Done!!! Playing on device.", reset_btn=True)

        except Exception as e:
            self.update_status_ui(f"Status: Failed - {str(e)}", reset_btn=True)

    def trigger_dlna_command(self, action):
        """Dispatches transport control signals asynchronously."""
        self.status_label.text = f"Status: Sending {action} command..."
        threading.Thread(target=self.bg_command_worker, args=(action,), daemon=True).start()

    def bg_command_worker(self, action):
        try:
            try:
                uri = 'http://192.168.1.18:60099'
                upnpclient.Device(uri)
            except:
                uri = 'http://192.168.1.2:49565/description.xml'
                try:
                    upnpclient.Device(uri)
                except:
                    print('Casting devices not found!!')
                    sys.exit()
#            uri = 'http://192.168.1.2:49565/description.xml'
            d = upnpclient.Device(uri)
            
            if action == 'Play':
                d.AVTransport.Play(InstanceID=0, Speed="1")
                self.update_status_ui("Status: Resumed playback.")
            elif action == 'Pause':
                d.AVTransport.Pause(InstanceID=0)
                self.update_status_ui("Status: Paused.")
            elif action == 'Stop':
                d.AVTransport.Stop(InstanceID=0)
                self.update_status_ui("Status: Stopped.")
        except Exception as e:
            self.update_status_ui(f"Status: Control Failed - {str(e)}")

    def update_status_ui(self, message, reset_btn=False):
        # Clock.schedule_once forces text changes to run safely on the Kivy graphics thread
        Clock.schedule_once(lambda dt: self._apply_ui_changes(message, reset_btn))

    def _apply_ui_changes(self, message, reset_btn):
        self.status_label.text = message
        if reset_btn:
            self.cast_btn.disabled = False

class MainApp(App):
    def build(self):
        self.title = 'DLNA Caster GUI'
        return DLNACasterGUI()

if __name__ == '__main__':
    MainApp().run()
