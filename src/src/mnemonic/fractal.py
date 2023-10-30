import time
import os
import hashlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

 # Directory to monitor
directory = "./"

class Fractal(object):
    def __init__(self, iterations) -> None:
        self.directory = directory
        self.iterations
    
    # Function to format the zoom coordinate
    def format_zoom_coordinate(self, zoom_coordinate, zoom):
        """
        Formats the zoom coordinate based on zoom direction.

        Args:
            zoom_coordinate (str): The current zoom coordinate.
            zoom (str): The zoom direction, either "in" or "out".

        Returns:
            tuple: A tuple of two formatted zoom coordinates for the real and imaginary axis.
        """
        zoom_coordinate = zoom_coordinate.split('E')
        exponent = "00"
        if zoom == "in":
            exponent = "-05"
        if zoom == "out":
            exponent = "+03"
        return f"1E{exponent}", f"1E{exponent}"

    # Function to generate fractal coordinates
    def generate_fractal(self, *coordinates):
        """
        Generates new fractal coordinates based on the current center and axis values.

        Args:
            coordinates (tuple): Tuple of four coordinates: center_x, center_y, real_axis, and imaginary_axis.

        Returns:
            tuple: A tuple of two formatted coordinates for the real and imaginary axis.
        """
        center_x, center_y, real_axis, imaginary_axis = coordinates
        
        center_x = center_x.split('E')
        integer_x = center_x[0].split('.')[0].replace('-','')
        decimal_x = center_x[0].split('.')[1][:5]
        real_axis = real_axis.split('E')
        if not '.' in real_axis[0]:
            real_axis_integer = real_axis[0]
            real_axis_decimal = '00000'
        else:
            real_axis_parts = real_axis[0].split('.')
            real_axis_integer = real_axis_parts[0]
            real_axis_decimal = real_axis_parts[1] if len(real_axis_parts) > 1 else '00000'
        real_axis_integer = real_axis[0].split('.')[0]
        real_axis_exponent = real_axis[1]
        new_real_axis = f"{real_axis_integer}.{integer_x}{decimal_x}{real_axis_decimal}E{real_axis_exponent}"
        
        center_y = center_y.split('E')
        integer_y = center_y[0].split('.')[0].replace('-','') 
        decimal_y = center_y[0].split('.')[1][:5]
        imaginary_axis = imaginary_axis.split('E')
        if not '.' in imaginary_axis[0]:
            imaginary_axis_integer = imaginary_axis[0]
            imaginary_axis_decimal = '00000'
        else:
            imaginary_axis_parts = imaginary_axis[0].split('.')
            imaginary_axis_integer = imaginary_axis_parts[0]
            imaginary_axis_decimal = imaginary_axis_parts[1] if len(imaginary_axis_parts) > 1 else '00000'
        imaginary_axis_exponent = imaginary_axis[1]
        new_imaginary_axis = f"{imaginary_axis_integer}.{integer_y}{decimal_y}{imaginary_axis_decimal}E{imaginary_axis_exponent}"
        return new_real_axis, new_imaginary_axis
        
    # Function to format coordinates
    def format_center_coordinates(self, *coordinates, truncation=5):
        """
        Formats the center coordinates based on truncation and exponent.

        Args:
            coordinates (tuple): Tuple of x and y center coordinates.
            truncation (int): Number of decimal places to truncate.

        Returns:
            tuple: A tuple of two formatted center coordinates for x and y.
        """
        x, y = coordinates
        x_parts = x.split('E')
        if len(x_parts) > 1:
            x_number, x_exponent = x_parts[0], x_parts[1]
            if '.' not in x_number:
                x_decimal = x_number
            else:
                x_number = x_number.split('.')
                x_decimal = x_number[1]
            x_integer = x_number[0]
            x_decimal = x_decimal[:truncation] + '0' * (len(x_decimal) - truncation)
            x_integer = x_number[0]
            x = f"{x_integer}.{x_decimal}E{x_exponent}"

        y_parts = y.split('E')
        if len(y_parts) > 1:
            y_number, y_exponent = y_parts[0], y_parts[1]
            if '.' not in y_number:
                y_decimal = y_number
            else:
                y_number = y_number.split('.')
                y_decimal = y_number[1]
            y_integer = y_number[0]
            y_decimal = y_decimal[:truncation] + '0' * (len(y_decimal) - truncation)
            y = f"{y_integer}.{y_decimal}E{y_exponent}"

        return x, y

    def prepare_next_fractal(self, file):
        """
        Prepares the next fractal configuration by updating the zoom direction.

        Args:
            file (str): The name of the .config file to update.
        """
        config_file_path = os.path.join(directory, file)
        if os.path.exists(config_file_path):
            with open(config_file_path, "r") as config_file:
                lines = config_file.readlines()
            center_zoom_line = lines[3].split()
            center_x = center_zoom_line[0]
            center_y = center_zoom_line[1]
            zoom = center_zoom_line[2]
            center_zoom_line[2], center_zoom_line[3] = self.format_zoom_coordinate(zoom, "in")
            center_zoom_line[0], center_zoom_line[1] = self.format_center_coordinates(center_x, center_y)
            center_zoom_line = ' '.join(center_zoom_line) + "\n"
            lines[3] = center_zoom_line
            with open(config_file_path, "w") as config_file:
                config_file.writelines(lines)

    def perform_generation_fractal(self, file):
        """
        Generates the next fractal based on the current configuration.

        Args:
            file (str): The name of the .config file to update.
        """
        config_file_path = os.path.join(directory, file)
        if os.path.exists(config_file_path):
            with open(config_file_path, "r") as config_file:
                lines = config_file.readlines()
            fractal_coordinates = lines[2].split()
            center_zoom_line = lines[3].split()
            real_axis = fractal_coordinates[0]
            imaginary_axis = fractal_coordinates[1]
            center_x = center_zoom_line[0]
            center_y = center_zoom_line[1]
            zoom = center_zoom_line[2]
            fractal_coordinates[0], fractal_coordinates[1] = self.generate_fractal(center_x, center_y, real_axis, imaginary_axis)
            center_zoom_line[2], center_zoom_line[3] = self.format_zoom_coordinate(zoom, "out")
            center_zoom_line[0], center_zoom_line[1] = self.format_center_coordinates(center_x, center_y)
            center_zoom_line = ' '.join(center_zoom_line) + "\n"
            fractal_coordinates = " ".join(fractal_coordinates) + "\n"
            lines[3] = center_zoom_line
            lines[2] = fractal_coordinates
            with open(config_file_path, "w") as config_file:
                config_file.writelines(lines)
            
