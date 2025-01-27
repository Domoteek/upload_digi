import os
import re
from bs4 import BeautifulSoup
import configparser
import ftplib
import subprocess
import sys
import tempfile
import shutil
from PyQt5 import QtWidgets, QtWebEngineWidgets, QtCore, QtGui, QtPrintSupport
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtGui import QColor, QPalette, QPageLayout, QPageSize
import base64
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog

# Obtenez le répertoire de l'application
app_dir = os.path.dirname(os.path.abspath(__file__))

GUIDE_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Guide d'utilisation - Upload DIGI Pro</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f4f4;
        }
        .logo {
            display: block;
            margin: 0 auto 20px;
            max-width: 200px;
            height: auto;
        }
        h1, h2 {
            color: #2c3e50;
        }
        h1 {
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            margin-top: 30px;
        }
        code {
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            border-radius: 3px;
            padding: 2px 5px;
            font-family: Consolas, monospace;
        }
        pre {
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            border-radius: 3px;
            padding: 10px;
            overflow-x: auto;
        }
        ul, ol {
            padding-left: 25px;
        }
        .note {
            background-color: #e7f2fa;
            border-left: 5px solid #3498db;
            padding: 10px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <h1>Guide d'utilisation - Upload DIGI Pro</h1>

    <div class="note">
        <strong>Note :</strong> Ce guide d'utilisation se trouve dans le répertoire "asset" de l'application et est accessible via le menu "Aide" de l'application.
    </div>

    <h2>Structure du répertoire "asset"</h2>
    <p>Pour utiliser correctement Upload DIGI Pro, vous devez avoir un répertoire "asset" structuré comme suit :</p>
    <pre>
asset/
├── SM 5000 BS/
│   ├── config.ini
│   ├── AUCHAN/
│   │   ├── slideshow/
│   │   └── movie/
│   ├── CARREFOUR/
│   │   ├── slideshow/
│   │   └── movie/
│   └── ... (autres magasins)
├── SM 5300 B/
├── SM 5300X B/
├── SM 5300X SSP/
└── SM 5500 B/
    </pre>

    <h2>Configuration des modèles et magasins</h2>
    <ol>
        <li>Créez un dossier pour chaque modèle de balance (ex: "SM 5000 BS", "SM 5300 B", etc.).</li>
        <li>Dans chaque dossier de modèle, créez un sous-dossier pour chaque magasin (ex: "AUCHAN", "CARREFOUR", etc.).</li>
        <li>Dans chaque dossier de magasin, créez deux sous-dossiers : "slideshow" et "movie".</li>
    </ol>

    <h2>Création du fichier config.ini</h2>
    <p>Pour chaque modèle, créez un fichier <code>config.ini</code> dans le dossier correspondant avec le contenu suivant :</p>
    <pre>
[Paths]
dest_ini = /opt/pcscale/cntry/22/ini/selfservice/theme/tare/userDefined/typeA/ini/
dest_img = /opt/pcscale/cntry/22/ini/selfservice/theme/tare/userDefined/typeA/images/img/
dest_slideshow = /chemin1/slideshow,/chemin2/slideshow,/chemin3/slideshow
dest_movie = /opt/pcscale/files/infomat/movies
    </pre>
    <p>Ajustez les chemins selon les spécifications de chaque modèle de balance.</p>

    <h2>Ajout de contenu</h2>
    <ul>
        <li>Placez les fichiers de diaporama (.png) dans le dossier "slideshow" de chaque magasin.</li>
        <li>Placez les fichiers images (.jpg) dans le dossier "movie" de chaque magasin.</li>
        <li>Pour les bandeaux, placez les fichiers .ini et .bmp directement dans le dossier du modèle.</li>
    </ul>

    <h2>Utilisation de l'application</h2>
    <ol>
        <li>Lancez Upload DIGI Pro.</li>
        <li>Sélectionnez le modèle de balance dans la liste déroulante.</li>
        <li>Choisissez le magasin concerné.</li>
        <li>Entrez l'adresse IP de la balance, l'identifiant et le mot de passe.</li>
        <li>Cochez les options d'upload souhaitées (Slideshow/Movie et/ou Bandeau).</li>
        <li>Cliquez sur "Upload" pour démarrer le transfert des fichiers.</li>
    </ol>

    <h2>Dépannage</h2>
    <ul>
        <li>Si un modèle ou un magasin n'apparaît pas dans les listes, vérifiez que les dossiers sont correctement nommés et structurés dans le répertoire "asset".</li>
        <li>Assurez-vous que le fichier <code>config.ini</code> est présent et correctement formaté pour chaque modèle.</li>
        <li>Vérifiez les logs de l'application pour plus de détails en cas d'erreur lors de l'upload.</li>
    </ul>

    <div class="note">
        <p>Pour toute assistance supplémentaire, veuillez contacter le support technique.</p>
    </div>
</body>
</html>
"""

# Styles pour les thèmes sombre et clair
DARK_STYLE = """
    QWidget {
        background-color: #2C3E50;
        color: #ECF0F1;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    QLabel { font-size: 14px; }
    QComboBox, QLineEdit {
        background-color: #34495E;
        border: 1px solid #7F8C8D;
        border-radius: 4px;
        padding: 5px;
        min-height: 30px;
    }
    QPushButton {
        background-color: #3498DB;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 10px;
        font-size: 16px;
    }
    QPushButton:hover { background-color: #2980B9; }
    QTextEdit {
        background-color: #34495E;
        border: 1px solid #7F8C8D;
        border-radius: 4px;
    }
    QMenuBar {
        background-color: #34495E;
        color: #ECF0F1;
    }
    QMenuBar::item:selected { background-color: #3498DB; }
    QMenu {
        background-color: #34495E;
        color: #ECF0F1;
    }
    QMenu::item:selected { background-color: #3498DB; }
"""

LIGHT_STYLE = """
    QWidget {
        background-color: #ECF0F1;
        color: #2C3E50;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    QLabel { font-size: 14px; }
    QComboBox, QLineEdit {
        background-color: white;
        border: 1px solid #BDC3C7;
        border-radius: 4px;
        padding: 5px;
        min-height: 30px;
    }
    QPushButton {
        background-color: #3498DB;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 10px;
        font-size: 16px;
    }
    QPushButton:hover { background-color: #2980B9; }
    QTextEdit {
        background-color: white;
        border: 1px solid #BDC3C7;
        border-radius: 4px;
    }
    QMenuBar {
        background-color: #BDC3C7;
        color: #2C3E50;
    }
    QMenuBar::item:selected { background-color: #3498DB; }
    QMenu {
        background-color: #ECF0F1;
        color: #2C3E50;
    }
    QMenu::item:selected {
        background-color: #3498DB;
        color: white;
    }
"""

# Fonction pour obtenir les chemins des fichiers bandeaux selon le modèle
def get_bandeau_paths(modele):
    if modele == "SM 5000 BS":
        dest_ini = "/opt/pcscale/cntry/22/ini/selfservice/"
        dest_img = "/opt/pcscale/img/standard/reg/"
    elif modele == "SM 5300X B":
        dest_ini = "/opt/pcscale/cntry/22/ini/selfservice/theme/tare/userDefined/typeA/ini/"
        dest_img = "/opt/pcscale/cntry/22/ini/selfservice/theme/tare/userDefined/typeA/img/"
    elif modele == "SM 5300 B":
        dest_ini = "/opt/pcscale/cntry/22/ini/selfservice/theme/tare/userDefined/typeA/ini/"
        dest_img = "/opt/pcscale/cntry/22/ini/selfservice/theme/tare/userDefined/typeA/images/img/"
    elif modele == "SM 5300X SSP":
        dest_ini = "/opt/pcscale/cntry/22/ini/setup_1280x1024/selfservice/theme/tare/userDefined/typeA/ini/"
        dest_img = dest_ini
    elif modele == "SM 5500 B":
        dest_ini = "/opt/pcscale/cntry/22/ini/selfservice/theme/tare/userDefined/typeA/ini/"
        dest_img = "/opt/pcscale/cntry/22/ini/selfservice/theme/tare/userDefined/typeA/images/img/"
    else:
        dest_ini = "/opt/pcscale/cntry/22/ini/selfservice/theme/tare/userDefined/typeA/ini/"
        dest_img = "/opt/pcscale/cntry/22/ini/selfservice/theme/tare/userDefined/typeA/images/img/"
    
    return dest_ini, dest_img


def get_asset_path():
    # Obtenir le chemin de l'exécutable
    if getattr(sys, 'frozen', False):
        # Si l'application est compilée (par exemple avec PyInstaller)
        application_path = sys._MEIPASS
    else:
        # Si l'application est exécutée en tant que script Python
        application_path = os.path.dirname(os.path.abspath(__file__))

    # Vérifier si un dossier 'asset' existe à côté de l'exécutable
    external_asset_path = os.path.join(os.path.dirname(sys.executable), 'asset')
    if os.path.isdir(external_asset_path):
        print(f"Utilisation du dossier asset externe : {external_asset_path}")
        return external_asset_path

    # Sinon, utiliser le dossier asset intégré
    internal_asset_path = os.path.join(application_path, 'asset')
    if os.path.isdir(internal_asset_path):
        print(f"Utilisation du dossier asset intégré : {internal_asset_path}")
        return internal_asset_path

    print("Aucun dossier asset trouvé.")
    return None

def read_model_config(model_path):
    config = configparser.ConfigParser()
    config_path = os.path.join(model_path, "config.ini")
    if os.path.exists(config_path):
        config.read(config_path)
        paths = {
            'dest_ini': config.get('Paths', 'dest_ini', fallback='').split(','),
            'dest_img': config.get('Paths', 'dest_img', fallback='').split(','),
            'dest_slideshow': config.get('Paths', 'dest_slideshow', fallback='').split(','),
            'dest_movie': config.get('Paths', 'dest_movie', fallback='')
        }
        return paths
    return None


# Modification de la fonction detect_models_and_magasins
def scan_models_and_configs(asset_path):
    models_info = {}
    for model in os.listdir(asset_path):
        model_path = os.path.join(asset_path, model)
        if os.path.isdir(model_path):
            paths = read_model_config(model_path)
            if paths:
                models_info[model] = {
                    'paths': paths,
                    'magasins': scan_magasins(model_path)
                }
            else:
                print(f"Configuration manquante pour le modèle {model}")
    return models_info

def scan_magasins(model_path):
    magasins = {}
    for magasin in os.listdir(model_path):
        magasin_path = os.path.join(model_path, magasin)
        if os.path.isdir(magasin_path):
            magasins[magasin] = {
                "slideshow": os.path.join(magasin_path, "slideshow"),
                "movie": os.path.join(magasin_path, "movie")
            }
    return magasins

class HtmlGuideViewer(QtWidgets.QWidget):
    def __init__(self, html_content, parent=None):
        super().__init__(parent, Qt.Window)
        self.setWindowTitle("Guide d'utilisation - Upload DIGI Pro")
        self.setGeometry(100, 100, 900, 700)

        layout = QtWidgets.QVBoxLayout(self)

        # Barre d'outils
        toolbar = QtWidgets.QToolBar()
        layout.addWidget(toolbar)

        # Boutons de zoom
        zoom_in_btn = QtWidgets.QAction(QtGui.QIcon.fromTheme("zoom-in"), "Zoom +", self)
        zoom_in_btn.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in_btn)

        zoom_out_btn = QtWidgets.QAction(QtGui.QIcon.fromTheme("zoom-out"), "Zoom -", self)
        zoom_out_btn.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out_btn)

        toolbar.addSeparator()

        # Bouton d'impression
        print_btn = QtWidgets.QAction(QtGui.QIcon.fromTheme("document-print"), "Imprimer", self)
        print_btn.triggered.connect(self.print_guide)
        toolbar.addAction(print_btn)

        # Vue Web
        self.web_view = QtWebEngineWidgets.QWebEngineView()
        layout.addWidget(self.web_view)

        # Charger et intégrer le logo
        logo_data = self.load_logo()
        self.modified_html = self.add_ids_and_logo_to_html(html_content, logo_data)

        # Connecter le signal loadFinished à notre méthode
        self.web_view.loadFinished.connect(self.on_load_finished)

        # Charger le contenu HTML
        self.web_view.setHtml(self.modified_html)

        # Zone de log
        self.log_output = QtWidgets.QTextEdit()
        self.log_output.setReadOnly(True)
        #layout.addWidget(self.log_output)

        # Timer pour vérifier l'état de l'impression
        self.print_check_timer = QTimer(self)
        self.print_check_timer.timeout.connect(self.check_print_status)
        self.print_start_time = None

    def load_logo(self):
        app_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(app_dir, "asset", "logogm.png")
        if os.path.exists(icon_path):
            with open(icon_path, "rb") as f:
                return base64.b64encode(f.read()).decode('utf-8')
        return None

    def add_ids_and_logo_to_html(self, html_content, logo_data):
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Ajouter des IDs aux titres
        for i, heading in enumerate(soup.find_all(['h1', 'h2', 'h3'])):
            heading_id = f"heading_{i}"
            heading['id'] = heading_id

        # Ajouter le logo si disponible
        if logo_data:
            logo_tag = soup.new_tag("img", src=f"data:image/png;base64,{logo_data}")
            logo_tag['style'] = "display: block; margin: 0 auto; max-width: 200px; height: auto;"
            soup.body.insert(0, logo_tag)

        return str(soup)

    def zoom_in(self):
        self.web_view.setZoomFactor(self.web_view.zoomFactor() * 1.2)

    def zoom_out(self):
        self.web_view.setZoomFactor(self.web_view.zoomFactor() / 1.2)

    def on_load_finished(self, ok):
        if ok:
            self.log("Page chargée avec succès.")
        else:
            self.log("Erreur lors du chargement de la page.")

    def print_guide(self):
        self.log("Début de la procédure d'impression...")
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageSize(QPageSize(QPageSize.A4))
        printer.setPageOrientation(QPageLayout.Portrait)

        print_dialog = QPrintDialog(printer, self)
        if print_dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.log("Impression acceptée par l'utilisateur")
            self.print_document(printer)
        else:
            self.log("Impression annulée par l'utilisateur")

    def print_document(self, printer):
        self.log("Début de l'impression...")
        try:
            def callback(success):
                if success:
                    self.log("Impression terminée avec succès.")
                    self.print_check_timer.stop()
                else:
                    self.log("Erreur lors de l'impression. Tentative d'impression alternative...")
                    self.print_alternative(printer)

            self.web_view.page().print(printer, callback)
            self.print_start_time = QtCore.QDateTime.currentDateTime()
            self.print_check_timer.start(1000)  # Vérifier toutes les secondes
        except Exception as e:
            self.log(f"Erreur lors de l'impression : {str(e)}")
            self.print_alternative(printer)

    def check_print_status(self):
        current_time = QtCore.QDateTime.currentDateTime()
        if self.print_start_time.msecsTo(current_time) > 30000:  # 30 secondes
            self.log("L'impression prend trop de temps. Tentative d'impression alternative...")
            self.print_check_timer.stop()
            #self.print_alternative(self.web_view.page().printer())

    def print_alternative(self, printer):
        try:
            self.log("Tentative d'impression alternative...")
            # Créer un QPainter et commencer l'impression
            painter = QtGui.QPainter()
            if painter.begin(printer):
                # Rendre la page web sur l'imprimante
                self.web_view.render(painter)
                painter.end()
                self.log("Impression alternative terminée.")
            else:
                self.log("Échec de l'initialisation du QPainter pour l'impression alternative.")
        except Exception as e:
            self.log(f"Erreur lors de l'impression alternative : {str(e)}")

    def log(self, message):
        self.log_output.append(message)
        print(f"HtmlGuideViewer: {message}")

# Classe principale de la fenêtre
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.guide_viewer = None
        self.temp_dir = tempfile.mkdtemp()
        
        self.setWindowTitle("Upload DIGI Pro")
        self.asset_path = get_asset_path()
        if not self.asset_path:
            QtWidgets.QMessageBox.critical(self, "Erreur", "Impossible de trouver le dossier asset.")
            sys.exit(1)
        
        self.models_info = scan_models_and_configs(self.asset_path)
        print("Modèles détectés :")
        for model in self.models_info:
            print(f"- {model}")
        self.resize(500, 600)
        self.center()
        self.set_icon()
        self.init_ui()
        self.create_menu()
        self.set_theme("dark")

    def show_guide(self):
        if not hasattr(self, 'guide_viewer') or not self.guide_viewer.isVisible():
            self.guide_viewer = HtmlGuideViewer(GUIDE_HTML, self)
            self.guide_viewer.show()
        else:
            self.guide_viewer.activateWindow()

    def set_icon(self):
        # Chemin vers le répertoire de l'application
        app_dir = os.path.dirname(os.path.abspath(__file__))
        # Chemin vers le fichier d'icône dans le répertoire asset
        icon_path = os.path.join(app_dir, "asset", "logogm.png")
        
        # Vérifier si le fichier d'icône existe
        if os.path.exists(icon_path):
            app_icon = QtGui.QIcon()
            app_icon.addFile(icon_path, QtCore.QSize(16,16))
            app_icon.addFile(icon_path, QtCore.QSize(24,24))
            app_icon.addFile(icon_path, QtCore.QSize(32,32))
            app_icon.addFile(icon_path, QtCore.QSize(48,48))
            app_icon.addFile(icon_path, QtCore.QSize(256,256))
            self.setWindowIcon(app_icon)
        else:
            print(f"Fichier d'icône non trouvé : {icon_path}")
        

    def log(self, message):        
        """Ajoute un message au QTextEdit de log et l'affiche dans la console."""
        self.log_output.append(message)
        print(message)


    def create_menu(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu('Fichier')
        file_menu.addAction(self.create_action('Nouveau', 'Ctrl+N', self.new_file))
        file_menu.addAction(self.create_action('Copier le répertoire asset', shortcut=None, callback=self.copy_asset_directory))
        file_menu.addAction(self.create_action('Quitter', 'Ctrl+Q', self.close))
        
        edit_menu = menubar.addMenu('Édition')
        edit_menu.addAction(self.create_action('Effacer les logs', shortcut=None, callback=self.clear_logs))
        
        view_menu = menubar.addMenu('Affichage')
        theme_menu = view_menu.addMenu('Thème')
        theme_menu.addAction(self.create_action('Sombre', 'Ctrl+D', callback=lambda: self.set_theme("dark")))
        theme_menu.addAction(self.create_action('Clair', 'Ctrl+L', callback=lambda: self.set_theme("light")))
        
        help_menu = menubar.addMenu('Aide')
        help_menu.addAction(self.create_action('Guide d\'utilisation', shortcut=None, callback=self.show_guide))
        help_menu.addAction(self.create_action('À propos', shortcut=None, callback=self.show_about))

    def show_guide(self):
        if not self.guide_viewer:
            self.guide_viewer = HtmlGuideViewer(GUIDE_HTML, self)
        self.guide_viewer.show()
    
    def show_help(self):
        if os.path.exists(self.guide_path):
            if sys.platform == "win32":
                os.startfile(self.guide_path)
            elif sys.platform == "darwin":  # macOS
                subprocess.call(["open", self.guide_path])
            else:  # linux variants
                subprocess.call(["xdg-open", self.guide_path])
        else:
            QtWidgets.QMessageBox.warning(self, "Erreur", "Le guide d'utilisation n'a pas pu être extrait.")

    def copy_asset_directory(self):
        if getattr(sys, 'frozen', False):
            # L'application est un exécutable
            source_asset = os.path.join(sys._MEIPASS, 'asset')
        else:
            # L'application est exécutée à partir du script
            source_asset = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'asset')

        target_asset = os.path.join(os.path.dirname(sys.executable), 'asset')

        if os.path.exists(target_asset):
            reply = QtWidgets.QMessageBox.question(self, 'Confirmer l\'écrasement',
                "Un répertoire 'asset' existe déjà. Voulez-vous l'écraser ?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.No:
                return

        try:
            if os.path.exists(target_asset):
                shutil.rmtree(target_asset)
            shutil.copytree(source_asset, target_asset)
            QtWidgets.QMessageBox.information(self, "Succès", "Le répertoire 'asset' a été copié avec succès.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erreur", f"Impossible de copier le répertoire 'asset': {str(e)}")


    def closeEvent(self, event):
        # Nettoyage du fichier temporaire lors de la fermeture de l'application
        try:
            os.remove(self.guide_path)
            os.rmdir(self.temp_dir)
        except:
            pass
        super().closeEvent(event)   

    def create_action(self, text, shortcut, callback):
        action = QtWidgets.QAction(text, self)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(callback)
        return action

    def set_theme(self, theme):
        if theme == "dark":
            self.setStyleSheet(DARK_STYLE)
            self.setPalette(self.dark_palette())
        else:
            self.setStyleSheet(LIGHT_STYLE)
            self.setPalette(self.light_palette())
        
        # Mettre à jour la palette pour les widgets enfants
        for widget in self.findChildren(QtWidgets.QWidget):
            widget.setPalette(self.palette())
            widget.update()

    def dark_palette(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(44, 62, 80))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(52, 73, 94))
        palette.setColor(QPalette.AlternateBase, QColor(44, 62, 80))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(52, 73, 94))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        return palette

    def light_palette(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(236, 240, 241))
        palette.setColor(QPalette.WindowText, QColor(44, 62, 80))
        palette.setColor(QPalette.Base, Qt.white)
        palette.setColor(QPalette.AlternateBase, QColor(236, 240, 241))
        palette.setColor(QPalette.ToolTipBase, QColor(44, 62, 80))
        palette.setColor(QPalette.ToolTipText, QColor(44, 62, 80))
        palette.setColor(QPalette.Text, QColor(44, 62, 80))
        palette.setColor(QPalette.Button, Qt.white)
        palette.setColor(QPalette.ButtonText, QColor(44, 62, 80))
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(41, 128, 185))
        palette.setColor(QPalette.Highlight, QColor(41, 128, 185))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        return palette

    def new_file(self):
        self.log_output.clear()
        self.ip_input.clear()
        self.slideshow_movie_checkbox.setChecked(False)
        self.bandeau_checkbox.setChecked(False)
        self.log("Nouvelle session commencée.")

    def clear_logs(self):
        self.log_output.clear()
        self.log("Logs effacés.")

    def show_about(self):
        title = "À propos de Upload DIGI Pro"
        version = "Version 1.1.0"
        description = (
            "Upload DIGI Pro permet aux utilisateurs de gérer facilement l'upload de différents types de contenus "
            "multimédias vers les balances DIGI. Elle prend en charge l'upload de diaporamas (slideshow), de movie, ainsi "
            "que de bandeaux reglementaire poids (fichiers .ini et .bmp).\n\n"
            "Fonctionnalités principales :\n"
            "- Sélection de Modèle : Choisissez parmi plusieurs modèles disponibles pour adapter l'upload aux besoins spécifiques.\n"
            "- Choix du Magasin : Sélectionnez le magasin approprié pour le contenu à uploader.\n"
            "- Connexion FTP : Entrez les informations de connexion (adresse IP, identifiant, mot de passe) pour établir une connexion sécurisée au serveur FTP.\n"
            "- Options d'Upload : Choisissez entre l'upload de diaporamas et de films ou l'upload de bandeaux, selon vos besoins.\n"
            "- Suivi des Actions : Suivez le processus d'upload en temps réel grâce à un journal d'activité intégré qui affiche tous les messages et erreurs.\n"
            "- Gestion des Erreurs : Recevez des notifications claires en cas d'erreurs lors de la connexion ou de l'upload, facilitant ainsi le dépannage."
        )
        
        about_text = f"{title}\n\n{version}\n\n{description}\n\nCréé par CAHAGNE Clément"
        
        QtWidgets.QMessageBox.about(self, title, about_text)    

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def init_menu(self):
        menubar = self.menuBar()
        helpMenu = menubar.addMenu('Aide')
        
        aboutAction = QtWidgets.QAction('À propos', self)
        aboutAction.triggered.connect(self.show_about)
        helpMenu.addAction(aboutAction)

    def init_ui(self):
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)

        form_layout = QtWidgets.QFormLayout()
        self.modele_combo = QtWidgets.QComboBox()
        self.modele_combo.addItems(self.models_info.keys())
        self.modele_combo.currentIndexChanged.connect(self.update_magasins)
        form_layout.addRow("Modèle :", self.modele_combo)

        self.magasin_combo = QtWidgets.QComboBox()
        form_layout.addRow("Magasin :", self.magasin_combo)

        self.ip_input = QtWidgets.QLineEdit()
        form_layout.addRow("IP Balance :", self.ip_input)

        self.identifiant_input = QtWidgets.QLineEdit("root")
        form_layout.addRow("Identifiant :", self.identifiant_input)

        self.motdepasse_input = QtWidgets.QLineEdit("teraoka")
        self.motdepasse_input.setEchoMode(QtWidgets.QLineEdit.Password)
        form_layout.addRow("Mot de passe :", self.motdepasse_input)

        main_layout.addLayout(form_layout)

        checkbox_layout = QtWidgets.QHBoxLayout()
        self.slideshow_movie_checkbox = QtWidgets.QCheckBox("Upload Slideshow/Movie")
        self.bandeau_checkbox = QtWidgets.QCheckBox("Upload Bandeau")
        checkbox_layout.addWidget(self.slideshow_movie_checkbox)
        checkbox_layout.addWidget(self.bandeau_checkbox)
        main_layout.addLayout(checkbox_layout)

        self.destination_paths = QtWidgets.QTextEdit()
        self.destination_paths.setReadOnly(True)
        self.destination_paths.setFixedHeight(100)
        main_layout.addWidget(QtWidgets.QLabel("Chemins de destination :"))
        main_layout.addWidget(self.destination_paths)

        self.log_output = QtWidgets.QTextEdit()
        self.log_output.setReadOnly(True)
        main_layout.addWidget(self.log_output)

        self.upload_btn = QtWidgets.QPushButton("Upload")
        self.upload_btn.setStyleSheet("background-color: #4CAF50; color: white; font-size: 16px;")
        self.upload_btn.clicked.connect(self.upload)
        self.upload_btn.setFixedHeight(40)
        main_layout.addWidget(self.upload_btn)

        self.slideshow_movie_checkbox.stateChanged.connect(self.update_upload_button_state)
        self.bandeau_checkbox.stateChanged.connect(self.update_upload_button_state)
        self.slideshow_movie_checkbox.stateChanged.connect(self.update_destination_paths)
        self.bandeau_checkbox.stateChanged.connect(self.update_destination_paths)

        self.update_magasins()
        self.update_destination_paths()
        self.update_upload_button_state()

        self.setStyleSheet("""
            QWidget { background-color: #2C3E50; color: white; font-family: Arial; font-size: 14px; }
            QLabel { color: #ECF0F1; }
            QComboBox, QLineEdit { background-color: #34495E; color: #ECF0F1; border: 1px solid #7F8C8D; padding: 5px; }
            QCheckBox { color: #ECF0F1; }
            QPushButton { background-color: #27AE60; color: white; font-size: 16px; border-radius: 5px; padding: 10px 15px; }
            QPushButton:hover { background-color: #2ECC71; }
            QTextEdit { background-color: #34495E; color: #ECF0F1; border: 1px solid #7F8C8D; }
        """)

       



    def update_magasins(self):
        modele = self.modele_combo.currentText()
        self.magasin_combo.clear()
        print(f"Mise à jour des magasins pour le modèle : {modele}")

        self.log_output.clear()
        self.log(f"Modèle sélectionné : {modele}")

        if modele in self.models_info:
            magasins = self.models_info[modele]['magasins'].keys()
            self.magasin_combo.addItems(magasins)
            self.log(f"Magasins disponibles : {', '.join(magasins)}")
        else:
            self.log(f"Aucun magasin trouvé pour le modèle : {modele}")

        self.update_destination_paths()

    def normalOutputWritten(self, text):
        """Append text to the QTextEdit."""
        cursor = self.log_output.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.log_output.setTextCursor(cursor)
        self.log_output.ensureCursorVisible()

    def update_upload_button_state(self):
        if self.slideshow_movie_checkbox.isChecked() or self.bandeau_checkbox.isChecked():
            self.upload_btn.setEnabled(True)
        else:
            self.upload_btn.setEnabled(False)

    def update_destination_paths(self):
        modele = self.modele_combo.currentText()
        paths_text = ""

        if self.slideshow_movie_checkbox.isChecked():
            if modele in self.models_info:
                slideshow_paths = self.models_info[modele]['paths']['dest_slideshow']
                movie_path = self.models_info[modele]['paths']['dest_movie']
                paths_text += "Slideshow :\n"
                for path in slideshow_paths:
                    paths_text += f" - {path}\n"
                paths_text += f"Movie : {movie_path}\n"
            else:
                paths_text += "Chemins de slideshow et movie non définis pour ce modèle.\n"

        if self.bandeau_checkbox.isChecked():
            if modele in self.models_info:
                dest_ini_list = self.models_info[modele]['paths']['dest_ini']
                dest_img_list = self.models_info[modele]['paths']['dest_img']
                paths_text += "Fichiers INI :\n"
                for path in dest_ini_list:
                    paths_text += f" - {path}\n"
                paths_text += "Fichiers BMP :\n"
                for path in dest_img_list:
                    paths_text += f" - {path}\n"
            else:
                paths_text += "Chemins de bandeau non définis pour ce modèle.\n"

        self.destination_paths.setText(paths_text)

    def upload(self):
        modele = self.modele_combo.currentText()
        magasin = self.magasin_combo.currentText()
        ip = self.ip_input.text().strip()
        identifiant = self.identifiant_input.text()
        motdepasse = self.motdepasse_input.text()

        if not ip:
            self.log("Erreur : L'adresse IP ne peut pas être vide.")
            return

        self.log("Début du processus d'upload...")
        self.log(f"Modèle sélectionné : {modele}")
        self.log(f"Magasin sélectionné : {magasin}")
        self.log(f"IP de la balance : {ip}")

        try:
            ftp = ftplib.FTP(ip)
            self.log("Connexion au serveur FTP...")
            ftp.login(identifiant, motdepasse)
            self.log("Connexion réussie.")

            try:
                # Upload Slideshow/Movie if checked
                if self.slideshow_movie_checkbox.isChecked():
                    print("Option sélectionnée : Upload Slideshow/Movie")
                    if modele in self.models_info:
                        dossiers = self.models_info[modele]['magasins'][magasin]
                        dossier_slideshow = dossiers["slideshow"]
                        dossier_movie = dossiers["movie"]
                        self.log(f"Dossier Slideshow source: {dossier_slideshow}")
                        self.log(f"Dossier Movie source: {dossier_movie}")

                        destinations_slideshow = self.models_info[modele]['paths']['dest_slideshow']
                        dossier_destination_movie = self.models_info[modele]['paths']['dest_movie']

                        # Upload slideshow
                        for dest in destinations_slideshow:
                            self.log(f"Début de l'upload du slideshow vers le répertoire {dest}...")
                            try:
                                ftp.cwd(dest)
                                for fichier in os.listdir(dossier_slideshow):
                                    chemin = os.path.join(dossier_slideshow, fichier)
                                    self.log(f"Envoi de {fichier}")
                                    with open(chemin, 'rb') as file:
                                        ftp.storbinary('STOR ' + fichier, file)
                                self.log(f"Slideshow uploadé avec succès vers le répertoire {dest}.")
                            except ftplib.error_perm:
                                self.log(f"Le répertoire {dest} n'existe pas. Passage au suivant.")

                        # Upload movie
                        try:
                            ftp.cwd(dossier_destination_movie)
                            if os.path.exists(dossier_movie):
                                self.log("Début de l'upload du film...")
                                for fichier in os.listdir(dossier_movie):
                                    chemin = os.path.join(dossier_movie, fichier)
                                    self.log(f"Envoi de {fichier}")
                                    with open(chemin, 'rb') as file:
                                        ftp.storbinary('STOR ' + fichier, file)
                                self.log("Film uploadé avec succès.")
                        except ftplib.error_perm:
                            self.log(f"Le répertoire {dossier_destination_movie} n'existe pas.")

                # Upload Bandeau if checked
                if self.bandeau_checkbox.isChecked():
                    self.log("Option sélectionnée : Upload Bandeau")
                    source_dir = os.path.join(self.asset_path, modele)
                    ini_files = [f for f in os.listdir(source_dir) if f.endswith('.ini') and f != 'config.ini']
                    bmp_files = [f for f in os.listdir(source_dir) if f.endswith('.bmp')]
                    png_files = [f for f in os.listdir(source_dir) if f.endswith('.png')]  # Ajout des fichiers PNG

                    if modele in self.models_info:
                        dest_ini_list = self.models_info[modele]['paths']['dest_ini']
                        dest_img_list = self.models_info[modele]['paths']['dest_img']
                    else:
                        self.log(f"Erreur : Impossible de trouver les chemins de destination pour le modèle {modele}")
                        return

                    # Create backup directory
                    backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backup", modele.replace(" ", ""))
                    os.makedirs(backup_dir, exist_ok=True)

                    # Upload ini files
                    for dest_ini in dest_ini_list:
                        dest_ini = dest_ini.rstrip('/')
                        self.log(f"Upload des fichiers INI vers : {dest_ini}")
                        for file_name in ini_files:
                            remote_file_path = os.path.join(dest_ini, file_name).replace('\\', '/').replace('//', '/')
                            local_backup_path = os.path.join(backup_dir, file_name)
                            try:
                                with open(local_backup_path, 'wb') as file:
                                    ftp.retrbinary(f'RETR {remote_file_path}', file.write)
                                self.log(f"Backup de {file_name} terminé.")
                            except ftplib.error_perm as e:
                                self.log(f"Fichier {file_name} non trouvé sur le serveur : {e}")

                            with open(os.path.join(source_dir, file_name), 'rb') as file:
                                ftp.storbinary(f'STOR {remote_file_path}', file)
                            self.log(f"Fichier {file_name} uploadé vers {dest_ini}")

                    # Upload bmp and png files
                    for dest_img in dest_img_list:
                        dest_img = dest_img.rstrip('/')
                        self.log(f"Upload des fichiers BMP et PNG vers : {dest_img}")
                        
                        # Upload BMP files
                        for file_name in bmp_files:
                            remote_file_path = os.path.join(dest_img, file_name).replace(os.path.sep, '/')
                            local_backup_path = os.path.join(backup_dir, file_name)
                            try:
                                with open(local_backup_path, 'wb') as file:
                                    ftp.retrbinary(f'RETR {remote_file_path}', file.write)
                                self.log(f"Backup de {file_name} terminé.")
                            except ftplib.error_perm as e:
                                self.log(f"Fichier {file_name} non trouvé sur le serveur : {e}")

                            with open(os.path.join(source_dir, file_name), 'rb') as file:
                                ftp.storbinary(f'STOR {remote_file_path}', file)
                            self.log(f"Fichier {file_name} uploadé vers {dest_img}")
                        
                        # Upload PNG files
                        for file_name in png_files:
                            remote_file_path = os.path.join(dest_img, file_name).replace(os.path.sep, '/')
                            local_backup_path = os.path.join(backup_dir, file_name)
                            try:
                                with open(local_backup_path, 'wb') as file:
                                    ftp.retrbinary(f'RETR {remote_file_path}', file.write)
                                self.log(f"Backup de {file_name} terminé.")
                            except ftplib.error_perm as e:
                                self.log(f"Fichier {file_name} non trouvé sur le serveur : {e}")

                            with open(os.path.join(source_dir, file_name), 'rb') as file:
                                ftp.storbinary(f'STOR {remote_file_path}', file)
                            self.log(f"Fichier {file_name} uploadé vers {dest_img}")

            finally:
                # Ensure FTP connection is properly closed
                try:
                    ftp.quit()
                except:
                    ftp.close()
                self.log("Déconnexion du serveur FTP.")
                self.log("Opération terminée.")

        except Exception as e:
            self.log(f"Erreur lors de l'upload : {str(e)}")
            try:
                ftp.quit()
            except:
                pass

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    win = MainWindow()
    win.show()
    app.exec_()