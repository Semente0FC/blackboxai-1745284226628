import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, 
                           QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
                           QLineEdit, QDateEdit, QSpinBox, QTextEdit, 
                           QPushButton, QTableWidget, QTableWidgetItem, 
                           QMessageBox, QHeaderView)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from game_stats_manager import GameStatsManager

class GamingStatsTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stats_manager = GameStatsManager()
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('Gaming Stats Tracker')
        self.setMinimumSize(800, 600)

        # Load stylesheet
        try:
            with open('styles.qss', 'r') as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Error loading stylesheet: {e}")

        # Create main tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create tabs
        self.init_dashboard_tab()
        self.init_add_stat_tab()
        self.init_history_tab()
        self.init_settings_tab()

    def init_dashboard_tab(self):
        """Initialize the dashboard tab with charts."""
        dashboard_widget = QWidget()
        layout = QVBoxLayout()

        # Create matplotlib figure
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Add refresh button
        refresh_btn = QPushButton('Refresh Dashboard')
        refresh_btn.clicked.connect(self.update_dashboard)
        layout.addWidget(refresh_btn)

        dashboard_widget.setLayout(layout)
        self.tabs.addTab(dashboard_widget, 'Dashboard')
        
        # Initial dashboard update
        self.update_dashboard()

    def update_dashboard(self):
        """Update the dashboard charts with latest data."""
        try:
            stats = self.stats_manager.get_stats_for_chart()
            
            # Clear previous plot
            self.ax.clear()
            
            if stats['dates'] and stats['scores']:
                # Plot scores over time
                self.ax.plot(range(len(stats['dates'])), stats['scores'], marker='o')
                self.ax.set_xticks(range(len(stats['dates'])))
                self.ax.set_xticklabels(stats['dates'], rotation=45)
                self.ax.set_ylabel('Score')
                self.ax.set_title('Gaming Performance Over Time')
                self.ax.grid(True)
                
                # Adjust layout to prevent label cutoff
                self.figure.tight_layout()
            else:
                self.ax.text(0.5, 0.5, 'No data available', 
                           horizontalalignment='center',
                           verticalalignment='center')
            
            self.canvas.draw()
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to update dashboard: {str(e)}')

    def init_add_stat_tab(self):
        """Initialize the add stat tab."""
        add_stat_widget = QWidget()
        layout = QFormLayout()

        # Create form fields
        self.game_name_input = QLineEdit()
        self.date_played_input = QDateEdit()
        self.date_played_input.setDate(QDate.currentDate())
        self.score_input = QSpinBox()
        self.score_input.setRange(0, 999999)
        self.comments_input = QTextEdit()

        # Add fields to layout
        layout.addRow('Game Name:', self.game_name_input)
        layout.addRow('Date Played:', self.date_played_input)
        layout.addRow('Score:', self.score_input)
        layout.addRow('Comments:', self.comments_input)

        # Add save button
        save_btn = QPushButton('Save Stats')
        save_btn.clicked.connect(self.save_stat)
        layout.addRow(save_btn)

        add_stat_widget.setLayout(layout)
        self.tabs.addTab(add_stat_widget, 'Add Stat')

    def save_stat(self):
        """Save the stat entry to database."""
        game_name = self.game_name_input.text().strip()
        date_played = self.date_played_input.date().toString(Qt.ISODate)
        score = self.score_input.value()
        comments = self.comments_input.toPlainText().strip()

        if not game_name:
            QMessageBox.warning(self, 'Error', 'Please enter a game name.')
            return

        try:
            self.stats_manager.add_stat(game_name, date_played, score, comments)
            QMessageBox.information(self, 'Success', 'Stat saved successfully!')
            
            # Clear form
            self.game_name_input.clear()
            self.date_played_input.setDate(QDate.currentDate())
            self.score_input.setValue(0)
            self.comments_input.clear()
            
            # Refresh history tab
            self.update_history_table()
            # Refresh dashboard
            self.update_dashboard()
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to save stat: {str(e)}')

    def init_history_tab(self):
        """Initialize the history tab."""
        history_widget = QWidget()
        layout = QVBoxLayout()

        # Create table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(['ID', 'Game', 'Date', 'Score', 'Comments'])
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        layout.addWidget(self.history_table)

        # Add buttons
        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton('Refresh')
        delete_btn = QPushButton('Delete Selected')
        delete_btn.setObjectName('deleteButton')
        
        refresh_btn.clicked.connect(self.update_history_table)
        delete_btn.clicked.connect(self.delete_selected_stat)
        
        btn_layout.addWidget(refresh_btn)
        btn_layout.addWidget(delete_btn)
        layout.addLayout(btn_layout)

        history_widget.setLayout(layout)
        self.tabs.addTab(history_widget, 'History')
        
        # Initial table population
        self.update_history_table()

    def update_history_table(self):
        """Update the history table with latest data."""
        try:
            stats = self.stats_manager.get_stats()
            self.history_table.setRowCount(len(stats))
            
            for row, stat in enumerate(stats):
                for col, value in enumerate(stat):
                    item = QTableWidgetItem(str(value))
                    if col == 0:  # Make ID column read-only
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.history_table.setItem(row, col, item)
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to update history: {str(e)}')

    def delete_selected_stat(self):
        """Delete the selected stat from the database."""
        selected_items = self.history_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, 'Error', 'Please select a stat to delete.')
            return

        row = selected_items[0].row()
        stat_id = int(self.history_table.item(row, 0).text())

        reply = QMessageBox.question(self, 'Confirm Delete',
                                   'Are you sure you want to delete this stat?',
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                self.stats_manager.delete_stat(stat_id)
                self.update_history_table()
                self.update_dashboard()
                QMessageBox.information(self, 'Success', 'Stat deleted successfully!')
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Failed to delete stat: {str(e)}')

    def init_settings_tab(self):
        """Initialize the settings tab."""
        settings_widget = QWidget()
        layout = QVBoxLayout()

        # Add reset database button
        reset_btn = QPushButton('Reset Database')
        reset_btn.setObjectName('deleteButton')
        reset_btn.clicked.connect(self.reset_database)
        layout.addWidget(reset_btn)

        settings_widget.setLayout(layout)
        self.tabs.addTab(settings_widget, 'Settings')

    def reset_database(self):
        """Reset the database after confirmation."""
        reply = QMessageBox.question(self, 'Confirm Reset',
                                   'Are you sure you want to reset the database? '
                                   'This will delete all stats!',
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                # Re-initialize database (drops and recreates tables)
                self.stats_manager.initialize_database()
                self.update_history_table()
                self.update_dashboard()
                QMessageBox.information(self, 'Success', 'Database reset successfully!')
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Failed to reset database: {str(e)}')

def main():
    app = QApplication(sys.argv)
    window = GamingStatsTracker()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
