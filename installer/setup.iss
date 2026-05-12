#define MyAppName "G-MetaMerge"
#define MyAppVersion "1.0"
#define MyAppPublisher "G-MetaMerge"
#define MyAppExeName "g_metamerge.exe"

[Setup]
AppId={{A6F83F0D-8C57-4D59-BD0E-123456789999}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\G-MetaMerge
DefaultGroupName=G-MetaMerge
DisableProgramGroupPage=yes
OutputDir=output
OutputBaseFilename=GMetaMergeSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

SetupIconFile=..\assets\logo\logo.ico
UninstallDisplayIcon={app}\g_metamerge.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create Desktop Icon"; GroupDescription: "Additional Icons:";

[Files]
Source: "..\build\windows\x64\runner\Release\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\G-MetaMerge"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\G-MetaMerge"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch G-MetaMerge"; Flags: nowait postinstall skipifsilent