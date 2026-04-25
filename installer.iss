; installer.iss — Inno Setup 6 Script
; Cria o instalador Windows do Controle de Gastos 2026
; Requisito: Inno Setup 6 instalado em C:\Program Files (x86)\Inno Setup 6\

#define AppName      "Controle de Gastos 2026"
#define AppVersion   "1.0.0"
#define AppPublisher "Geral"
#define AppURL       "http://localhost:8501"
#define AppExeName   "launcher.exe"
#define SourceDir    "dist\launcher"

[Setup]
; Identificação única do aplicativo (GUID gerado)
AppId={{B7E3C2A1-4F8D-4B9E-A2C1-D3F5E6A7B8C9}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}

; Instalação por usuário (não requer admin)
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Diretório padrão de instalação
DefaultDirName={autopf}\Controle de Gastos
DefaultGroupName={#AppName}
AllowNoIcons=yes

; Saída
OutputDir=Output
OutputBaseFilename=ControleDeGastos_Setup_v{#AppVersion}
SetupIconFile=icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64

; Wizard visual
WizardStyle=modern
DisableProgramGroupPage=auto
DisableWelcomePage=no
ShowLanguageDialog=no

; Não criar entrada de desinstalação no Painel de Controle se preferir
UninstallDisplayIcon={app}\{#AppExeName}
UninstallDisplayName={#AppName}

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
; Ícone na área de trabalho
Name: "desktopicon"; Description: "Criar ícone na Área de Trabalho"; GroupDescription: "Atalhos:"; Flags: unchecked
; Iniciar automaticamente com o Windows
Name: "startupentry"; Description: "Iniciar {#AppName} com o Windows"; GroupDescription: "Opções:"

[Files]
; Todos os arquivos do pacote PyInstaller
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Menu Iniciar
Name: "{group}\{#AppName}";       Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\icon.ico"
Name: "{group}\Desinstalar";      Filename: "{uninstallexe}"

; Área de trabalho (opcional)
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Registry]
; Adiciona ao startup do Windows se o usuário escolheu
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; \
  ValueType: string; ValueName: "{#AppName}"; \
  ValueData: """{app}\{#AppExeName}"""; \
  Flags: uninsdeletevalue; Tasks: startupentry

[Run]
; Opção de abrir o app após a instalação
Filename: "{app}\{#AppExeName}"; \
  Description: "Abrir {#AppName} agora"; \
  Flags: nowait postinstall skipifsilent

[UninstallRun]
; Para o processo antes de desinstalar
Filename: "taskkill"; Parameters: "/f /im {#AppExeName}"; Flags: runhidden; RunOnceId: "KillApp"
