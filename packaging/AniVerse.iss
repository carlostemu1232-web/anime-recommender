[Setup]
AppId={{7A2DCD4E-2B1F-4D7D-A9B2-4E7E0900A001}}
AppName=AniVerse
AppVersion=0.9.0
AppPublisher=AniVerse
DefaultDirName={localappdata}\Programs\AniVerse
DefaultGroupName=AniVerse
OutputDir=..\installer
OutputBaseFilename=AniVerse-0.9.0-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\AniVerse.exe

[Files]
Source: "..\dist\AniVerse\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\AniVerse"; Filename: "{app}\AniVerse.exe"
Name: "{autodesktop}\AniVerse"; Filename: "{app}\AniVerse.exe"

[Run]
Filename: "{app}\AniVerse.exe"; Description: "Launch AniVerse"; Flags: nowait postinstall skipifsilent
