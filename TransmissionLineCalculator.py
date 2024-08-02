from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QLineEdit, QPushButton, QMessageBox
from PySide6.QtCore import Qt
import math

epsilon_0 = 8.854187817620389e-12

# Define tower types and their specifications
tower_types = {
    "Type-1": {
        "max_height": 39,
        "min_height": 23,
        "max_horizontal_distance": 4,
        "min_horizontal_distance": 2.2,
        "voltage_level": 66,
        "max_conductors_bundle": 3
    },
    "Type-2": {
        "max_height": 43,
        "min_height": 38.25,
        "max_horizontal_distance": 11.5,
        "min_horizontal_distance": 9.4,
        "max_horizontal_distance_center_phase": 8.9,
        "voltage_level": 400,
        "max_conductors_bundle": 4
    },
    "Type-3": {
        "max_height": 48.8,
        "min_height": 36,
        "max_horizontal_distance": 5.35,
        "min_horizontal_distance": 1.8,
        "voltage_level": 154,
        "max_conductors_bundle": 3
    }
}

# Define conductor types and their specifications
conductor_types = {
    "Hawk": {"diameter": 21.793, "gmr": 8.809, "ac_resistance": 0.132, "current_capacity": 659},
    "Drake": {"diameter": 28.143, "gmr": 11.369, "ac_resistance": 0.080, "current_capacity": 907},
    "Cardinal": {"diameter": 30.378, "gmr": 12.253, "ac_resistance": 0.067, "current_capacity": 996},
    "Rail": {"diameter": 29.591, "gmr": 11.765, "ac_resistance": 0.068, "current_capacity": 993},
    "Pheasant": {"diameter": 35.103, "gmr": 14.204, "ac_resistance": 0.051, "current_capacity": 1187}
}

def calculate_distance(coord1, coord2):
    x1, y1 = coord1
    x2, y2 = coord2
    distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    return distance

def calculate_gmr_bundle(num_conductors, gmr_conductor, distance):
    if num_conductors == 1:
        return gmr_conductor / 1000
    elif num_conductors == 2:
        return ((gmr_conductor / 1000) * distance) ** 0.5  # divided by 1000 due to mm to m conversion because distance is in meters
    elif num_conductors == 3:
        return ((gmr_conductor / 1000) * distance * distance) ** (1 / 3)
    elif num_conductors == 4:
        return ((gmr_conductor / 1000) * distance * distance * distance * (2 ** 0.5)) ** (1 / 4)
    else:
        return None

def calculate_req_bundle(number_conductor, d, distance):
    if number_conductor == 1:
        return d / 2000
    elif number_conductor == 2:
        return ((d / 2000) * distance) ** 0.5  # d(diameter) is divided by 2000 because distance is in meters
    elif number_conductor == 3:
        return ((d / 2000) * distance * distance) ** (1 / 3)
    elif number_conductor == 4:
        return ((d / 2000) * distance * distance * distance * (2 ** 0.5)) ** (1 / 4)
    else:
        return None

class TransmissionLineCalculatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transmission Line Calculator")
        self.setGeometry(100, 100, 700, 550)
        self.setup_ui()

    def setup_ui(self):
        # Instruction label for input format
        self.instruction_label = QLabel("NOTE: Coordinates should be given as x,y without parenthesis. If single-circuit is used, enter prime coordinates as trivial 0,0.", self)
        self.instruction_label.setGeometry(20, 10, 800, 20)

        # Tower type selection
        self.tower_label = QLabel("Select Tower Type:", self)
        self.tower_label.setGeometry(20, 40, 130, 30)
        self.tower_combobox = QComboBox(self)
        self.tower_combobox.addItems(list(tower_types.keys()))
        self.tower_combobox.setGeometry(150, 40, 200, 30)

        # Number of circuits input
        self.circuit_label = QLabel("Number of Circuits:", self)
        self.circuit_label.setGeometry(20, 90, 130, 30)
        self.circuit_entry = QLineEdit(self)
        self.circuit_entry.setGeometry(150, 90, 200, 30)

        # Phase A coordinates input
        self.phase_a_label = QLabel("Phase A Coordinates X,Y:", self)
        self.phase_a_label.setGeometry(20, 140, 180, 30)
        self.phase_a_entry = QLineEdit(self)
        self.phase_a_entry.setGeometry(220, 140, 130, 30)
        
        self.phase_aprime_label = QLabel("Phase A' Coordinates X,Y:\n(Enter 0,0 if single-circuit)", self)
        self.phase_aprime_label.setGeometry(380, 140, 180, 30)
        self.phase_aprime_entry = QLineEdit(self)
        self.phase_aprime_entry.setGeometry(560, 140, 130, 30)

        # Phase B coordinates input
        self.phase_b_label = QLabel("Phase B Coordinates X,Y:", self)
        self.phase_b_label.setGeometry(20, 190, 180, 30)
        self.phase_b_entry = QLineEdit(self)
        self.phase_b_entry.setGeometry(220, 190, 130, 30)

        self.phase_bprime_label = QLabel("Phase B' Coordinates X,Y:\n(Enter 0,0 if single-circuit)", self)
        self.phase_bprime_label.setGeometry(380, 190, 180, 30)
        self.phase_bprime_entry = QLineEdit(self)
        self.phase_bprime_entry.setGeometry(560, 190, 130, 30)
        
        # Phase C coordinates input
        self.phase_c_label = QLabel("Phase C Coordinates X,Y:", self)
        self.phase_c_label.setGeometry(20, 240, 180, 30)
        self.phase_c_entry = QLineEdit(self)
        self.phase_c_entry.setGeometry(220, 240, 130, 30)

        self.phase_cprime_label = QLabel("Phase C' Coordinates X,Y:\n(Enter 0,0 if single-circuit)", self)
        self.phase_cprime_label.setGeometry(380, 240, 180, 30)
        self.phase_cprime_entry = QLineEdit(self)
        self.phase_cprime_entry.setGeometry(560, 240, 130, 30)

        # Number of conductors in the bundle input
        self.conductors_label = QLabel("Number of Conductors in the Bundle:", self)
        self.conductors_label.setGeometry(20, 290, 200, 30)
        self.conductors_entry = QLineEdit(self)
        self.conductors_entry.setGeometry(250, 290, 100, 30)

        # Distance between conductors input
        self.distance_label = QLabel("Distance Between Conductors (in meters):", self)
        self.distance_label.setGeometry(20, 340, 250, 30)
        self.distance_entry = QLineEdit(self)
        self.distance_entry.setGeometry(270, 340, 80, 30)

        # Conductor type selection
        self.conductor_label = QLabel("Select Conductor Type:", self)
        self.conductor_label.setGeometry(20, 390, 150, 30)
        self.conductor_combobox = QComboBox(self)
        self.conductor_combobox.addItems(list(conductor_types.keys()))
        self.conductor_combobox.setGeometry(180, 390, 170, 30)

        # Length of transmission line input
        self.length_label = QLabel("Length of Transmission Line (in km):", self)
        self.length_label.setGeometry(20, 440, 220, 30)
        self.length_entry = QLineEdit(self)
        self.length_entry.setGeometry(250, 440, 100, 30)

        # Calculate button
        self.calculate_button = QPushButton("Calculate", self)
        self.calculate_button.setGeometry(150, 490, 400, 50)
        self.calculate_button.clicked.connect(self.calculate_parameters)

    def calculate_parameters(self):

        # Get the coordinates of phase A and phase B and phase C
        phase_a_coord = tuple(map(float, self.phase_a_entry.text().split(',')))
        phase_b_coord = tuple(map(float, self.phase_b_entry.text().split(',')))
        phase_c_coord = tuple(map(float, self.phase_c_entry.text().split(',')))
        phase_a_coord_reg = phase_a_coord
        phase_b_coord_reg = phase_b_coord
        phase_c_coord_reg = phase_c_coord
        phase_aprime_coord = tuple(map(float, self.phase_aprime_entry.text().split(',')))
        phase_bprime_coord = tuple(map(float, self.phase_bprime_entry.text().split(',')))
        phase_cprime_coord = tuple(map(float, self.phase_cprime_entry.text().split(',')))


        # Calculate the distance between phase A and phase B
        distance_phase_a_b = calculate_distance(phase_a_coord, phase_b_coord)

        # Calculate the distance between phase A and phase C
        distance_phase_a_c = calculate_distance(phase_a_coord, phase_c_coord)

        # Calculate the distance between phase B and phase C
        distance_phase_b_c = calculate_distance(phase_b_coord, phase_c_coord)

        distance_a_aprime = calculate_distance(phase_a_coord, phase_aprime_coord)
        distance_b_bprime = calculate_distance(phase_b_coord, phase_bprime_coord)
        distance_c_cprime = calculate_distance(phase_c_coord, phase_cprime_coord)



        tower_type = self.tower_combobox.currentText()
        circuit_number = int(self.circuit_entry.text())
        phase_a_coord = self.phase_a_entry.text()
        phase_b_coord = self.phase_b_entry.text()
        phase_c_coord = self.phase_c_entry.text()
        conductors_bundle = int(self.conductors_entry.text())
        distance = float(self.distance_entry.text())
        conductor_type = self.conductor_combobox.currentText()
        length = float(self.length_entry.text())

        # Retrieve tower and conductor specifications
        tower_spec = tower_types[tower_type]
        conductor_spec = conductor_types.get(conductor_type)

        # Error Messages
        error_messages = []  # If there are several errors detected in the input values simultaneously, we can accumulate the error messages and display them all at once rather than aborting the calculation process after encountering the first error
        phase_coords = [phase_a_coord, phase_b_coord, phase_c_coord]
        phase_side_check_tw2 = [phase_a_coord, phase_c_coord]
        if not (conductors_bundle <= tower_spec["max_conductors_bundle"]):
            error_messages.append("Invalid numbers of bundle in conductor.")
        if not circuit_number == 1 and tower_type in ["Type-1", "Type-2"]:
            error_messages.append("Invalid number of circuits for selected tower type.")
        if tower_type == "Type-3" and circuit_number not in [1, 2]:
            error_messages.append("Invalid number of circuits. The number of circuits for Type-3 tower must be 1 or 2.")
        if tower_type == "Type-2" and (
                phase_a_coord.split(",")[1] != phase_b_coord.split(",")[1] or phase_a_coord.split(",")[1] !=
                phase_c_coord.split(",")[1] or phase_b_coord.split(",")[1] != phase_c_coord.split(",")[1]):
            error_messages.append("The height of the bundles should be same")

        # Calculate max and min y-values of phase coordinates
        max_y = max(float(coord.split(',')[1]) for coord in phase_coords)
        min_y = min(float(coord.split(',')[1]) for coord in phase_coords)
        max_x = max(abs(float(coord.split(',')[0])) for coord in phase_coords)
        min_x = min(abs(float(coord.split(',')[0])) for coord in phase_coords)
        # Check if max or min y-values exceed the tower height limits
        if max_y > tower_spec["max_height"]:
            error_messages.append("Maximum height of phase lines exceeded.")
        if min_y < tower_spec["min_height"]:
            error_messages.append("Minimum height of phase lines not met.")

        if tower_type in ["Type-1", "Type-3"]:
            if abs(max_x) > tower_spec["max_horizontal_distance"]:
                error_messages.append("Maximum horizontal distance of phase lines exceeded.")
        if tower_type in ["Type-1", "Type-3"]:
            if abs(min_x) < tower_spec["min_horizontal_distance"]:
                error_messages.append("Minimum horizontal distance of phase lines not met.")
        if tower_type == "Type-2":
            if not (abs(float(phase_b_coord_reg[0])) <= tower_spec["max_horizontal_distance_center_phase"]):
                error_messages.append(f"The absolute x-coordinate of phase B  is out of the "
                                      f"allowed horizontal distance range")

        if tower_type == "Type-2":
            if not (max(abs(float(coord.split(',')[0])) for coord in phase_side_check_tw2) <= tower_spec["max_horizontal_distance"] ):
                error_messages.append("Maximum horizontal distance of phase lines exceeded.")
        if tower_type == "Type-2":
            if not (min(abs(float(coord.split(',')[0])) for coord in phase_side_check_tw2) >= tower_spec["min_horizontal_distance"]):
                error_messages.append("Minimum horizontal distance of phase lines are not met.")

        # Display error messages if any
        if error_messages:
            QMessageBox.warning(self, "Input Errors", "\n".join(error_messages))
            return

        # Perform calculations
        if circuit_number == 1:
            GMD_phases = (distance_phase_a_b * distance_phase_a_c * distance_phase_b_c) ** (1 / 3)
            GMR_bundle = calculate_gmr_bundle(conductors_bundle, conductor_spec['gmr'], distance)
            R_eq = calculate_req_bundle(conductors_bundle, conductor_spec['diameter'], distance)
        elif circuit_number == 2:
            GMR_onephase = calculate_gmr_bundle(conductors_bundle, conductor_spec['gmr'], distance)
            GMR_bundle = (math.sqrt((distance_a_aprime * GMR_onephase) * (distance_b_bprime * GMR_onephase) * (distance_c_cprime * GMR_onephase))) ** (1 / 3)
            GMD_AB = ((calculate_distance(phase_a_coord_reg, phase_b_coord_reg) * calculate_distance(phase_a_coord_reg,phase_bprime_coord) * calculate_distance(phase_aprime_coord, phase_b_coord_reg) * calculate_distance(phase_aprime_coord, phase_bprime_coord))) ** (1 / 4)
            GMD_BC = ((calculate_distance(phase_b_coord_reg, phase_c_coord_reg) * calculate_distance(phase_b_coord_reg,phase_cprime_coord) * calculate_distance(phase_bprime_coord, phase_c_coord_reg) * calculate_distance(phase_bprime_coord, phase_cprime_coord))) ** (1 / 4)
            GMD_CA = ((calculate_distance(phase_c_coord_reg, phase_a_coord_reg) * calculate_distance(phase_c_coord_reg,phase_aprime_coord) * calculate_distance(phase_cprime_coord, phase_a_coord_reg) * calculate_distance(phase_cprime_coord, phase_aprime_coord))) ** (1 / 4)
            GMD_phases = (GMD_AB * GMD_BC * GMD_CA) ** (1 / 3)
            R_onephase = calculate_req_bundle(conductors_bundle, conductor_spec['diameter'], distance)
            R_eq = (math.sqrt((distance_a_aprime * R_onephase) * (distance_b_bprime * R_onephase) * (distance_c_cprime * R_onephase))) ** (1 / 3)

        # Calculation logic goes here
        line_resistance = conductor_spec['ac_resistance'] * length / conductors_bundle / circuit_number
        line_inductance = (2 * 10 ** (-7)) * math.log(GMD_phases / GMR_bundle)*length*1000*1000  #1000 due to km to m conversion and 10^6 is due to mH representation
        line_capacitance = (2 * math.pi * epsilon_0) / (math.log(GMD_phases / R_eq))*length*1000*1000000  ##1000 due to km to m conversion and 10^6 is due to uF representation
        line_capacity = math.sqrt(3) * tower_spec['voltage_level'] * conductor_spec['current_capacity'] * conductors_bundle * circuit_number * 1000 / 1000000  # 1000 due to kV and 10^6 is due to represent in MVA
        # Display results
        QMessageBox.information(self, "Results",
                                f"Line Resistance R: {line_resistance} ohm\nLine Inductance L: {line_inductance}mH\nLine Charging Capacitance C: {line_capacitance}uF\nLine Capacity: {line_capacity}MVA")


if __name__ == "__main__":
    app = QApplication([])
    window = TransmissionLineCalculatorApp()
    window.show()
    app.exec()
