[Setup]
AppName=Systems Biology Simulator
AppVersion=1.1.1
AppId={{8B9C6C4D-2C2C-4E15-A111-SystemsBioSim}}
DefaultDirName={autopf}\Systems Biology Simulator
DefaultGroupName=Systems Biology Simulator
OutputDir=.
OutputBaseFilename=SystemsBiologySimulatorSetup-1.1.1
SetupIconFile=assets\app.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "..\dist\SystemsBiologySimulator\*"; DestDir: "{app}"; Flags: recursesubdirs
Source: "assets\app.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Systems Biology Simulator"; Filename: "{app}\SystemsBiologySimulator.exe"; IconFilename: "{app}\app.ico"
Name: "{commondesktop}\Systems Biology Simulator"; Filename: "{app}\SystemsBiologySimulator.exe"; IconFilename: "{app}\app.ico"; Tasks: desktopicon