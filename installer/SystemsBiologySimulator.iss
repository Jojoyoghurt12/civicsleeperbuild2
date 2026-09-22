[Setup]
AppName=Systems Biology Simulator
AppVersion=1.0.0
AppId={{8B9C6C4D-2C2C-4E15-A111-SystemsBioSim}}
DefaultDirName={autopf}\Systems Biology Simulator
DefaultGroupName=Systems Biology Simulator
OutputDir=.
OutputBaseFilename=SystemsBiologySimulatorSetup-1.0.0
SetupIconFile=assets\app.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "..\dist\SystemsBiologySimulator\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\Systems Biology Simulator"; Filename: "{app}\SystemsBiologySimulator.exe"; IconFilename: "{app}\SystemsBiologySimulator.exe"
Name: "{commondesktop}\Systems Biology Simulator"; Filename: "{app}\SystemsBiologySimulator.exe"; IconFilename: "{app}\SystemsBiologySimulator.exe"; Tasks: desktopicon