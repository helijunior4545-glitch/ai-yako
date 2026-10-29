import pathlib
#!/usr/bin/env python3
"""AI_YAKO_DESKTOP_V1041: Janela desktop Linux do AI Yako, sem browser externo."""
import importlib.util
import os
from pathlib import Path
import sys
import threading

ROOT = Path(__file__).resolve().parent
ENGINE = ROOT / 'yako_v1034'


def main():
    try:
        from PySide6.QtCore import QUrl, Qt
        from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QToolBar, QToolButton
        from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings
        from PySide6.QtWebEngineWidgets import QWebEngineView
    except ImportError as exc:
        print('Dependencia Qt ausente:', exc, file=sys.stderr)
        print('Instale no ambiente virtual: python3 -m pip install PySide6 PySide6-Addons', file=sys.stderr)
        return 2

    if not (ENGINE / 'yako_v102_server.py').is_file():
        print('Servidor V10.34 nao encontrado:', ENGINE, file=sys.stderr)
        return 2

    sys.path.insert(0, str(ENGINE))
    spec = importlib.util.spec_from_file_location('yako_desktop_v1034_server', ENGINE / 'yako_v102_server.py')
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        module.init_db()
        server = module.ThreadingHTTPServer(('127.0.0.1', 0), module.Handler)
    except Exception as exc:
        print('Falha ao inicializar motor local:', repr(exc), file=sys.stderr)
        return 1

    worker = threading.Thread(target=server.serve_forever, name='ai-yako-local', daemon=True)
    worker.start()
    url = f'http://127.0.0.1:{server.server_port}/'

    app = QApplication(sys.argv)
    # YAKO_BRAND_V1043
    from PySide6.QtGui import QIcon
    app.setWindowIcon(QIcon(str(pathlib.Path(__file__).resolve().parent / "brand" / "yako-256.png")))
    app.setApplicationName('AI Yako')
    app.setOrganizationName('AI Yako')

    class LocalPage(QWebEnginePage):
        def acceptNavigationRequest(self, target, nav_type, is_main_frame):
            return (target.scheme() == 'http'
                    and target.host() == '127.0.0.1'
                    and target.port() == server.server_port)

    class Window(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle('AI Yako — Financial Intelligence')
            self.resize(1280, 850)
            self.setMinimumSize(420, 560)
            self.view = QWebEngineView(self)
            self.profile = QWebEngineProfile(self.view)
            self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.MemoryHttpCache)
            self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)
            self.page = LocalPage(self.profile, self.view)
            self.page.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, False)
            self.view.setPage(self.page)
            self.setCentralWidget(self.view)
            self.view.load(QUrl(url))
            # AI_YAKO_V10631_RELOAD — Native toolbar; no inline JS or CSP changes.
            toolbar = QToolBar('Atualização da interface', self)
            toolbar.setMovable(False)
            toolbar.setFloatable(False)
            toolbar.setObjectName('yakoReloadToolbar')
            toolbar.setStyleSheet('''
                QToolBar#yakoReloadToolbar {
                    background: #161718; border: 0;
                    border-bottom: 1px solid #303236; spacing: 6px; padding: 3px 9px;
                }
                QToolButton {
                    color: #dce2d5; background: #252827;
                    border: 1px solid #454b40; border-radius: 8px;
                    padding: 5px 12px; font-size: 12px;
                }
                QToolButton:hover { background: #30382b; border-color: #c9ff47; }
                QToolButton:pressed { background: #3b4930; }
            ''')
            self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
            reload_button = QToolButton(self)
            reload_button.setText('↻  Atualizar')
            reload_button.setToolTip('Recarregar interface (F5 ou Ctrl+R)')
            reload_button.clicked.connect(lambda: self.yako_reload(False))
            toolbar.addWidget(reload_button)
            hard_button = QToolButton(self)
            hard_button.setText('⟳')
            hard_button.setToolTip('Recarregar sem cache (Ctrl+Shift+R)')
            hard_button.clicked.connect(lambda: self.yako_reload(True))
            toolbar.addWidget(hard_button)
            from PySide6.QtGui import QShortcut, QKeySequence
            self._reload_shortcuts = []
            for combo, bypass in (('F5', False), ('Ctrl+R', False), ('Ctrl+Shift+R', True)):
                shortcut = QShortcut(QKeySequence(combo), self)
                shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
                shortcut.activated.connect(lambda bypass=bypass: self.yako_reload(bypass))
                self._reload_shortcuts.append(shortcut)
            self._yako_reload_pending = False

        def yako_reload(self, bypass_cache=False):
            if self._yako_reload_pending:
                return
            self._yako_reload_pending = True
            # Read-only inspection; JS does not navigate, fetch, or mutate app state.
            probe = """(function(){
                const p=document.getElementById('prompt');
                const draft=!!(p&&p.value&&p.value.trim());
                const busy=!!(document.querySelector('.yako-processing,.yako-v1040-processing,.yako46-busy,.yako-thinking-v1039.is-active'));
                return {draft:draft,busy:busy};
            })()"""
            def finish(state):
                self._yako_reload_pending = False
                state = state if isinstance(state, dict) else {}
                if state.get('draft') or state.get('busy'):
                    answer = QMessageBox.question(
                        self, 'AI Yako — Atualizar',
                        'Existe texto não enviado ou uma análise em andamento. '
                        'Recarregar pode interromper o processamento ou descartar o rascunho. Continuar?',
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No,
                    )
                    if answer != QMessageBox.StandardButton.Yes:
                        return
                if bypass_cache:
                    try:
                        action = QWebEnginePage.WebAction.ReloadAndBypassCache
                        self.page.triggerAction(action)
                        return
                    except (AttributeError, TypeError):
                        # Older Qt versions: clear memory cache then reload.
                        self.profile.clearHttpCache()
                self.view.reload()
            self.page.runJavaScript(probe, finish)


        def closeEvent(self, event):
            self.view.setUrl(QUrl('about:blank'))
            super().closeEvent(event)

    window = Window()
    # AI_YAKO_V1044_DESKTOP_ICON
    from PySide6.QtGui import QIcon
    _yako_icon = QIcon(str(ROOT / "brand" / "yako-256.png"))
    if _yako_icon.isNull():
        print("AI Yako: ícone não encontrado", file=sys.stderr)
    else:
        app.setWindowIcon(_yako_icon)
        window.setWindowIcon(_yako_icon)
    window.show()
    try:
        return app.exec()
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=3)


if __name__ == '__main__':
    raise SystemExit(main())
