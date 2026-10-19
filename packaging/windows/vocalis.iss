; Inno Setup Script for Vocalis AI Noise Reduction
; Compatible with Windows 10 and Windows 11 (64-bit)

#define MyAppName "Vocalis"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Void Studio"
#define MyAppURL "https://www.voidstudio.com.br"
#define MyAppExeName "vocalis.exe"

[Setup]
; Unique AppId generated for Vocalis
AppId={{9C83F6A0-1A88-4D56-8A33-28D8A7E0182E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupIconFile=..\..\icon.ico
LicenseFile=..\..\LICENSE
OutputDir=..\..\dist
OutputBaseFilename=Vocalis-Setup-v{#MyAppVersion}-x64
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
DisableProgramGroupPage=yes
VersionInfoVersion={#MyAppVersion}.0
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=AI-Powered Noise Reduction Studio & Virtual Microphone
VersionInfoProductVersion={#MyAppVersion}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "startmenuicon"; Description: "Create Start Menu shortcut"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\logo.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