def calculate_hash(file_path):
    """
    Calculates the sha256 hash of a file.

    Args:
        file_path (str): The path to the file to calculate the hash for.

    Returns:
        str: The sha256 hash of the file.
    """
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()


class MyHandler(FileSystemEventHandler):
    def __init__(self, fractal):
        self.config_file_to_monitor = None
        self.config_file_hash = None
        self.fractal = fractal
        
    def on_modified(self, event):
        """
        Handles the file modification event.
        
        Args:
            event (FileSystemEvent): The event triggered by the file system observer.
        """
        if event.src_path == self.config_file_to_monitor:
            try:
                current_hash = calculate_hash(self.config_file_to_monitor)
                if current_hash != self.config_file_hash:
                    self.fractal.prepare_next_fractal(self.config_file_to_monitor)
                    self.fractal.perform_generation_fractal(self.config_file_to_monitor)
                    self.config_file_hash = calculate_hash(self.config_file_to_monitor)
                    print("Modified")
            except Exception as e:
                print(f"Error in file modification: {e}")

def startFractal():
    observer = Observer()
    fractal = Fractal()
    event_handler = MyHandler(fractal)
    observer.schedule(event_handler, path=directory, recursive=False)
    observer.start()
    
    try:
        config_file_name = input("Enter the name of the .config file (e.g., 'fractal.config'): ").strip()
        existing_file_path = os.path.join(directory, config_file_name)
        while not (config_file_name.endswith(".config") and os.path.exists(existing_file_path)):
            print("Invalid or non-existent .config file")
            config_file_name = input("Enter the name of the .config file (e.g., 'fractal.config'): ").strip()
            existing_file_path = os.path.join(directory, config_file_name)

        event_handler.config_file_to_monitor = existing_file_path
        fractal.prepare_next_fractal(event_handler.config_file_to_monitor)
        fractal.perform_generation_fractal(event_handler.config_file_to_monitor)
        event_handler.config_file_hash = calculate_hash(event_handler.config_file_to_monitor)
        print("Monitoring file:", event_handler.config_file_to_monitor)

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        observer.stop()
        observer.join()
        quit()

if __name__ == "__main__":
    startFractal()