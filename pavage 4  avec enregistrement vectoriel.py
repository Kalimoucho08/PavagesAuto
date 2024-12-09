import sys
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import Voronoi
from shapely.geometry import Polygon, LineString
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QMessageBox, QScrollArea
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class PavageApp(QWidget):

    def __init__(self):
        super().__init__()
        self.width = None
        self.height = None
        self.n_polygons = None
        self.vor = None
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        # Inputs
        input_layout = QHBoxLayout()
        self.width_input = QLineEdit()
        self.height_input = QLineEdit()
        self.polygons_input = QLineEdit()

        input_layout.addWidget(QLabel("Largeur (mm):"))
        input_layout.addWidget(self.width_input)
        input_layout.addWidget(QLabel("Hauteur (mm):"))
        input_layout.addWidget(self.height_input)
        input_layout.addWidget(QLabel("Nombre de polygones:"))
        input_layout.addWidget(self.polygons_input)

        main_layout.addLayout(input_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.generate_button = QPushButton("Générer le pavage")
        self.generate_button.clicked.connect(self.generate_pavage)

        self.regenerate_button = QPushButton("Régénérer")
        self.regenerate_button.clicked.connect(self.regenerate_pavage)

        self.save_button = QPushButton("Sauvegarder")
        self.save_button.clicked.connect(self.save_pavage)

        self.change_params_button = QPushButton("Changer les paramètres")
        self.change_params_button.clicked.connect(self.change_parameters)

        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.regenerate_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.change_params_button)

        main_layout.addLayout(button_layout)

        # Preview with ScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.figure, self.ax = plt.subplots(figsize=(6, 6))
        self.canvas = FigureCanvas(self.figure)

        self.scroll_area.setWidget(self.canvas)
        main_layout.addWidget(self.scroll_area)

        self.setLayout(main_layout)
        self.setWindowTitle('Générateur de Pavage')
        self.resize(800, 600)  # Set initial window size
        self.show()

    def generate_pavage(self):
        try:
            self.width = float(self.width_input.text())
            self.height = float(self.height_input.text())
            self.n_polygons = int(self.polygons_input.text())

            if self.width <= 0 or self.height <= 0:
                raise ValueError("Les dimensions doivent être positives.")
            if self.n_polygons < 5:
                raise ValueError("Le nombre de polygones doit être au moins 5.")

            self.vor = self.create_pavage(self.width, self.height, self.n_polygons)
            self.plot_pavage()

            self.regenerate_button.setEnabled(True)
            self.save_button.setEnabled(True)

        except ValueError as e:
            QMessageBox.warning(self, "Erreur", str(e))

    def regenerate_pavage(self):
        if self.width and self.height and self.n_polygons:
            self.vor = self.create_pavage(self.width, self.height, self.n_polygons)
            self.plot_pavage()

    def save_pavage(self):
        if self.vor:
            options = "Images JPG (*.jpg);;Images EPS (*.eps);;Images SVG (*.svg)"
            filename, _ = QFileDialog.getSaveFileName(self, "Sauvegarder le pavage", "", options)
            if filename:
                # Déterminer le format à partir de l'extension du fichier
                if filename.endswith('.jpg'):
                    self.figure.savefig(filename, format='jpg', dpi=300, bbox_inches='tight', pad_inches=0)
                elif filename.endswith('.eps'):
                    self.figure.savefig(filename, format='eps', bbox_inches='tight', pad_inches=0)
                elif filename.endswith('.svg'):
                    self.figure.savefig(filename, format='svg', bbox_inches='tight', pad_inches=0)
                else:
                    QMessageBox.warning(self, "Erreur", "Format de fichier non pris en charge.")
                    return

                QMessageBox.information(self, "Succès", f"Le pavage a été sauvegardé dans : {filename}")

    def change_parameters(self):
        self.width_input.clear()
        self.height_input.clear()
        self.polygons_input.clear()

    def create_pavage(self, width, height, n_points):
        x = np.linspace(0, width, int(np.sqrt(n_points)))
        y = np.linspace(0, height, int(np.sqrt(n_points)))

        xx, yy = np.meshgrid(x, y)

        points = np.column_stack([xx.ravel(), yy.ravel()])

        points += np.random.normal(0, min(width, height) / 20, points.shape)

        border_points = np.array([[0, 0], [0, height], [width, 0], [width, height]])

        points = np.vstack([points, border_points])

        return Voronoi(points)

    def plot_pavage(self):
        self.ax.clear()

        page = Polygon([(0, 0), (self.width, 0), (self.width, self.height), (0, self.height)])

        for simplex in self.vor.ridge_vertices:
            if -1 not in simplex:
                p1, p2 = [self.vor.vertices[i] for i in simplex]
                line = LineString([p1, p2])

                if line.intersects(page):
                    intersection = line.intersection(page)
                    if intersection.is_empty:
                        continue

                    x_ints, y_ints = intersection.xy

                    if len(x_ints) > 1:  # Ensure there are intersection points to plot
                        self.ax.plot(x_ints, y_ints, 'k-', linewidth=0.5)

        # Draw the boundary of the page
        boundary_x = [0, self.width, self.width, 0]
        boundary_y = [0, 0, self.height, self.height]

        # Plot the boundary of the page
        self.ax.plot(boundary_x + [boundary_x[0]], boundary_y + [boundary_y[0]], 'k-', linewidth=1.5)

        # Set limits and aspect ratio
        # Maintain equal aspect ratio and hide axes
        # Remove axes for better visualization

        plt.axis('off')
        plt.tight_layout(pad=0)  # Redraw the canvas to update the plot

        # Redraw the canvas to update the plot
        self.canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PavageApp()
    sys.exit(app.exec_())
