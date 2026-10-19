; Inno Setup Script for Vocalis AI Noise Reduction
; Target: Microsoft Windows 10 and Windows 11 (64-bit architecture)
; Maintained by Void Studio (https://www.voidstudio.com.br)

#define RootDir "..\.."

#ifndef MyAppName
  #define MyAppName "Vocalis"
#endif

#ifndef MyAppVersion
  #define MyAppVersion "1.0.0"
#endif

#ifndef MyAppPublisher
  #define MyAppPublisher "Void Studio"
#endif

#ifndef MyAppURL
  #define MyAppURL "https://www.voidstudio.com.br"
#endif

#ifndef MyAppExeName
  #define MyAppExeName "vocalis.exe"
#endif

[Setup]
; Unique application GUID for Vocalis
AppId={{9C83F6A0-1A88-4D56-8A33-28D8A7E0182E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Standard target installation path (User vs System-wide)
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}

; Modern Windows UI & Compatibility
WizardStyle=modern
MinVersion=10.0
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; Dual-mode: Allows installation without elevation (into AppData) or elevated (into Program Files)
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Output configuration
SourceDir={#RootDir}
OutputDir=dist
OutputBaseFilename=Vocalis-Setup-v{#MyAppVersion}-x64
SetupIconFile=icon.ico
LicenseFile=LICENSE
Compression=lzma2/ultra64
SolidCompression=yes

; Process Management & Safe Updates
CloseApplications=yes
CloseApplicationsFilter=*.exe
RestartApplications=no

; Uninstaller configuration
Uninstallable=yes
CreateUninstallRegKey=yes
UninstallDisplayName={#MyAppName} (AI Noise Reduction Studio)
UninstallDisplayIcon={app}\{#MyAppExeName}

; Metadata
VersionInfoVersion={#MyAppVersion}.0
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=AI-Powered Noise Reduction Studio & Virtual Microphone
VersionInfoProductVersion={#MyAppVersion}
VersionInfoCopyright=Copyright (C) 2024-2026 {#MyAppPublisher}

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "startmenuicon"; Description: "Criar atalho no Menu Iniciar"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Core binary and application assets
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "logo.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
